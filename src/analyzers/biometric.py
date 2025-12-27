"""Biometric analysis coordinator - combines eye and movement analysis."""

from __future__ import annotations
from typing import List
import numpy as np
from src.models import EyeAnalysisResult, LayerResult
from src.preprocessing.face import FaceProcessor
from src.analyzers.eye import EyeAnalyzer
from src.analyzers.movement import MovementAnalyzer


class BiometricAnalyzer:
    """Coordinates biometric analysis for deepfake detection."""
    
    def __init__(self):
        self.face_processor = FaceProcessor()
        self.eye_analyzer = EyeAnalyzer(self.face_processor)
        self.movement_analyzer = MovementAnalyzer(self.face_processor)
    
    def analyze_eye_movement(self, frames: List[np.ndarray], fps: float) -> EyeAnalysisResult:
        """Analyze eye movements and blink patterns."""
        return self.eye_analyzer.analyze(frames, fps)
    
    def analyze_facial_expressions(self, frames: List[np.ndarray], fps: float) -> LayerResult:
        """Analyze facial micro-expressions."""
        return self.movement_analyzer.analyze_expressions(frames, fps)
    
    def analyze_body_movement(self, frames: List[np.ndarray], fps: float) -> LayerResult:
        """Analyze body movement patterns."""
        return self.movement_analyzer.analyze_body(frames, fps)
    
    def close(self):
        """Release resources."""
        self.face_processor.close()
