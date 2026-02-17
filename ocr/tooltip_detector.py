import cv2
import numpy as np

# Tooltip always appears in center-left of 2560x1440 screenshots.
# The "Equipped" label is consistently at approximately x=1191, y=339.
# The tooltip text extends below and to the right of that anchor.
DEFAULT_CROP = (1100, 320, 600, 880)  # (x, y, w, h)


def detect_tooltip_region(image: np.ndarray) -> tuple[int, int, int, int] | None:
    """Find the tooltip region in a game screenshot.

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


def detect_separator_line(tooltip_img: np.ndarray) -> int | None:
    """Find the y-position of the base-stat separator line in a tooltip crop.

    The separator is a thin gray line sitting just below the base stat text
    (e.g. "565 Max Energy Shield") and above the affix section. It's
    distinguished from the energy bar borders by having bright text content
    within ~30px above it.

    Args:
        tooltip_img: BGR cropped tooltip image.

    Returns:
        Y-coordinate of the separator line in crop space, or None if not found.
    """
    gray = cv2.cvtColor(tooltip_img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    x_lo, x_hi = 100, min(450, w)

    # Scan for candidate horizontal lines, keeping the LAST one found.
    # Start at y=200 to skip past the energy bar area (y≈150-195).
    last_sep = None

    for y in range(200, min(400, h - 3)):
        row = gray[y, x_lo:x_hi]
        line_pixels = int(np.sum((row > 60) & (row < 180)))
        text_pixels = int(np.sum(row > 180))

        # Must be a clear line with few text pixels on it
        if line_pixels < 150 or text_pixels > 30:
            continue

        # Rows 3px above and below must be mostly dark (thin line)
        row_above = gray[y - 3, x_lo:x_hi]
        row_below = gray[y + 3, x_lo:x_hi]
        if np.sum(row_above < 60) < 250 or np.sum(row_below < 60) < 250:
            continue

        last_sep = y

    return last_sep
