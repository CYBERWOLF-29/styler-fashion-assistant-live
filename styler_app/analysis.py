from __future__ import annotations

import colorsys
import io
import math
import re
from collections import Counter
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
from PIL import Image


CATEGORY_NAMES = {
    "TOP WEAR": ["T-shirt", "Oversized T-shirt", "Shirt", "Oversized shirt", "Polo", "Hoodie", "Sweatshirt", "Sweater", "Jacket", "Blazer"],
    "BOTTOM WEAR": ["Jeans", "Bootcut trousers", "Straight-fit trousers", "Pleated trousers", "Gurkha pants", "Chinos", "Cargo pants", "Joggers", "Shorts"],
    "FOOTWEAR": ["Sneakers", "Formal shoes", "Loafers", "Boots", "Sandals"],
    "ACCESSORIES": ["Watches", "Belts", "Sunglasses", "Bracelets", "Bags"],
}

COLOUR_MAP = {
    "Warm cream": "#F7F1E7",
    "Olive green": "#7A8D5A",
    "Navy": "#1F2A44",
    "Charcoal": "#2D2D2D",
    "Terracotta": "#C76C4C",
    "Dusty rose": "#C99AA5",
    "Soft beige": "#C9B39A",
    "Chocolate brown": "#4E2D1B",
    "Muted blue": "#6F8FA6",
    "Forest green": "#3B5C41",
    "Black": "#000000",
    "White": "#FFFFFF",
    "Camel": "#B58A5B",
    "Stone": "#B8B1A5",
    "Cobalt": "#2E5B9F",
    "Wine": "#5D2E3B",
    "Moss": "#6B7F52",
}


def _hex_to_rgb(value: str) -> Tuple[int, int, int]:
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    value = value[:6]
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb).upper()


