# 🔍 Deepfake Detection Tool

**AI-powered identity verification and deepfake detection for secure video authentication.**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Why This Tool Exists](#why-this-tool-exists)
- [How It Works](#how-it-works)
- [Repository Structure](#repository-structure)
- [Data Flow Process](#data-flow-process)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Understanding Results](#understanding-results)
- [Training Data](#training-data)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **Deepfake Detection Tool** is an AI-powered system that verifies whether a video is authentic or artificially generated (deepfake). It uses **Google Gemini** as its sole AI engine for comprehensive multimodal analysis.

### Key Features

| Feature | Description |
|---------|-------------|
| **Identity Verification** | Compares video subject to a reference photo |
| **Book Authenticity Check** | Verifies if book is real/published, checks for spelling errors |
| **Body Movement Analysis** | Analyzes body pacing, movement paths, hand tremors |
| **AI Signal Detection** | Detects blending artifacts, lighting issues, temporal anomalies |
| **Detailed Reporting** | JSON output with layer-by-layer breakdown |

---

## Why This Tool Exists

### The Business Problem

Companies often need to verify that a **real person** is performing an action themselves, not through manipulation or impersonation. Common scenarios include:

- **Remote Identity Verification**: Verifying that the person submitting documents is who they claim to be
- **Video KYC (Know Your Customer)**: Banks and financial services requiring video proof of identity
- **Remote Onboarding**: Companies verifying new employees or customers via video
- **High-Value Transactions**: Confirming the account holder personally authorizes actions
- **Legal Documentation**: Ensuring the signer is present and aware of the document

### The Solution

This tool provides a **multi-layer verification system** that:

1. **Confirms Identity**: The person in the video matches the provided reference photo
2. **Proves Awareness**: The subject holds a physical book (difficult to fake) and states their name/workplace
3. **Detects Manipulation**: Multiple analysis layers detect AI-generated or manipulated content
4. **Provides Confidence Scores**: Clear verdict with detailed reasoning for human review

### Why Hold a Book?

The book requirement serves as a **physical proof of presence**:
- Books are unique real-world objects that are hard to generate convincingly
- Text on covers provides OCR verification opportunities
- The book can be verified against online databases (Is it a real book?)
- Holding an object tests natural hand movements and interactions

---

## How It Works

### Input Requirements

| Input | Description | Format |
|-------|-------------|--------|
| **Reference Photo** | Clear photo of the person's face | JPEG, PNG, WebP (min 512×512px) |
| **Verification Video** | Video of person stating name/workplace while holding a book | MP4, WebM, MOV (max 60s) |

### Analysis Layers (All Powered by Gemini)

```
┌─────────────────────────────────────────────────────────────────────┐
│                  GEMINI MULTIMODAL ANALYSIS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ BOOK ANALYSIS   │  │ MOVEMENT        │  │ AI SIGNALS      │     │
│  │ • Is book real? │  │ • Body pacing   │  │ • Blend artifacts│    │
│  │ • Spelling check│  │ • Movement paths│  │ • Lighting issues│    │
│  │ • AI text detect│  │ • Hand tremors  │  │ • Temporal glitch│    │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘     │
│           │                    │                     │              │
│  ┌────────▼────────┐  ┌────────▼────────┐                          │
│  │ EYE ANALYSIS    │  │ IDENTITY MATCH  │                          │
│  │ • Blink patterns│  │ • Photo matching│                          │
│  │ • Gaze tracking │  │ • Frame-to-frame│                          │
│  └────────┬────────┘  └────────┬────────┘                          │
│           │                    │                                    │
│           └────────────────────┘                                    │
│                    │                                                │
│        ┌───────────▼───────────┐                                   │
│        │   WEIGHTED SCORING    │                                   │
│        │   & FINAL VERDICT     │                                   │
│        └───────────────────────┘                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
deepfake-detection/
│
├── 📄 README.md                 # This documentation
├── 📄 PRD.md                    # Product Requirements Document
├── 📄 QUICKSTART.md             # Quick start guide
├── 📄 PROMPTS_LOG.md            # Development session prompts
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example              # Environment variable template
│
├── 📁 src/                      # Source code
│   ├── config.py                # Configuration management
│   ├── models.py                # Data models & types
│   ├── detector.py              # Main Gemini-powered detector
│   ├── main.py                  # CLI entry point
│   ├── cli_output.py            # CLI formatting utilities
│   │
│   ├── 📁 preprocessing/        # Input processing
│   │   ├── video.py             # Video frame extraction
│   │   ├── face.py              # Face detection
│   │   └── audio.py             # Audio extraction
│   │
│   ├── 📁 analyzers/            # Gemini analysis
│   │   ├── gemini.py            # Gemini API integration
│   │   └── prompts.py           # Analysis prompts
│   │
│   └── 📁 utils/                # Utilities
│       └── helpers.py           # Helper functions
│
└── 📁 training/                 # Training data (optional)
    ├── 📁 real/                 # Known authentic videos
    └── 📁 fake/                 # Known deepfake videos
```

---

## Data Flow Process

### Step-by-Step Analysis Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GEMINI-ONLY DATA FLOW PROCESS                         │
└─────────────────────────────────────────────────────────────────────────┘

   INPUT                    PREPROCESSING                 GEMINI ANALYSIS
┌─────────────┐          ┌─────────────────┐         ┌─────────────────────┐
│ Reference   │          │                 │         │                     │
│ Photo       │─────────▶│  Load Image     │────────▶│                     │
│ (photo.jpg) │          │                 │         │                     │
└─────────────┘          └─────────────────┘         │   GEMINI ANALYSIS   │
                                                     │                     │
┌─────────────┐          ┌─────────────────┐         │  • Book Authenticity│
│ Video File  │          │                 │         │  • Spelling Errors  │
│ (video.mp4) │─────────▶│ Frame Extraction│────────▶│  • Body Pacing      │
│             │          │ (10 fps)        │         │  • Movement Paths   │
└─────────────┘          └────────┬────────┘         │  • AI Signals       │
                                  │                  │  • Eye Analysis     │
                                  ▼                  │  • Identity Match   │
                         ┌─────────────────┐         │                     │
                         │ Audio Extraction│────────▶│                     │
                         │ (optional)      │         └──────────┬──────────┘
                         └─────────────────┘                    │
                                                                ▼
                                              ┌─────────────────────────┐
                                              │    RESULT PROCESSING    │
                                              │  • Weighted scoring     │
                                              │  • Confidence calculation│
                                              │  • Final verdict        │
                                              └────────────┬────────────┘
                                                           │
                                                           ▼
   OUTPUT
┌─────────────────────────────────────────────────────────────────────────┐
│ DETECTION REPORT                                                        │
│ • Verdict: LIKELY_DEEPFAKE / LIKELY_AUTHENTIC / INCONCLUSIVE           │
│ • Confidence Score: 0-100%                                              │
│ • Layer-by-layer findings                                               │
│ • Evidence frames                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Detailed Step Descriptions

| Step | Module | What It Does | Possible Results |
|------|--------|--------------|------------------|
| **1. Load Reference** | `detector.py` | Loads reference photo as image array | Image ready for Gemini |
| **2. Frame Extraction** | `video.py` | Extracts video frames at 10 fps | Frames ready for analysis |
| **3. Audio Extraction** | `audio.py` | Extracts audio track (optional) | Transcription for context |
| **4. Gemini Analysis** | `gemini.py` | Sends frames + reference to Gemini | Comprehensive analysis JSON |
| **5. Score Processing** | `detector.py` | Converts Gemini response to layer scores | Per-layer scores |
| **6. Verdict** | `detector.py` | Calculates weighted score, determines verdict | LIKELY_DEEPFAKE / LIKELY_AUTHENTIC / INCONCLUSIVE |

---

## Installation

### Prerequisites

| Dependency | Purpose | Required |
|------------|---------|----------|
| **FFmpeg** | Video frame extraction | ✅ Yes |
| **Python 3.10+** | Runtime | ✅ Yes |

### Step 1: Install System Dependencies

```bash
# macOS (using Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_api_key_here
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" → "Create API Key"
4. Copy the key and paste into your `.env` file

---

## Usage Guide

### Basic Usage

The tool requires two inputs:
1. **Reference Photo** (`--photo` or `-p`): A clear photo of the person's face
2. **Video File** (`--video` or `-v`): The video to analyze

```bash
# Basic analysis
python -m src.main --photo reference.jpg --video verification.mp4

# Short form
python -m src.main -p reference.jpg -v verification.mp4
```

### Save Results to File

```bash
# Save JSON report
python -m src.main -p reference.jpg -v verification.mp4 --output result.json
```

### CLI Options

| Option | Description |
|--------|-------------|
| `-p, --photo` | Reference photo path (required) |
| `-v, --video` | Video file path (required) |
| `-o, --output` | Save JSON report to file |
| `--api-key` | Gemini API key (overrides .env) |

### Provide API Key via Command Line

```bash
python -m src.main -p photo.jpg -v video.mp4 --api-key YOUR_API_KEY
```

### Programmatic Usage

```python
from src.detector import DeepfakeDetector

# Initialize detector
detector = DeepfakeDetector()

# Run analysis
result = detector.analyze(
    reference_photo="path/to/reference.jpg",
    video_path="path/to/video.mp4"
)

# Access results
print(f"Verdict: {result.verdict.value}")
print(f"Confidence: {result.confidence_score:.2%}")

# Get detailed layer results
if result.book_verification:
    print(f"Book Title: {result.book_verification.book_title}")
    print(f"Book Found: {result.book_verification.book_found}")

# Save to JSON
import json
with open("result.json", "w") as f:
    json.dump(result.to_dict(), f, indent=2)

# Clean up
detector.close()
```

---

## Understanding Results

### Verdicts Explained

| Verdict | Confidence Score | Meaning |
|---------|------------------|---------|
| **LIKELY_AUTHENTIC** | 0% - 50% | Video appears genuine, low manipulation indicators |
| **INCONCLUSIVE** | 50% - 70% | Unable to determine, requires human review |
| **LIKELY_DEEPFAKE** | 70% - 100% | Strong indicators of manipulation detected |

> **Note**: Score represents likelihood of deepfake. Lower = more likely authentic.

---

### Example 1: LIKELY_AUTHENTIC (Low Suspicion)

```
============================================================
ANALYSIS RESULTS
============================================================

VERDICT:             LIKELY_AUTHENTIC
Confidence Score:    23.00%
Processing Time:     18.5s

------------------------------------------------------------
LAYER SCORES (Gemini Analysis)
------------------------------------------------------------

Book Verification: 15.00%
  • Detected title: Thinking, Fast and Slow
  • Book is REAL: 'Thinking, Fast and Slow' by Daniel Kahneman
  • No spelling errors detected

Movement Analysis: 20.00%
  • Body pacing: natural
  • No movement path issues detected

AI Signals: 10.00%
  • No blending artifacts
  • Consistent lighting
  • No temporal anomalies

Eye Analysis: 25.00%
  • Normal blink patterns observed

Identity Match: 30.00%
  • Matches reference photo
  • High consistency across frames

============================================================
```

**What This Means:**
- ✅ The book is real and correctly spelled
- ✅ Body movements appear natural
- ✅ No AI generation artifacts detected
- ✅ The person matches the reference photo
- ✅ **Recommended Action**: Approve the verification

---

### Example 2: LIKELY_DEEPFAKE (High Suspicion)

```
============================================================
ANALYSIS RESULTS
============================================================

VERDICT:             LIKELY_DEEPFAKE
Confidence Score:    85.00%
Processing Time:     38.7s

------------------------------------------------------------
LAYER SCORES
------------------------------------------------------------

Book Verification: 80.00%
  • Detected title: Thinkng Fast adn Slow
  • Spelling issues: ['Thinkng', 'adn']
  • Book not found in online databases

Eye Analysis: 90.00%
  • Very low blink rate: 3.2/min (normal: 15-20)
  • Abnormal blink duration: 45ms

Facial Expressions: 85.00%
  • Very static facial movements detected
  • Inconsistent micro-expression patterns

Body Movement: 75.00%
  • Unusually still head position
  • Jerky head movements detected

Identity Match: 70.00%
  • Moderate identity match: 58.00%
  • High identity variance across frames: 0.0823

------------------------------------------------------------
EVIDENCE FRAMES
------------------------------------------------------------
  Frame 45 (00:01.87): Blink anomaly detected
  Frame 128 (00:05.33): Identity drift observed
  Frame 256 (00:10.67): Book text distortion

============================================================
```

**What This Means:**
- ❌ The book title has spelling errors (AI-generated text artifact)
- ❌ The person barely blinks (3.2/min vs normal 15-20/min)
- ❌ Facial movements are unnaturally static
- ❌ Identity varies significantly across frames
- ❌ **Recommended Action**: REJECT - Request in-person verification

---

### Example 3: INCONCLUSIVE (Requires Review)

```
============================================================
ANALYSIS RESULTS
============================================================

VERDICT:             INCONCLUSIVE
Confidence Score:    58.00%
Processing Time:     45.1s

------------------------------------------------------------
LAYER SCORES
------------------------------------------------------------

Book Verification: 45.00%
  • Detected title: The Art of War
  • Book found: 'The Art of War' by Sun Tzu
  • Gemini: Text partially obscured by hand

Eye Analysis: 65.00%
  • Low blink rate: 11.3/min (normal: 15-20)
  • Normal blink duration: 312ms

Facial Expressions: 55.00%
  • Moderate facial movement variance
  • Some micro-expression inconsistencies

Body Movement: 50.00%
  • Natural head movement patterns
  • Some unusual hand positioning

Identity Match: 60.00%
  • Moderate identity match: 71.00%
  • Moderate identity variance: 0.0312

============================================================
```

**What This Means:**
- ⚠️ Book is real but text is partially hidden
- ⚠️ Blink rate is slightly below normal range
- ⚠️ Some inconsistencies but not definitive
- ⚠️ Identity match is borderline (71%)
- ⚠️ **Recommended Action**: Request human review or additional verification

---

### Recommended Actions by Verdict

| Verdict | Action | Details |
|---------|--------|---------|
| **LIKELY_AUTHENTIC** | ✅ Approve | Proceed with verification |
| **INCONCLUSIVE** | 👁️ Human Review | Have a trained operator review the video |
| **LIKELY_DEEPFAKE** | ❌ Reject | Request in-person verification or additional proof |

---

## Training Data

### Purpose

Training data helps calibrate the system for your specific use case. While the tool works out-of-the-box, providing examples of real and fake videos improves accuracy.

### Directory Structure

Create a `training/` folder in your project root:

```
training/
├── real/                        # Known authentic videos
│   ├── person1_real_01.mp4      # Real video of person 1
│   ├── person1_real_02.mp4      # Another real video of person 1
│   ├── person2_real_01.mp4      # Real video of person 2
│   └── ...
│
└── fake/                        # Known deepfake videos
    ├── person1_fake_01.mp4      # Deepfake of person 1
    ├── person1_fake_02.mp4      # Another deepfake of person 1
    ├── person2_fake_01.mp4      # Deepfake of person 2
    └── ...
```

### File Naming Convention

Use this naming pattern for training files:

```
{person_id}_{label}_{sequence}.{extension}
```

| Component | Values | Example |
|-----------|--------|---------|
| `person_id` | Unique identifier for the person | `person1`, `john_doe`, `user_12345` |
| `label` | `real` or `fake` | `real`, `fake` |
| `sequence` | Number for multiple videos | `01`, `02`, `03` |
| `extension` | Video format | `mp4`, `webm`, `mov` |

**Examples:**
- `john_doe_real_01.mp4` - Real video of John Doe
- `john_doe_fake_01.mp4` - Deepfake video of John Doe
- `user_12345_real_02.mp4` - Second real video of user 12345

### Reference Photos for Training

Place reference photos alongside training videos:

```
training/
├── references/                  # Reference photos
│   ├── person1_reference.jpg
│   ├── person2_reference.jpg
│   └── ...
├── real/
│   └── ...
└── fake/
    └── ...
```

### Running Training Evaluation

```bash
# Evaluate accuracy on training set (future feature)
python -m src.main --evaluate training/
```

---

## Configuration

### Environment Variables

Edit `.env` file:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Detection thresholds (optional)
DEEPFAKE_THRESHOLD=0.35          # Below this = LIKELY_AUTHENTIC
AUTHENTIC_THRESHOLD=0.55         # Above this = LIKELY_DEEPFAKE

# Processing settings (optional)
MAX_VIDEO_DURATION=60            # Maximum video length in seconds
FRAME_EXTRACTION_FPS=10          # Frames per second to extract

# Gemini model (optional)
GEMINI_MODEL=models/gemini-2.5-flash
```

### Threshold Tuning

Adjust thresholds based on your security requirements:

| Use Case | DEEPFAKE_THRESHOLD | AUTHENTIC_THRESHOLD |
|----------|-------------------|---------------------|
| **High Security** (banking) | 0.4 | 0.6 |
| **Standard** (default) | 0.5 | 0.7 |
| **Lenient** (low-risk) | 0.6 | 0.8 |

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `GEMINI_API_KEY is required` | Set API key in `.env` or use `--api-key` |
| `Cannot open video` | Check video format (MP4, WebM, MOV supported) |
| `No face detected in reference` | Use a clearer, front-facing photo |
| `OCR error` | Install Tesseract: `brew install tesseract` |
| `Audio extraction failed` | Install FFmpeg: `brew install ffmpeg` |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | LIKELY_AUTHENTIC - Verification passed |
| 1 | INCONCLUSIVE - Requires human review |
| 2 | LIKELY_DEEPFAKE - Verification failed |

---

## License

MIT License - See LICENSE file for details.

---

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Review the PRD.md for detailed technical specifications
