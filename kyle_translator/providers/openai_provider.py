from __future__ import annotations

import json
from typing import Optional

import httpx
from openai import OpenAI

from ..models import ProviderResult, TranslationCandidate
from .base import Provider


PROMPT = (
    "You are a precise translator. Translate the given word from {source} to {target}. "
    "Return a concise JSON with keys: translation (string), gloss (optional string), confidence (0..1 float)."
)


class OpenAIProvider(Provider):
    def __init__(self, api_key: str, model: str) -> None:
        super().__init__(name="openai")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def translate(self, text: str, source_lang: str, target_lang: str, *, timeout_seconds: Optional[int] = None) -> ProviderResult:
        result = self._result(text, source_lang, target_lang)
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PROMPT.format(source=source_lang, target=target_lang)},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
                timeout=timeout_seconds or 60,
            )
            content = completion.choices[0].message.content or "{}"
            data = json.loads(content)
            translation = data.get("translation") or data.get("translated") or ""
            gloss = data.get("gloss")
            conf = float(data.get("confidence", 0.6))
            result.candidate = TranslationCandidate(translation=translation, gloss=gloss, self_confidence=max(0.0, min(1.0, conf)))
        except Exception as e:  # pragma: no cover
            result.error = str(e)
        return result
