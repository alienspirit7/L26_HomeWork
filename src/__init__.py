"""Deepfake Detection Tool - Main Package."""

from src.detector import DeepfakeDetector
from src.models import DetectionResult, DetectionVerdict

__version__ = "1.0.0"
__all__ = ["DeepfakeDetector", "DetectionResult", "DetectionVerdict"]
