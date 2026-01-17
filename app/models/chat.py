"""Chat Request and Response Models"""
from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request schema."""
    
    user_id: str = Field(..., description="Unique user identifier")
    message: str = Field(..., description="User's message")
    context: Optional[Dict] = Field(default=None, description="Optional context data")
    conversation_id: Optional[str] = Field(default=None, description="Optional conversation ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "message": "Tell me a story about ancient civilizations",
                "context": {"mood": "educational"},
                "conversation_id": "conv456"
            }
        }


class ChatResponse(BaseModel):
    """Chat response schema."""
    
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="AI response message")
    model: str = Field(..., description="Model used for generation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "message": "Once upon a time in Mali...",
                "model": "gpt-4",
                "timestamp": "2024-01-17T10:30:00"
            }
        }
