import re
from dataclasses import dataclass, field

from .ocr_engine import OcrResult

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

@dataclass
class ItemData:
    name: str = ""
    equipment_type: str = ""
    custom_affixes: list[str] = field(default_factory=lambda: [])

    def to_dict(self) -> dict[str, str | list[str]]:
        return {
            "name": self.name,
            "equipmentType": self.equipment_type,
            "customAffixes": self.custom_affixes,
        }


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



def parse_tooltip_text(
    ocr_results: list[OcrResult],
) -> ItemData:
    """Parse OCR results into structured item data.

    Args:
        ocr_results: List of (bbox, text, confidence, hsv) from extract_text.

    Returns:
        Structured ItemData with name, type, and affixes.
    """
    item = ItemData()

    # Phase 1: collect all valid lines
    valid_lines: list[tuple[str, bool]] = []

    for _bbox, raw_text, confidence, hsv, has_bullet in ocr_results:
        if confidence < MIN_CONFIDENCE:
            continue

        text = clean_ocr_text(raw_text)
        if not text or len(text) <= 2:
            continue

        if _is_flavor_text(hsv):
            break

        if any(p.search(text) for p in EXCLUDE_PATTERNS):
            continue

        valid_lines.append((text, has_bullet))

    if not valid_lines:
        return item

    # Phase 2: assign roles
    # First line = name
    item.name = valid_lines[0][0]

    # Second line = equipment type (if it looks like a type line)
    if len(valid_lines) > 1:
        item.equipment_type = _extract_equipment_type(valid_lines[1][0])

    # Phase 3: extract affixes
    # Base stats have no bullet point and appear before the first bulleted line.
    # Skip them — keep only lines from the first bullet onward.
    remaining = valid_lines[2:]
    first_bullet = next((i for i, (_, b) in enumerate(remaining) if b), 0)
    item.custom_affixes = [text for text, _ in remaining[first_bullet:]]

    return item
