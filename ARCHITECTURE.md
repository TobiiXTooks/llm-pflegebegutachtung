# Architecture

## Goal

The project uses several tools: benchmark generation, JSON/JSONL validation, manual editing, comparison, tracing and visualization. The architecture has been consolidated so the project can be operated the same way on Windows, macOS and Linux.

## New architecture

```text
ai-project-main/
  pyproject.toml
  README.md
  WORKFLOW.md
  ARCHITECTURE.md
  tasks.py                         
  src/
    pflegebench/                   # new cross-platform workflow package
      __main__.py                  # enables: python -m pflegebench
      cli.py                       # argparse command interface
      workflow.py                  # command implementations
      paths.py                     # OS-neutral repository paths
      process.py                   # OS-neutral subprocess/browser helpers
      matching.py                  # benchmark filename matching rules
    benchmark.py                   # legacy GUI tool, launched by workflow
    handling_jsonl_file.py         # legacy GUI editor, launched by workflow
    compare_full_catalog.py        # comparison engine
    compare_answers.py             # older comparison engine
    workflow_dashboard.py          # static HTML dashboard generator
    expert-eval-tool.html          # browser validation tool
    tracing/                       # tracing experiments and Langfuse/OpenRouter tools
  data/benchmark/
    to_validate/                   # raw/model outputs awaiting validation
    validated/                     # reviewed baseline files
  reports/                         # generated comparison reports
  docs/                            # generated and static HTML documentation
```

## Primary interface

The primary interface is now:

```bash
python -m pflegebench <command>
```

## Command layers

### 1. Stable package layer

`src/pflegebench/` contains the new stable workflow API. New functionality should be added here first.

Important files:

- `cli.py`: parses command line arguments.
- `workflow.py`: implements each command.
- `paths.py`: defines project directories and path resolution.
- `process.py`: runs child tools safely across operating systems.
- `matching.py`: contains reusable filename matching logic.

### 2. Legacy tool layer

Existing project tools remain in `src/` and are started by the workflow layer:

- `benchmark.py`
- `handling_jsonl_file.py`
- `compare_full_catalog.py`
- `workflow_dashboard.py`
- `expert-eval-tool.html`
- `tracing/...`

This avoids risky rewrites of working tools while making the project easier to operate.

## Workflow overview

```text
Generate model output
        │
        ▼
Validate/edit JSON or JSONL
        │
        ▼
Compare against validated baseline
        │
        ▼
Write reports/*.json and reports/*.csv
        │
        ▼
Build docs/benchmark_dashboard.html
        │
        ▼
Serve or submit docs/ and reports/
```

## Recommended commands

```bash
python -m pflegebench doctor
python -m pflegebench check
python -m pflegebench gui-benchmark
python -m pflegebench gui-editor
python -m pflegebench eval-html
python -m pflegebench compare-folder
python -m pflegebench dashboard --open
python -m pflegebench docs
```

## Future development rule

New workflow functionality should not be added as separate `.bat`, `.ps1`, `.sh` or ad-hoc command snippets. Add it as a new function in `src/pflegebench/workflow.py` and expose it in `src/pflegebench/cli.py`. This keeps the project portable.

## Runtime configuration layer

Environment handling is centralized in `src/pflegebench/env.py`.

Responsibilities:

- load `.env` from the repository root;
- avoid import-time crashes when API keys are missing;
- validate `OPENROUTER_API_KEY` only at the point where a model call is made;
- treat Langfuse as optional for GUI usage;
- keep local comparison, dashboard and editor workflows independent from external services.