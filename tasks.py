"""Compatibility wrapper for users who prefer Invoke.

The primary cross-platform interface is now:

    python -m pflegebench <command>

Invoke remains optional. These tasks delegate to the same Python workflow layer
and do not use shell=True or pty=True, so they also work on Windows.
"""

from __future__ import annotations

import sys
from pathlib import Path

from invoke import task

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pflegebench import workflow  # noqa: E402


@task(name="overview")
def overview(c) -> None:
    """Show the recommended project workflow and common commands."""
    workflow.overview()


@task
def setup(c, upgrade_pip: bool = False) -> None:
    """Install the project in editable mode."""
    workflow.setup(upgrade_pip=upgrade_pip)


@task
def doctor(c) -> None:
    """Show OS, Python and dependency diagnostics."""
    raise SystemExit(workflow.doctor())


@task
def check(c) -> None:
    """Run syntax and benchmark JSON checks."""
    raise SystemExit(workflow.check())


@task(name="gui-benchmark")
def gui_benchmark(c) -> None:
    """Open the CustomTkinter benchmark generation GUI."""
    workflow.gui_benchmark()


@task(name="gui-editor")
def gui_editor(c) -> None:
    """Open the JSON/JSONL benchmark editor GUI."""
    workflow.gui_editor()


@task(name="eval-html")
def eval_html(c) -> None:
    """Open the browser-based expert evaluation tool."""
    workflow.eval_html()


@task
def compare(
    c,
    baseline: str,
    model: str,
    out: str = "reports/comparison_report.json",
    errors_csv: str = "",
    top_errors: int = 50,
    key_mode: str = "auto",
) -> None:
    """Compare a model output file against a validated baseline."""
    workflow.compare(baseline, model, out, errors_csv or None, top_errors, key_mode)


@task(name="compare-basic")
def compare_basic(c, baseline: str, model: str) -> None:
    """Run the older pairwise comparison script."""
    workflow.compare_basic(baseline, model)


@task(name="compare-folder")
def compare_folder(
    c,
    validated_dir: str = "data/benchmark/validated",
    model_dir: str = "data/benchmark/to_validate",
    out_dir: str = "reports",
    top_errors: int = 50,
    key_mode: str = "auto",
) -> None:
    """Compare all matching files from to_validate/ against validated/ baselines."""
    raise SystemExit(workflow.compare_folder(validated_dir, model_dir, out_dir, top_errors, key_mode))


@task
def dashboard(
    c,
    reports: str = "reports",
    out: str = "docs/benchmark_dashboard.html",
    open_browser: bool = False,
) -> None:
    """Build a static HTML dashboard from comparison JSON reports."""
    workflow.dashboard(reports, out, open_browser)


@task
def docs(c, port: int = 8000) -> None:
    """Serve docs/ locally so HTML reports can be viewed in the browser."""
    workflow.docs(port)


@task
def trace(c, model: str = "google/gemini-2.5-pro") -> None:
    """Start a traced OpenRouter/Langfuse conversation."""
    workflow.trace(model)


@task(name="trace-smoke")
def trace_smoke(c) -> None:
    """Run the simple OpenRouter tracing proof of concept."""
    workflow.trace_smoke()


@task
def clean(c) -> None:
    """Remove generated local workflow artifacts."""
    workflow.clean()
