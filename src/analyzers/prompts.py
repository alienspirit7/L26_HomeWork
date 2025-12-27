"""Gemini prompts for deepfake analysis."""

DEEPFAKE_ANALYSIS_PROMPT = """You are an expert deepfake detection analyst. Analyze the provided video frames and reference photo for signs of video manipulation or AI generation.

## Analysis Tasks:

1. **Book Cover Analysis**: Identify book, check text spelling, look for AI artifacts
2. **Eye Movement Analysis**: Check blinking patterns, unnatural movements
3. **Facial Expressions**: Check micro-expressions, frozen faces, symmetry
4. **Body Movement**: Evaluate pacing, jerky/smooth motions, hand tremor
5. **Audio-Visual Sync**: Check lip sync alignment
6. **Identity Consistency**: Match to reference photo, cross-frame consistency

## Response Format (JSON):
```json
{
    "overall_assessment": "LIKELY_DEEPFAKE | LIKELY_AUTHENTIC | INCONCLUSIVE",
    "confidence": 0.0-1.0,
    "book_analysis": {
        "book_detected": true/false,
        "title": "string or null",
        "spelling_issues": [],
        "score": 0.0-1.0
    },
    "eye_analysis": {"observations": [], "abnormalities": [], "score": 0.0-1.0},
    "expression_analysis": {"observations": [], "abnormalities": [], "score": 0.0-1.0},
    "movement_analysis": {"observations": [], "abnormalities": [], "score": 0.0-1.0},
    "identity_analysis": {"matches_reference": true/false, "score": 0.0-1.0},
    "key_findings": [],
    "evidence_frames": [{"frame_index": 0, "issue": "description"}]
}
```

Score: 0.0=authentic, 0.5=uncertain, 1.0=deepfake. Analyze carefully."""


BOOK_ANALYSIS_PROMPT = """Analyze this book cover image:
1. What is the book title?
2. Who is the author?
3. Are there spelling errors or text anomalies?
4. Does text look natural or AI-generated?
5. Is this a real published book?

Respond in JSON:
```json
{
    "title": "string",
    "author": "string",
    "spelling_errors": [],
    "text_quality": "description",
    "likely_real_book": true/false,
    "confidence": 0.0-1.0
}
```"""
