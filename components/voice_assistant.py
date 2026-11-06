"""Browser voice component for the STYLER wake-word experience."""

from pathlib import Path
from typing import Any, Dict, Optional

import streamlit.components.v1 as components

_voice_widget = components.declare_component(
    "styler_browser_voice",
    path=str(Path(__file__).with_name("voice_component")),
)


def render_voice_assistant(
    response: str = "",
    response_id: str = "",
    language: str = "en-US",
) -> Optional[Dict[str, Any]]:
    """Render a foreground browser listener and return recognized wake-word commands."""
    return _voice_widget(
        response=response,
        response_id=response_id,
        language=language,
        default=None,
        key="styler_browser_voice_widget",
    )
