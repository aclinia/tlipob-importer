from typing import Any

import pytest
import easyocr  # type: ignore[import-untyped]

from ocr.ocr import process_screenshot

EXAMPLES_DIR = "examples/inventory"


@pytest.fixture(scope="module")
def reader() -> Any:
    return easyocr.Reader(["en"], gpu=True)


def test_screenshot_1(reader: Any) -> None:
    item = process_screenshot(f"{EXAMPLES_DIR}/screenshot_1.png", reader)
    assert item is not None
    d = item.to_dict()
    assert d["name"] == "LongNight Sorcerer' sMask-Priceless"
    assert d["equipmentType"] == "INT Helmet"
    assert d["baseStats"] == "565 Max Energy Shield"
    assert d["customAffixes"] == [
        "+8% Sealed Mana",
        "Compensation",
        "+20% Skill Area",
        "-14% Cooldown Recovery Speed",
        "+419 gear Energy Shield",
        "+25% Sealed Mana",
        "Compensation",
        "+74 Strength",
        "+11 Support Skill Level",
        "+59% Skill Area",
        "+59% Minion Skill Area",
        "+115% Critical Strike Rating",
    ]


def test_screenshot_2(reader: Any) -> None:
    item = process_screenshot(f"{EXAMPLES_DIR}/screenshot_2.png", reader)
    assert item is not None
    d = item.to_dict()
    assert d["name"] == "Broken Sun Ring"
    assert d["equipmentType"] == "Necklace"
    assert d["baseStats"] is None
    assert d["customAffixes"] == [
        "+8 Dexterity",
        "+257 Max Life",
        "+15% Elemental Resistance",
        "+32% additional Steep Strike",
        "Damage",
        "Corona",
    ]


def test_screenshot_3(reader: Any) -> None:
    item = process_screenshot(f"{EXAMPLES_DIR}/screenshot_3.png", reader)
    assert item is not None
    d = item.to_dict()
    assert d["name"] == "Eternity"
    assert d["equipmentType"] == "Belt"
    assert d["baseStats"] is None
    assert d["customAffixes"] == [
        "+110 Max Life",
        "Transition",
        "+184 Max Life",
        "+4go chance to",
        "1stacks",
        "gain",
        "of Eternal Morale on defeat",
        "+30% chance to gain 1 stacks",
        "of Eternal Nightmare on",
        "defeat",
        "+11% chance to",
        "1stacks",
        "gain",
        "of Eternal Shadow on defeat",
        "+50% chance to gain 1 stacks",
        "of Eternal Guard upon",
        "defeating Magic monsters",
        "+10% chance to",
        "1stacks",
        "gain",
        "of Eternal Simulacra upon",
        "defeating Magic monsters",
        "+50% chance to gain 1 stacks",
        "of Eternal Reign upon",
    ]


def test_screenshot_4(reader: Any) -> None:
    item = process_screenshot(f"{EXAMPLES_DIR}/screenshot_4.png", reader)
    assert item is not None
    d = item.to_dict()
    assert d["name"] == "Myriad Radiance WardRing-Priceless"
    assert d["equipmentType"] == "Ring"
    assert d["baseStats"] == "+4% Elemental Resistance"
    assert d["customAffixes"] == [
        "+17 Strength",
        "+52 Strength",
        "+25% Elemental and Erosion",
        "Resistance Penetration",
        "+334 Max Energy Shield",
        "+23% chance to deal Double",
        "Damage",
        "+47% Critical Strike Damage",
        "+111% Critical Strike Rating",
    ]


def test_screenshot_5(reader: Any) -> None:
    item = process_screenshot(f"{EXAMPLES_DIR}/screenshot_5.png", reader)
    assert item is not None
    d = item.to_dict()
    assert d["name"] == "Shadowless Swordsman's Blade-Priceless"
    assert d["equipmentType"] == "One-Handed Sword"
    assert d["baseStats"] == "371 Physical DPS"
    assert d["customAffixes"] == [
        "+Ito Max Focus Blessing",
        "Stacks",
        "+20% Attack Critical Strike",
        "Rating for this gear",
        "+2 to Attack Skill Level",
        "+94 Strength",
        "+114% Melee Damage",
        "+30% Steep Strike chance:",
        "+29% additional Steep Strike",
        "Damage",
        "+61% Attack Critical Strike",
        "Rating for this gear",
        "+39% gear Attack Speed",
    ]


