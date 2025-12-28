"""Data models for the Deepfake Detection Tool."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
import uuid


class DetectionVerdict(Enum):
    """Possible detection verdicts."""
    LIKELY_DEEPFAKE = "LIKELY_DEEPFAKE"
    LIKELY_AUTHENTIC = "LIKELY_AUTHENTIC"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class LayerResult:
    """Result from a single detection layer."""
    score: float
    findings: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class BookVerificationResult(LayerResult):
    """Book verification specific result."""
    book_found: bool = False
    book_title: Optional[str] = None
    book_author: Optional[str] = None
    spelling_errors: List[str] = field(default_factory=list)
    ocr_text: Optional[str] = None


@dataclass
class EyeAnalysisResult(LayerResult):
    """Eye analysis specific result."""
    blink_rate: Optional[float] = None
    blink_count: int = 0
    expected_rate_range: tuple = (15, 20)


@dataclass
class IdentityMatchResult(LayerResult):
    """Identity matching specific result."""
    reference_similarity: float = 0.0
    frame_variance: float = 0.0
    frames_analyzed: int = 0


@dataclass
class EvidenceFrame:
    """Evidence frame with detected issue."""
    frame_number: int
    timestamp: str
    issue: str
    confidence: float = 0.0


@dataclass
class DetectionResult:
    """Complete detection result."""
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    verdict: DetectionVerdict = DetectionVerdict.INCONCLUSIVE
    fake_confidence_score: float = 0.5
    processing_time_seconds: float = 0.0
    
    book_verification: Optional[BookVerificationResult] = None
    eye_analysis: Optional[EyeAnalysisResult] = None
    facial_microexpressions: Optional[LayerResult] = None
    body_movement: Optional[LayerResult] = None
    audio_visual_sync: Optional[LayerResult] = None
    identity_match: Optional[IdentityMatchResult] = None
    evidence_frames: List[EvidenceFrame] = field(default_factory=list)
    gemini_analysis: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "analysis_id": self.analysis_id,
            "timestamp": self.timestamp,
            "verdict": self.verdict.value,
            "fake_confidence_score": self.fake_confidence_score,
            "processing_time_seconds": self.processing_time_seconds,
            "detection_layers": {
                "book_verification": self._layer_to_dict(self.book_verification),
                "eye_analysis": self._layer_to_dict(self.eye_analysis),
                "facial_microexpressions": self._layer_to_dict(self.facial_microexpressions),
                "body_movement": self._layer_to_dict(self.body_movement),
                "audio_visual_sync": self._layer_to_dict(self.audio_visual_sync),
                "identity_match": self._layer_to_dict(self.identity_match),
            },
            "evidence_frames": [
                {"frame": e.frame_number, "timestamp": e.timestamp, "issue": e.issue}
                for e in self.evidence_frames
            ],
        }
    
    def _layer_to_dict(self, layer: Optional[LayerResult]) -> Optional[dict]:
        if layer is None:
            return None
        result = {"score": layer.score, "findings": layer.findings}
        if hasattr(layer, "book_found"):
            result["book_found"] = layer.book_found
            result["book_title"] = layer.book_title
            result["spelling_errors"] = layer.spelling_errors
        if hasattr(layer, "blink_rate"):
            result["blink_rate"] = layer.blink_rate
            result["expected_rate_range"] = list(layer.expected_rate_range)
        if hasattr(layer, "reference_similarity"):
            result["reference_similarity"] = layer.reference_similarity
            result["frame_variance"] = layer.frame_variance
        return result


@dataclass
class VideoMetadata:
    """Metadata extracted from video."""
    duration_seconds: float
    fps: float
    width: int
    height: int
    total_frames: int
    has_audio: bool = False
