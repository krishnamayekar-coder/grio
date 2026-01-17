"""Time Utilities"""
from datetime import datetime, timezone
from typing import Optional


def get_utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def iso_format(dt: Optional[datetime] = None) -> str:
    """
    Get ISO format timestamp.
    
    Args:
        dt: DateTime object (defaults to current UTC time)
        
    Returns:
        ISO format string
    """
    if dt is None:
        dt = get_utc_now()
    return dt.isoformat()


def timestamp_to_datetime(timestamp: float) -> datetime:
    """
    Convert Unix timestamp to datetime.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        DateTime object
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
