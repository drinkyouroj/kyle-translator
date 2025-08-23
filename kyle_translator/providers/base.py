from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Optional

from ..models import ProviderResult, TranslationCandidate


class Provider(ABC):
    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str, *, timeout_seconds: Optional[int] = None) -> ProviderResult:
        raise NotImplementedError

    def _result(self, text: str, source_lang: str, target_lang: str) -> ProviderResult:
        return ProviderResult(provider=self.name, text=text, source_lang=source_lang, target_lang=target_lang)


def time_call(func):
    def wrapper(self: Provider, *args, **kwargs):
        start = time.perf_counter()
        try:
            result: ProviderResult = func(self, *args, **kwargs)
            return result
        finally:
            end = time.perf_counter()
            if isinstance(result, ProviderResult):
                result.latency_ms = (end - start) * 1000.0
    return wrapper
