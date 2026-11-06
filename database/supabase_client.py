"""Supabase connectivity helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional


class SupabaseClient:
    """Thin wrapper to keep remote storage provider swappable."""

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url
        self.key = key

    def get_client(self) -> Dict[str, Any]:
        return {"url": self.url, "key": self.key, "status": "stubbed"}
