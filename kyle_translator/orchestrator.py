from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List

from .config import AppConfig
from .models import MasterResult, ProviderResult, WordAggregate
from .providers.base import Provider
from .scoring import compute_agreement_scores, compute_back_translation_scores, compute_final_scores


def translate_with_provider(provider: Provider, word: str, source: str, target: str, timeout_seconds: int) -> ProviderResult:
    return provider.translate(word, source, target, timeout_seconds=timeout_seconds)


def back_translate_with_provider(provider: Provider, text: str, source: str, target: str, timeout_seconds: int) -> ProviderResult:
    return provider.translate(text, source, target, timeout_seconds=timeout_seconds)


def run_translation(
    config: AppConfig,
    providers: List[Provider],
    words: Iterable[str],
    source_lang: str,
    target_lang: str,
) -> MasterResult:
    aggregates: List[WordAggregate] = []
    words_list = [w.strip() for w in words if w and w.strip()]

    for word in words_list:
        aggregate = WordAggregate(word=word, source_lang=source_lang, target_lang=target_lang)
        results: List[ProviderResult] = []
        with ThreadPoolExecutor(max_workers=min(len(providers), config.max_workers)) as ex:
            futs = [
                ex.submit(
                    translate_with_provider,
                    p,
                    word,
                    source_lang,
                    target_lang,
                    config.timeout_seconds,
                )
                for p in providers
            ]
            for fut in as_completed(futs):
                try:
                    res = fut.result()
                    results.append(res)
                except Exception as e:  # pragma: no cover
                    results.append(
                        ProviderResult(
                            provider="unknown",
                            text=word,
                            source_lang=source_lang,
                            target_lang=target_lang,
                            error=str(e),
                        )
                    )
        aggregate.results = results

        if config.enable_back_translation and results:
            with ThreadPoolExecutor(max_workers=min(len(providers), config.max_workers)) as ex:
                futs_bt = []
                for r in aggregate.results:
                    if r.candidate and r.candidate.translation:
                        # find the same provider instance by name
                        prov = next((p for p in providers if p.name == r.provider), None)
                        if prov is not None:
                            futs_bt.append(
                                (r.provider, ex.submit(back_translate_with_provider, prov, r.candidate.translation, target_lang, source_lang, config.timeout_seconds))
                            )
                for pname, fut in futs_bt:
                    try:
                        bt_res = fut.result()
                        for r in aggregate.results:
                            if r.provider == pname:
                                r.back_translation = bt_res.candidate.translation if bt_res.candidate else None
                    except Exception:
                        pass

        aggregate.agreement_scores = compute_agreement_scores(aggregate.results)
        aggregate.back_translation_scores = compute_back_translation_scores(word, aggregate.results)
        compute_final_scores(config, aggregate)
        aggregates.append(aggregate)

    return MasterResult(words=aggregates)
