from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TranslationCandidate(BaseModel):
    translation: str
    gloss: Optional[str] = None
    self_confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class ProviderResult(BaseModel):
    provider: str
    text: str
    source_lang: str
    target_lang: str
    candidate: Optional[TranslationCandidate] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    back_translation: Optional[str] = None


class WordAggregate(BaseModel):
    word: str
    source_lang: str
    target_lang: str
    results: List[ProviderResult] = Field(default_factory=list)
    agreement_scores: Dict[str, float] = Field(default_factory=dict)
    back_translation_scores: Dict[str, float] = Field(default_factory=dict)
    final_choice_provider: Optional[str] = None
    final_translation: Optional[str] = None
    final_gloss: Optional[str] = None
    final_score: Optional[float] = None


class MasterResult(BaseModel):
    words: List[WordAggregate]
