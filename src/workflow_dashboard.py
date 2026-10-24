"""Build a static HTML dashboard from PflegeBench comparison reports.

This script intentionally uses only the Python standard library so it can run
without Jupyter, Plotly, or a browser automation stack.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PflegeBench Workflow Dashboard</title>
<style>
:root {{
  --bg: #f6f8fb;
  --card: #ffffff;
  --text: #172033;
  --muted: #64748b;
  --line: #d8dee9;
  --accent: #1e3a8a;
  --soft: #e8eefc;
  --danger: #7f1d1d;
}}
body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: var(--bg); color: var(--text); }}
header {{ padding: 28px 36px; background: var(--accent); color: white; }}
header h1 {{ margin: 0 0 6px 0; font-size: 28px; }}
header p {{ margin: 0; opacity: 0.9; }}
main {{ padding: 28px 36px 48px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin-bottom: 22px; }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 18px; box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04); }}
.metric {{ font-size: 30px; font-weight: 700; margin-top: 8px; }}
.label {{ color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; }}
section {{ margin-top: 24px; }}
h2 {{ margin: 0 0 12px 0; color: var(--accent); }}
table {{ width: 100%; border-collapse: collapse; background: var(--card); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }}
th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
th {{ background: var(--soft); font-size: 13px; }}
tr:last-child td {{ border-bottom: none; }}
.muted {{ color: var(--muted); }}
.bad {{ color: var(--danger); font-weight: 700; }}
.chart-row {{ margin: 18px 0 26px; }}
.chart-title {{ margin: 0 0 8px 0; font-weight: 700; }}
svg {{ width: 100%; max-width: 940px; height: auto; background: var(--card); border: 1px solid var(--line); border-radius: 14px; }}
.empty {{ padding: 20px; border: 1px dashed var(--line); border-radius: 14px; background: var(--card); }}
code {{ background: #eef2ff; padding: 2px 5px; border-radius: 4px; }}
</style>
</head>
<body>
<header>
  <h1>PflegeBench Workflow Dashboard</h1>
  <p>Generated {generated_at}</p>
</header>
<main>
  {content}
</main>
</body>
</html>
"""


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "n/a"


def num(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.3f}".rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return "n/a"


def read_reports(path: Path) -> list[dict[str, Any]]:
    files = sorted(path.glob("*.json")) if path.is_dir() else [path]
    reports: list[dict[str, Any]] = []
    for file in files:
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"Skipping invalid report {file}: {exc}", file=sys.stderr)
            continue
        if isinstance(data, dict) and data.get("tool") == "compare_full_catalog.py":
            data["__report_file"] = str(file)
            reports.append(data)
    return reports


def build_summary(reports: list[dict[str, Any]]) -> str:
    total_reports = len(reports)
    total_common = sum(r.get("coverage", {}).get("common_items", 0) for r in reports)
    total_incorrect = sum(len(r.get("incorrect_items", [])) for r in reports)
    accuracies = [r.get("overall", {}).get("criterion_accuracy") for r in reports]
    valid_acc = [float(a) for a in accuracies if isinstance(a, (int, float))]
    avg_accuracy = sum(valid_acc) / len(valid_acc) if valid_acc else None
    return f"""
<div class="grid">
  <div class="card"><div class="label">Reports</div><div class="metric">{total_reports}</div></div>
  <div class="card"><div class="label">Compared items</div><div class="metric">{total_common}</div></div>
  <div class="card"><div class="label">Incorrect items</div><div class="metric">{total_incorrect}</div></div>
  <div class="card"><div class="label">Average criterion accuracy</div><div class="metric">{pct(avg_accuracy)}</div></div>
</div>
"""


