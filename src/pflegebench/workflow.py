"""Cross-platform workflow operations for PflegeBench."""

from __future__ import annotations

import compileall
import importlib.util
import platform
import shutil
import sys
from pathlib import Path

from .env import openrouter_configured, langfuse_configured
from .matching import is_data_file, normalized_benchmark_stem, safe_report_name
from .paths import BENCHMARK_DIR, DOCS_DIR, LEGACY_SRC_DIR, PROJECT_ROOT, REPORTS_DIR, resolve_repo_path
from .process import open_in_browser, run_python


OVERVIEW_TEXT = """
PflegeBench workflow

Primary cross-platform command surface:
  python -m pflegebench <command>

After editable installation, the short console command is also available:
  pfbench <command>

Common commands:
  python -m pflegebench doctor
  python -m pflegebench check
  python -m pflegebench gui-benchmark
  python -m pflegebench gui-editor
  python -m pflegebench eval-html
  python -m pflegebench compare --baseline <validated.json> --model <model.json> --out reports/run.json
  python -m pflegebench compare-folder
  python -m pflegebench dashboard --open
  python -m pflegebench docs
  python -m pflegebench trace --model google/gemini-2.5-pro

Recommended sequence:
  1. Generate model outputs with gui-benchmark or trace.
  2. Validate/edit JSON or JSONL with gui-editor or eval-html.
  3. Compare files with compare or compare-folder.
  4. Build a visual static HTML dashboard with dashboard.
  5. Serve docs locally with docs.
""".strip()




