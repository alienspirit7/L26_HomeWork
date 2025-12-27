# 🚀 Quick Start Guide

Get the Deepfake Detection Tool running in 5 minutes.

---

## Supported File Formats

| Input | Formats | Requirements |
|-------|---------|--------------|
| **Photo** | `.jpg`, `.jpeg`, `.png`, `.webp` | Min 512×512px, clear frontal face |
| **Video** | `.mp4`, `.webm`, `.mov` | Max 60 seconds, min 480p |

---

## 1. Prerequisites

Install system dependencies first:

```bash
# macOS
brew install cmake tesseract ffmpeg

# Ubuntu/Debian
sudo apt install cmake tesseract-ocr ffmpeg
```

---

## 2. Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env → add your GEMINI_API_KEY
```

**Get API Key:** [Google AI Studio](https://aistudio.google.com/) → Get API Key → Create

---

## 3. Run Analysis

```bash
python -m src.main --photo reference.jpg --video test_video.mp4
```

### Options

| Flag | Description |
|------|-------------|
| `-p`, `--photo` | Reference photo (required) |
| `-v`, `--video` | Video to analyze (required) |
| `-o`, `--output` | Save JSON results to file |
| `--gemini-only` | Skip preprocessing, use Gemini only |
| `--no-gemini` | Skip Gemini, use preprocessing only |

---

## 4. Training Files (Optional)

Organize your known real/fake videos:

```bash
mkdir -p training/references training/real training/fake
```

### File Naming Convention

```
training/
├── references/
│   └── {person}_reference.jpg     # e.g., john_reference.jpg
├── real/
│   └── {person}_real_{nn}.mp4     # e.g., john_real_01.mp4
└── fake/
    └── {person}_fake_{nn}.mp4     # e.g., john_fake_01.mp4
```

### Test Against Training Files

```bash
# Test real video (should show LIKELY_AUTHENTIC)
python -m src.main -p training/references/john_reference.jpg -v training/real/john_real_01.mp4

# Test fake video (should show LIKELY_DEEPFAKE)
python -m src.main -p training/references/john_reference.jpg -v training/fake/john_fake_01.mp4
```

---

## 5. Understanding Results

| Verdict | Score | Meaning |
|---------|-------|---------|
| **LIKELY_AUTHENTIC** | 0-50% | Video appears genuine |
| **INCONCLUSIVE** | 50-70% | Needs human review |
| **LIKELY_DEEPFAKE** | 70-100% | Manipulation detected |

### Exit Codes

| Code | Verdict |
|------|---------|
| 0 | LIKELY_AUTHENTIC |
| 1 | INCONCLUSIVE |
| 2 | LIKELY_DEEPFAKE |

---

## Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate

# Basic analysis
python -m src.main -p photo.jpg -v video.mp4

# Save JSON output
python -m src.main -p photo.jpg -v video.mp4 -o result.json

# Fast mode (Gemini only)
python -m src.main -p photo.jpg -v video.mp4 --gemini-only
```

---

For detailed documentation, see [README.md](README.md).
