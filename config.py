import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Settings:
    APP_NAME = "STYLER"
    APP_TAGLINE = "Your Wardrobe. Your Colours. Your Style."
    DEBUG = os.getenv("STYLER_DEBUG", "false").lower() == "true"
    DEFAULT_OCCASION = os.getenv("STYLER_DEFAULT_OCCASION", "Work")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    STORAGE_BUCKET = os.getenv("STYLER_STORAGE_BUCKET", "wardrobe")
    VOICE_LANGUAGE = os.getenv("STYLER_VOICE_LANGUAGE", "en-US")


settings = Settings()


def get_setting(name: str, default: str | None = None) -> str | None:
    return getattr(settings, name, default)
