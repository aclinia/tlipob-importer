# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

tlipob-importer is a Python OCR tool that extracts structured item data (name, equipment type, base stats, affixes) from game tooltip screenshots. It uses EasyOCR for text extraction and OpenCV for image processing.

## Commands

```bash
# Run all tests (requires example screenshots in /examples/inventory/)
uv run pytest

# Run a single test
uv run pytest tests/test_ocr.py::test_screenshot_1

# Type checking (strict mode)
uv run pyright

# Lint and format
uv run ruff check --fix

# Run CLI on screenshots
uv run python -m src.ocr.main path/to/screenshot.png
```

Uses `uv` as the package manager. Python 3.13+.

## Architecture

All source code is in `src/ocr/`. The pipeline flows through four modules:

1. **tooltip_detector.py** — Detects tooltip region in 2560x1440 screenshots using hardcoded crop coordinates. Finds separator line between base stats and affixes via pixel analysis.

2. **ocr_engine.py** — Preprocesses tooltip (2x upscale), runs EasyOCR with character allowlist, extracts median HSV color per text region. MIN_CONFIDENCE = 0.3.

3. **parser.py** — Three-phase parsing: (1) filter lines by confidence/length/color, (2) assign roles (name, equipment type), (3) split into base stats vs custom affixes using separator position or regex fallback. Uses HSV color ranges to detect and exclude flavor text.

4. **main.py** — CLI entry point accepting screenshot paths, outputs JSON.

Key types: `ItemData` (dataclass), `Bbox` (list of corner points), `OcrResult` (tuple of bbox, text, confidence, hsv_color).

## Code Quality

- Pyright strict mode with Python 3.13 target
- Tests are pytest-based with a module-scoped EasyOCR `reader` fixture (GPU-enabled)
- Imports use `src` prefix (e.g., `from src.ocr import ...`)
