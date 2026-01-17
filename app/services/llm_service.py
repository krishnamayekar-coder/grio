"""LLM Service - OpenAI Interaction"""
from typing import Optional
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.models.chat import ChatRequest, ChatResponse
from app.prompts.griot import GRIOT_SYSTEM_PROMPT

logger = get_logger(__name__)


class LLMService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize LLM service with API key."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def generate_response(self, request: ChatRequest) -> ChatResponse:
        """
        Generate a response using OpenAI API.
        
        Args:
            request: Chat request with user message and context
            
        Returns:
            ChatResponse with generated message
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": GRIOT_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            return ChatResponse(
                user_id=request.user_id,
                message=content,
                model=self.model
            )
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
