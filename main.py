import sys

import cv2
import easyocr

from ocr_engine import extract_text
from parser import parse_tooltip_text
from tooltip_detector import detect_tooltip_region


def process_screenshot(image_path: str, reader: easyocr.Reader) -> str | None:
    """Process a single screenshot through the full pipeline.

    Returns newline-joined stat text, or None if tooltip not found.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: could not read {image_path}", file=sys.stderr)
        return None

    region = detect_tooltip_region(image)
    if region is None:
        print(f"Warning: no tooltip found in {image_path}", file=sys.stderr)
        return None

    x, y, w, h = region
    tooltip_img = image[y : y + h, x : x + w]

    ocr_results = extract_text(tooltip_img, reader)
    lines = parse_tooltip_text(ocr_results)

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <screenshot> [screenshot ...]", file=sys.stderr)
        sys.exit(1)

    reader = easyocr.Reader(["en"], gpu=True)

    for path in sys.argv[1:]:
        result = process_screenshot(path, reader)
        if result:
            if len(sys.argv) > 2:
                print(f"--- {path} ---")
            print(result)
            print()


if __name__ == "__main__":
    main()
