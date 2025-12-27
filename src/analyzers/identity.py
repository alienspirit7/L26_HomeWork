"""Identity verification by comparing faces."""

from __future__ import annotations
from typing import Optional, List
import numpy as np
from src.models import IdentityMatchResult
from src.preprocessing.face import FaceProcessor


class IdentityAnalyzer:
    """Analyzes identity match between reference photo and video frames."""
    
    HIGH_MATCH_THRESHOLD = 0.6
    LOW_MATCH_THRESHOLD = 0.4
    
    def __init__(self):
        self.face_processor = FaceProcessor()
    
    def get_reference_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract face embedding from reference photo."""
        return self.face_processor.get_face_embedding(image)
    
    def analyze(
        self, 
        reference_image: np.ndarray, 
        frames: List[np.ndarray],
        sample_rate: int = 5
    ) -> IdentityMatchResult:
        """Compare reference face to faces in video frames."""
        findings = []
        
        ref_embedding = self.get_reference_embedding(reference_image)
        if ref_embedding is None:
            findings.append("Could not detect face in reference photo")
            return IdentityMatchResult(
                score=0.5, findings=findings,
                reference_similarity=0.0, frame_variance=0.0, frames_analyzed=0)
        
        sampled_frames = frames[::sample_rate]
        similarities = []
        
        for frame in sampled_frames:
            frame_embedding = self.face_processor.get_face_embedding(frame)
            if frame_embedding is not None:
                similarity = self.face_processor.compare_faces(ref_embedding, frame_embedding)
                similarities.append(similarity)
        
        if not similarities:
            findings.append("Could not detect faces in video frames")
            return IdentityMatchResult(
                score=0.5, findings=findings,
                reference_similarity=0.0, frame_variance=0.0, frames_analyzed=len(sampled_frames))
        
        avg_similarity = np.mean(similarities)
        variance = np.var(similarities)
        min_sim, max_sim = np.min(similarities), np.max(similarities)
        score = 0.5
        
        if avg_similarity >= self.HIGH_MATCH_THRESHOLD:
            findings.append(f"High identity match: {avg_similarity:.2%}")
            score -= 0.15
        elif avg_similarity >= self.LOW_MATCH_THRESHOLD:
            findings.append(f"Moderate identity match: {avg_similarity:.2%}")
        else:
            findings.append(f"Low identity match: {avg_similarity:.2%}")
            score += 0.2
        
        if variance > 0.05:
            findings.append(f"High identity variance across frames: {variance:.4f}")
            score += 0.15
        elif variance > 0.02:
            findings.append(f"Moderate identity variance: {variance:.4f}")
            score += 0.05
        else:
            findings.append("Consistent identity across frames")
            score -= 0.1
        
        if max_sim - min_sim > 0.3:
            findings.append(f"Large identity fluctuation detected: {min_sim:.2%} to {max_sim:.2%}")
            score += 0.1
        
        return IdentityMatchResult(
            score=max(0.0, min(1.0, score)),
            findings=findings,
            reference_similarity=avg_similarity,
            frame_variance=variance,
            frames_analyzed=len(similarities))
    
    def close(self):
        """Release resources."""
        self.face_processor.close()
