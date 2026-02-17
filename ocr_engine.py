import cv2
import numpy as np


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


def extract_text(
    tooltip_img: np.ndarray, reader
) -> list[tuple[list, str, float]]:
    """Run OCR on a tooltip image.

    Args:
        tooltip_img: BGR cropped tooltip image.
        reader: An initialized easyocr.Reader instance.

    Returns:
        List of (bbox, text, confidence) sorted top-to-bottom.
    """
    processed = preprocess_tooltip(tooltip_img)

    results = reader.readtext(
        processed,
        paragraph=False,
        text_threshold=0.5,
        low_text=0.3,
        width_ths=0.7,
    )

    # Sort by vertical position (top of bounding box)
    results.sort(key=lambda r: r[0][0][1])

    return results
