"""Command line interface for PflegeBench."""

from __future__ import annotations

import argparse
from typing import Sequence

from . import __version__
from . import workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pfbench",
        description="Cross-platform PflegeBench workflow manager",
    )
    parser.add_argument("--version", action="version", version=f"PflegeBench {__version__}")
    parser.add_argument("--list", action="store_true", help="List available commands and exit")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("overview", help="Show recommended workflow")
    setup_p = sub.add_parser("setup", help="Install project in editable mode")
    setup_p.add_argument("--upgrade-pip", action="store_true", help="Upgrade pip before installing")
    sub.add_parser("doctor", help="Show OS, Python and dependency diagnostics")
    sub.add_parser("check", help="Run syntax and JSON checks")
    sub.add_parser("gui-benchmark", help="Open benchmark generation GUI")
    sub.add_parser("cli-benchmark", help="Start interactive In-Memory & Streaming Pipeline (CLI)")
    sub.add_parser("gui-editor", help="Open JSON/JSONL editor GUI")
    sub.add_parser("eval-html", help="Open browser validation tool")

    compare_p = sub.add_parser("compare", help="Compare one model output with one validated baseline")
    compare_p.add_argument("--baseline", required=True, help="Validated baseline JSON/JSONL file")
    compare_p.add_argument("--model", required=True, help="Model output JSON/JSONL file")
    compare_p.add_argument("--out", default="reports/comparison_report.json", help="Output report JSON path")
    compare_p.add_argument("--errors-csv", default=None, help="Optional detailed error CSV path")
    compare_p.add_argument("--top-errors", type=int, default=50, help="Number of wrong items printed/stored")
    compare_p.add_argument("--key-mode", choices=["auto", "id", "criterion"], default="auto", help="Comparison key strategy")

    compare_basic_p = sub.add_parser("compare-basic", help="Run older pairwise comparison script")
    compare_basic_p.add_argument("--baseline", required=True)
    compare_basic_p.add_argument("--model", required=True)

    folder_p = sub.add_parser("compare-folder", help="Compare all matching files in benchmark folders")
    folder_p.add_argument("--validated-dir", default="data/benchmark/validated")
    folder_p.add_argument("--model-dir", default="data/benchmark/to_validate")
    folder_p.add_argument("--out-dir", default="reports")
    folder_p.add_argument("--top-errors", type=int, default=50)
    folder_p.add_argument("--key-mode", choices=["auto", "id", "criterion"], default="auto", help="Comparison key strategy")

    dash_p = sub.add_parser("dashboard", help="Build static HTML dashboard")
    dash_p.add_argument("--reports", default="reports")
    dash_p.add_argument("--out", default="docs/benchmark_dashboard.html")
    dash_p.add_argument("--open", action="store_true", help="Open dashboard after generation")

    docs_p = sub.add_parser("docs", help="Serve docs/ locally")
    docs_p.add_argument("--port", type=int, default=8000)

    trace_p = sub.add_parser("trace", help="Start traced OpenRouter/Langfuse conversation")
    trace_p.add_argument("--model", default="google/gemini-2.5-pro")
    sub.add_parser("trace-smoke", help="Run OpenRouter generation smoke test")
    sub.add_parser("clean", help="Remove generated reports/dashboard artifacts")

    return parser


def print_command_list() -> None:
    print(
        """
Available PflegeBench commands:
  overview
  setup [--upgrade-pip]
  doctor
  check
  gui-benchmark
  gui-editor
  eval-html
  compare --baseline <file> --model <file> [--out <file>] [--errors-csv <file>] [--key-mode auto|id|criterion]
  compare-basic --baseline <file> --model <file>
  compare-folder [--validated-dir <dir>] [--model-dir <dir>] [--out-dir <dir>]
  dashboard [--reports <dir>] [--out <html>] [--open]
  docs [--port 8000]
  trace [--model <openrouter-model-id>]
  trace-smoke
  clean
""".strip()
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        print_command_list()
        return 0

    if args.command is None:
        workflow.overview()
        return 0

    if args.command == "overview":
        workflow.overview()
    elif args.command == "setup":
        workflow.setup(upgrade_pip=args.upgrade_pip)
    elif args.command == "doctor":
        return workflow.doctor()
    elif args.command == "check":
        return workflow.check()
    elif args.command == "gui-benchmark":
        workflow.gui_benchmark()
    elif args.command == "cli-benchmark":
        workflow.cli_benchmark()
    elif args.command == "gui-editor":
        workflow.gui_editor()
    elif args.command == "eval-html":
        workflow.eval_html()
    elif args.command == "compare":
        workflow.compare(args.baseline, args.model, args.out, args.errors_csv, args.top_errors, args.key_mode)
    elif args.command == "compare-basic":
        workflow.compare_basic(args.baseline, args.model)
    elif args.command == "compare-folder":
        return workflow.compare_folder(args.validated_dir, args.model_dir, args.out_dir, args.top_errors, args.key_mode)
    elif args.command == "dashboard":
        workflow.dashboard(args.reports, args.out, args.open)
    elif args.command == "docs":
        workflow.docs(args.port)
    elif args.command == "trace":
        workflow.trace(args.model)
    elif args.command == "trace-smoke":
        workflow.trace_smoke()
    elif args.command == "clean":
        workflow.clean()
    else:
        parser.error(f"unknown command: {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
