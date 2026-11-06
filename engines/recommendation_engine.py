"""Recommendation engine used to rank possible outfits."""

from __future__ import annotations

from typing import Any, Dict, List


def rank_outfits(profile: Dict[str, Any], wardrobe: List[Dict[str, Any]], occasion: str = "Work") -> List[Dict[str, Any]]:
    """Return outfit suggestions prioritised by compatibility and occasion fit."""
    suggestions = []
    tops = [item for item in wardrobe if str(item.get("category", "")).upper() == "TOP WEAR"]
    bottoms = [item for item in wardrobe if str(item.get("category", "")).upper() == "BOTTOM WEAR"]
    for top in tops[:3]:
        for bottom in bottoms[:3]:
            score = 80
            if top.get("main_colour") == bottom.get("main_colour"):
                score -= 10
            if occasion.lower() in str(profile.get("common_occasions", "")).lower():
                score += 10
            suggestions.append({
                "top": top.get("name", "Top"),
                "bottom": bottom.get("name", "Bottom"),
                "score": min(score, 100),
                "occasion": occasion,
            })
    return sorted(suggestions, key=lambda item: item["score"], reverse=True)[:4]