def _load_compare_engine():
    """Load the legacy comparison engine from src/ without requiring packaging."""

    module_path = LEGACY_SRC_DIR / "compare_full_catalog.py"
    spec = importlib.util.spec_from_file_location("pflegebench_compare_full_catalog", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load comparison engine: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _accuracy_text(value) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "n/a"

def overview() -> None:
    print(OVERVIEW_TEXT)


def doctor() -> int:
    """Print environment diagnostics and return 0 for a usable base setup."""

    print("PflegeBench environment")
    print(f"  OS              : {platform.system()} {platform.release()} ({platform.platform()})")
    print(f"  Python          : {sys.version.split()[0]}")
    print(f"  Executable      : {sys.executable}")
    print(f"  Project root    : {PROJECT_ROOT}")
    print(f"  Source dir      : {LEGACY_SRC_DIR}")
    print(f"  Benchmark dir   : {BENCHMARK_DIR}")

    required = ["customtkinter", "dotenv", "requests"]
    optional = ["duckdb", "langfuse", "openai"]
    missing_required: list[str] = []

    print("\nPython packages")
    for name in required:
        ok = importlib.util.find_spec(name) is not None
        print(f"  {'OK' if ok else 'MISSING':7} {name}")
        if not ok:
            missing_required.append(name)
    for name in optional:
        ok = importlib.util.find_spec(name) is not None
        print(f"  {'OK' if ok else 'MISSING':7} {name} (optional for selected workflows)")

    print("\nImportant files")
    for path in [PROJECT_ROOT / "pyproject.toml", PROJECT_ROOT / ".env.example", LEGACY_SRC_DIR / "benchmark.py"]:
        print(f"  {'OK' if path.exists() else 'MISSING':7} {path.relative_to(PROJECT_ROOT) if path.exists() else path}")

    print("\nRuntime configuration")
    print(f"  {'OK' if openrouter_configured() else 'MISSING':7} OPENROUTER_API_KEY (required for model calls, integrated in .env.example)")
    print(f"  {'OK' if langfuse_configured() else 'MISSING':7} LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY (optional for remote tracing)")
    if not openrouter_configured():
        print("  To configure locally: copy .env.example to .env and fill OPENROUTER_API_KEY.")

    if missing_required:
        print("\nInstall missing packages with:")
        print("  python -m pip install -e .")
        return 1
    return 0


def setup(upgrade_pip: bool = False) -> None:
    """Install the project in editable mode with the current interpreter."""

    if upgrade_pip:
        run_python(["-m", "pip", "install", "-U", "pip"])
    run_python(["-m", "pip", "install", "-e", str(PROJECT_ROOT)])


def check() -> int:
    """Run local checks that do not require API keys or a GUI display."""

    ok = compileall.compile_dir(str(LEGACY_SRC_DIR), quiet=1)
    ok = compileall.compile_dir(str(PROJECT_ROOT / "src" / "pflegebench"), quiet=1) and ok
    if not ok:
        print("Python syntax check failed.")
        return 1

    run_python([str(LEGACY_SRC_DIR / "workflow_dashboard.py"), "--check-json", str(BENCHMARK_DIR)])
    return 0


def gui_benchmark() -> None:
    """Open the CustomTkinter benchmark generation GUI."""

    run_python([str(LEGACY_SRC_DIR / "benchmark.py")])

def cli_benchmark() -> None:
    """Start the interactive In-Memory & Streaming Pipeline (CLI)"""

    run_python([str(LEGACY_SRC_DIR / "benchmark.py"), "--cli"])

def gui_editor() -> None:
    """Open the JSON/JSONL editor GUI."""

    run_python([str(LEGACY_SRC_DIR / "handling_jsonl_file.py")])


def eval_html() -> None:
    """Open the browser-based validation tool."""

    open_in_browser(LEGACY_SRC_DIR / "expert-eval-tool.html")


def compare(
    baseline: str | Path,
    model: str | Path,
    out: str | Path = "reports/comparison_report.json",
    errors_csv: str | Path | None = None,
    top_errors: int = 50,
    key_mode: str = "auto",
    verbose: bool = True,
) -> None:
    """Compare one model output against one validated baseline."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    command: list[str | Path] = [
        str(LEGACY_SRC_DIR / "compare_full_catalog.py"),
        str(resolve_repo_path(baseline)),
        str(resolve_repo_path(model)),
        "--out",
        str(resolve_repo_path(out)),
        "--top-errors",
        str(top_errors),
        "--key-mode",
        key_mode,
    ]
    if errors_csv:
        command.extend(["--errors-csv", str(resolve_repo_path(errors_csv))])
    run_python(command, allowed_exit_codes=(0, 3), quiet=not verbose)


def compare_basic(baseline: str | Path, model: str | Path) -> None:
    """Run the older pairwise comparison script."""

    run_python([str(LEGACY_SRC_DIR / "compare_answers.py"), str(resolve_repo_path(baseline)), str(resolve_repo_path(model))])


def compare_folder(
    validated_dir: str | Path = "data/benchmark/validated",
    model_dir: str | Path = "data/benchmark/to_validate",
    out_dir: str | Path = "reports",
    top_errors: int = 50,
    key_mode: str = "auto",
) -> int:
    """Compare all matching model files against validated files."""

    validated_path = resolve_repo_path(validated_dir)
    model_path = resolve_repo_path(model_dir)
    reports_path = resolve_repo_path(out_dir)
    reports_path.mkdir(parents=True, exist_ok=True)

    validated_files = [path for path in validated_path.rglob("*") if is_data_file(path)]
    model_files = [path for path in model_path.rglob("*") if is_data_file(path)]
    baseline_by_stem = {normalized_benchmark_stem(path): path for path in validated_files}

    engine = _load_compare_engine()

    matched = 0
    failed = 0
    missing: list[str] = []
    for model_file in sorted(model_files):
        key = normalized_benchmark_stem(model_file)
        baseline_file = baseline_by_stem.get(key)
        if baseline_file is None:
            missing.append(str(model_file.relative_to(PROJECT_ROOT)))
            continue

        matched += 1
        report_name = safe_report_name(key)
        report_file = reports_path / f"{report_name}_report.json"
        errors_file = reports_path / f"{report_name}_errors.csv"

        baseline_loaded = engine.load_file(str(baseline_file))
        model_loaded = engine.load_file(str(model_file))
        report = engine.compare_catalog(baseline_loaded, model_loaded, key_mode=key_mode)
        engine.write_json_report(report, str(report_file))
        engine.write_errors_csv(report, str(errors_file))

        syntax_failed = bool(report["syntax_errors"]["baseline"] or report["syntax_errors"]["model"])
        no_overlap = report["coverage"]["common_items"] == 0
        status = "syntax-error" if syntax_failed else "no-overlap" if no_overlap else "ok"
        if syntax_failed:
            failed += 1
        accuracy = _accuracy_text(report.get("overall", {}).get("criterion_accuracy"))
        print(
            f"[{matched}/{len(model_files)}] {status:12} "
            f"common={report['coverage']['common_items']:>3} "
            f"acc={accuracy:>8} "
            f"{model_file.relative_to(PROJECT_ROOT)} -> {report_file.relative_to(PROJECT_ROOT)}"
        )

    print(f"Matched comparisons: {matched}")
    if failed:
        print(f"Failed comparisons with syntax errors: {failed}")
    if missing:
        print("Files without matching validated baseline:")
        for name in missing:
            print(f"  {name}")
    return 1 if failed else 0


def dashboard(reports: str | Path = "reports", out: str | Path = "docs/benchmark_dashboard.html", open_browser: bool = False) -> None:
    """Build the static HTML dashboard from comparison reports."""

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = resolve_repo_path(out)
    run_python([str(LEGACY_SRC_DIR / "workflow_dashboard.py"), "--reports", str(resolve_repo_path(reports)), "--out", str(out_path)])
    if open_browser:
        open_in_browser(out_path)


def docs(port: int = 8000) -> None:
    """Serve docs/ with Python's built-in HTTP server."""

    run_python(["-m", "http.server", str(port), "--directory", str(DOCS_DIR)])


def trace(model: str = "google/gemini-2.5-pro") -> None:
    """Start a traced OpenRouter/Langfuse conversation."""

    run_python([str(LEGACY_SRC_DIR / "tracing" / "langfuse" / "conversation.py"), "--model", model])


def trace_smoke() -> None:
    """Run the simple OpenRouter generation smoke test."""

    run_python([str(LEGACY_SRC_DIR / "tracing" / "poc-openrouter-otel.py")])


def clean() -> None:
    """Remove generated workflow artifacts."""

    if REPORTS_DIR.exists():
        shutil.rmtree(REPORTS_DIR)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / ".gitkeep").write_text("", encoding="utf-8")

    dashboard_file = DOCS_DIR / "benchmark_dashboard.html"
    if dashboard_file.exists():
        dashboard_file.unlink()
