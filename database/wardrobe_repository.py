"""Repository for wardrobe persistence."""

from __future__ import annotations

from typing import Any, List


class WardrobeRepository:
    """Repository for wardrobe records."""

    def list_items(self) -> List[dict[str, Any]]:
        return []

    def save_item(self, item: dict[str, Any]) -> dict[str, Any]:
        return item
