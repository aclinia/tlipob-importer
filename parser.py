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

# When a line matches one of these, stop processing (flavor text starts)
FLAVOR_INDICATORS = [
    re.compile(r"^At first", re.IGNORECASE),
    re.compile(r"^The road ahead", re.IGNORECASE),
    re.compile(r"^A\s*bunch of", re.IGNORECASE),
    re.compile(r"^A hero is", re.IGNORECASE),
    re.compile(r"^After about", re.IGNORECASE),
    re.compile(r"the dream", re.IGNORECASE),
    re.compile(r"^Legend has", re.IGNORECASE),
    re.compile(r"^calm[;,]?\s*and", re.IGNORECASE),
    re.compile(r"^adventure and", re.IGNORECASE),
    re.compile(r"^thorns cover", re.IGNORECASE),
    re.compile(r"^land[;,]", re.IGNORECASE),
    re.compile(r"of the Fire Lord", re.IGNORECASE),
    re.compile(r"neatly cut flames", re.IGNORECASE),
]

MIN_CONFIDENCE = 0.3


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


def parse_tooltip_text(ocr_results: list[tuple[list, str, float]]) -> list[str]:
    """Filter and clean OCR results into item stat lines.

    Args:
        ocr_results: List of (bbox, text, confidence) from EasyOCR.

    Returns:
        Cleaned lines: item name, type, base stat, modifiers.
    """
    lines = []

    for _bbox, raw_text, confidence in ocr_results:
        if confidence < MIN_CONFIDENCE:
            continue

        text = clean_ocr_text(raw_text)
        if not text:
            continue

        # Skip very short garbage lines (single chars, digits)
        if len(text) <= 2 and not re.match(r"^\d+$", text):
            continue
        # Skip standalone single digits (OCR noise)
        if re.match(r"^\d$", text):
            continue

        # Check for flavor text — stop processing
        if any(p.search(text) for p in FLAVOR_INDICATORS):
            break

        # Skip excluded lines
        if any(p.search(text) for p in EXCLUDE_PATTERNS):
            continue

        lines.append(text)

    return lines
