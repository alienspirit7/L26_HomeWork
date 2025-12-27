"""Face detection and processing using MediaPipe and DeepFace."""

from __future__ import annotations
from typing import Optional
import numpy as np
from dataclasses import dataclass
from PIL import Image
import mediapipe as mp


@dataclass
class FaceData:
    """Detected face data."""
    bbox: tuple
    landmarks: dict
    embedding: Optional[np.ndarray] = None
    frame_index: int = 0


@dataclass
class FaceMeshData:
    """Face mesh landmarks from MediaPipe."""
    landmarks: list
    frame_index: int = 0


class FaceProcessor:
    """Handles face detection, landmark extraction, and embedding."""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1,
            refine_landmarks=True, min_detection_confidence=0.5)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5)
    
    def detect_face(self, image: np.ndarray) -> Optional[FaceData]:
        """Detect face in image and return face data."""
        results = self.face_detection.process(image)
        if not results.detections:
            return None
        bbox = results.detections[0].location_data.relative_bounding_box
        h, w = image.shape[:2]
        return FaceData(
            bbox=(int(bbox.xmin * w), int(bbox.ymin * h), int(bbox.width * w), int(bbox.height * h)),
            landmarks={})
    
    def get_face_mesh(self, image: np.ndarray, frame_index: int = 0) -> Optional[FaceMeshData]:
        """Extract 468 face mesh landmarks."""
        results = self.face_mesh.process(image)
        if not results.multi_face_landmarks:
            return None
        landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in results.multi_face_landmarks[0].landmark]
        return FaceMeshData(landmarks=landmarks, frame_index=frame_index)
    
    def get_face_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Get face embedding using DeepFace."""
        try:
            from deepface import DeepFace
            result = DeepFace.represent(image, model_name="Facenet", enforce_detection=False)
            if result and len(result) > 0:
                return np.array(result[0]["embedding"])
            return None
        except Exception as e:
            print(f"Face encoding error: {e}")
            return None
    
    def compare_faces(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compare two face embeddings and return similarity score."""
        try:
            dot = np.dot(emb1, emb2)
            norm1, norm2 = np.linalg.norm(emb1), np.linalg.norm(emb2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            similarity = dot / (norm1 * norm2)
            return (similarity + 1) / 2
        except Exception as e:
            print(f"Face comparison error: {e}")
            return 0.0
    
    def calculate_eye_aspect_ratio(self, mesh: FaceMeshData) -> dict:
        """Calculate Eye Aspect Ratio (EAR) for blink detection."""
        if not mesh or not mesh.landmarks:
            return {"left": 0, "right": 0}
        
        def ear(p1, p2, p3, p4, p5, p6):
            def dist(a, b): return np.sqrt((a["x"]-b["x"])**2 + (a["y"]-b["y"])**2)
            lm = mesh.landmarks
            h = dist(lm[p1], lm[p4])
            return (dist(lm[p2], lm[p6]) + dist(lm[p3], lm[p5])) / (2.0 * h) if h else 0
        
        return {"left": ear(33, 160, 158, 133, 153, 144), "right": ear(362, 385, 387, 263, 373, 380)}
    
    def load_reference_image(self, path: str) -> np.ndarray:
        """Load reference image and convert to RGB numpy array."""
        return np.array(Image.open(path).convert("RGB"))
    
    def close(self):
        """Release resources."""
        self.face_mesh.close()
        self.face_detection.close()
