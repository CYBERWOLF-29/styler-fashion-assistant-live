"""Image-generation service abstraction."""


class ImageGenerationService:
    """Generate preview visuals for outfit combinations."""

    def generate(self, prompt: str) -> str:
        return prompt
