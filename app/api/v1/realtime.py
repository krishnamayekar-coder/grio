"""Real-time Voice WebSocket Endpoint - Listen for wake word "Griot" then process queries"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import io
import asyncio

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
    manager.connect(websocket)
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
            try:
                # Receive audio chunk from client
                data = await websocket.receive()
            except Exception as e:
                logger.error(f"Error receiving data: {str(e)}")
                break
            
            if "bytes" in data:
                # Audio chunk received (already in WAV format from client)
                audio_buffer.write(data["bytes"])
                
                # Transcribe accumulated audio when we have enough data
                if audio_buffer.tell() > 8000:  # Enough data to transcribe
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
                            
                            # Now listen for the actual query with a timeout
                            await websocket.send_json({
                                "type": "status",
                                "message": "🎯 Listening for your question (listening for up to 5 seconds)..."
                            })
                            
                            # Accumulate next audio for the query
                            query_audio_buffer = io.BytesIO()
                            query_start_time = None
                            last_audio_time = None
                            query_timeout = 5.0  # Max 5 seconds to listen
                            silence_timeout = 2.0  # 2 seconds of silence = end of query
                            
                            try:
                                while True:
                                    try:
                                        # Wait for audio with short timeout
                                        query_data = await asyncio.wait_for(
                                            websocket.receive(),
                                            timeout=0.1
                                        )
                                        
                                        if "bytes" in query_data:
                                            if query_start_time is None:
                                                query_start_time = asyncio.get_event_loop().time()
                                            
                                            query_audio_buffer.write(query_data["bytes"])
                                            last_audio_time = asyncio.get_event_loop().time()
                                    
                                    except asyncio.TimeoutError:
                                        # Check if we should stop listening
                                        current_time = asyncio.get_event_loop().time()
                                        
                                        # If we have audio and silence timeout reached
                                        if query_start_time is not None and last_audio_time is not None:
                                            time_since_audio = current_time - last_audio_time
                                            if time_since_audio > silence_timeout:
                                                logger.info(f"Silence detected ({time_since_audio:.1f}s), ending query")
                                                break
                                            
                                            # Check total timeout
                                            total_time = current_time - query_start_time
                                            if total_time > query_timeout:
                                                logger.info(f"Total timeout reached ({total_time:.1f}s), ending query")
                                                break
                                        
                                        continue
                            
                            except Exception as e:
                                logger.error(f"Error receiving query audio: {str(e)}")
                            
                            # Process the query if we have audio
                            if query_audio_buffer.tell() > 0:
                                query_audio = query_audio_buffer.getvalue()
                                logger.info(f"Query audio size: {len(query_audio)} bytes")
                                
                                await websocket.send_json({
                                    "type": "processing",
                                    "message": "📖 Processing your query..."
                                })
                                
                                try:
                                    # Transcribe query
                                    logger.info("Transcribing query audio...")
                                    query_text = await voice_service.speech_to_text(query_audio)
                                    logger.info(f"Query transcribed: '{query_text}'")
                                    
                                    if query_text.strip():
                                        # Generate response
                                        logger.info("Generating response...")
                                        chat_request = ChatRequest(
                                            user_id="voice_ws_user",
                                            message=query_text
                                        )
                                        response = await llm_service.generate_response(chat_request)
                                        logger.info(f"Response generated: {response.message[:100]}...")
                                        
                                        # Convert response to speech
                                        logger.info("Converting response to speech...")
                                        response_audio = await voice_service.text_to_speech(
                                            response.message,
                                            voice="nova"
                                        )
                                        logger.info(f"Audio response size: {len(response_audio)} bytes")
                                        
                                        # Send response
                                        import base64
                                        await websocket.send_json({
                                            "type": "response",
                                            "text": response.message,
                                            "audio": base64.b64encode(response_audio).decode('utf-8')
                                        })
                                    else:
                                        logger.warning("Query text is empty after transcription")
                                        await websocket.send_json({
                                            "type": "error",
                                            "message": "Could not transcribe your question. Please try again."
                                        })
                                
                                except Exception as e:
                                    logger.error(f"Error processing query: {str(e)}", exc_info=True)
                                    await websocket.send_json({
                                        "type": "error",
                                        "message": f"Error: {str(e)}"
                                    })
                            else:
                                logger.warning("No audio received for query")
                                await websocket.send_json({
                                    "type": "error",
                                    "message": "No audio detected after wake word. Please try again."
                                })
                            
                            # Reset for next interaction
                            await websocket.send_json({
                                "type": "status",
                                "message": "🎤 Listening for 'Griot' again..."
                            })
                            audio_buffer = io.BytesIO()
                            # Continue the outer loop to keep listening
                            continue
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
