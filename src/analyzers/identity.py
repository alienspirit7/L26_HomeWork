"""Identity verification by comparing faces."""

import numpy as np
from src.models import IdentityMatchResult
from src.preprocessing.face import FaceProcessor


class IdentityAnalyzer:
    """Analyzes identity match between reference photo and video frames."""
    
    # Similarity thresholds
    HIGH_MATCH_THRESHOLD = 0.6
    LOW_MATCH_THRESHOLD = 0.4
    
    def __init__(self):
        self.face_processor = FaceProcessor()
    
    def get_reference_embedding(self, image: np.ndarray) -> np.ndarray | None:
        """Extract face embedding from reference photo."""
        return self.face_processor.get_face_embedding(image)
    
    def analyze(
        self, 
        reference_image: np.ndarray, 
        frames: list[np.ndarray],
        sample_rate: int = 5
    ) -> IdentityMatchResult:
        """Compare reference face to faces in video frames."""
        findings = []
        
        # Get reference embedding
        ref_embedding = self.get_reference_embedding(reference_image)
        if ref_embedding is None:
            findings.append("Could not detect face in reference photo")
            return IdentityMatchResult(
                score=0.5,
                findings=findings,
                reference_similarity=0.0,
                frame_variance=0.0,
                frames_analyzed=0,
            )
        
        # Sample frames for analysis
        sampled_frames = frames[::sample_rate]
        
        # Get embeddings from video frames
        similarities = []
        for i, frame in enumerate(sampled_frames):
            frame_embedding = self.face_processor.get_face_embedding(frame)
            if frame_embedding is not None:
                similarity = self.face_processor.compare_faces(ref_embedding, frame_embedding)
                similarities.append(similarity)
        
        if not similarities:
            findings.append("Could not detect faces in video frames")
            return IdentityMatchResult(
                score=0.5,
                findings=findings,
                reference_similarity=0.0,
                frame_variance=0.0,
                frames_analyzed=len(sampled_frames),
            )
        
        # Calculate statistics
        avg_similarity = np.mean(similarities)
        variance = np.var(similarities)
        min_sim = np.min(similarities)
        max_sim = np.max(similarities)
        
        # Calculate score based on findings
        score = 0.5
        
        # Check identity match
        if avg_similarity >= self.HIGH_MATCH_THRESHOLD:
            findings.append(f"High identity match: {avg_similarity:.2%}")
            score -= 0.15
        elif avg_similarity >= self.LOW_MATCH_THRESHOLD:
            findings.append(f"Moderate identity match: {avg_similarity:.2%}")
        else:
            findings.append(f"Low identity match: {avg_similarity:.2%}")
            score += 0.2
        
        # Check for temporal consistency (deepfakes may have fluctuating identity)
        if variance > 0.05:
            findings.append(f"High identity variance across frames: {variance:.4f}")
            score += 0.15
        elif variance > 0.02:
            findings.append(f"Moderate identity variance: {variance:.4f}")
            score += 0.05
        else:
            findings.append(f"Consistent identity across frames")
            score -= 0.1
        
        # Check for sudden identity shifts
        if max_sim - min_sim > 0.3:
            findings.append(f"Large identity fluctuation detected: {min_sim:.2%} to {max_sim:.2%}")
            score += 0.1
        
        score = max(0.0, min(1.0, score))
        
        return IdentityMatchResult(
            score=score,
            findings=findings,
            reference_similarity=avg_similarity,
            frame_variance=variance,
            frames_analyzed=len(similarities),
        )
    
    def close(self):
        """Release resources."""
        self.face_processor.close()
