# 🔍 Deepfake Detection Tool

**AI-powered identity verification and deepfake detection for secure video authentication.**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Why This Tool Exists](#why-this-tool-exists)
- [How It Works](#how-it-works)
- [Repository Structure](#repository-structure)
- [Data Flow Process](#data-flow-process)
- [Scoring Logic](#scoring-logic)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Understanding Results](#understanding-results)
- [Real-World Test Results](#real-world-test-results)
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
- AI struggles to generate readable, consistent text—making fake books obvious

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
│                    GEMINI MULTIMODAL ANALYSIS                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐        │
│  │ BOOK ANALYSIS   │ │ BODY MOVEMENT   │ │ AI SIGNALS      │        │
│  │ • Is book real? │ │ • Body pacing   │ │ • Blend artifacts│       │
│  │ • Spelling check│ │ • Movement paths│ │ • Lighting issues│       │
│  │ • AI text detect│ │ • Hand tremors  │ │ • Temporal glitch│       │
│  │ Weight: 30%     │ │ Weight: 20%     │ │ Weight: 25%      │       │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘        │
│           │                   │                   │                 │
│  ┌────────┴────────┐ ┌────────┴────────┐          │                 │
│  │ EYE ANALYSIS    │ │ IDENTITY MATCH  │          │                 │
│  │ • Blink patterns│ │ • Photo matching│          │                 │
│  │ • Gaze tracking │ │ • Frame-to-frame│          │                 │
│  │ Weight: 15%     │ │ Weight: 10%     │          │                 │
│  └────────┬────────┘ └────────┬────────┘          │                 │
│           │                   │                   │                 │
│           └─────────────┬─────┴───────────────────┘                 │
│                         │                                           │
│              ┌──────────▼──────────┐                                │
│              │  WEIGHTED SCORING   │                                │
│              │  & FINAL VERDICT    │                                │
│              └─────────────────────┘                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
L26_HomeWork/
│
├── 📄 README.md                 # This documentation
├── 📄 PRD.md                    # Product Requirements Document
├── 📄 QUICKSTART.md             # Quick start guide
├── 📄 PROMPTS_LOG.md            # Development session prompts
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example              # Environment variable template
│
├── 📁 src/                      # Source code
│   ├── __init__.py              # Package exports
│   ├── config.py                # Configuration management (thresholds, weights)
│   ├── models.py                # Data models & types (DetectionResult, LayerResult)
│   ├── detector.py              # Main detector orchestrator (DeepfakeDetector)
│   ├── main.py                  # CLI entry point
│   ├── cli_output.py            # CLI formatting utilities
│   │
│   ├── 📁 preprocessing/        # Input processing
│   │   ├── __init__.py          # Exports VideoProcessor, AudioProcessor
│   │   ├── video.py             # Video frame extraction (10 fps default)
│   │   ├── face.py              # Face detection utilities
│   │   └── audio.py             # Audio extraction & transcription
│   │
│   ├── 📁 analyzers/            # AI analysis
│   │   ├── __init__.py          # Exports GeminiAnalyzer
│   │   ├── gemini.py            # Gemini API integration
│   │   └── prompts.py           # Analysis prompts with detection tasks
│   │
│   └── 📁 utils/                # Utilities
│       ├── __init__.py
│       └── helpers.py           # Helper functions (timestamp formatting)
│
├── 📁 files_to_check/           # Input files for testing
│   ├── elena_reference.jpeg     # Reference photo
│   └── elena_video_*.mov        # Videos to analyze
│
├── 📁 results/                  # Analysis output files
│   ├── nurik_test_01.json       # REAL video result
│   ├── nurik_test_02.json       # FAKE video result (93.75% confidence)
│   ├── nurik_test_03.json       # FAKE video result (64.50% confidence)
│   └── nurik_test_04.json       # FAKE video result (85.50% confidence)
│
├── 📁 training/                 # Training data
│   ├── 📁 references/           # Reference photos for training
│   │   └── nurik_reference.jpeg
│   ├── 📁 real/                 # Known authentic videos
│   │   └── nurik_real_01.mov
│   └── 📁 fake/                 # Known deepfake videos
│       ├── nurik_fake_01.mov
│       ├── nurik_fake_02.mov
│       └── nurik_fake_03.mov
│
└── 📁 tests/                    # Test files
```

---

## Data Flow Process

### Complete Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW PROCESS                                │
└─────────────────────────────────────────────────────────────────────────┘

     INPUTS                PREPROCESSING              GEMINI ANALYSIS
┌──────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ Reference Photo  │    │                     │    │                     │
│ (photo.jpg)      │───▶│ Load as RGB array   │───▶│                     │
│                  │    │ via PIL             │    │                     │
└──────────────────┘    └─────────────────────┘    │  GEMINI 2.5 FLASH   │
                                                   │                     │
┌──────────────────┐    ┌─────────────────────┐    │  Multimodal prompt: │
│ Video File       │    │                     │    │  • Book analysis    │
│ (video.mp4)      │───▶│ Frame Extraction    │───▶│  • Spelling/text    │
│                  │    │ (10 fps → 8 frames) │    │  • Body movement    │
└──────────────────┘    └─────────────────────┘    │  • AI signals       │
                                                   │  • Eye analysis     │
                        ┌─────────────────────┐    │  • Identity match   │
                        │ Audio Extraction    │───▶│                     │
                        │ (optional)          │    └──────────┬──────────┘
                        └─────────────────────┘               │
                                                              ▼
                                                   ┌─────────────────────┐
                                                   │  GEMINI RESPONSE    │
                                                   │  (Structured JSON)  │
                                                   └──────────┬──────────┘
                                                              │
                                                              ▼
                                               ┌──────────────────────────┐
                                               │   RESULT PROCESSING      │
                                               │                          │
                                               │  1. Parse layer scores   │
                                               │  2. Apply weights        │
                                               │  3. Calculate confidence │
                                               │  4. Add evidence penalty │
                                               │  5. Determine verdict    │
                                               └────────────┬─────────────┘
                                                            │
                                                            ▼
      OUTPUT
┌─────────────────────────────────────────────────────────────────────────┐
│ DETECTION RESULT (JSON)                                                 │
│                                                                         │
│ • analysis_id: Unique UUID for tracking                                 │
│ • timestamp: ISO 8601 timestamp                                         │
│ • verdict: LIKELY_DEEPFAKE | LIKELY_AUTHENTIC | INCONCLUSIVE           │
│ • fake_confidence_score: 0.0 (authentic) to 1.0 (deepfake)             │
│ • detection_layers: Per-layer scores and findings                       │
│ • evidence_frames: Specific frames with issues                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Stage-by-Stage Breakdown

| Stage | Module | Input | Output | Description |
|-------|--------|-------|--------|-------------|
| **1. Load Reference** | `detector.py` | Photo path | RGB numpy array | Opens reference photo via PIL, converts to RGB |
| **2. Extract Frames** | `preprocessing/video.py` | Video path | List of frames | Extracts at 10 fps, selects up to 8 representative frames |
| **3. Extract Audio** | `preprocessing/audio.py` | Video path | Transcription text | Optional: Extracts audio for context |
| **4. Gemini Analysis** | `analyzers/gemini.py` | Reference + Frames | Structured JSON | Sends to Gemini with detailed prompt, returns analysis |
| **5. Process Results** | `detector.py` | Gemini JSON | Layer results | Converts to `DetectionResult` with typed layers |
| **6. Calculate Verdict** | `detector.py` | Layer scores | Final verdict | Weighted average + evidence penalty → verdict |

---

## Scoring Logic

### Layer Weights

Each analysis layer contributes to the final score with the following weights:

| Layer | Weight | What It Detects |
|-------|--------|-----------------|
| **Book Verification** | 30% | Fake/non-existent books, gibberish text, spelling errors |
| **AI Signals** | 25% | Blending artifacts, lighting issues, temporal anomalies, texture problems |
| **Body Movement** | 20% | Unnatural pacing, impossible physics, teleportation |
| **Eye Analysis** | 15% | Missing blinks, artificial reflections, unnatural gaze |
| **Identity Match** | 10% | Consistency with reference photo across frames |

### Confidence Score Calculation

```
weighted_score = Σ (layer_score × layer_weight) / Σ weights

# Evidence penalty (more evidence = higher confidence in deepfake)
evidence_penalty = min(0.2, evidence_frame_count × 0.03)
final_score = weighted_score + evidence_penalty
```

### Verdict Thresholds

| Confidence Score | Verdict |
|-----------------|---------|
| **0% - 35%** | `LIKELY_AUTHENTIC` |
| **35% - 55%** | `INCONCLUSIVE` |
| **55% - 100%** | `LIKELY_DEEPFAKE` |

> **Score Interpretation**: The score represents *likelihood of being a deepfake*. 
> - **Lower score** = More likely authentic
> - **Higher score** = More likely fake

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
print(f"Fake Confidence: {result.fake_confidence_score:.2%}")

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
| **LIKELY_AUTHENTIC** | 0% - 35% | Video appears genuine, low manipulation indicators |
| **INCONCLUSIVE** | 35% - 55% | Unable to determine, requires human review |
| **LIKELY_DEEPFAKE** | 55% - 100% | Strong indicators of manipulation detected |

### Output JSON Structure

```json
{
  "analysis_id": "unique-uuid-v4",
  "timestamp": "2025-12-27T23:56:09.583292Z",
  "verdict": "LIKELY_DEEPFAKE | LIKELY_AUTHENTIC | INCONCLUSIVE",
  "fake_confidence_score": 0.0-1.0,
  "processing_time_seconds": 14.09,
  "detection_layers": {
    "book_verification": {
      "score": 0.0-1.0,
      "findings": ["list of observations"],
      "book_found": true/false,
      "book_title": "string or null",
      "spelling_errors": ["list of errors"]
    },
    "eye_analysis": {
      "score": 0.0-1.0,
      "findings": ["list of observations"],
      "blink_rate": null,
      "expected_rate_range": [15, 20]
    },
    "facial_microexpressions": {
      "score": 0.0-1.0,
      "findings": ["AI signal observations"]
    },
    "body_movement": {
      "score": 0.0-1.0,
      "findings": ["movement observations"]
    },
    "identity_match": {
      "score": 0.0-1.0,
      "findings": ["Consistency: high/medium/low"],
      "reference_similarity": 0.0-1.0,
      "frame_variance": 0.0
    }
  },
  "evidence_frames": [
    {"frame": 2, "timestamp": "00:00.20", "issue": "description of issue"}
  ]
}
```

---

## Real-World Test Results

The following results are from actual test runs using the `nurik` training dataset.

### Test 01: REAL Video (nurik_real_01.mov)

| Field | Value |
|-------|-------|
| **Verdict** | ✅ `LIKELY_AUTHENTIC` |
| **Confidence** | 0.00% |
| **Processing Time** | 14.1 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 0% | "Trillion Dollar Coach" is a legitimate publication with no spelling errors |
| Eye Analysis | 0% | Natural eye movements, consistent gaze direction |
| Body Movement | 0% | No anomalies detected |
| Identity Match | 0% | High consistency with reference photo |

**Key Findings:**
- ✅ Book is REAL - "Trillion Dollar Coach" verified as legitimate publication
- ✅ No spelling errors or AI-generated text artifacts
- ✅ Natural facial expressions and hand movements
- ✅ High identity consistency

---

### Test 02: FAKE Video (nurik_fake_01.mov)

| Field | Value |
|-------|-------|
| **Verdict** | ❌ `LIKELY_DEEPFAKE` |
| **Confidence** | 93.75% |
| **Processing Time** | 20.9 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 100% | Extensive gibberish text: "SUTOLKT", "IÇIYHOUOЯ", "TEPBSAICMORBS" |
| Eye Analysis | 70% | No blinks observed, artificial eye reflections |
| AI Signals | 85% | Plastic-like skin, stuttering expressions |
| Body Movement | 90% | Book "teleports" into hand between frames |
| Identity Match | 20% | High consistency (person matches, but video is fake) |

**Evidence Frames:**
| Frame | Time | Issue |
|-------|------|-------|
| 2 | 00:00.20 | Book appears instantly with gibberish text |
| 3 | 00:00.30 | Visible gibberish text; unnatural mouth movement |
| 4 | 00:00.40 | AI-generated text artifacts; overly smooth skin |
| 5 | 00:00.50 | Rigid finger grip on book |

---

### Test 03: FAKE Video (nurik_fake_02.mov)

| Field | Value |
|-------|-------|
| **Verdict** | ❌ `LIKELY_DEEPFAKE` |
| **Confidence** | 64.50% |
| **Processing Time** | 16.1 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 100% | Non-existent title "SCIENTARK NIRSINE", gibberish author name |
| Eye Analysis | 10% | Natural blink detected (Frame 2) |
| AI Signals | 80% | "Painted" hair, unnaturally smooth jawline |
| Body Movement | 20% | Natural movements |
| Identity Match | 0% | High consistency |

**Key Evidence:**
- ❌ Book title is FAKE - "SCIENTARK NIRSINE" doesn't exist
- ❌ Gibberish text on cover: "DANIELA RULLE AMMUR DUUDU DIIIIIIIUAS"
- ⚠️ Eye blinks detected (positive sign)
- ❌ Skin texture too smooth, teeth unnaturally perfect

---

### Test 04: FAKE Video (nurik_fake_03.mov)

| Field | Value |
|-------|-------|
| **Verdict** | ❌ `LIKELY_DEEPFAKE` |
| **Confidence** | 85.50% |
| **Processing Time** | 18.1 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 100% | Misspelled words: "SURCIOTIC" (Surgical?), "TECHIOQVS" (Techniques?) |
| Eye Analysis | 50% | No full blinks in 8-frame sequence |
| AI Signals | 80% | "Painted" hair, flat lighting, airbrush-like skin |
| Body Movement | 70% | Overly smooth body pacing |
| Identity Match | 20% | High consistency |

**Key Evidence:**
- ❌ Book title contains obvious misspellings
- ❌ Publisher "AURIOROBES" is gibberish
- ❌ Skin has "plasticky" airbrushed appearance
- ❌ Hair lacks individual strand detail

---

### Detection Summary

| Test | Ground Truth | Verdict | Confidence | Correct? |
|------|--------------|---------|------------|----------|
| nurik_test_01 | REAL | `LIKELY_AUTHENTIC` | 0.00% | ✅ |
| nurik_test_02 | FAKE | `LIKELY_DEEPFAKE` | 93.75% | ✅ |
| nurik_test_03 | FAKE | `LIKELY_DEEPFAKE` | 64.50% | ✅ |
| nurik_test_04 | FAKE | `LIKELY_DEEPFAKE` | 85.50% | ✅ |

**Accuracy: 100% (4/4 correct classifications)**

---

### Elena Test Dataset Results

A second test dataset using **Elena's reference photo** was analyzed with 7 videos:
- **Tests 01-03**: Real authentic videos
- **Tests 04-07**: AI-generated deepfake videos

#### Test Elena-01: REAL Video ✅

| Field | Value |
|-------|-------|
| **Verdict** | ✅ `LIKELY_AUTHENTIC` |
| **Confidence** | 0.00% |
| **Processing Time** | 17.7 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 0% | "Trustworthy Online Controlled Experiments" - verified real publication |
| Eye Analysis | 0% | Natural gaze, consistent reflections |
| Body Movement | 0% | Natural movements |
| Identity Match | 0% | High consistency |

---

#### Test Elena-02: REAL Video ✅

| Field | Value |
|-------|-------|
| **Verdict** | ✅ `LIKELY_AUTHENTIC` |
| **Confidence** | 0.00% |
| **Processing Time** | 14.8 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 0% | "The Four" by Scott Galloway - verified real publication |
| Eye Analysis | 0% | Natural blinking observed, consistent gaze |
| Body Movement | 0% | Natural movements |
| Identity Match | 0% | High consistency |

---

#### Test Elena-03: REAL Video ❌ (False Positive)

| Field | Value |
|-------|-------|
| **Verdict** | ❌ `LIKELY_DEEPFAKE` (Incorrect) |
| **Confidence** | 73.25% |
| **Processing Time** | 25.9 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 0% | Real book detected correctly |
| Eye Analysis | 70% | Gaze felt "slightly fixed" |
| AI Signals | 95% | Flagged smooth skin, waxy texture on hands |
| Body Movement | 90% | Marked as "slightly robotic" |
| Identity Match | 10% | High consistency |

**Key Observation:** Despite detecting a **real book** (score 0%), the final verdict was incorrectly flagged as deepfake due to video quality/compression issues being misinterpreted as AI artifacts.

---

#### Test Elena-04: FAKE Video ✅

| Field | Value |
|-------|-------|
| **Verdict** | ✅ `LIKELY_DEEPFAKE` |
| **Confidence** | 69.50% |
| **Processing Time** | 24.2 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 100% | **GIBBERISH**: "MACHINIE LEARNDGGY TATA SCUBLICTAI", Author: "BOFEKGIJE" |
| Eye Analysis | 20% | Consistent gaze |
| AI Signals | 70% | Smooth skin, painted hair |
| Body Movement | 30% | Inconclusive (static frames) |
| Identity Match | 10% | High consistency |

---

#### Test Elena-05: FAKE Video ✅

| Field | Value |
|-------|-------|
| **Verdict** | ✅ `LIKELY_DEEPFAKE` |
| **Confidence** | 83.75% |
| **Processing Time** | 20.2 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 100% | **GIBBERISH**: "Mastieriiing PREDIENTIVE ANALLYKa.G" |
| Eye Analysis | 30% | Single blink observed |
| AI Signals | 85% | Temporal flickering, blending artifacts |
| Body Movement | 70% | Robotic facial expressions |
| Identity Match | 20% | High consistency |

---

#### Test Elena-06: FAKE Video ✅

| Field | Value |
|-------|-------|
| **Verdict** | ✅ `LIKELY_DEEPFAKE` |
| **Confidence** | 84.50% |
| **Processing Time** | 21.8 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 100% | **MISSPELLING**: "ALCHOANITHMS" (should be ALGORITHMS), gibberish: "AIMAFELN DTOY" |
| Eye Analysis | 60% | No blinks in 8 frames |
| AI Signals | 70% | Warping text, soft edges |
| Body Movement | 60% | Constrained movements |
| Identity Match | 10% | High consistency |

---

#### Test Elena-07: FAKE Video ✅

| Field | Value |
|-------|-------|
| **Verdict** | ✅ `LIKELY_DEEPFAKE` |
| **Confidence** | 80.50% |
| **Processing Time** | 22.3 seconds |

**Layer Scores:**
| Layer | Score | Key Findings |
|-------|-------|--------------|
| Book Verification | 100% | **REPETITIVE**: "data data science science", mixed English/Russian text |
| Eye Analysis | 10% | Consistent gaze |
| AI Signals | 80% | Blocky hair, flat lighting |
| Body Movement | 70% | Stiff upper body |
| Identity Match | 0% | High consistency |

---

### Elena Detection Summary

| Test | Ground Truth | Final Verdict | Confidence | Book Score | Correct? |
|------|--------------|---------------|------------|------------|----------|
| elena_01 | REAL | `LIKELY_AUTHENTIC` | 0.00% | 0% (Real) | ✅ |
| elena_02 | REAL | `LIKELY_AUTHENTIC` | 0.00% | 0% (Real) | ✅ |
| elena_03 | REAL | `LIKELY_DEEPFAKE` | 73.25% | 0% (Real) | ❌ False Positive |
| elena_04 | FAKE | `LIKELY_DEEPFAKE` | 69.50% | 100% (Gibberish) | ✅ |
| elena_05 | FAKE | `LIKELY_DEEPFAKE` | 83.75% | 100% (Gibberish) | ✅ |
| elena_06 | FAKE | `LIKELY_DEEPFAKE` | 84.50% | 100% (Misspelling) | ✅ |
| elena_07 | FAKE | `LIKELY_DEEPFAKE` | 80.50% | 100% (Repetitive) | ✅ |

**Final Accuracy: 85.7% (6/7 correct classifications)**

---

### Book-Only vs Final Decision Analysis

| Test | Book Score | Book-Only Decision | Final Decision | Better Approach? |
|------|------------|-------------------|----------------|------------------|
| elena_01 | 0% | ✅ AUTHENTIC | ✅ AUTHENTIC | Same |
| elena_02 | 0% | ✅ AUTHENTIC | ✅ AUTHENTIC | Same |
| elena_03 | 0% | ✅ AUTHENTIC | ❌ DEEPFAKE | **Book-only wins** |
| elena_04 | 100% | ❌ DEEPFAKE | ❌ DEEPFAKE | Same |
| elena_05 | 100% | ❌ DEEPFAKE | ❌ DEEPFAKE | Same |
| elena_06 | 100% | ❌ DEEPFAKE | ❌ DEEPFAKE | Same |
| elena_07 | 100% | ❌ DEEPFAKE | ❌ DEEPFAKE | Same |

**Book-Only Accuracy: 100% (7/7)**
**Final Decision Accuracy: 85.7% (6/7)**

> [!IMPORTANT]
> **Key Finding**: In this test set, the **book verification layer alone achieved 100% accuracy**, while the combined multi-layer approach introduced a false positive. This suggests that book text analysis is the most reliable deepfake indicator in scenarios where the subject holds a book.

> [!WARNING]
> **Inconsistent Book Detection**: On some test runs, book detection was not consistent and created **false positive alerts** when the AI misread only one or two words on the book cover (treating minor OCR errors as "misspellings"). This suggests that **prompt fine-tuning may be needed** to:
> - Ignore 1-2 inconsistent or very similar words that could be OCR artifacts
> - Distinguish between genuine gibberish text (e.g., "BOFEKGIJE", "SCUBLICTAI") vs. minor word misreadings
> - Apply a higher threshold before flagging text as AI-generated

---

### Conclusions: AI's Inability to Generate Convincing Text

The test results reveal a **critical weakness in current AI video generation**: the inability to produce coherent, realistic text on objects like book covers.

#### Observed AI Text Generation Failures

| Pattern | Examples from Tests |
|---------|---------------------|
| **Gibberish Words** | "MACHINIE LEARNDGGY", "BOFEKGIJE", "SCUBLICTAI", "ANALLYKa.G" |
| **Character Substitution** | "ALCHOANITHMS" → ALGORITHMS, "PREDIENTIVE" → PREDICTIVE |
| **Word Repetition** | "data data science science" |
| **Inconsistent Languages** | Mixed English/Russian on same cover |
| **Nonsense Subtitles** | "Sata Dnretyles for thecbaiyes", "AIMAFELN DTOY" |

#### Why AI Struggles with Text

1. **Semantic Understanding**: AI generates patterns that *look* like text but lack semantic meaning
2. **Consistency Requirements**: Text must remain stable across frames—AI often produces temporal flickering
3. **Knowledge Gap**: AI cannot verify if a book title/author actually exists
4. **Multi-language Confusion**: AI mixes languages inappropriately when generating text
5. **Font Rendering**: AI struggles to maintain consistent font sizing and spacing

> [!NOTE]
> **Conclusion**: Current AI video generation technology **cannot reliably produce readable, semantically correct text**. This makes the "hold a real book" verification approach highly effective for deepfake detection.

---

### Suggested Next Steps for Testing (Version 2.0)

#### 1. Address False Positive Issue

The false positive in `elena_03` suggests the non-book layers may over-trigger on:
- Compressed video artifacts
- Low-quality camera footage
- Natural skin smoothing (makeup, lighting)

**Recommendations:**
- [ ] Increase weight of book verification layer from 30% → 40%
- [ ] Add video quality detection to adjust thresholds dynamically
- [ ] Implement "high book confidence override" - if book is clearly real, reduce AI signal weight

#### 2. Expand Book Verification Testing

- [ ] Test with books in different languages (Spanish, French, Chinese)
- [ ] Test with handwritten notes/signs instead of printed books
- [ ] Test with digital screens showing text (tablets, monitors)
- [ ] Test with partial book title visibility

#### 3. Test Against Advanced Deepfake Methods

- [ ] Test with AI-generated videos that use **real book cover images** (not AI-generated text)
- [ ] Test with face-swap deepfakes on otherwise real footage
- [ ] Test with audio deepfakes paired with real video

#### 4. Improve Detection Metrics

- [ ] Track false positive rate (FPR) and false negative rate (FNR) separately
- [ ] Implement confidence intervals for verdicts
- [ ] Add "certainty level" indicator (high/medium/low)

#### 5. Additional Verification Layers

- [ ] Add audio-visual sync analysis (currently null in all tests)
- [ ] Implement temporal consistency scoring across more frames
- [ ] Add background consistency checking (bookshelf text in elena_04 was also gibberish)

> [!TIP]
> **Priority Improvement**: Given that book verification achieved 100% accuracy while other layers introduced errors, consider a **hierarchical decision system**: if book verification score is 0% (real book), require stronger evidence from other layers before flagging as deepfake.

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
| **High Security** (banking) | 0.30 | 0.50 |
| **Standard** (default) | 0.35 | 0.55 |
| **Lenient** (low-risk) | 0.45 | 0.65 |

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `GEMINI_API_KEY is required` | Set API key in `.env` or use `--api-key` |
| `Cannot open video` | Check video format (MP4, WebM, MOV supported) |
| `No face detected in reference` | Use a clearer, front-facing photo |
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
