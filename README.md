# Vision-Based Desktop Automation with Dynamic Icon Grounding

A Python application that uses OCR-based computer vision to dynamically locate and interact with desktop icons on Windows. The system finds the Notepad icon **regardless of its position** on the desktop, enabling robust automation even when icon positions change.

## 🎯 Features

- **Dynamic Icon Grounding**: Uses EasyOCR to find icon text labels, then clicks above the text where the icon image is located
- **Position Independent**: Works regardless of where the icon is on the desktop (top-left, center, bottom-right)
- **Robust Error Handling**: Exponential backoff retries with graceful exit on failure
- **Annotated Screenshots**: Generates visual proof of icon detection for deliverables

## 📋 Requirements

- **OS**: Windows 10/11
- **Resolution**: 1920x1080 (configurable)
- **Python**: 3.9+
- **Pre-requisite**: Create a Notepad shortcut icon on the desktop

## 🚀 Installation

```bash
# Clone the repository
git clone <repository-url>
cd vision-desktop-automation

# Install dependencies with uv
uv sync

# Copy environment configuration
cp .env.example .env
```

## 💻 Usage

### Test Grounding Only
Test that the system can find the Notepad icon without running full automation:
```bash
uv run python -m src.main --test-grounding
```

### Run Full Automation
Process blog posts from JSONPlaceholder API:
```bash
# Process 10 posts (default)
uv run python -m src.main

# Process fewer posts
uv run python -m src.main --posts 3
```

## ⚙️ Configuration

Environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SCREEN_WIDTH` | 1920 | Screen width in pixels |
| `SCREEN_HEIGHT` | 1080 | Screen height in pixels |
| `OUTPUT_DIR` | tjm-project | Output folder on Desktop |
| `MAX_RETRIES` | 3 | Max grounding attempts |
| `RETRY_DELAY` | 1.0 | Base delay for exponential backoff |

## 🔍 How It Works

### Grounding Approach: OCR-Based Detection

1. **Screenshot**: Capture the desktop using `mss`
2. **OCR**: EasyOCR scans for all text labels with bounding boxes
3. **Match**: Find text matching "Notepad" (exact or partial match)
4. **Calculate**: Return coordinates ~45 pixels above text center (where icon image is)
5. **Click**: Double-click to launch the application

```
┌─────────────────────┐
│     [Icon Image]    │  ← Click here (text center - 45px)
│                     │
│      "Notepad"      │  ← OCR detects this text
└─────────────────────┘
```

### Why OCR Over VLM Image Analysis?

| Aspect | OCR | VLM (GPT-4V, Gemini) |
|--------|-----|---------------------|
| **Speed** | Fast (local) | Slow (API round-trip) |
| **Cost** | Free | Per-token charges |
| **Reliability** | Exact text positions | Sometimes inaccurate |
| **Offline** | ✓ Works offline | ✗ Requires internet |

## 📁 Project Structure

```
src/
├── main.py           # Entry point, CLI
├── config.py         # Environment configuration
├── screenshot.py     # Desktop screenshot capture
├── ocr_grounder.py   # EasyOCR-based icon grounding
├── mouse_keyboard.py # Mouse/keyboard automation
├── api_client.py     # JSONPlaceholder API client
├── notepad.py        # Notepad automation workflow
└── annotations.py    # Screenshot annotation for deliverables
```

## 🎓 Interview Discussion Points

### Icon Detection Approach
- OCR finds text labels and clicks above them
- Works for **any icon with readable text** - no pre-existing images needed
- Handles different fonts and sizes as long as text is legible

### Failure Cases & Mitigations
| Failure Case | Mitigation |
|--------------|------------|
| Icon text not detected | Retry with fresh screenshot |
| Multiple similar icons | Exact match prioritized over partial |
| Obscured by windows | Win+D shows desktop first |
| API unavailable | Graceful exit with error message |

### Robustness
- **Themes**: OCR works on both light and dark themes
- **Icon sizes**: Text labels scale proportionally with icons
- **Backgrounds**: High-contrast text remains readable
- **Similar names**: "Notepad" matches before "Notepad++"

### Scaling the Solution
- Add more target labels to find any desktop icon
- Multi-language OCR for international systems
- Could add LLM fallback for fuzzy matching if needed

## 📄 License

MIT
