from __future__ import annotations

from ..models import ProviderResult, TranslationCandidate
from .base import Provider


MOCK_DICT = {
    ("en", "es", "hello"): "hola",
    ("en", "es", "world"): "mundo",
    ("en", "fr", "hello"): "bonjour",
    ("en", "fr", "world"): "monde",
}


class MockProvider(Provider):
    def __init__(self) -> None:
        super().__init__(name="mock")

    def translate(self, text: str, source_lang: str, target_lang: str, *, timeout_seconds: int | None = None) -> ProviderResult:
        key = (source_lang or "en", target_lang or "es", text.lower())
        translation = MOCK_DICT.get(key, f"{text}-{target_lang}")
        confidence = 0.9 if key in MOCK_DICT else 0.5
        result = self._result(text, source_lang, target_lang)
        result.candidate = TranslationCandidate(translation=translation, gloss=None, self_confidence=confidence)
        return result
