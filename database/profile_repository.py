"""Repository for profile persistence."""

from __future__ import annotations

from typing import Any, Dict


class ProfileRepository:
    """Repository for user profile and style settings."""

    def load(self) -> Dict[str, Any]:
        return {}

    def save(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        return profile
