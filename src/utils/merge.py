"""Result merging utilities for combining analysis results."""

from src.models import DetectionResult, EvidenceFrame
from src.utils.helpers import format_timestamp


def merge_gemini_results(result: DetectionResult, gemini: dict) -> DetectionResult:
    """Merge Gemini analysis results with preprocessing results."""
    
    # Update book verification with Gemini insights
    if "book_analysis" in gemini and result.book_verification:
        book = gemini["book_analysis"]
        if book.get("spelling_issues"):
            result.book_verification.spelling_errors.extend(book["spelling_issues"])
        if book.get("text_quality"):
            result.book_verification.findings.append(f"Gemini: {book['text_quality']}")
    
    # Update eye analysis
    if "eye_analysis" in gemini and result.eye_analysis:
        for obs in gemini["eye_analysis"].get("observations", []):
            result.eye_analysis.findings.append(f"Gemini: {obs}")
    
    # Add evidence frames from Gemini
    for ef in gemini.get("evidence_frames", []):
        result.evidence_frames.append(EvidenceFrame(
            frame_number=ef.get("frame_index", 0),
            timestamp=format_timestamp(ef.get("frame_index", 0) / 10),
            issue=ef.get("issue", ""),
            confidence=0.7
        ))
    
    # Add key findings
    if result.book_verification:
        for finding in gemini.get("key_findings", []):
            if isinstance(finding, str):
                result.book_verification.findings.append(f"Key: {finding}")
    
    return result
