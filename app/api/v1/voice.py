"""Voice API Endpoints - Speech Input/Output"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import io

from app.services.voice_service import VoiceService
from app.services.llm_service import LLMService
from app.models.chat import ChatRequest, ChatResponse
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)
voice_service = VoiceService()
llm_service = LLMService()


@router.post("/voice")
async def voice_interaction(audio: UploadFile = File(...)):
    """
    Listen to voice input, process it, and respond with voice output.
    
    This endpoint:
    1. Transcribes the audio (speech-to-text)
    2. Generates a Griot response
    3. Converts response to speech (text-to-speech)
    4. Returns audio file
    
    Args:
        audio: Audio file (mp3, wav, m4a, etc.)
        
    Returns:
        Audio response from Griot (MP3)
    """
    try:
        # Read audio file
        logger.info(f"Received audio file: {audio.filename}")
        audio_bytes = await audio.read()
        
        # Convert speech to text
        logger.info("Transcribing speech...")
        user_message = await voice_service.speech_to_text(audio_bytes)
        logger.info(f"User said: {user_message}")
        
        # Generate Griot response
        logger.info("Generating response...")
        chat_request = ChatRequest(
            user_id="voice_user",
            message=user_message
        )
        response = await llm_service.generate_response(chat_request)
        logger.info(f"Generated response: {response.message[:100]}...")
        
        # Convert response to speech
        logger.info("Converting response to speech...")
        audio_response = await voice_service.text_to_speech(
            response.message,
            voice="nova"  # Griot's voice
        )
        
        return StreamingResponse(
            io.BytesIO(audio_response),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=griot_response.mp3"}
        )
        
    except Exception as e:
        logger.error(f"Error in voice interaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/text")
async def text_to_speech_only(text: str, voice: str = "nova"):
    """
    Convert text to speech without speech recognition.
    
    Args:
        text: Text to convert to speech
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        
    Returns:
        Audio response (MP3)
    """
    try:
        logger.info(f"Converting text to speech: {text[:50]}...")
        audio_response = await voice_service.text_to_speech(text, voice)
        
        return StreamingResponse(
            io.BytesIO(audio_response),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=griot_response.mp3"}
        )
    except Exception as e:
        logger.error(f"Error converting text to speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
