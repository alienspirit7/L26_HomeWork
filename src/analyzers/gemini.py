"""Gemini API integration for multimodal deepfake analysis."""

from __future__ import annotations
from typing import List
import json
import re
import numpy as np
from PIL import Image
from google import genai

from src.config import config
from src.analyzers.prompts import DEEPFAKE_ANALYSIS_PROMPT


class GeminiAnalyzer:
    """Uses Gemini for multimodal deepfake detection."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key required")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = config.gemini_model
    
    def analyze(self, reference: np.ndarray, frames: List[np.ndarray], transcription: str = "") -> dict:
        """Perform multimodal analysis using Gemini."""
        prompt = DEEPFAKE_ANALYSIS_PROMPT
        if transcription:
            prompt += f"\n\n## Audio Transcription:\n{transcription}"
        
        # Build content parts
        parts = [prompt, "\n\n## Reference Photo:"]
        parts.append(Image.fromarray(reference))
        parts.append("\n\n## Video Frames (in order):")
        
        max_frames, step = 8, max(1, len(frames) // 8)
        for i, idx in enumerate(range(0, len(frames), step)):
            if i >= max_frames:
                break
            parts.append(f"\nFrame {i+1}:")
            parts.append(Image.fromarray(frames[idx]))
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=parts
            )
            return self._parse_response(response.text)
        except Exception as e:
            print(f"Gemini API error: {e}")
            return {"error": str(e), "overall_assessment": "INCONCLUSIVE", "confidence": 0.5}
    
    def _parse_response(self, text: str) -> dict:
        """Parse Gemini's JSON response."""
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw_response": text, "overall_assessment": "INCONCLUSIVE", "confidence": 0.5}

