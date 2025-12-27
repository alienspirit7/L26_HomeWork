"""Video processing utilities using OpenCV."""

from __future__ import annotations
from typing import List
import cv2
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from src.models import VideoMetadata


@dataclass
class ExtractedFrames:
    """Container for extracted video frames."""
    frames: List[np.ndarray]
    timestamps: List[float]
    fps: float
    metadata: VideoMetadata


class VideoProcessor:
    """Handles video loading and frame extraction."""
    
    def __init__(self, target_fps: int = 10):
        self.target_fps = target_fps
    
    def get_metadata(self, video_path: str) -> VideoMetadata:
        """Extract video metadata."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        cap.release()
        
        return VideoMetadata(
            duration_seconds=duration,
            fps=fps,
            width=width,
            height=height,
            total_frames=total_frames,
            has_audio=self._check_audio(video_path),
        )
    
    def _check_audio(self, video_path: str) -> bool:
        """Check if video has audio track."""
        try:
            import subprocess
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "a",
                 "-show_entries", "stream=codec_type", "-of", "csv=p=0", video_path],
                capture_output=True, text=True, timeout=10
            )
            return "audio" in result.stdout
        except Exception:
            return False
    
    def extract_frames(self, video_path: str, max_frames: int = None) -> ExtractedFrames:
        """Extract frames from video at target FPS."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        metadata = self.get_metadata(video_path)
        frame_interval = max(1, int(metadata.fps / self.target_fps))
        
        frames, timestamps = [], []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
                timestamps.append(frame_count / metadata.fps)
                
                if max_frames and len(frames) >= max_frames:
                    break
            
            frame_count += 1
        
        cap.release()
        
        return ExtractedFrames(
            frames=frames,
            timestamps=timestamps,
            fps=self.target_fps,
            metadata=metadata,
        )
    
    def extract_keyframes(self, video_path: str, num_keyframes: int = 5) -> List[np.ndarray]:
        """Extract evenly spaced keyframes for analysis."""
        metadata = self.get_metadata(video_path)
        if metadata.total_frames == 0:
            return []
        
        indices = np.linspace(0, metadata.total_frames - 1, num_keyframes, dtype=int)
        cap = cv2.VideoCapture(video_path)
        keyframes = []
        
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                keyframes.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        cap.release()
        return keyframes
    
    def save_frame(self, frame: np.ndarray, output_path: str) -> str:
        """Save a frame to disk."""
        cv2.imwrite(output_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        return output_path
    
    def frames_to_temp_images(self, frames: List[np.ndarray], temp_dir: str) -> List[str]:
        """Save frames to temporary image files."""
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        paths = []
        for i, frame in enumerate(frames):
            path = f"{temp_dir}/frame_{i:04d}.jpg"
            self.save_frame(frame, path)
            paths.append(path)
        return paths
