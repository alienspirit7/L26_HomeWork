"""Output formatting utilities for CLI."""


def print_header(photo: str, video: str):
    """Print analysis header."""
    print("=" * 60)
    print("DEEPFAKE DETECTION TOOL")
    print("=" * 60)
    print(f"Reference Photo: {photo}")
    print(f"Video File: {video}")
    print("-" * 60)


def print_results(result):
    """Print analysis results."""
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print(f"\n{'VERDICT:':<20} {result.verdict.value}")
    print(f"{'Confidence Score:':<20} {result.confidence_score:.2%}")
    print(f"{'Processing Time:':<20} {result.processing_time_seconds:.1f}s")
    
    print("\n" + "-" * 60)
    print("LAYER SCORES")
    print("-" * 60)
    
    layers = [
        ("Book Verification", result.book_verification),
        ("Eye Analysis", result.eye_analysis),
        ("Facial Expressions", result.facial_microexpressions),
        ("Body Movement", result.body_movement),
        ("Audio-Visual Sync", result.audio_visual_sync),
        ("Identity Match", result.identity_match),
    ]
    
    for name, layer in layers:
        if layer:
            print(f"\n{name}: {layer.score:.2%}")
            for finding in layer.findings[:3]:
                print(f"  • {finding}")
    
    if result.evidence_frames:
        print("\n" + "-" * 60)
        print("EVIDENCE FRAMES")
        print("-" * 60)
        for ef in result.evidence_frames[:5]:
            print(f"  Frame {ef.frame_number} ({ef.timestamp}): {ef.issue}")
    
    print("\n" + "=" * 60)