def test_screenshot_6(reader: Any) -> None:
    item = process_screenshot(f"{EXAMPLES_DIR}/screenshot_6.png", reader)
    assert item is not None
    d = item.to_dict()
    assert d["name"] == "LongNight Sorcerer' sRobe-Priceless"
    assert d["equipmentType"] == "INT Chest Armor"
    assert d["baseStats"] == "999 Max Energy Shield"
    assert d["customAffixes"] == [
        "+8% Aura Effect",
        "+8% Aura Effect",
        "-1% Max Elemental Resistance",
        "+14% additional Max Energy",
        "Shield",
        "+414 gear Energy Shield",
        "+71% gear Energy Shield",
        "+68% chance to avoid",
        "Elemental Ailments",
        "+6% Elemental Resistance",
        "+24% Erosion Resistance",
    ]


def test_screenshot_7(reader: Any) -> None:
    item = process_screenshot(f"{EXAMPLES_DIR}/screenshot_7.png", reader)
    assert item is not None
    d = item.to_dict()
    assert d["name"] == "Vorax Limb: Hands"
    assert d["equipmentType"] == "Vorax Gear"
    assert d["baseStats"] is None
    assert d["customAffixes"] == [
        "Double Life Regain",
        "Doubled Energy Shield Regain",
        "-10% Life Regain and Energy",
        "Shield Regain",
        "Double Rainbow+15%",
        "additional damage and -5%",
        "additional damage taken",
        "when two Elemental",
        "Resistances are identical",
        "multiplies)",
        "+9% additional Max Energy",
        "Shield",
        "Cicada Shell-80% Energy",
        "Shield charge Speed",
        "Adds Elemental Damage",
        "equal to 1.3% of Max Energy",
        "Shield to Attacks and Spells",
        "+19% additional damage",
        "while having Fervor",
        "+39% Skill Area",
        "+39% Minion Skill Area",
    ]


def test_screenshot_8(reader: Any) -> None:
    item = process_screenshot(f"{EXAMPLES_DIR}/screenshot_8.png", reader)
    assert item is not None
    d = item.to_dict()
    assert d["name"] == "Lone Walker's Boots"
    assert d["equipmentType"] == "DEX Boots"
    assert d["baseStats"] == "1615 Evasion"
    assert d["customAffixes"] == [
        "You have a lv: 20 Precise",
        "Spell Amplification:",
        "464%6 Movemen. Speed",
        "+24% Aura effect when",
        "affected by 4 or more Auras",
        "+2% Aura Effect per +3%",
        "Sealed Mana Compensation",
    ]


def test_screenshot_9(reader: Any) -> None:
    item = process_screenshot(f"{EXAMPLES_DIR}/screenshot_9.png", reader)
    assert item is not None
    d = item.to_dict()
    assert d["name"] == "Myriad Radiance WardRing-Priceless"
    assert d["equipmentType"] == "Ring"
    assert d["baseStats"] == "+4% Elemental Resistance"
    assert d["customAffixes"] == [
        "Gains Attack Aggression when",
        "casting an Attack Skill",
        "+15% Armor DMG Mitigation",
        "Penetration",
        "+32 Strength",
        "+436 Max Energy Shield",
        "100% chance to gain a Barrier",
        "for every 5 m you move",
        "+92% Critical Strike Rating",
        "+7% Elemental Resistance",
        "+7% Erosion Resistance",
    ]


def test_screenshot_10(reader: Any) -> None:
    item = process_screenshot(f"{EXAMPLES_DIR}/screenshot_10.png", reader)
    assert item is not None
    d = item.to_dict()
    assert d["name"] == "Ninth Apostle'sMagic Shield-Priceless"
    assert d["equipmentType"] == "INT Shield"
    assert d["baseStats"] == "146 Max Energy Shield"
    assert d["customAffixes"] == [
        "+4O Dexterity",
        "Converts 44% of Erosion Damage",
        "taken to Cold Damage",
        "-Ito Max Tenacity Blessing",
        "Stacks",
        "All Passive Skill slots are",
        "supported by Lv: 30 Precise:",
        "Restrain",
        "+396 Max Energy Shield",
        "+25% Armor DMG Mitigation",
        "Penetration",
        "+25% Armor DMG Mitigation",
        "Penetration for Minions",
        "+4 Active Skill Level",
        "+10z% Critical Strike Damage",
        "+44% Warcry Effect",
        "+17 Elemental Resistance",
    ]
