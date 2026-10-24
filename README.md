# PflegeBench – LLM Benchmark for German Care Assessment

PflegeBench is a benchmark and tool suite for evaluating large language models on the
German long-term care assessment (*Pflegebegutachtung*, NBA modules M1–M6). It contains
synthetically generated multiple-choice vignettes with rationales, tools to generate,
validate and edit them, and a comparison pipeline across models.

Built as a team project in the AI bachelor's programme at TH Deggendorf (KI-Projekt, summer 2026)
by Tobias Litke, Alaa Malla Ali and Marius Wicht.

## Features

- **Benchmark generation** via OpenRouter (GUI and CLI) for any supported model
- **Validation and editing** of JSON/JSONL vignettes (desktop editor and browser-based expert evaluation tool)
- **Model comparison** across the full catalog, with an HTML dashboard
- **Tracing** of model calls with Langfuse (optional)

## Repository layout

```text
data/benchmark/   validated and to-be-validated benchmark items (see SCHEMA.md)
data/archive/     earlier test runs and raw generations
docs/             model comparison report and project presentation
src/pflegebench/  cross-platform workflow package (python -m pflegebench)
src/              benchmark GUI, editor, comparison engine, tracing tools
```

## Cross-platform workflow entry point

The project workflow is consolidated in the Python package `pflegebench`.
Use this command form on Windows, macOS and Linux:

```bash
python -m pflegebench --list
python -m pflegebench doctor
python -m pflegebench check
```

### Installation

From the project root:

```bash
python -m pip install -e .
```

### Typical workflow

```bash
python -m pflegebench gui-benchmark
python -m pflegebench cli-benchmark
python -m pflegebench gui-editor
python -m pflegebench compare-folder
python -m pflegebench dashboard --open
python -m pflegebench docs
```

Further documentation:

- `WORKFLOW.md` — concrete operating workflow
- `ARCHITECTURE.md` — cross-platform architecture and design decisions

### API keys

The GUI starts even when API keys are missing. Real model calls require `OPENROUTER_API_KEY`.

```powershell
Copy-Item .env.example .env
notepad .env
```

Langfuse keys are optional. Without them, remote tracing is skipped and local exports still work.
