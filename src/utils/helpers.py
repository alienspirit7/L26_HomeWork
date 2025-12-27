"""Utility helper functions."""

from __future__ import annotations
from typing import List


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS.ms format."""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:05.2f}"


def calculate_weighted_score(layer_scores: dict, weights: dict) -> float:
    """Calculate weighted average score from layer scores."""
    total_weight = 0
    weighted_sum = 0
    
    for layer, score in layer_scores.items():
        if score is not None and layer in weights:
            weight = weights[layer]
            weighted_sum += score * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0.5
    
    return weighted_sum / total_weight


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp value to range."""
    return max(min_val, min(max_val, value))


def merge_findings(*finding_lists) -> List[str]:
    """Merge multiple finding lists, removing duplicates."""
    seen = set()
    merged = []
    for findings in finding_lists:
        if findings:
            for f in findings:
                if f not in seen:
                    seen.add(f)
                    merged.append(f)
    return merged


def get_frame_at_percentage(frames: list, percentage: float):
    """Get frame at specific percentage of video."""
    if not frames:
        return None
    idx = int(len(frames) * percentage)
    idx = max(0, min(idx, len(frames) - 1))
    return frames[idx]
