"""Real-time Voice WebSocket Endpoint - Listen for wake word "Griot" then process queries"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import io

from app.services.voice_service import VoiceService
from app.services.llm_service import LLMService
from app.services.wake_word_service import WakeWordDetector
from app.models.chat import ChatRequest
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

voice_service = VoiceService()
llm_service = LLMService()
wake_word_detector = WakeWordDetector(wake_word="griot")


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections = []
    
    def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)


manager = ConnectionManager()


@router.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice interaction.
    
    Protocol:
    1. Client sends audio chunks as binary data
    2. Server listens for wake word "griot"
    3. Once wake word detected, server indicates readiness
    4. Client sends the actual query audio
    5. Server transcribes, generates response, and sends back audio
    
    JSON Messages:
    - {"type": "status", "message": "listening"} - Server is listening for wake word
    - {"type": "wake_word_detected"} - Wake word was detected, ready for query
    - {"type": "processing"} - Server is processing the request
    - {"type": "response", "audio": "<base64>"} - Server's audio response
    - {"type": "error", "message": "..."} - Error occurred
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        # Tell client we're listening for wake word
        await websocket.send_json({
            "type": "status",
            "message": "🎤 Listening for 'Griot'... say 'Griot' to activate"
        })
        
        # Accumulate audio for transcription
        audio_buffer = io.BytesIO()
        
        while True:
            # Receive audio chunk from client
            data = await websocket.receive()
            
            if "bytes" in data:
                # Audio chunk received
                audio_buffer.write(data["bytes"])
                
                # Transcribe accumulated audio (every ~2 seconds of audio)
                if audio_buffer.tell() > 32000:  # ~1 second at 16kHz
                    audio_bytes = audio_buffer.getvalue()
                    audio_buffer = io.BytesIO()
                    
                    try:
                        # Transcribe audio
                        transcribed_text = await voice_service.speech_to_text(audio_bytes)
                        logger.info(f"Transcribed: {transcribed_text}")
                        
                        # Check for wake word
                        wake_detected, user_query = wake_word_detector.detect(transcribed_text)
                        
                        if wake_detected:
                            # Wake word detected!
                            await websocket.send_json({
                                "type": "wake_word_detected",
                                "message": f"✨ Hello! I'm listening... what would you like to know?"
                            })
                            
                            # Now listen for the actual query
                            await websocket.send_json({
                                "type": "status",
                                "message": "🎯 Listening for your question..."
                            })
                            
                            # Accumulate next audio for the query
                            query_audio_buffer = io.BytesIO()
                            query_accumulated = False
                            
                            while True:
                                query_data = await websocket.receive()
                                
                                if "bytes" in query_data:
                                    query_audio_buffer.write(query_data["bytes"])
                                    query_accumulated = True
                                
                                elif "text" in query_data:
                                    # Signal to process query
                                    json_data = json.loads(query_data["text"])
                                    if json_data.get("action") == "process_query":
                                        break
                            
                            if query_accumulated:
                                # Process the query
                                await websocket.send_json({
                                    "type": "processing",
                                    "message": "📖 Processing your query..."
                                })
                                
                                query_audio = query_audio_buffer.getvalue()
                                
                                # Transcribe query
                                query_text = await voice_service.speech_to_text(query_audio)
                                logger.info(f"User query: {query_text}")
                                
                                # Generate response
                                chat_request = ChatRequest(
                                    user_id="voice_ws_user",
                                    message=query_text
                                )
                                response = await llm_service.generate_response(chat_request)
                                logger.info(f"Generated response: {response.message[:100]}...")
                                
                                # Convert response to speech
                                response_audio = await voice_service.text_to_speech(
                                    response.message,
                                    voice="nova"
                                )
                                
                                # Send response
                                import base64
                                await websocket.send_json({
                                    "type": "response",
                                    "text": response.message,
                                    "audio": base64.b64encode(response_audio).decode('utf-8')
                                })
                                
                                # Reset for next interaction
                                await websocket.send_json({
                                    "type": "status",
                                    "message": "🎤 Listening for 'Griot' again..."
                                })
                                audio_buffer = io.BytesIO()
                                break
                        else:
                            # No wake word yet, keep listening
                            await websocket.send_json({
                                "type": "waiting",
                                "heard": transcribed_text,
                                "message": "🎤 Say 'Griot' to activate..."
                            })
                    
                    except Exception as e:
                        logger.error(f"Transcription error: {str(e)}")
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Could not transcribe audio: {str(e)}"
                        })
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        manager.disconnect(websocket)
