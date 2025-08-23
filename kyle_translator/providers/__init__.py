from __future__ import annotations

from typing import List

from ..config import AppConfig
from .base import Provider
from .mock_provider import MockProvider

try:
    from .openai_provider import OpenAIProvider  # type: ignore
except Exception:  # pragma: no cover
    OpenAIProvider = None  # type: ignore

try:
    from .anthropic_provider import AnthropicProvider  # type: ignore
except Exception:  # pragma: no cover
    AnthropicProvider = None  # type: ignore


def make_providers(names: List[str], config: AppConfig) -> List[Provider]:
    providers: List[Provider] = []
    for name in names:
        key = name.strip().lower()
        if key == "mock":
            providers.append(MockProvider())
        elif key == "openai" and OpenAIProvider is not None and config.provider.openai_api_key:
            providers.append(OpenAIProvider(api_key=config.provider.openai_api_key, model=config.provider.openai_model))
        elif key == "anthropic" and AnthropicProvider is not None and config.provider.anthropic_api_key:
            providers.append(AnthropicProvider(api_key=config.provider.anthropic_api_key, model=config.provider.anthropic_model))
    return providers
