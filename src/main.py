#!/usr/bin/env python3
"""Deepfake Detection Tool - Main Entry Point."""

import argparse
import json
import sys
from pathlib import Path

from src.detector import DeepfakeDetector
from src.cli_output import print_header, print_results


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Deepfake Detection Tool using Gemini 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m src.main --photo person.jpg --video test.mp4
    python -m src.main --photo person.jpg --video test.mp4 --output result.json
    python -m src.main --photo person.jpg --video test.mp4 --gemini-only
        """)
    parser.add_argument("--photo", "-p", required=True, help="Reference photo path")
    parser.add_argument("--video", "-v", required=True, help="Video file path")
    parser.add_argument("--output", "-o", help="JSON output path")
    parser.add_argument("--gemini-only", action="store_true", help="Skip preprocessing")
    parser.add_argument("--no-gemini", action="store_true", help="Skip Gemini analysis")
    parser.add_argument("--api-key", help="Gemini API key (overrides .env)")
    return parser.parse_args()


def main():
    args = parse_args()
    
    if not Path(args.photo).exists():
        print(f"Error: Reference photo not found: {args.photo}")
        sys.exit(1)
    if not Path(args.video).exists():
        print(f"Error: Video file not found: {args.video}")
        sys.exit(1)
    
    try:
        detector = DeepfakeDetector(api_key=args.api_key)
    except ValueError as e:
        print(f"Error: {e}\nPlease set GEMINI_API_KEY in .env or use --api-key")
        sys.exit(1)
    
    print_header(args.photo, args.video)
    
    try:
        result = detector.analyze(
            reference_photo=args.photo,
            video_path=args.video,
            use_gemini=not args.no_gemini,
            use_preprocessing=not args.gemini_only)
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)
    finally:
        detector.close()
    
    print_results(result)
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"\nResult saved to: {args.output}")
    
    sys.exit(2 if result.verdict.value == "LIKELY_DEEPFAKE" else 
             0 if result.verdict.value == "LIKELY_AUTHENTIC" else 1)


if __name__ == "__main__":
    main()
