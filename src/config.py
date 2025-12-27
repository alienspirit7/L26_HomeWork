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
    
    # Detection thresholds (higher score = more likely fake)
    # Below deepfake_threshold = LIKELY_AUTHENTIC
    # Above authentic_threshold = LIKELY_DEEPFAKE  
    # Between = INCONCLUSIVE
    deepfake_threshold: float = float(os.getenv("DEEPFAKE_THRESHOLD", "0.35"))
    authentic_threshold: float = float(os.getenv("AUTHENTIC_THRESHOLD", "0.55"))
    
    # Processing settings
    max_video_duration: int = int(os.getenv("MAX_VIDEO_DURATION", "60"))
    frame_extraction_fps: int = int(os.getenv("FRAME_EXTRACTION_FPS", "10"))
    
    # Gemini model - using models/ prefix for google.genai
    gemini_model: str = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
    
    # Layer weights for final score (all analyzed by Gemini)
    layer_weights: dict = None
    
    def __post_init__(self):
        if self.layer_weights is None:
            self.layer_weights = {
                "book_verification": 0.30,  # Book authenticity, spelling errors
                "ai_signals": 0.25,          # AI artifacts, lighting, temporal issues
                "body_movement": 0.20,       # Body pacing, movement paths
                "eye_analysis": 0.15,        # Blinking patterns, gaze
                "identity_match": 0.10,      # Reference matching
            }
    
    def validate(self) -> bool:
        """Validate required configuration."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env file.")
        return True


# Global config instance
config = Config()