def _normalize_rgb(pixel: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return tuple(max(0, min(255, int(v))) for v in pixel)


def _rgb_to_hsv(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    r, g, b = [v / 255 for v in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h, s, v


def _sample_palette(image: Image.Image, sample_count: int = 6) -> List[str]:
    img = image.convert("RGB")
    arr = np.asarray(img.resize((48, 48)))
    pixels = arr.reshape(-1, 3)
    quantized = [tuple(np.round(pixel / 32) * 32).astype(int) for pixel in pixels]
    counter = Counter(tuple(p) for p in quantized)
    dominant = [tuple(c[0]) for c in counter.most_common(sample_count)]
    palette = [_rgb_to_hex(_normalize_rgb(pixel)) for pixel in dominant if sum(pixel) > 20]
    return palette[:sample_count]


def _approximate_category(image: Image.Image) -> str:
    width, height = image.size
    ratio = width / max(height, 1)
    if ratio > 1.35:
        return "TOP WEAR"
    if 0.75 <= ratio <= 1.2:
        return "ACCESSORIES"
    if ratio < 0.75:
        return "BOTTOM WEAR"
    return "FOOTWEAR"


def _categorize_subcategory(category: str, ratio: float) -> str:
    if category == "TOP WEAR":
        if ratio > 1.8:
            return "Shirt"
        if ratio > 1.5:
            return "T-shirt"
        return "Sweater"
    if category == "BOTTOM WEAR":
        if ratio < 0.7:
            return "Shorts"
        return "Jeans"
    if category == "FOOTWEAR":
        return "Sneakers"
    return "Bag"


def _pattern_guess(image: Image.Image) -> str:
    arr = np.asarray(image.convert("RGB").resize((32, 32)))
    hsv = np.array([colorsys.rgb_to_hsv(r / 255, g / 255, b / 255) for r, g, b in arr.reshape(-1, 3)])
    sat = hsv[:, 1].mean()
    if sat > 0.46:
        return "Patterned"
    return "Solid"


def _fit_guess(image: Image.Image) -> str:
    width, height = image.size
    ratio = width / max(height, 1)
    if ratio > 1.8:
        return "Relaxed"
    if ratio > 1.3:
        return "Regular"
    return "Tailored"


def _season_from_palette(colors: List[str]) -> str:
    tones = []
    for hex_value in colors:
        rgb = _hex_to_rgb(hex_value)
        h, s, v = _rgb_to_hsv(rgb)
        if 20 <= h * 360 <= 80:
            tones.append("warm")
        elif 180 <= h * 360 <= 260:
            tones.append("cool")
        else:
            tones.append("neutral")
    return "Autumn" if "warm" in tones else "Summer" if "cool" in tones else "Spring"


def _get_formality(category: str) -> str:
    if category in {"TOP WEAR", "BOTTOM WEAR"}:
        return "Smart casual"
    if category == "FOOTWEAR":
        return "Casual"
    return "Elevated"


def _derive_fabric(pattern: str) -> str:
    return "Cotton blend" if pattern == "Solid" else "Textured woven fabric"


def analyze_wardrobe_image(file_bytes: bytes, file_name: str = "item.jpg") -> Dict[str, str]:
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    category = _approximate_category(image)
    ratio = image.size[0] / max(image.size[1], 1)
    subcategory = _categorize_subcategory(category, ratio)
    palette = _sample_palette(image, 5)
    dominant = palette[0] if palette else "#A9A9A9"
    secondary = palette[1] if len(palette) > 1 else "#D9D9D9"
    pattern = _pattern_guess(image)
    return {
        "category": category,
        "subcategory": subcategory,
        "main_colour": dominant,
        "secondary_colour": secondary,
        "pattern": pattern,
        "fabric": _derive_fabric(pattern),
        "fit": _fit_guess(image),
        "style": "Contemporary",
        "season": _season_from_palette(palette),
        "formality": _get_formality(category),
        "notes": f"AI wardrobe analysis for {file_name} suggests a {subcategory.lower()} in a {pattern.lower()} finish.",
    }


def _estimate_undertone(pixels: Iterable[Tuple[int, int, int]]) -> str:
    sample = list(pixels)
    if not sample:
        return "Neutral"
    colors = []
    for r, g, b in sample:
        h, s, v = _rgb_to_hsv((r, g, b))
        if s > 0.1:
            colors.append(h)
    if not colors:
        return "Neutral"
    avg_h = sum(colors) / len(colors)
    if 0.0 <= avg_h <= 0.09 or 0.82 <= avg_h <= 1.0:
        return "Warm"
    if 0.44 <= avg_h <= 0.68:
        return "Cool"
    return "Neutral"


def _estimate_depth(pixels: Iterable[Tuple[int, int, int]]) -> str:
    sample = list(pixels)
    if not sample:
        return "Medium"
    brightness = [sum(value) / 3 for value in sample]
    avg = sum(brightness) / len(brightness)
    if avg < 90:
        return "Deep"
    if avg > 170:
        return "Light"
    return "Medium"


def _estimate_contrast(pixels: Iterable[Tuple[int, int, int]]) -> str:
    sample = list(pixels)
    if not sample:
        return "Medium"
    brightness = [sum(value) / 3 for value in sample]
    spread = max(brightness) - min(brightness)
    if spread > 110:
        return "High"
    if spread < 55:
        return "Low"
    return "Medium"


def analyse_portrait(file_bytes: bytes) -> Dict[str, str]:
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    arr = np.asarray(image.resize((80, 80)))
    pixels = arr.reshape(-1, 3)
    # Approximate a portrait-type crop by focusing on the central region of the image.
    height, width = arr.shape[:2]
    cx, cy = width // 2, height // 2
    radius_x = max(8, width // 3)
    radius_y = max(8, height // 3)
    mask = []
    for y in range(height):
        for x in range(width):
            if abs(x - cx) < radius_x and abs(y - cy) < radius_y:
                mask.append(tuple(arr[y, x]))
    undertone = _estimate_undertone(mask)
    depth = _estimate_depth(mask)
    contrast = _estimate_contrast(mask)
    seasonal = {
        "Warm": {"Light": "Spring", "Medium": "Autumn", "Deep": "Autumn"},
        "Cool": {"Light": "Summer", "Medium": "Winter", "Deep": "Winter"},
        "Neutral": {"Light": "Spring", "Medium": "Autumn", "Deep": "Winter"},
    }.get(undertone, {}).get(depth, "Autumn")
    return {
        "skin_undertone": undertone,
        "skin_depth": depth,
        "natural_contrast": contrast,
        "seasonal_family": seasonal,
        "confidence": "Moderate confidence. Please confirm in natural lighting if the result feels off.",
    }


def _normalise_color_name(value: str) -> str:
    if not value:
        return ""
    text = str(value).lower().replace("#", " ")
    text = re.sub(r"[^a-z\s]", " ", text)
    return " ".join(text.split())


def _hex_to_named_colour(value: str) -> str:
    rgb = _hex_to_rgb(value)
    best_name = "neutral"
    best_distance = float("inf")
    for name, hex_value in COLOUR_MAP.items():
        candidate = _hex_to_rgb(hex_value)
        distance = sum((a - b) ** 2 for a, b in zip(rgb, candidate)) ** 0.5
        if distance < best_distance:
            best_name = name.lower()
            best_distance = distance
    return best_name


def _colour_harmony(value: str, profile: Dict[str, Any]) -> int:
    profile_colours = {_normalise_color_name(colour) for colour in profile.get("favourite_colours", [])}
    avoided_colours = {_normalise_color_name(colour) for colour in profile.get("colours_disliked", [])}
    value_name = _normalise_color_name(value)
    value_name = _hex_to_named_colour(value) if not value_name else value_name
    if value_name in profile_colours:
        return 100
    if value_name in avoided_colours:
        return 25
    if any(keyword in value_name for keyword in ["cream", "beige", "camel", "stone", "ivory"]):
        return 90
    if any(keyword in value_name for keyword in ["olive", "green", "moss", "forest"]):
        return 88
    if any(keyword in value_name for keyword in ["navy", "charcoal", "black", "brown", "chocolate"]):
        return 82
    if any(keyword in value_name for keyword in ["blue", "muted blue", "cobalt"]):
        return 78
    if any(keyword in value_name for keyword in ["terracotta", "rose", "wine", "dusty rose"]):
        return 76
    return 70


def build_colour_palette(profile: Dict[str, Any]) -> Dict[str, List[str]]:
    profile_colours = profile.get("favourite_colours", [])
    core = [COLOUR_MAP.get(colour, "#C7B39A") for colour in profile_colours if colour in COLOUR_MAP]
    if not core:
        core = ["#F7F1E7", "#7A8D5A", "#1F2A44"]
    palette = {
        "recommended": core[:4],
        "neutral": ["#F8F5F0", "#CDB89C", "#2D2D2D", "#7A6E5F"],
        "accent": ["#C76C4C", "#5D2E3B", "#6B7F52", "#2E5B9F"],
        "avoid": ["#E8546E", "#FFB703", "#00A7E1"],
    }
    return palette


def _clean_season(profile: Dict[str, Any]) -> str:
    return profile.get("seasonal_family", "Autumn")


def generate_outfit_recommendations(
    profile: Dict[str, Any],
    wardrobe: List[Dict[str, Any]],
    occasion: str = "Work",
    exclude_combinations: Iterable[Tuple[str, str]] = (),
    max_results: Optional[int] = 4,
) -> List[Dict[str, str]]:
    seasonal = _clean_season(profile)
    recommendations = []
    excluded = set(exclude_combinations)

    def available(item: Dict[str, Any]) -> bool:
        status = str(item.get("status", "")).lower().replace("_", " ")
        availability = item.get("available", True)
        if isinstance(availability, str):
            availability = availability.lower() not in {"false", "no", "unavailable", "laundry", "in laundry"}
        return availability is not False and status not in {"unavailable", "laundry", "in laundry"}

    top_items = [item for item in wardrobe if item.get("category") == "TOP WEAR" and available(item)]
    bottoms = [item for item in wardrobe if item.get("category") == "BOTTOM WEAR" and available(item)]

    for top in top_items:
        for bottom in bottoms:
            top_id = str(top.get("id") or top.get("name", ""))
            bottom_id = str(bottom.get("id") or bottom.get("name", ""))
            if (top_id, bottom_id) in excluded:
                continue
            top_score = _colour_harmony(top.get("main_colour", "#FFFFFF"), profile)
            bottom_score = _colour_harmony(bottom.get("main_colour", "#FFFFFF"), profile)
            harmony_score = min(100, int(round((top_score + bottom_score) / 2)))
            occasion_boost = 8 if occasion.lower() in str(profile.get("common_occasions", "")).lower() else 3
            score = min(100, harmony_score + occasion_boost)
            note = f"{occasion} styling built around {profile.get('preferred_aesthetic', 'Minimal luxury')} preferences with a {seasonal} palette and a balanced neutral-to-earth look."
            recommendations.append({
                "top": top.get("name", "Essential top"),
                "bottom": bottom.get("name", "Classic trouser"),
                "top_id": top_id,
                "bottom_id": bottom_id,
                "colour_story": f"{top.get('main_colour', '#F7F1E7')} + {bottom.get('main_colour', '#1F2A44')}",
                "score": f"{score}/100",
                "note": note,
            })
    recommendations.sort(key=lambda item: int(item["score"].split("/")[0]), reverse=True)
    return recommendations[:max_results] if max_results is not None else recommendations


def build_shopping_list(profile: Dict[str, Any], budget: str = "250") -> List[Dict[str, str]]:
    try:
        budget_value = int(str(budget).split("-")[-1].replace("$", "").replace(",", "")) if "-" in str(budget) else int(str(budget).replace("$", "").replace(",", ""))
    except ValueError:
        budget_value = 250

    suggestions = [
        {"item": "Relaxed cotton shirt", "category": "TOP WEAR", "budget": "$90", "reason": "Works with tailored basics and soft neutrals."},
        {"item": "Straight-leg trouser", "category": "BOTTOM WEAR", "budget": "$110", "reason": "Balances warm and cool tones while keeping shapes polished."},
        {"item": "Leather belt", "category": "ACCESSORIES", "budget": "$55", "reason": "Adds structure to tonal outfits."},
        {"item": "Leather loafers", "category": "FOOTWEAR", "budget": "$145", "reason": "Smart casual, refined and seasonless."},
    ]
    filtered = [item for item in suggestions if budget_value >= int(item["budget"].replace("$", ""))]
    return filtered[:3] if filtered else suggestions[:3]
