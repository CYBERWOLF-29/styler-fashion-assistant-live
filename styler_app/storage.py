from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

PROFILE_PATH = DATA_DIR / "styler_profile.json"
WARDROBE_PATH = DATA_DIR / "styler_wardrobe.json"
OUTFITS_PATH = DATA_DIR / "styler_outfits.json"


DEFAULT_PROFILE: Dict[str, Any] = {
    "is_onboarded": False,
    "name": "",
    "preferred_nickname": "",
    "age_range": "",
    "gender_presentation": "",
    "country": "",
    "location": "",
    "height": "",
    "preferred_sizes": "",
    "preferred_aesthetic": "Minimal luxury",
    "preferred_fit": "Relaxed",
    "favourite_colours": ["Warm cream", "Olive green", "Navy"],
    "colours_disliked": ["Neon pink"],
    "budget_range": "150-350",
    "shopping_preferences": "Classic essentials, elevated basics",
    "common_occasions": ["Work", "Weekend brunch", "Evening events"],
    "skintone": "Warm",
    "skin_depth": "Medium",
    "natural_contrast": "Medium",
    "hair_colour": "",
    "eye_colour": "",
    "seasonal_family": "Autumn",
    "body_notes": "Athletic build; prefers soft structured fits.",
    "wardrobe_goal": "Build versatile everyday outfits.",
}


DEMO_PROFILE: Dict[str, Any] = {
    **DEFAULT_PROFILE,
    "is_onboarded": True,
    "name": "Style Guest",
    "preferred_nickname": "there",
    "preferred_aesthetic": "Modern heritage",
    "preferred_fit": "Relaxed",
    "favourite_colours": ["Warm cream", "Olive green", "Navy"],
    "colours_disliked": ["Neon pink"],
    "common_occasions": ["Work", "Weekend brunch", "Travel"],
    "default_occasion": "Work",
}

DEMO_WARDROBE: List[Dict[str, Any]] = [
    {
        "id": "demo-top-cream-shirt",
        "name": "Cream linen shirt",
        "category": "TOP WEAR",
        "subcategory": "Shirt",
        "main_colour": "#F7F1E7",
        "secondary_colour": "#E7D9C8",
        "pattern": "Solid",
        "fit": "Relaxed",
        "style": "Modern classic",
        "available": True,
    },
    {
        "id": "demo-top-olive-polo",
        "name": "Olive knit polo",
        "category": "TOP WEAR",
        "subcategory": "Polo",
        "main_colour": "#7A8D5A",
        "secondary_colour": "#7A8D5A",
        "pattern": "Textured",
        "fit": "Regular",
        "style": "Smart casual",
        "available": True,
    },
    {
        "id": "demo-top-navy-tee",
        "name": "Navy cotton tee",
        "category": "TOP WEAR",
        "subcategory": "T-shirt",
        "main_colour": "#1F2A44",
        "secondary_colour": "#1F2A44",
        "pattern": "Solid",
        "fit": "Relaxed",
        "style": "Casual",
        "available": True,
    },
    {
        "id": "demo-bottom-stone-trouser",
        "name": "Stone pleated trousers",
        "category": "BOTTOM WEAR",
        "subcategory": "Pleated trousers",
        "main_colour": "#B8B1A5",
        "secondary_colour": "#B8B1A5",
        "pattern": "Solid",
        "fit": "Straight",
        "style": "Smart casual",
        "available": True,
    },
    {
        "id": "demo-bottom-dark-denim",
        "name": "Dark indigo jeans",
        "category": "BOTTOM WEAR",
        "subcategory": "Jeans",
        "main_colour": "#293B58",
        "secondary_colour": "#293B58",
        "pattern": "Solid",
        "fit": "Straight",
        "style": "Casual",
        "available": True,
    },
    {
        "id": "demo-shoes-sneakers",
        "name": "Ivory leather sneakers",
        "category": "FOOTWEAR",
        "subcategory": "Sneakers",
        "main_colour": "#F7F1E7",
        "secondary_colour": "#B58A5B",
        "pattern": "Solid",
        "fit": "Classic",
        "style": "Casual",
        "available": True,
    },
    {
        "id": "demo-accessory-belt",
        "name": "Chocolate leather belt",
        "category": "ACCESSORIES",
        "subcategory": "Belt",
        "main_colour": "#4E2D1B",
        "secondary_colour": "#B58A5B",
        "pattern": "Solid",
        "fit": "Classic",
        "style": "Modern classic",
        "available": True,
    },
]


def is_demo_mode() -> bool:
    """Return whether persistent shared storage is disabled for a public demo."""
    enabled = os.getenv("STYLER_DEMO_MODE", "").strip().lower()
    if enabled in {"1", "true", "yes", "on"}:
        return True

    import streamlit as st
    from streamlit.errors import StreamlitSecretNotFoundError

    try:
        return str(st.secrets.get("STYLER_DEMO_MODE", "false")).strip().lower() in {"1", "true", "yes", "on"}
    except StreamlitSecretNotFoundError:
        return False


def _safe_load_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    return fallback


def load_profile() -> Dict[str, Any]:
    if is_demo_mode():
        return deepcopy(DEMO_PROFILE)
    profile = _safe_load_json(PROFILE_PATH, DEFAULT_PROFILE.copy())
    merged = DEFAULT_PROFILE.copy()
    merged.update(profile)
    return merged


def save_profile(profile: Dict[str, Any]) -> None:
    if is_demo_mode():
        return
    PROFILE_PATH.write_text(json.dumps(profile, indent=2), encoding="utf-8")


def load_wardrobe() -> List[Dict[str, Any]]:
    if is_demo_mode():
        return deepcopy(DEMO_WARDROBE)
    data = _safe_load_json(WARDROBE_PATH, [])
    if isinstance(data, list):
        return data
    return []


def save_wardrobe(items: List[Dict[str, Any]]) -> None:
    if is_demo_mode():
        return
    WARDROBE_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8")


def load_outfits() -> List[Dict[str, Any]]:
    if is_demo_mode():
        return []
    data = _safe_load_json(OUTFITS_PATH, [])
    if isinstance(data, list):
        return data
    return []


def save_outfits(items: List[Dict[str, Any]]) -> None:
    if is_demo_mode():
        return
    OUTFITS_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8")
