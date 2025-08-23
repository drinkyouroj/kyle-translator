## Translation Confidence Aggregator

A Python tool that queries multiple LLM providers to translate words between languages, computes confidence scores using self-reported confidence, cross-model agreement, and optional back-translation, and outputs a master list of highest-confidence translations.

### Features
- Multiple providers (OpenAI, Anthropic, Mock)
- Scoring via self-confidence, agreement, and optional back-translation
- Configurable weights via env or CLI
- CLI for batch processing, outputs JSON/CSV

### Setup
1. Create and activate venv (recommended), then install deps:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
2. Configure environment variables (copy `.env.example` to `.env`):
```bash
cp .env.example .env
```
Fill in API keys as needed.

### Usage
Run on a text file of words (one per line):
```bash
python -m kyle_translator.cli run \
  --source en --target es \
  --providers mock openai anthropic \
  --input-file sample_words.txt \
  --output-json out.json --output-csv out.csv \
  --back-translate
```

You can also pass words directly:
```bash
python -m kyle_translator.cli run --source en --target fr --providers mock --words hello world
```

### Configuration
- Weights and provider settings can be set via env or CLI flags. See `kyle_translator/config.py` for details.

### Testing
```bash
pytest -q
```

### Notes
- Providers without configured API keys are skipped with a warning.
- Back-translation increases latency and API usage.
