"""Voice Service - Speech-to-Text and Text-to-Speech"""
import io
from typing import Optional
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VoiceService:
    """Service for voice interaction - speech-to-text and text-to-speech."""
    
    def __init__(self):
        """Initialize voice service."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def speech_to_text(self, audio_file: bytes) -> str:
        """
        Convert speech to text using OpenAI Whisper API.
        
        Args:
            audio_file: Audio file bytes (supports mp3, mp4, mpeg, mpga, m4a, wav, webm)
            
        Returns:
            Transcribed text
        """
        try:
            # Create a file-like object from bytes
            audio_stream = io.BytesIO(audio_file)
            audio_stream.name = "audio.wav"
            
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_stream,
                language="en"
            )
            
            text = transcript.text
            logger.info(f"Transcribed speech to text: {text[:100]}...")
            return text
        except Exception as e:
            logger.error(f"Error transcribing speech: {str(e)}")
            raise
    
    async def text_to_speech(self, text: str, voice: str = "nova") -> bytes:
        """
        Convert text to speech using OpenAI TTS API.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Audio file bytes (MP3 format)
        """
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            logger.info(f"Generated speech from text: {text[:100]}...")
            return response.content
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            raise
