from __future__ import annotations

import json
import os
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
        return DEFAULT_PROFILE.copy()
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
        return []
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
