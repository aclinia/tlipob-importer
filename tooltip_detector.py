import cv2
import numpy as np

# Tooltip always appears in center-left of 2560x1440 screenshots.
# The "Equipped" label is consistently at approximately x=1191, y=339.
# The tooltip text extends below and to the right of that anchor.
DEFAULT_CROP = (1100, 320, 600, 880)  # (x, y, w, h)


def detect_tooltip_region(image: np.ndarray) -> tuple[int, int, int, int] | None:
    """Find the tooltip region in a game screenshot.

    Uses a fixed crop region where the tooltip appears in 2560x1440 screenshots,
    then trims vertically based on where text content actually exists.

    Args:
        image: BGR image (2560x1440 expected).

    Returns:
        (x, y, w, h) bounding box, or None if not found.
    """
    h_img, w_img = image.shape[:2]

    x0, y0, w0, h0 = DEFAULT_CROP

    # Clamp to image bounds
    x0 = max(0, min(x0, w_img - 1))
    y0 = max(0, min(y0, h_img - 1))
    w0 = min(w0, w_img - x0)
    h0 = min(h0, h_img - y0)

    return (x0, y0, w0, h0)
