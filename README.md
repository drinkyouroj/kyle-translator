## Translation Confidence Aggregator

A Python tool that queries multiple LLM providers to translate words between languages, computes confidence scores using self-reported confidence, cross-model agreement, and optional back-translation, and outputs a master list of highest-confidence translations.

### Quick Start
```bash
# Install and setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .

# Run with mock provider (no API keys needed)
python -m kyle_translator.cli chicken breast leg thigh

# Use real providers (requires API keys in .env)
python -m kyle_translator.cli --providers "openai,anthropic" hello world
```

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

#### Basic Translation
Translate words directly using positional arguments:
```bash
python -m kyle_translator.cli chicken breast leg thigh
```

#### Multiple Providers
Use comma-separated provider names:
```bash
python -m kyle_translator.cli --providers "mock,openai,anthropic" chicken breast
```

#### Custom Languages
Override default source/target languages:
```bash
python -m kyle_translator.cli --source fr --target de --providers "mock,openai" bonjour monde
```

#### Input File
Process words from a text file (one word per line):
```bash
python -m kyle_translator.cli --input-file sample_words.txt --providers "mock,openai"
```

#### Output Files
Save results to JSON and/or CSV:
```bash
python -m kyle_translator.cli --providers "mock,openai" --output-json results.json --output-csv results.csv chicken breast
```

#### Back-Translation
Enable back-translation scoring (increases latency):
```bash
python -m kyle_translator.cli --providers "mock,openai" --back-translate chicken breast
```

#### Environment Variables
The CLI automatically loads settings from `.env` file:
- `SOURCE_LANG` and `TARGET_LANG` for default languages
- `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` for API access
- Scoring weights and other configuration options

### Configuration

Create a `.env` file in the project root with your settings:

```bash
# Copy the example file
cp .env.example .env

# Edit with your API keys and preferences
nano .env
```

#### Key Environment Variables
- **API Keys**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- **Default Languages**: `SOURCE_LANG=en`, `TARGET_LANG=es`
- **Models**: `OPENAI_MODEL`, `ANTHROPIC_MODEL`
- **Scoring Weights**: `WEIGHT_SELF_CONFIDENCE`, `WEIGHT_AGREEMENT`, `WEIGHT_BACK_TRANSLATION`
- **Behavior**: `ENABLE_BACK_TRANSLATION`, `MAX_WORKERS`, `TIMEOUT_SECONDS`

All weights are automatically normalized to sum to 1.0.

### Testing
```bash
pytest -q
```

### Notes
- Providers without configured API keys are skipped with a warning.
- Back-translation increases latency and API usage.
