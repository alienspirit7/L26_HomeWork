"""Configuration settings for the Deepfake Detection Tool."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration."""
    
    # API Keys
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    google_books_api_key: str = os.getenv("GOOGLE_BOOKS_API_KEY", "")
    
    # Detection thresholds
    deepfake_threshold: float = float(os.getenv("DEEPFAKE_THRESHOLD", "0.5"))
    authentic_threshold: float = float(os.getenv("AUTHENTIC_THRESHOLD", "0.7"))
    
    # Processing settings
    max_video_duration: int = int(os.getenv("MAX_VIDEO_DURATION", "60"))
    frame_extraction_fps: int = int(os.getenv("FRAME_EXTRACTION_FPS", "10"))
    
    # Gemini model - using 1.5 flash for better quota availability
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Layer weights for final score
    layer_weights: dict = None
    
    def __post_init__(self):
        if self.layer_weights is None:
            self.layer_weights = {
                "book_verification": 0.20,
                "eye_analysis": 0.20,
                "facial_microexpressions": 0.15,
                "body_movement": 0.15,
                "audio_visual_sync": 0.15,
                "identity_match": 0.15,
            }
    
    def validate(self) -> bool:
        """Validate required configuration."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env file.")
        return True


# Global config instance
config = Config()
