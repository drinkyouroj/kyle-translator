from __future__ import annotations

import json
from typing import Optional

from anthropic import Anthropic

from ..models import ProviderResult, TranslationCandidate
from .base import Provider


SYSTEM = (
    "You are a precise translator. Translate the given word from {source} to {target}. "
    "Reply ONLY in strict JSON with keys: translation (string), gloss (optional string), confidence (float 0..1)."
)


class AnthropicProvider(Provider):
    def __init__(self, api_key: str, model: str) -> None:
        super().__init__(name="anthropic")
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def translate(self, text: str, source_lang: str, target_lang: str, *, timeout_seconds: Optional[int] = None) -> ProviderResult:
        result = self._result(text, source_lang, target_lang)
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=256,
                system=SYSTEM.format(source=source_lang, target=target_lang),
                messages=[{"role": "user", "content": text}],
            )
            content = "".join([b.text for b in message.content if getattr(b, "type", "") == "text"]) or "{}"
            data = json.loads(content)
            translation = data.get("translation") or ""
            gloss = data.get("gloss")
            conf = float(data.get("confidence", 0.6))
            result.candidate = TranslationCandidate(translation=translation, gloss=gloss, self_confidence=max(0.0, min(1.0, conf)))
        except Exception as e:  # pragma: no cover
            result.error = str(e)
        return result
