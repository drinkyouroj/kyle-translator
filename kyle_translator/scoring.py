from __future__ import annotations

from typing import Dict, List
from rapidfuzz import fuzz

from .config import AppConfig
from .models import ProviderResult, WordAggregate


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def compute_agreement_scores(results: List[ProviderResult]) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    if not results:
        return scores
    for i, r in enumerate(results):
        if r.candidate is None or r.candidate.translation is None:
            scores[r.provider] = 0.0
            continue
        similarities: List[float] = []
        for j, other in enumerate(results):
            if i == j:
                continue
            if other.candidate is None or other.candidate.translation is None:
                continue
            sim = fuzz.ratio(r.candidate.translation, other.candidate.translation) / 100.0
            similarities.append(sim)
        scores[r.provider] = sum(similarities) / len(similarities) if similarities else 0.0
    return scores


def compute_back_translation_scores(word: str, results: List[ProviderResult]) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    for r in results:
        if r.back_translation:
            scores[r.provider] = fuzz.ratio(word, r.back_translation) / 100.0
        else:
            scores[r.provider] = 0.0
    return scores


def compute_final_scores(config: AppConfig, aggregate: WordAggregate) -> None:
    weights = config.weights
    for r in aggregate.results:
        self_conf = r.candidate.self_confidence if r.candidate else 0.0
        agree = aggregate.agreement_scores.get(r.provider, 0.0)
        back = aggregate.back_translation_scores.get(r.provider, 0.0)
        final_score = (
            weights.weight_self_confidence * self_conf
            + weights.weight_agreement * agree
            + weights.weight_back_translation * back
        )
        r_score = clamp01(final_score)
        # select best as we go
        if aggregate.final_score is None or r_score > aggregate.final_score:
            aggregate.final_score = r_score
            aggregate.final_choice_provider = r.provider
            aggregate.final_translation = r.candidate.translation if r.candidate else None
            aggregate.final_gloss = r.candidate.gloss if r.candidate else None
