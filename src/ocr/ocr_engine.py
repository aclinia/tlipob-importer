from typing import Any

import cv2
import numpy as np

# EasyOCR bbox: 4 corner points, each [x, y]
type Bbox = list[list[int]]
type OcrResult = tuple[Bbox, str, float, tuple[float, float, float]]


def preprocess_tooltip(tooltip_img: np.ndarray) -> np.ndarray:
    """Preprocess a cropped tooltip image for OCR.

    The tooltip has colored text on a semi-transparent dark background.
    EasyOCR handles this well with just upscaling — heavy preprocessing
    (inversion, binarization) actually hurts because game-world elements
    bleed through the semi-transparent overlay.
    """
    h, w = tooltip_img.shape[:2]
    upscaled = cv2.resize(tooltip_img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
    return upscaled


def _median_text_hsv(
    image_hsv: np.ndarray, image_gray: np.ndarray, bbox: Bbox
) -> tuple[float, float, float]:
    """Compute the median HSV of bright (text) pixels within a bounding box."""
    pts = np.array(bbox, dtype=np.int32)
    y1 = max(0, pts[:, 1].min())
    y2 = min(image_hsv.shape[0], pts[:, 1].max())
    x1 = max(0, pts[:, 0].min())
    x2 = min(image_hsv.shape[1], pts[:, 0].max())

    roi_hsv = image_hsv[y1:y2, x1:x2]
    roi_gray = image_gray[y1:y2, x1:x2]

    bright = roi_gray > 100
    if np.sum(bright) < 5:
        return (0.0, 0.0, 0.0)

    return (
        float(np.median(roi_hsv[:, :, 0][bright])),
        float(np.median(roi_hsv[:, :, 1][bright])),
        float(np.median(roi_hsv[:, :, 2][bright])),
    )


def extract_text(
    tooltip_img: np.ndarray, reader: Any
) -> list[OcrResult]:
    """Run OCR on a tooltip image.

    Args:
        tooltip_img: BGR cropped tooltip image.
        reader: An initialized easyocr.Reader instance.

    Returns:
        List of (bbox, text, confidence, hsv) sorted top-to-bottom,
        where hsv is the median (H, S, V) of the text pixels.
    """
    processed = preprocess_tooltip(tooltip_img)
    hsv = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

    results: list[tuple[Bbox, str, float]] = reader.readtext(
        processed,
        paragraph=False,
        text_threshold=0.5,
        low_text=0.3,
        width_ths=0.7,
    )

    # Sort by vertical position (top of bounding box)
    results.sort(key=lambda r: r[0][0][1])

    # Annotate each result with text color
    annotated: list[OcrResult] = []
    for bbox, text, conf in results:
        text_hsv = _median_text_hsv(hsv, gray, bbox)
        annotated.append((bbox, text, conf, text_hsv))

    return annotated
