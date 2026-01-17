"""Chat API Endpoints"""
from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)
llm_service = LLMService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat request and return a response from the Griot AI.
    
    Args:
        request: Chat request containing user message and optional context
        
    Returns:
        ChatResponse with the AI's response
    """
    try:
        logger.info(f"Chat request from user: {request.user_id}")
        response = await llm_service.generate_response(request)
        return response
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
