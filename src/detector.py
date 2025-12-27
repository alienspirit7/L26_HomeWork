"""Core Deepfake Detector - orchestrates all analysis components."""

import time
from pathlib import Path
import numpy as np
from PIL import Image

from src.config import config
from src.models import DetectionResult, DetectionVerdict
from src.preprocessing import VideoProcessor, AudioProcessor
from src.analyzers import BookAnalyzer, BiometricAnalyzer, IdentityAnalyzer, GeminiAnalyzer
from src.utils.helpers import calculate_weighted_score
from src.utils.merge import merge_gemini_results


class DeepfakeDetector:
    """Main deepfake detection orchestrator."""
    
    def __init__(self, api_key: str = None):
        """Initialize detector with optional API key override."""
        self.config = config
        if api_key:
            self.config.gemini_api_key = api_key
        self.config.validate()
        
        self.video_processor = VideoProcessor(target_fps=config.frame_extraction_fps)
        self.audio_processor = AudioProcessor()
        self.book_analyzer = BookAnalyzer(google_books_api_key=config.google_books_api_key)
        self.biometric_analyzer = BiometricAnalyzer()
        self.identity_analyzer = IdentityAnalyzer()
        self.gemini_analyzer = GeminiAnalyzer(api_key=self.config.gemini_api_key)
    
    def analyze(self, reference_photo: str, video_path: str, 
                use_gemini: bool = True, use_preprocessing: bool = True) -> DetectionResult:
        """Perform full deepfake detection analysis."""
        start_time = time.time()
        result = DetectionResult()
        
        if not Path(reference_photo).exists():
            raise FileNotFoundError(f"Reference photo not found: {reference_photo}")
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        ref_image = np.array(Image.open(reference_photo).convert("RGB"))
        
        print("Extracting video frames...")
        extracted = self.video_processor.extract_frames(video_path)
        if not extracted.frames:
            result.verdict = DetectionVerdict.INCONCLUSIVE
            result.processing_time_seconds = time.time() - start_time
            return result
        
        print(f"Extracted {len(extracted.frames)} frames at {extracted.fps} fps")
        
        transcription = ""
        if extracted.metadata.has_audio:
            audio_data = self.audio_processor.extract_audio(video_path)
            if audio_data:
                transcription = self.audio_processor.transcribe(audio_data.audio_path)
        
        if use_preprocessing:
            result = self._run_preprocessing(result, ref_image, extracted.frames, extracted.fps)
        
        if use_gemini:
            result = self._run_gemini(result, ref_image, extracted.frames, transcription)
        
        result = self._calculate_verdict(result)
        result.processing_time_seconds = time.time() - start_time
        print(f"Analysis complete in {result.processing_time_seconds:.1f}s")
        return result
    
    def _run_preprocessing(self, result, ref_image, frames, fps):
        """Run local preprocessing analyzers."""
        print("Running preprocessing analysis...")
        mid_frame = frames[len(frames) // 2]
        result.book_verification = self.book_analyzer.analyze(mid_frame)
        result.eye_analysis = self.biometric_analyzer.analyze_eye_movement(frames, fps)
        result.facial_microexpressions = self.biometric_analyzer.analyze_facial_expressions(frames, fps)
        result.body_movement = self.biometric_analyzer.analyze_body_movement(frames, fps)
        result.identity_match = self.identity_analyzer.analyze(ref_image, frames)
        return result
    
    def _run_gemini(self, result, ref_image, frames, transcription):
        """Run Gemini multimodal analysis."""
        print("Running Gemini analysis...")
        gemini_result = self.gemini_analyzer.analyze(ref_image, frames, transcription)
        result.gemini_analysis = str(gemini_result)
        if "error" not in gemini_result:
            result = merge_gemini_results(result, gemini_result)
        return result
    
    def _calculate_verdict(self, result):
        """Calculate final verdict based on all layer scores.
        
        Score interpretation:
        - Higher score = more manipulation indicators detected = LIKELY_DEEPFAKE
        - Lower score = fewer anomalies = LIKELY_AUTHENTIC
        """
        scores = {}
        if result.book_verification: scores["book_verification"] = result.book_verification.score
        if result.eye_analysis: scores["eye_analysis"] = result.eye_analysis.score
        if result.facial_microexpressions: scores["facial_microexpressions"] = result.facial_microexpressions.score
        if result.body_movement: scores["body_movement"] = result.body_movement.score
        if result.audio_visual_sync: scores["audio_visual_sync"] = result.audio_visual_sync.score
        if result.identity_match: scores["identity_match"] = result.identity_match.score
        
        if scores:
            result.confidence_score = calculate_weighted_score(scores, self.config.layer_weights)
        
        # Add penalty for evidence frames (each documented issue adds fakeness)
        if result.evidence_frames:
            evidence_penalty = min(0.2, len(result.evidence_frames) * 0.03)
            result.confidence_score = min(1.0, result.confidence_score + evidence_penalty)
        
        # Verdict based on thresholds (higher score = more fake)
        if result.confidence_score >= self.config.authentic_threshold:
            result.verdict = DetectionVerdict.LIKELY_DEEPFAKE
        elif result.confidence_score <= self.config.deepfake_threshold:
            result.verdict = DetectionVerdict.LIKELY_AUTHENTIC
        else:
            result.verdict = DetectionVerdict.INCONCLUSIVE
        return result
    
    def close(self):
        """Release all resources."""
        self.biometric_analyzer.close()
        self.identity_analyzer.close()
