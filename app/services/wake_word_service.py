"""Wake Word Detection Service"""
import re
from typing import Optional, Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)


class WakeWordDetector:
    """
    Service for detecting wake words in transcribed text.
    Uses simple pattern matching for "griot" keyword.
    """
    
    def __init__(self, wake_word: str = "griot", confidence_threshold: float = 0.7):
        """
        Initialize wake word detector.
        
        Args:
            wake_word: The wake word to listen for (default: "griot")
            confidence_threshold: Minimum confidence score (0-1)
        """
        self.wake_word = wake_word.lower()
        self.confidence_threshold = confidence_threshold
    
    def detect(self, text: str) -> Tuple[bool, str]:
        """
        Detect if wake word is present in text.
        
        Args:
            text: Transcribed text to check
            
        Returns:
            Tuple of (wake_word_detected, cleaned_text)
            cleaned_text: Original text without the wake word
        """
        text_lower = text.lower().strip()
        
        # Check if wake word is at the beginning
        if text_lower.startswith(self.wake_word):
            # Remove wake word and get the rest
            cleaned = text_lower[len(self.wake_word):].strip()
            logger.info(f"✨ Wake word '{self.wake_word}' detected!")
            return True, cleaned
        
        # Check if wake word is in the text with word boundaries
        pattern = rf'\b{re.escape(self.wake_word)}\b'
        if re.search(pattern, text_lower):
            # Remove wake word from text
            cleaned = re.sub(pattern, '', text_lower, count=1).strip()
            logger.info(f"✨ Wake word '{self.wake_word}' detected in text!")
            return True, cleaned
        
        return False, text
    
    def is_silence(self, text: str, min_length: int = 2) -> bool:
        """
        Check if transcribed text is essentially silence/noise.
        
        Args:
            text: Transcribed text
            min_length: Minimum characters to consider as speech
            
        Returns:
            True if text is silence/noise
        """
        return len(text.strip()) < min_length
