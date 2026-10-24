# PflegeBench workflow

## Installation

From the project root:

```bash
python -m pip install -e .
```

The most reliable command form on every OS is:

```bash
python -m pflegebench --list
```

## Main commands

Check environment:

```bash
python -m pflegebench doctor
```

Run local checks:

```bash
python -m pflegebench check
```

Open benchmark generation GUI:

```bash
python -m pflegebench gui-benchmark
```

Open JSON/JSONL editor GUI:

```bash
python -m pflegebench gui-editor
```

Open browser validation tool:

```bash
python -m pflegebench eval-html
```

Compare one model output with one validated baseline:

```bash
python -m pflegebench compare --baseline data/benchmark/validated/1_complete-benchmark_chatgpt_5-5_26-05-15_v.json --model data/benchmark/to_validate/chatgpt/1_complete-benchmark_chatgpt_5-5_26-05-15.json --out reports/chatgpt_1_report.json   --errors-csv reports/chatgpt_1_errors.csv --key-mode auto
```

`--key-mode auto` first tries matching by `id`. If the IDs differ between raw and validated files, it falls back to matching by `module + criterion`. This keeps comparisons usable when validation changed only the IDs.

Compare all matching files:

```bash
python -m pflegebench compare-folder
```

Build dashboard:

```bash
python -m pflegebench dashboard
```

Build and open dashboard:

```bash
python -m pflegebench dashboard --open
```

Serve documentation locally:

```bash
python -m pflegebench docs
```

Then open:

```text
http://localhost:8000/benchmark_dashboard.html
```

Start traced conversation:

```bash
python -m pflegebench trace --model google/gemini-2.5-pro
```

Clean generated workflow output:

```bash
python -m pflegebench clean
```

## Recommended end-to-end workflow

1. **Generate model outputs**
   - `python -m pflegebench gui-benchmark`
   - or `python -m pflegebench trace --model <model-id>`

2. **Store raw outputs**
   - Files awaiting review go into `data/benchmark/to_validate/`.

3. **Validate/edit**
   - `python -m pflegebench gui-editor`
   - or `python -m pflegebench eval-html`
   - reviewed files go into `data/benchmark/validated/`.

4. **Compare**
   - single pair: `python -m pflegebench compare ...`
   - complete folders: `python -m pflegebench compare-folder`

5. **Visualize**
   - `python -m pflegebench dashboard`
   - result: `docs/benchmark_dashboard.html`

6. **Serve or submit**
   - `python -m pflegebench docs`
   - submit/commit the relevant files from `docs/` and `reports/`.

