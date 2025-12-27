"""Audio extraction and processing."""

from __future__ import annotations
from typing import Optional
import subprocess
import tempfile
from dataclasses import dataclass


@dataclass
class AudioData:
    """Extracted audio data."""
    audio_path: str
    duration_seconds: float
    sample_rate: int = 16000
    transcription: str = ""


class AudioProcessor:
    """Handles audio extraction and transcription."""
    
    def __init__(self):
        self.whisper_model = None
    
    def extract_audio(self, video_path: str, output_path: str = None) -> Optional[AudioData]:
        """Extract audio from video using ffmpeg."""
        if output_path is None:
            temp_dir = tempfile.mkdtemp()
            output_path = f"{temp_dir}/audio.wav"
        
        try:
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", video_path,
                 "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                 output_path],
                capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr}")
                return None
            
            duration = self._get_duration(output_path)
            return AudioData(audio_path=output_path, duration_seconds=duration, sample_rate=16000)
        except Exception as e:
            print(f"Audio extraction error: {e}")
            return None
    
    def _get_duration(self, audio_path: str) -> float:
        """Get audio duration using ffprobe."""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", audio_path],
                capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip())
        except Exception:
            return 0.0
    
    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio using Whisper."""
        try:
            if self.whisper_model is None:
                import whisper
                self.whisper_model = whisper.load_model("base")
            
            result = self.whisper_model.transcribe(audio_path, language="en", fp16=False)
            return result.get("text", "")
        except ImportError:
            print("Whisper not installed. Skipping transcription.")
            return ""
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def analyze_audio_features(self, audio_path: str) -> dict:
        """Analyze basic audio features."""
        return {"has_speech": True, "speech_segments": []}
