"""Vision AI service abstraction."""


class VisionAIService:
    """Perform visual garment and personal-colour analysis."""

    def describe(self, image_bytes: bytes) -> dict:
        return {"status": "stubbed", "confidence": "low"}
