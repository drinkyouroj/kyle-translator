from __future__ import annotations

import os
from typing import List, Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv


class ProviderConfig(BaseModel):
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    anthropic_api_key: Optional[str] = Field(default=None)
    anthropic_model: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620"))


class WeightConfig(BaseModel):
    weight_self_confidence: float = 0.5
    weight_agreement: float = 0.4
    weight_back_translation: float = 0.1

    def normalized(self) -> "WeightConfig":
        total = self.weight_self_confidence + self.weight_agreement + self.weight_back_translation
        if total <= 0:
            # fallback to equal weights
            return WeightConfig(
                weight_self_confidence=1 / 3,
                weight_agreement=1 / 3,
                weight_back_translation=1 / 3,
            )
        return WeightConfig(
            weight_self_confidence=self.weight_self_confidence / total,
            weight_agreement=self.weight_agreement / total,
            weight_back_translation=self.weight_back_translation / total,
        )


class AppConfig(BaseModel):
    provider: ProviderConfig
    weights: WeightConfig
    enable_back_translation: bool = False
    max_workers: int = 8
    timeout_seconds: int = 60


def load_config() -> AppConfig:
    load_dotenv(override=False)

    provider = ProviderConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    weights = WeightConfig(
        weight_self_confidence=float(os.getenv("WEIGHT_SELF_CONFIDENCE", "0.5")),
        weight_agreement=float(os.getenv("WEIGHT_AGREEMENT", "0.4")),
        weight_back_translation=float(os.getenv("WEIGHT_BACK_TRANSLATION", "0.1")),
    ).normalized()

    enable_back_translation = os.getenv("ENABLE_BACK_TRANSLATION", "false").lower() in {"1", "true", "yes", "on"}
    max_workers = int(os.getenv("MAX_WORKERS", "8"))
    timeout_seconds = int(os.getenv("TIMEOUT_SECONDS", "60"))

    return AppConfig(
        provider=provider,
        weights=weights,
        enable_back_translation=enable_back_translation,
        max_workers=max_workers,
        timeout_seconds=timeout_seconds,
    )
