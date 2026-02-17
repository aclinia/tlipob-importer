import re

# Lines matching these patterns are excluded entirely
EXCLUDE_PATTERNS = [
    re.compile(r"^Equipped", re.IGNORECASE),
    re.compile(r"^Require", re.IGNORECASE),
    re.compile(r"^Lv\s*[.\d]", re.IGNORECASE),
    re.compile(r"^L[uv]?\.\s*\d", re.IGNORECASE),  # OCR variants of standalone "Lv.90"
    re.compile(r"Energy\s*#?\d", re.IGNORECASE),
    re.compile(r"@Energy", re.IGNORECASE),
    re.compile(r"^\d+\s*Energy\s*$", re.IGNORECASE),
    re.compile(r"^Corroded$", re.IGNORECASE),
    re.compile(r"^Priceless$", re.IGNORECASE),
    re.compile(r"^Rarity", re.IGNORECASE),
]

# Flavor text color in HSV (warm yellow/orange, H≈15-25, S≈100-150)
FLAVOR_HUE_RANGE = (12, 28)
FLAVOR_SAT_RANGE = (80, 170)

MIN_CONFIDENCE = 0.3


def _is_flavor_text(hsv: tuple[float, float, float]) -> bool:
    """Check if the text color matches the flavor text style (warm orange/yellow)."""
    h, s, _v = hsv
    return FLAVOR_HUE_RANGE[0] <= h <= FLAVOR_HUE_RANGE[1] and FLAVOR_SAT_RANGE[0] <= s <= FLAVOR_SAT_RANGE[1]


def clean_ocr_text(text: str) -> str:
    """Clean up common OCR artifacts."""
    # Remove bullet point characters
    text = re.sub(r"[•●○◦⚫⬤]", "", text)
    # Fullwidth percent sign → normal
    text = text.replace("\uff05", "%")
    # Remove [ ] bracket artifacts from OCR
    text = re.sub(r"^[\[\(]+\s*", "", text)
    text = re.sub(r"\s*\]+$", "", text)
    # Clean up "[Lv" → "Lv" mid-line
    text = re.sub(r"\s*\[(?=Lv)", " ", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_tooltip_text(
    ocr_results: list[tuple[list, str, float, tuple[float, float, float]]],
) -> list[str]:
    """Filter and clean OCR results into item stat lines.

    Args:
        ocr_results: List of (bbox, text, confidence, hsv) from extract_text.

    Returns:
        Cleaned lines: item name, type, base stat, modifiers.
    """
    lines = []

    for _, raw_text, confidence, hsv in ocr_results:
        if confidence < MIN_CONFIDENCE:
            continue

        text = clean_ocr_text(raw_text)
        if not text:
            continue

        # Skip very short garbage lines (single chars, digits)
        if len(text) <= 2:
            continue

        # Flavor text is warm yellow/orange — stop processing once we hit it
        if _is_flavor_text(hsv):
            break

        # Skip excluded lines
        if any(p.search(text) for p in EXCLUDE_PATTERNS):
            continue

        lines.append(text)

    return lines
