"""Core Deepfake Detector - Gemini-only analysis."""

import time
from pathlib import Path
import numpy as np
from PIL import Image

from src.config import config
from src.models import (
    DetectionResult, DetectionVerdict, LayerResult,
    BookVerificationResult, EyeAnalysisResult, IdentityMatchResult, EvidenceFrame
)
from src.preprocessing import VideoProcessor, AudioProcessor
from src.analyzers import GeminiAnalyzer
from src.utils.helpers import format_timestamp


class DeepfakeDetector:
    """Gemini-powered deepfake detection."""
    
    def __init__(self, api_key: str = None):
        """Initialize detector with optional API key override."""
        self.config = config
        if api_key:
            self.config.gemini_api_key = api_key
        self.config.validate()
        
        self.video_processor = VideoProcessor(target_fps=config.frame_extraction_fps)
        self.audio_processor = AudioProcessor()
        self.gemini_analyzer = GeminiAnalyzer(api_key=self.config.gemini_api_key)
    
    def analyze(self, reference_photo: str, video_path: str) -> DetectionResult:
        """Perform Gemini-powered deepfake detection analysis."""
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
        
        print("Running Gemini analysis...")
        gemini_result = self.gemini_analyzer.analyze(ref_image, extracted.frames, transcription)
        result.gemini_analysis = str(gemini_result)
        
        if "error" not in gemini_result:
            result = self._process_gemini_results(result, gemini_result, extracted.fps)
        
        result = self._calculate_verdict(result, gemini_result)
        result.processing_time_seconds = time.time() - start_time
        print(f"Analysis complete in {result.processing_time_seconds:.1f}s")
        return result
    
    def _process_gemini_results(self, result: DetectionResult, gemini: dict, fps: float) -> DetectionResult:
        """Convert Gemini analysis to detection layer results."""
        # Book verification
        if "book_analysis" in gemini:
            book = gemini["book_analysis"]
            result.book_verification = BookVerificationResult(
                score=book.get("score", 0.5),
                findings=book.get("spelling_issues", []) + book.get("ai_text_artifacts", []),
                book_found=book.get("book_detected", False),
                book_title=book.get("title"),
                book_author=book.get("author"),
                spelling_errors=book.get("spelling_issues", [])
            )
            if not book.get("likely_real_book", True) and book.get("book_detected"):
                result.book_verification.findings.append("Book appears to be AI-generated or fake")
        
        # Eye analysis
        if "eye_analysis" in gemini:
            eye = gemini["eye_analysis"]
            result.eye_analysis = EyeAnalysisResult(
                score=eye.get("score", 0.5),
                findings=eye.get("observations", []) + eye.get("abnormalities", [])
            )
        
        # Movement analysis (includes body pacing and movement paths)
        if "movement_analysis" in gemini:
            move = gemini["movement_analysis"]
            findings = move.get("movement_path_issues", []) + move.get("impossible_physics", [])
            if move.get("body_pacing") and move.get("body_pacing") != "natural":
                findings.append(f"Body pacing: {move.get('body_pacing')}")
            if move.get("hand_tremor_detected"):
                findings.append("Hand tremor/glitches detected")
            result.body_movement = LayerResult(
                score=move.get("score", 0.5),
                findings=findings
            )
        
        # AI signals analysis
        if "ai_signals" in gemini:
            signals = gemini["ai_signals"]
            findings = (
                signals.get("blending_artifacts", []) +
                signals.get("lighting_issues", []) +
                signals.get("temporal_anomalies", []) +
                signals.get("body_part_anomalies", [])
            )
            result.facial_microexpressions = LayerResult(
                score=signals.get("score", 0.5),
                findings=findings
            )
        
        # Identity analysis
        if "identity_analysis" in gemini:
            identity = gemini["identity_analysis"]
            result.identity_match = IdentityMatchResult(
                score=identity.get("score", 0.5),
                findings=[f"Consistency: {identity.get('consistency', 'unknown')}"],
                reference_similarity=1.0 if identity.get("matches_reference") else 0.0
            )
        
        # Evidence frames
        for ef in gemini.get("evidence_frames", []):
            frame_idx = ef.get("frame_index", 0)
            result.evidence_frames.append(EvidenceFrame(
                frame_number=frame_idx,
                timestamp=format_timestamp(frame_idx / fps if fps else 0),
                issue=ef.get("issue", ""),
                confidence=0.8
            ))
        
        # Key findings as additional book verification notes
        if result.book_verification:
            for finding in gemini.get("key_findings", []):
                result.book_verification.findings.append(f"Key: {finding}")
        
        return result
    
    def _calculate_verdict(self, result: DetectionResult, gemini: dict) -> DetectionResult:
        """Calculate final verdict based on Gemini analysis."""
        # Use Gemini's overall assessment and confidence
        overall = gemini.get("overall_assessment", "INCONCLUSIVE")
        confidence = gemini.get("confidence", 0.5)
        
        # Calculate weighted score from layer results
        scores = {}
        if result.book_verification:
            scores["book_verification"] = result.book_verification.score
        if result.eye_analysis:
            scores["eye_analysis"] = result.eye_analysis.score
        if result.facial_microexpressions:
            scores["ai_signals"] = result.facial_microexpressions.score
        if result.body_movement:
            scores["body_movement"] = result.body_movement.score
        if result.identity_match:
            scores["identity_match"] = result.identity_match.score
        
        if scores:
            weights = self.config.layer_weights
            total_weight = sum(weights.get(k, 0.2) for k in scores)
            result.fake_confidence_score = sum(
                scores[k] * weights.get(k, 0.2) for k in scores
            ) / total_weight if total_weight > 0 else confidence
        else:
            result.fake_confidence_score = confidence
        
        # Evidence penalty
        if result.evidence_frames:
            evidence_penalty = min(0.2, len(result.evidence_frames) * 0.03)
            result.fake_confidence_score = min(1.0, result.fake_confidence_score + evidence_penalty)
        
        # Determine verdict
        if overall == "LIKELY_DEEPFAKE" or result.fake_confidence_score >= self.config.authentic_threshold:
            result.verdict = DetectionVerdict.LIKELY_DEEPFAKE
        elif overall == "LIKELY_AUTHENTIC" or result.fake_confidence_score <= self.config.deepfake_threshold:
            result.verdict = DetectionVerdict.LIKELY_AUTHENTIC
        else:
            result.verdict = DetectionVerdict.INCONCLUSIVE
        
        return result
    
    def close(self):
        """Release resources."""
        pass

