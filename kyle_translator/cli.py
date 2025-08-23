from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import pandas as pd
import typer
from rich import print

from .config import load_config
from .orchestrator import run_translation
from .providers import make_providers

app = typer.Typer(add_completion=False)


def main(
    source: str = typer.Option(None, "--source", help="Source language code"),
    target: str = typer.Option(None, "--target", help="Target language code"),
    providers: Optional[str] = typer.Option(None, "--providers", help="Providers to use (comma-separated)"),
    words: Optional[List[str]] = typer.Argument(None, help="Words to translate"),
    input_file: Optional[Path] = typer.Option(None, "--input-file", exists=True, file_okay=True, readable=True, help="File with one word per line"),
    output_json: Optional[Path] = typer.Option(None, "--output-json", help="Path to write JSON output"),
    output_csv: Optional[Path] = typer.Option(None, "--output-csv", help="Path to write CSV output"),
    back_translate: bool = typer.Option(False, "--back-translate", help="Enable back-translation scoring"),
):
    """Translate words using multiple LLM providers and aggregate by confidence scores."""
    config = load_config()
    config.enable_back_translation = bool(back_translate)
    
    # Load source and target from .env if not specified
    if source is None:
        source = config.source_lang if hasattr(config, 'source_lang') else "en"
    if target is None:
        target = config.target_lang if hasattr(config, 'target_lang') else "es"
    
    # Parse providers from comma-separated string or use default
    if providers is None:
        providers_list = ["mock"]
    else:
        providers_list = [p.strip() for p in providers.split(",") if p.strip()]
    
    # Debug: show what providers were requested
    print(f"[blue]Requested providers: {providers_list}[/blue]")
    print(f"[blue]Source: {source}, Target: {target}[/blue]")
    
    provs = make_providers(providers_list, config)
    if not provs:
        print("[yellow]No providers available. Check API keys or provider names.[/yellow]")
        raise typer.Exit(code=1)
    
    print(f"[blue]Available providers: {[p.name for p in provs]}[/blue]")

    all_words: List[str] = list(words or [])
    if input_file:
        all_words += [w.strip() for w in input_file.read_text().splitlines() if w.strip()]

    if not all_words:
        print("[yellow]No words provided. Use positional arguments or --input-file.[/yellow]")
        raise typer.Exit(code=1)

    master = run_translation(config, provs, all_words, source, target)

    # Print brief summary
    for agg in master.words:
        print(f"[bold]{agg.word}[/bold] -> {agg.final_translation} (by {agg.final_choice_provider}, score={agg.final_score:.2f})")

    if output_json:
        output_json.write_text(json.dumps(master.model_dump(), ensure_ascii=False, indent=2))
        print(f"[green]JSON output written to {output_json}[/green]")
    if output_csv:
        rows = []
        for agg in master.words:
            rows.append({
                "word": agg.word,
                "source_lang": agg.source_lang,
                "target_lang": agg.target_lang,
                "translation": agg.final_translation,
                "gloss": agg.final_gloss,
                "provider": agg.final_choice_provider,
                "score": agg.final_score,
            })
        pd.DataFrame(rows).to_csv(output_csv, index=False)
        print(f"[green]CSV output written to {output_csv}[/green]")


# Register the main function as the default command
app.command()(main)


if __name__ == "__main__":
    app()
