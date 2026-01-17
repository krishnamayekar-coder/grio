"""Logging Configuration"""
import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """Configure logging for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance by name."""
    return logging.getLogger(name)
