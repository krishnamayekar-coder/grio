"""ID Generation Utilities"""
import uuid
from typing import Optional


def generate_uuid() -> str:
    """
    Generate a UUID4 string.
    
    Returns:
        UUID4 string
    """
    return str(uuid.uuid4())


def generate_user_id(prefix: str = "user") -> str:
    """
    Generate a user ID with optional prefix.
    
    Args:
        prefix: ID prefix
        
    Returns:
        Generated user ID
    """
    return f"{prefix}_{generate_uuid()}"


def generate_conversation_id(prefix: str = "conv") -> str:
    """
    Generate a conversation ID with optional prefix.
    
    Args:
        prefix: ID prefix
        
    Returns:
        Generated conversation ID
    """
    return f"{prefix}_{generate_uuid()}"


def is_valid_uuid(value: str) -> bool:
    """
    Validate if string is a valid UUID.
    
    Args:
        value: String to validate
        
    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False
