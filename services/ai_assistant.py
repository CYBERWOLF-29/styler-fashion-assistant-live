"""Local voice-command interpretation and wardrobe-first responses."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from styler_app.analysis import generate_outfit_recommendations

Outfit = Dict[str, str]
Combination = Tuple[str, str]

_OCCASIONS = (
    (("college", "class", "school", "campus"), "College"),
    (("work", "office", "meeting"), "Work"),
    (("party", "celebration"), "Party"),
    (("formal", "interview", "business"), "Formal event"),
    (("date", "dinner"), "Date"),
    (("travel", "trip", "airport"), "Travel"),
    (("wedding", "family function"), "Family function"),
    (("casual", "weekend", "outing"), "Casual outing"),
)


def _occasion_for(command: str, profile: Dict[str, Any], last_occasion: Optional[str]) -> str:
    lowered = command.lower()
    for words, occasion in _OCCASIONS:
        if any(word in lowered for word in words):
            return occasion
    preferred = last_occasion or profile.get("default_occasion")
    if preferred:
        return str(preferred)
    common = profile.get("common_occasions", [])
    return str(common[0]) if common else "Everyday"


def _outfit_text(outfit: Outfit, occasion: str) -> str:
    return (
        f"For {occasion.lower()}, I recommend your {outfit['top']} with your "
        f"{outfit['bottom']}. The match score is {outfit['score']}. "
        f"{outfit['note']} This suggestion uses items from your saved wardrobe."
    )


def respond_to_voice_command(
    command: str,
    profile: Dict[str, Any],
    wardrobe: List[Dict[str, Any]],
    recent_combinations: List[Combination],
    last_outfit: Optional[Outfit],
    last_occasion: Optional[str] = None,
) -> Tuple[str, Optional[Outfit], List[Combination], str]:
    """Handle a voice command using saved wardrobe items only."""
    lowered = command.lower().strip()
    occasion = _occasion_for(command, profile, last_occasion)

    if re.search(r"\b(why|explain|reason)\b", lowered):
        if not last_outfit:
            return "I haven’t suggested an outfit yet. Ask me what to wear, and I’ll explain my choice.", None, [], occasion
        return (
            f"I chose your {last_outfit['top']} with your {last_outfit['bottom']} "
            f"for its colour balance and your style preferences. Colour matching is "
            f"subjective, so treat this as a suggestion rather than a certainty.",
            last_outfit,
            [],
            occasion,
        )

    another = bool(re.search(r"\b(another|different|one more)\b", lowered))
    count = 3 if re.search(r"\b(three|3)\b", lowered) else 1
    if another:
        count = 1
    suggestions = generate_outfit_recommendations(
        profile,
        wardrobe,
        occasion,
        exclude_combinations=recent_combinations,
        max_results=None,
    )
    if not suggestions:
        return (
            "I couldn’t find another complete outfit in your available wardrobe. "
            "Please add an available top and bottom, or ask me to suggest a different occasion.",
            None,
            [],
            occasion,
        )

    selected = suggestions[:count]
    new_combinations = [(item["top_id"], item["bottom_id"]) for item in selected]
    if count == 1:
        response = _outfit_text(selected[0], occasion)
    else:
        response = "Here are three combinations from your wardrobe: " + "; ".join(
            f"{item['top']} with {item['bottom']}" for item in selected
        ) + "."
        if len(selected) < 3:
            response = f"I found {len(selected)} available combination(s) in your wardrobe: " + "; ".join(
                f"{item['top']} with {item['bottom']}" for item in selected
            ) + "."
    return response, selected[0], new_combinations, occasion
