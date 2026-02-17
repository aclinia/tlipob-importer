import sys

import cv2
import easyocr

from .ocr_engine import extract_text
from .parser import ItemData, parse_tooltip_text
from .tooltip_detector import detect_separator_line, detect_tooltip_region


def process_screenshot(image_path: str, reader: easyocr.Reader) -> ItemData | None:
    """Process a single screenshot through the full pipeline."""
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

    separator_y = detect_separator_line(tooltip_img)
    ocr_results = extract_text(tooltip_img, reader)

    return parse_tooltip_text(ocr_results, separator_y)
