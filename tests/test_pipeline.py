from __future__ import annotations

from kyle_translator.config import load_config
from kyle_translator.orchestrator import run_translation
from kyle_translator.providers import make_providers


def test_mock_pipeline_basic(tmp_path):
    config = load_config()
    config.enable_back_translation = False
    providers = make_providers(["mock"], config)
    words = ["hello", "world", "apple"]
    master = run_translation(config, providers, words, source_lang="en", target_lang="es")
    assert len(master.words) == 3
    agg0 = master.words[0]
    assert agg0.word == "hello"
    assert agg0.final_translation in {"hola", "hello-es"}
    assert agg0.final_choice_provider == "mock"
