"""Eye analysis for blink detection and movement patterns."""

import numpy as np
from dataclasses import dataclass
from src.models import EyeAnalysisResult
from src.preprocessing.face import FaceProcessor


@dataclass
class BlinkEvent:
    """Detected blink event."""
    frame_start: int
    frame_end: int
    duration_frames: int
    ear_min: float


class EyeAnalyzer:
    """Analyzes eye movements and blink patterns."""
    
    EAR_THRESHOLD = 0.2
    NORMAL_BLINK_RANGE = (15, 20)
    NORMAL_BLINK_DURATION = (0.1, 0.4)
    
    def __init__(self, face_processor: FaceProcessor = None):
        self.face_processor = face_processor or FaceProcessor()
    
    def _detect_blinks(self, frames: list, fps: float) -> tuple[list[BlinkEvent], float]:
        """Detect blinks from eye aspect ratio changes."""
        ear_values = []
        for i, frame in enumerate(frames):
            mesh = self.face_processor.get_face_mesh(frame, frame_index=i)
            if mesh:
                ear = self.face_processor.calculate_eye_aspect_ratio(mesh)
                ear_values.append((i, (ear["left"] + ear["right"]) / 2))
            else:
                ear_values.append((i, None))
        
        blinks, in_blink, blink_start, min_ear = [], False, 0, 1.0
        for frame_idx, ear in ear_values:
            if ear is None:
                continue
            if ear < self.EAR_THRESHOLD and not in_blink:
                in_blink, blink_start, min_ear = True, frame_idx, ear
            elif ear < self.EAR_THRESHOLD and in_blink:
                min_ear = min(min_ear, ear)
            elif ear >= self.EAR_THRESHOLD and in_blink:
                in_blink = False
                blinks.append(BlinkEvent(blink_start, frame_idx, frame_idx - blink_start, min_ear))
        
        duration_min = (len(frames) / fps / 60) if fps > 0 else 1
        return blinks, len(blinks) / duration_min if duration_min > 0 else 0
    
    def analyze(self, frames: list[np.ndarray], fps: float) -> EyeAnalysisResult:
        """Full eye movement analysis."""
        findings, score = [], 0.5
        blinks, blink_rate = self._detect_blinks(frames, fps)
        min_rate, max_rate = self.NORMAL_BLINK_RANGE
        
        if blink_rate < min_rate * 0.5:
            findings.append(f"Very low blink rate: {blink_rate:.1f}/min (normal: {min_rate}-{max_rate})")
            score += 0.25
        elif blink_rate < min_rate:
            findings.append(f"Low blink rate: {blink_rate:.1f}/min (normal: {min_rate}-{max_rate})")
            score += 0.1
        elif blink_rate > max_rate * 2:
            findings.append(f"Unusually high blink rate: {blink_rate:.1f}/min")
            score += 0.1
        else:
            findings.append(f"Normal blink rate: {blink_rate:.1f}/min")
            score -= 0.1
        
        if blinks:
            durations = [b.duration_frames / fps for b in blinks]
            avg_dur = np.mean(durations)
            min_d, max_d = self.NORMAL_BLINK_DURATION
            if avg_dur < min_d * 0.5 or avg_dur > max_d * 2:
                findings.append(f"Abnormal blink duration: {avg_dur*1000:.0f}ms")
                score += 0.15
            else:
                findings.append(f"Normal blink duration: {avg_dur*1000:.0f}ms")
        
        return EyeAnalysisResult(
            score=max(0.0, min(1.0, score)),
            findings=findings,
            blink_rate=blink_rate,
            blink_count=len(blinks),
            expected_rate_range=self.NORMAL_BLINK_RANGE,
        )