def build_table(reports: list[dict[str, Any]]) -> str:
    rows = []
    for r in reports:
        cov = r.get("coverage", {})
        overall = r.get("overall", {})
        rows.append(
            "<tr>"
            f"<td>{html.escape(Path(r.get('__report_file', '')).name)}</td>"
            f"<td>{html.escape(Path(r.get('baseline_file', '')).name)}</td>"
            f"<td>{html.escape(Path(r.get('model_file', '')).name)}</td>"
            f"<td>{cov.get('common_items', 0)}</td>"
            f"<td>{html.escape(str(r.get('key_mode', 'n/a')))}</td>"
            f"<td>{pct(overall.get('criterion_accuracy'))}</td>"
            f"<td>{num(overall.get('raw_point_value_mae'))}</td>"
            f"<td>{len(r.get('incorrect_items', []))}</td>"
            "</tr>"
        )
    return """
<section>
  <h2>Comparison reports</h2>
  <table>
    <thead><tr><th>Report</th><th>Baseline</th><th>Model</th><th>Common</th><th>Key mode</th><th>Accuracy</th><th>Raw point MAE</th><th>Incorrect</th></tr></thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</section>
""".format(rows="\n".join(rows))


def bar_svg(values: list[tuple[str, float | None]]) -> str:
    width = 940
    row_h = 34
    left = 145
    right = 70
    height = max(80, 30 + row_h * len(values))
    bar_w = width - left - right
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img">']
    parts.append(f'<line x1="{left}" y1="18" x2="{left}" y2="{height - 18}" stroke="#d8dee9"/>')
    parts.append(f'<line x1="{left + bar_w}" y1="18" x2="{left + bar_w}" y2="{height - 18}" stroke="#d8dee9"/>')
    for i, (label, value) in enumerate(values):
        y = 28 + i * row_h
        safe_label = html.escape(label)
        display = pct(value)
        frac = max(0.0, min(1.0, float(value))) if isinstance(value, (int, float)) else 0.0
        parts.append(f'<text x="14" y="{y + 17}" font-size="13" fill="#172033">{safe_label}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w}" height="20" fill="#edf2ff" rx="5"/>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_w * frac:.1f}" height="20" fill="#1e3a8a" rx="5"/>')
        parts.append(f'<text x="{left + bar_w + 12}" y="{y + 15}" font-size="12" fill="#172033">{display}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def build_charts(reports: list[dict[str, Any]]) -> str:
    sections = []
    for r in reports:
        per_module = r.get("per_module", {})
        values = []
        for module, stats in sorted(per_module.items()):
            values.append((module, stats.get("criterion_accuracy")))
        title = html.escape(Path(r.get("model_file", "report")).name)
        sections.append(
            f'<div class="chart-row"><p class="chart-title">{title}: criterion accuracy by module</p>{bar_svg(values)}</div>'
        )
    return f"<section><h2>Visual module overview</h2>{''.join(sections)}</section>"


def build_content(reports: list[dict[str, Any]]) -> str:
    if not reports:
        return """
<div class="empty">
  No comparison reports found. Create one with:<br>
  <code>python -m pflegebench compare --baseline data/benchmark/validated/example_v.json --model data/benchmark/to_validate/example.json --out reports/example.json</code><br><br>
  Then run:<br>
  <code>python -m pflegebench dashboard</code>
</div>
"""
    return build_summary(reports) + build_table(reports) + build_charts(reports)


def write_dashboard(reports_path: Path, out_path: Path) -> None:
    reports = read_reports(reports_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html_text = HTML_TEMPLATE.format(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        content=build_content(reports),
    )
    out_path.write_text(html_text, encoding="utf-8")
    print(f"Dashboard written to {out_path}")


def check_json(path: Path) -> int:
    files = list(path.rglob("*.json")) + list(path.rglob("*.jsonl"))
    errors = 0
    for file in sorted(files):
        try:
            if file.suffix == ".jsonl":
                for line_no, line in enumerate(file.read_text(encoding="utf-8").splitlines(), start=1):
                    if line.strip():
                        json.loads(line)
            else:
                json.loads(file.read_text(encoding="utf-8"))
        except Exception as exc:
            errors += 1
            print(f"Invalid JSON in {file}: {exc}", file=sys.stderr)
    print(f"Checked {len(files)} JSON/JSONL file(s), errors: {errors}")
    return 1 if errors else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build PflegeBench workflow dashboard")
    parser.add_argument("--reports", default="reports", help="Report JSON file or directory")
    parser.add_argument("--out", default="docs/benchmark_dashboard.html", help="HTML output path")
    parser.add_argument("--check-json", help="Validate JSON/JSONL files below this path and exit")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.check_json:
        return check_json(Path(args.check_json))
    write_dashboard(Path(args.reports), Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
