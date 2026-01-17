"""Memory Service - Short and Long-term Memory Management"""
from typing import List, Dict, Optional
from datetime import datetime
from app.core.logging import get_logger

logger = get_logger(__name__)


class MemoryService:
    """Service for managing short-term and long-term memory."""
    
    def __init__(self):
        """Initialize memory service."""
        self.short_term_memory: List[Dict] = []
        self.max_short_term = 10
    
    def add_short_term_memory(self, user_id: str, content: str) -> None:
        """
        Add content to short-term memory.
        
        Args:
            user_id: User identifier
            content: Memory content
        """
        self.short_term_memory.append({
            "user_id": user_id,
            "content": content,
            "timestamp": datetime.utcnow()
        })
        
        # Keep only recent memories
        if len(self.short_term_memory) > self.max_short_term:
            self.short_term_memory.pop(0)
    
    def get_short_term_memory(self, user_id: str) -> List[Dict]:
        """
        Retrieve short-term memory for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of recent memories
        """
        return [m for m in self.short_term_memory if m["user_id"] == user_id]
    
    async def save_long_term_memory(self, user_id: str, content: str) -> None:
        """
        Save content to long-term memory (database).
        
        Args:
            user_id: User identifier
            content: Memory content
        """
        # TODO: Implement database persistence
        logger.info(f"Saving long-term memory for user {user_id}")
