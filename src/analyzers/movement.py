"""Movement analysis for facial expressions and body movement."""

import numpy as np
from src.models import LayerResult
from src.preprocessing.face import FaceProcessor


class MovementAnalyzer:
    """Analyzes facial expressions and body movement patterns."""
    
    def __init__(self, face_processor: FaceProcessor = None):
        self.face_processor = face_processor or FaceProcessor()
    
    def analyze_expressions(self, frames: list[np.ndarray], fps: float) -> LayerResult:
        """Analyze facial micro-expressions for consistency."""
        findings, score = [], 0.5
        landmark_positions = []
        key_indices = [61, 291, 70, 300, 105, 334]  # Mouth corners, eyebrows
        
        for frame in frames:
            mesh = self.face_processor.get_face_mesh(frame)
            if mesh:
                positions = {}
                for idx in key_indices:
                    if idx < len(mesh.landmarks):
                        lm = mesh.landmarks[idx]
                        positions[idx] = (lm["x"], lm["y"])
                landmark_positions.append(positions)
        
        if len(landmark_positions) < 2:
            return LayerResult(score=0.5, findings=["Insufficient frames for expression analysis"])
        
        movements = []
        for i in range(1, len(landmark_positions)):
            if landmark_positions[i] and landmark_positions[i-1]:
                for idx in landmark_positions[i]:
                    if idx in landmark_positions[i-1]:
                        curr, prev = landmark_positions[i][idx], landmark_positions[i-1][idx]
                        movements.append(np.sqrt((curr[0]-prev[0])**2 + (curr[1]-prev[1])**2))
        
        if movements:
            variance, mean_mov = np.var(movements), np.mean(movements)
            if variance < 0.00001 and mean_mov < 0.0001:
                findings.append("Very static facial movements detected")
                score += 0.2
            elif variance > 0.01:
                findings.append("Inconsistent facial movements detected")
                score += 0.15
            else:
                findings.append("Natural facial movement patterns")
                score -= 0.1
        
        return LayerResult(score=max(0.0, min(1.0, score)), findings=findings)
    
    def analyze_body(self, frames: list[np.ndarray], fps: float) -> LayerResult:
        """Analyze body movement and pacing."""
        findings, score = [], 0.5
        face_positions = []
        
        for frame in frames:
            face = self.face_processor.detect_face(frame)
            if face:
                x, y, w, h = face.bbox
                face_positions.append((x + w/2, y + h/2))
        
        if len(face_positions) < 2:
            return LayerResult(score=0.5, findings=["Insufficient face detections for movement analysis"])
        
        movements = []
        for i in range(1, len(face_positions)):
            dx = face_positions[i][0] - face_positions[i-1][0]
            dy = face_positions[i][1] - face_positions[i-1][1]
            movements.append(np.sqrt(dx**2 + dy**2))
        
        if movements:
            variance, mean_mov = np.var(movements), np.mean(movements)
            if mean_mov < 0.5:
                findings.append("Unusually still head position")
                score += 0.15
            elif variance > 100:
                findings.append("Jerky head movements detected")
                score += 0.1
            else:
                findings.append("Natural head movement patterns")
                score -= 0.1
        
        return LayerResult(score=max(0.0, min(1.0, score)), findings=findings)
