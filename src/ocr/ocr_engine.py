from typing import Any

import cv2
import numpy as np

# OCR bbox: 4 corner points, each [x, y]
type Bbox = list[list[int]]
type OcrResult = tuple[Bbox, str, float, tuple[float, float, float], bool]

def preprocess_tooltip(tooltip_img: np.ndarray) -> np.ndarray:
    """Preprocess a cropped tooltip image for OCR.

    The tooltip has colored text on a semi-transparent dark background.
    PaddleOCR handles this well at native resolution — no upscaling needed.
    """
    return tooltip_img


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


def _has_bullet_left(image_hsv: np.ndarray, bbox: Bbox) -> bool:
    """Check for a colored bullet point in the strip to the left of a text bbox."""
    x_min = min(p[0] for p in bbox)
    y_min = min(p[1] for p in bbox)
    y_max = max(p[1] for p in bbox)

    strip_x1 = max(0, x_min - 35)
    strip_x2 = max(0, x_min - 3)
    if strip_x2 <= strip_x1:
        return False

    strip = image_hsv[y_min:y_max, strip_x1:strip_x2]
    bright_saturated = (strip[:, :, 1] > 50) & (strip[:, :, 2] > 100)
    return bool(np.sum(bright_saturated) > 50)


def _merge_same_line(results: list[OcrResult], y_threshold: float = 15.0) -> list[OcrResult]:
    """Merge OCR fragments that share the same visual line.

    PaddleOCR often splits a single line into multiple fragments
    (e.g., "+257", "Max", "Life"). This groups fragments whose vertical
    centers are within y_threshold pixels, then merges each group
    left-to-right into a single result.
    """
    if not results:
        return results

    # Compute y-center for each result
    def y_mid(r: OcrResult) -> float:
        bbox = r[0]
        ys = [p[1] for p in bbox]
        return (min(ys) + max(ys)) / 2.0

    # Group fragments by similar y-center
    groups: list[list[OcrResult]] = []
    sorted_results = sorted(results, key=y_mid)

    current_group: list[OcrResult] = [sorted_results[0]]
    current_y = y_mid(sorted_results[0])

    for r in sorted_results[1:]:
        ym = y_mid(r)
        if abs(ym - current_y) <= y_threshold:
            current_group.append(r)
        else:
            groups.append(current_group)
            current_group = [r]
            current_y = ym

    groups.append(current_group)

    # Merge each group into a single OcrResult
    merged: list[OcrResult] = []
    for group in groups:
        if len(group) == 1:
            merged.append(group[0])
            continue

        # Sort left-to-right by x position
        group.sort(key=lambda r: min(p[0] for p in r[0]))

        # Compute enclosing bounding box
        all_xs = [p[0] for r in group for p in r[0]]
        all_ys = [p[1] for r in group for p in r[0]]
        x1, x2 = min(all_xs), max(all_xs)
        y1, y2 = min(all_ys), max(all_ys)
        bbox: Bbox = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]

        text = " ".join(r[1] for r in group)
        conf = min(r[2] for r in group)
        hsv_color = group[0][3]  # leftmost fragment's color
        has_bullet = any(r[4] for r in group)

        merged.append((bbox, text, conf, hsv_color, has_bullet))

    return merged


def extract_text(
    tooltip_img: np.ndarray, reader: Any
) -> list[OcrResult]:
    """Run OCR on a tooltip image.

    Args:
        tooltip_img: BGR cropped tooltip image.
        reader: An initialized PaddleOCR instance.

    Returns:
        List of (bbox, text, confidence, hsv, has_bullet) sorted top-to-bottom,
        where hsv is the median (H, S, V) of the text pixels and has_bullet
        indicates a colored bullet point to the left of the text.
    """
    processed = preprocess_tooltip(tooltip_img)
    hsv = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

    # PaddleOCR 3.4+ predict() returns OCRResult objects with parallel lists
    page_results = reader.predict(processed)
    results: list[tuple[Bbox, str, float]] = []
    for page in page_results:
        for poly, text, score in zip(
            page["dt_polys"], page["rec_texts"], page["rec_scores"]
        ):
            bbox: Bbox = [[int(p[0]), int(p[1])] for p in poly]
            results.append((bbox, text, float(score)))

    # Sort by vertical position (top of bounding box)
    results.sort(key=lambda r: r[0][0][1])

    # Annotate each result with text color and bullet presence
    annotated: list[OcrResult] = []
    for bbox, text, conf in results:
        text_hsv = _median_text_hsv(hsv, gray, bbox)
        has_bullet = _has_bullet_left(hsv, bbox)
        annotated.append((bbox, text, conf, text_hsv, has_bullet))

    return _merge_same_line(annotated)
