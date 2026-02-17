import re
from dataclasses import dataclass, field

from .ocr_engine import Bbox, OcrResult

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

# Pattern to extract equipment type (strip parenthetical and Lv info)
EQUIP_TYPE_RE = re.compile(r"^(.+?)\s*\(")

# Base stat pattern: a bare number + stat name, e.g. "565 Max Energy Shield", "1615 Evasion"
# Does NOT start with +/- (those are affixes)
BASE_STAT_RE = re.compile(r"^\d+\s+[A-Z]")


@dataclass
class ItemData:
    name: str = ""
    equipment_type: str = ""
    base_stats: str = ""
    custom_affixes: list[str] = field(default_factory=lambda: [])

    def to_dict(self) -> dict[str, str | list[str] | None]:
        result: dict[str, str | list[str] | None] = {
            "name": self.name,
            "equipmentType": self.equipment_type,
            "baseStats": self.base_stats if self.base_stats else None,
            "customAffixes": self.custom_affixes,
        }
        return result


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


def _extract_equipment_type(text: str) -> str:
    """Extract equipment type, stripping the parenthetical slot and Lv info.

    e.g. 'INT Helmet(Helmet) Lv.100' -> 'INT Helmet'
    """
    m = EQUIP_TYPE_RE.match(text)
    if m:
        return m.group(1).strip()
    # Fallback: strip Lv.XXX from the end
    return re.sub(r"\s*Lv\.\d+\s*$", "", text).strip()


def _ocr_line_y(bbox: Bbox) -> float:
    """Get the vertical center of an OCR bounding box (in upscaled coordinates)."""
    import numpy as np

    pts = np.array(bbox, dtype=np.int32)
    return float((pts[:, 1].min() + pts[:, 1].max()) / 2)


def parse_tooltip_text(
    ocr_results: list[OcrResult],
    separator_y: int | None = None,
) -> ItemData:
    """Parse OCR results into structured item data.

    Args:
        ocr_results: List of (bbox, text, confidence, hsv) from extract_text.
        separator_y: Y-position of the separator line in the original tooltip
                     crop (before 2x upscale). None if no separator found.

    Returns:
        Structured ItemData with name, type, base stats, and affixes.
    """
    item = ItemData()

    # Separator y in upscaled (2x) coordinates to match OCR bboxes
    sep_y_upscaled = separator_y * 2 if separator_y is not None else None

    # Phase 1: collect all valid lines with their y-positions
    valid_lines: list[tuple[float, str]] = []

    for bbox, raw_text, confidence, hsv in ocr_results:
        if confidence < MIN_CONFIDENCE:
            continue

        text = clean_ocr_text(raw_text)
        if not text or len(text) <= 2:
            continue

        if _is_flavor_text(hsv):
            break

        if any(p.search(text) for p in EXCLUDE_PATTERNS):
            continue

        y_pos = _ocr_line_y(bbox)
        valid_lines.append((y_pos, text))

    if not valid_lines:
        return item

    # Phase 2: assign roles
    # First line = name
    item.name = valid_lines[0][1]

    # Second line = equipment type (if it looks like a type line)
    if len(valid_lines) > 1:
        item.equipment_type = _extract_equipment_type(valid_lines[1][1])

    # Phase 3: split remaining lines by separator
    remaining = valid_lines[2:]  # skip name and type

    if sep_y_upscaled is not None and remaining:
        # Lines above separator = base stats, below = affixes
        above = [text for y, text in remaining if y < sep_y_upscaled]
        below = [text for y, text in remaining if y >= sep_y_upscaled]

        if above:
            item.base_stats = " ".join(above)
        item.custom_affixes = below
    else:
        # No separator detected. Use pattern matching as fallback:
        # if the first remaining line looks like a base stat (number + name),
        # treat it as the base stat and the rest as affixes.
        texts = [text for _, text in remaining]
        if texts and BASE_STAT_RE.match(texts[0]):
            item.base_stats = texts[0]
            item.custom_affixes = texts[1:]
        else:
            item.custom_affixes = texts

    return item
