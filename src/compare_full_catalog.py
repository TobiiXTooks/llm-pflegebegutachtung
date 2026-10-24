#!/usr/bin/env python3
"""
compare_full_catalog.py
-----------------------
Evaluates model answers against an expert/baseline catalog for a full M1-M6
Pflegebegutachtung case or catalog.

This version intentionally does NOT calculate Pflegegrad/Pflegescore.
It focuses on criterion-level evaluation:

- ID coverage
- Overall answer_idx accuracy
- Per-module criterion accuracy
- Per-criterion accuracy
- Mean absolute error on raw point_value, if present
- point_scale_id accuracy, if present
- Missing/extra IDs and invalid/missing fields

Supported input formats:
- JSONL: one JSON object per line
- JSON: top-level list, single object, or nested object containing lists such as
  items, answers, records, criteria, questions, modules

Usage:
    python compare_full_catalog.py <baseline_file> <model_file>
    python compare_full_catalog.py gold.json model.json --out report.json
    python compare_full_catalog.py gold.jsonl model.jsonl --errors-csv errors.csv

Expected item fields, if available:
    id, module, criterion, answer_idx, point_value, point_scale_id

If an item has no id, the tool falls back to a composite key:
    <module>::<criterion>
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

EXPECTED_MODULES = {"M1", "M2", "M3", "M4", "M5", "M6"}
NESTED_ITEM_KEYS = ("items", "answers", "records", "criteria", "questions", "catalog", "modules")
INTERNAL_KEYS = {"__line__", "__source_path__", "__comparison_key__"}


@dataclass
class LoadedFile:
    path: str
    items: list[dict[str, Any]]
    syntax_errors: list[dict[str, Any]]
    warnings: list[str]
    raw_lines: list[str]


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------

def detect_format(filepath: str) -> str:
    return "jsonl" if Path(filepath).suffix.lower() == ".jsonl" else "json"


def find_id_line(raw_lines: list[str], item_id: str) -> int | None:
    if not item_id:
        return None
    pattern = re.compile(r'"id"\s*:\s*"?' + re.escape(str(item_id)) + r'"?')
    for i, line in enumerate(raw_lines, start=1):
        if pattern.search(line):
            return i
    return None


def extract_items(data: Any, warnings: list[str], path_hint: str = "$") -> list[dict[str, Any]]:
    """
    Recursively extract benchmark-like objects.
    An item is any dict that has either:
      - an id, or
      - module + criterion, or
      - answer_idx/point_value together with module/criterion-like metadata.
    """
    items: list[dict[str, Any]] = []

    def looks_like_item(obj: dict[str, Any]) -> bool:
        has_identity = "id" in obj or ("module" in obj and "criterion" in obj)
        has_answer = any(k in obj for k in ("answer_idx", "point_value", "point_scale_id"))
        has_text = any(k in obj for k in ("stem", "question", "prompt"))
        return bool(has_identity and (has_answer or has_text))

    def walk(node: Any, where: str) -> None:
        if isinstance(node, list):
            for idx, value in enumerate(node):
                walk(value, f"{where}[{idx}]")
            return

        if isinstance(node, dict):
            if looks_like_item(node):
                items.append(dict(node))
                return

            # Prefer known container keys first, then recursively inspect remaining values.
            seen_keys: set[str] = set()
            for key in NESTED_ITEM_KEYS:
                if key in node:
                    seen_keys.add(key)
                    walk(node[key], f"{where}.{key}")
            for key, value in node.items():
                if key not in seen_keys and isinstance(value, (list, dict)):
                    walk(value, f"{where}.{key}")

    walk(data, path_hint)
    if not items:
        warnings.append("No benchmark items were found in the parsed JSON structure.")
    return items


def load_file(filepath: str) -> LoadedFile:
    fmt = detect_format(filepath)
    items: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    warnings: list[str] = []

    with open(filepath, "r", encoding="utf-8") as fh:
        raw = fh.read()
    raw_lines = raw.splitlines()

    if fmt == "jsonl":
        for lineno, line in enumerate(raw_lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
                if isinstance(obj, dict):
                    obj = dict(obj)
                    obj["__line__"] = lineno
                    items.append(obj)
                else:
                    errors.append({
                        "line": lineno,
                        "col": 1,
                        "message": "JSONL line is not a JSON object.",
                        "snippet": stripped[:120],
                    })
            except json.JSONDecodeError as exc:
                errors.append({
                    "line": lineno,
                    "col": exc.colno,
                    "message": exc.msg,
                    "snippet": stripped[:120],
                })
    else:
        try:
            data = json.loads(raw)
            items = extract_items(data, warnings)
            for item in items:
                item_id = item.get("id")
                item["__line__"] = find_id_line(raw_lines, str(item_id)) if item_id is not None else None
        except json.JSONDecodeError as exc:
            errors.append({
                "line": exc.lineno,
                "col": exc.colno,
                "message": exc.msg,
                "snippet": raw_lines[exc.lineno - 1][:120] if exc.lineno <= len(raw_lines) else "",
            })

    for item in items:
        item["__source_path__"] = filepath

    return LoadedFile(filepath, items, errors, warnings, raw_lines)


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def normalize_module(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    s = str(value).strip().upper().replace(" ", "")
    match = re.search(r"M\s*([1-6])", s)
    if match:
        return f"M{match.group(1)}"
    return s or "UNKNOWN"


def normalize_criterion(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    if isinstance(value, list):
        return " | ".join(str(v).strip() for v in value)
    return str(value).strip()


def comparison_key(item: dict[str, Any], key_mode: str = "id") -> str:
    if key_mode == "criterion":
        return f"{normalize_module(item.get('module'))}::{normalize_criterion(item.get('criterion'))}"
    if item.get("id") is not None and str(item.get("id")).strip() != "":
        return str(item["id"]).strip()
    return f"{normalize_module(item.get('module'))}::{normalize_criterion(item.get('criterion'))}"


def as_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    if isinstance(value, str):
        s = value.strip().replace(",", ".")
        # Extract first number from strings such as "3 Punkte".
        match = re.search(r"-?\d+(?:\.\d+)?", s)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return None
    return None


def safe_accuracy(correct: int, total: int) -> float | None:
    return round(correct / total, 6) if total else None


def mean(values: Iterable[float]) -> float | None:
    vals = list(values)
    return round(sum(vals) / len(vals), 6) if vals else None


def natural_sort_key(value: str) -> list[Any]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", str(value))]


# ---------------------------------------------------------------------------
# Validation and indexing
# ---------------------------------------------------------------------------

def index_items(items: list[dict[str, Any]], key_mode: str = "id") -> tuple[dict[str, dict[str, Any]], dict[str, int], list[str]]:
    warnings: list[str] = []
    counts: Counter[str] = Counter()
    indexed: dict[str, dict[str, Any]] = {}

    for item in items:
        key = comparison_key(item, key_mode=key_mode)
        item["__comparison_key__"] = key
        counts[key] += 1
        # Keep first occurrence for deterministic comparison; duplicate is reported.
        if key not in indexed:
            indexed[key] = item

    duplicates = {key: count for key, count in counts.items() if count > 1}
    for key, count in sorted(duplicates.items(), key=lambda kv: natural_sort_key(kv[0])):
        warnings.append(f"Duplicate comparison key '{key}' occurs {count} times; first occurrence is used.")

    return indexed, dict(counts), warnings


def validate_items(label: str, items: list[dict[str, Any]], key_mode: str = "id") -> list[str]:
    warnings: list[str] = []
    modules = {normalize_module(item.get("module")) for item in items}
    present_expected = modules & EXPECTED_MODULES
    missing_expected = sorted(EXPECTED_MODULES - present_expected, key=natural_sort_key)
    unknown_modules = sorted(modules - EXPECTED_MODULES - {"UNKNOWN"}, key=natural_sort_key)

    if missing_expected:
        warnings.append(f"{label}: expected modules missing: {', '.join(missing_expected)}")
    if "UNKNOWN" in modules:
        warnings.append(f"{label}: at least one item has no recognizable module.")
    if unknown_modules:
        warnings.append(f"{label}: unknown module labels: {', '.join(unknown_modules)}")

    missing_answer = [comparison_key(item, key_mode=key_mode) for item in items if "answer_idx" not in item]
    if missing_answer:
        sample = ", ".join(missing_answer[:10])
        more = "..." if len(missing_answer) > 10 else ""
        warnings.append(f"{label}: {len(missing_answer)} item(s) have no answer_idx: {sample}{more}")

    return warnings


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compare_catalog(baseline: LoadedFile, model: LoadedFile, key_mode: str = "auto") -> dict[str, Any]:
    if key_mode not in {"auto", "id", "criterion"}:
        raise ValueError("key_mode must be one of: auto, id, criterion")

    effective_key_mode = "id" if key_mode == "auto" else key_mode

    def build_indexes(mode: str):
        b_idx, b_cnt, b_warn = index_items(baseline.items, key_mode=mode)
        m_idx, m_cnt, m_warn = index_items(model.items, key_mode=mode)
        b_ids = set(b_idx)
        m_ids = set(m_idx)
        common = sorted(b_ids & m_ids, key=natural_sort_key)
        return b_idx, b_cnt, b_warn, m_idx, m_cnt, m_warn, b_ids, m_ids, common

    (
        b_map, b_counts, b_index_warnings,
        m_map, m_counts, m_index_warnings,
        baseline_ids, model_ids, common_ids,
    ) = build_indexes(effective_key_mode)

    warnings: list[str] = []
    if key_mode == "auto" and not common_ids:
        (
            alt_b_map, alt_b_counts, alt_b_warnings,
            alt_m_map, alt_m_counts, alt_m_warnings,
            alt_baseline_ids, alt_model_ids, alt_common_ids,
        ) = build_indexes("criterion")
        if alt_common_ids:
            effective_key_mode = "criterion"
            b_map, b_counts, b_index_warnings = alt_b_map, alt_b_counts, alt_b_warnings
            m_map, m_counts, m_index_warnings = alt_m_map, alt_m_counts, alt_m_warnings
            baseline_ids, model_ids, common_ids = alt_baseline_ids, alt_model_ids, alt_common_ids
            warnings.append("key_mode=auto: no shared IDs found; compared by module + criterion instead.")

    only_baseline = sorted(baseline_ids - model_ids, key=natural_sort_key)
    only_model = sorted(model_ids - baseline_ids, key=natural_sort_key)

    warnings.extend(baseline.warnings)
    warnings.extend(model.warnings)
    warnings.extend(validate_items("baseline", baseline.items, key_mode=effective_key_mode))
    warnings.extend(validate_items("model", model.items, key_mode=effective_key_mode))
    warnings.extend([f"baseline: {w}" for w in b_index_warnings])
    warnings.extend([f"model: {w}" for w in m_index_warnings])

    item_results: list[dict[str, Any]] = []

    for key in common_ids:
        b = b_map[key]
        m = m_map[key]
        module = normalize_module(b.get("module", m.get("module")))
        criterion = normalize_criterion(b.get("criterion", m.get("criterion")))

        b_answer = b.get("answer_idx")
        m_answer = m.get("answer_idx")
        answer_comparable = "answer_idx" in b and "answer_idx" in m
        answer_correct = (b_answer == m_answer) if answer_comparable else None

        b_point = as_number(b.get("point_value"))
        m_point = as_number(m.get("point_value"))
        point_abs_error = abs(b_point - m_point) if b_point is not None and m_point is not None else None

        b_point_scale = b.get("point_scale_id")
        m_point_scale = m.get("point_scale_id")
        point_scale_comparable = "point_scale_id" in b and "point_scale_id" in m
        point_scale_correct = (b_point_scale == m_point_scale) if point_scale_comparable else None

        item_results.append({
            "id": key,
            "module": module,
            "criterion": criterion,
            "baseline_answer_idx": b_answer,
            "model_answer_idx": m_answer,
            "answer_comparable": answer_comparable,
            "answer_correct": answer_correct,
            "baseline_point_value": b_point,
            "model_point_value": m_point,
            "point_value_abs_error": point_abs_error,
            "baseline_point_scale_id": b_point_scale,
            "model_point_scale_id": m_point_scale,
            "point_scale_comparable": point_scale_comparable,
            "point_scale_correct": point_scale_correct,
            "baseline_line": b.get("__line__"),
            "model_line": m.get("__line__"),
        })

    def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
        answer_rows = [r for r in rows if r["answer_comparable"]]
        answer_correct = sum(1 for r in answer_rows if r["answer_correct"] is True)
        point_errors = [r["point_value_abs_error"] for r in rows if r["point_value_abs_error"] is not None]
        point_scale_rows = [r for r in rows if r["point_scale_comparable"]]
        point_scale_correct = sum(1 for r in point_scale_rows if r["point_scale_correct"] is True)
        return {
            "criterion_accuracy": safe_accuracy(answer_correct, len(answer_rows)),
            "answer_idx_correct": answer_correct,
            "answer_idx_compared": len(answer_rows),
            "raw_point_value_mae": mean(point_errors),
            "raw_point_value_compared": len(point_errors),
            "point_scale_id_accuracy": safe_accuracy(point_scale_correct, len(point_scale_rows)),
            "point_scale_id_correct": point_scale_correct,
            "point_scale_id_compared": len(point_scale_rows),
        }

    overall = aggregate(item_results)

    per_module: dict[str, Any] = {}
    all_modules = sorted(
        {normalize_module(item.get("module")) for item in baseline.items + model.items},
        key=natural_sort_key,
    )
    for module in all_modules:
        rows = [r for r in item_results if r["module"] == module]
        baseline_module_ids = {key for key, item in b_map.items() if normalize_module(item.get("module")) == module}
        model_module_ids = {key for key, item in m_map.items() if normalize_module(item.get("module")) == module}
        per_module[module] = {
            **aggregate(rows),
            "baseline_items": len(baseline_module_ids),
            "model_items": len(model_module_ids),
            "common_items": len(baseline_module_ids & model_module_ids),
            "missing_in_model": sorted(baseline_module_ids - model_module_ids, key=natural_sort_key),
            "extra_in_model": sorted(model_module_ids - baseline_module_ids, key=natural_sort_key),
        }

    per_criterion: dict[str, Any] = {}
    criterion_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in item_results:
        criterion_groups[f"{row['module']}::{row['criterion']}"] .append(row)
    for key, rows in sorted(criterion_groups.items(), key=lambda kv: natural_sort_key(kv[0])):
        per_criterion[key] = aggregate(rows)

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tool": "compare_full_catalog.py",
        "pflegescore_enabled": False,
        "pflegescore_note": "Pflegegrad/Pflegescore calculation is intentionally omitted in this version.",
        "key_mode": effective_key_mode,
        "baseline_file": baseline.path,
        "model_file": model.path,
        "syntax_errors": {
            "baseline": baseline.syntax_errors,
            "model": model.syntax_errors,
        },
        "warnings": warnings,
        "coverage": {
            "baseline_items": len(b_map),
            "model_items": len(m_map),
            "common_items": len(common_ids),
            "only_in_baseline_count": len(only_baseline),
            "only_in_model_count": len(only_model),
            "only_in_baseline": only_baseline,
            "only_in_model": only_model,
            "baseline_duplicate_counts": {k: v for k, v in b_counts.items() if v > 1},
            "model_duplicate_counts": {k: v for k, v in m_counts.items() if v > 1},
        },
        "overall": overall,
        "per_module": per_module,
        "per_criterion": per_criterion,
        "incorrect_items": [r for r in item_results if r["answer_correct"] is False],
        "uncomparable_items": [r for r in item_results if not r["answer_comparable"]],
        "item_results": item_results,
    }
    return report


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def number(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.4f}".rstrip("0").rstrip(".")


def print_report(report: dict[str, Any], top_errors: int) -> None:
    width = 96
    print("\n" + "=" * width)
    print("M1-M6 FULL CATALOG BENCHMARK REPORT")
    print("=" * width)
    print(f"Baseline: {report['baseline_file']}")
    print(f"Model   : {report['model_file']}")

    syntax = report["syntax_errors"]
    if syntax["baseline"] or syntax["model"]:
        print("\nSYNTAX ERRORS")
        for label in ("baseline", "model"):
            for err in syntax[label]:
                print(f"  {label}: line {err.get('line')}, col {err.get('col')}: {err.get('message')}")
        print("\nFix syntax errors before relying on the metrics.")

    coverage = report["coverage"]
    print("\nCOVERAGE")
    print(f"  Baseline items      : {coverage['baseline_items']}")
    print(f"  Model items         : {coverage['model_items']}")
    print(f"  Common items        : {coverage['common_items']}")
    print(f"  Only in baseline    : {coverage['only_in_baseline_count']}")
    print(f"  Only in model       : {coverage['only_in_model_count']}")

    overall = report["overall"]
    print("\nOVERALL METRICS")
    print(f"  Criterion accuracy  : {percent(overall['criterion_accuracy'])} "
          f"({overall['answer_idx_correct']}/{overall['answer_idx_compared']})")
    print(f"  Raw point MAE       : {number(overall['raw_point_value_mae'])} "
          f"({overall['raw_point_value_compared']} compared)")
    print(f"  point_scale accuracy: {percent(overall['point_scale_id_accuracy'])} "
          f"({overall['point_scale_id_correct']}/{overall['point_scale_id_compared']})")

    print("\nPER-MODULE METRICS")
    header = (
        f"{'Module':<8} {'Acc':>10} {'Correct':>13} {'Raw MAE':>12} "
        f"{'Common':>8} {'Missing':>8} {'Extra':>8}"
    )
    print("  " + header)
    print("  " + "-" * len(header))
    for module, stats in sorted(report["per_module"].items(), key=lambda kv: natural_sort_key(kv[0])):
        print(
            f"  {module:<8} "
            f"{percent(stats['criterion_accuracy']):>10} "
            f"{str(stats['answer_idx_correct']) + '/' + str(stats['answer_idx_compared']):>13} "
            f"{number(stats['raw_point_value_mae']):>12} "
            f"{stats['common_items']:>8} "
            f"{len(stats['missing_in_model']):>8} "
            f"{len(stats['extra_in_model']):>8}"
        )

    if report["warnings"]:
        print("\nWARNINGS")
        for warning in report["warnings"][:30]:
            print(f"  - {warning}")
        if len(report["warnings"]) > 30:
            print(f"  - ... {len(report['warnings']) - 30} more warning(s)")

    incorrect = report["incorrect_items"]
    if incorrect:
        print(f"\nINCORRECT ANSWER_IDX ITEMS (showing up to {top_errors})")
        for row in incorrect[:top_errors]:
            print(
                f"  [{row['id']}] {row['module']} | {row['criterion']} | "
                f"baseline={row['baseline_answer_idx']} model={row['model_answer_idx']} | "
                f"point_error={number(row['point_value_abs_error'])}"
            )
        if len(incorrect) > top_errors:
            print(f"  ... {len(incorrect) - top_errors} more incorrect item(s)")
    else:
        print("\nINCORRECT ANSWER_IDX ITEMS")
        print("  None among comparable common items.")

    print()


def write_json_report(report: dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)


def write_errors_csv(report: dict[str, Any], path: str) -> None:
    fields = [
        "id", "module", "criterion",
        "baseline_answer_idx", "model_answer_idx",
        "baseline_point_value", "model_point_value", "point_value_abs_error",
        "baseline_point_scale_id", "model_point_scale_id",
        "baseline_line", "model_line",
    ]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in report["incorrect_items"]:
            writer.writerow(row)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare a full M1-M6 benchmark catalog without Pflegegrad/Pflegescore calculation."
    )
    parser.add_argument("baseline_file", help="Expert/baseline JSON or JSONL file")
    parser.add_argument("model_file", help="Model answer JSON or JSONL file")
    parser.add_argument("--out", help="Optional JSON report output path")
    parser.add_argument("--errors-csv", help="Optional CSV file with incorrect answer_idx items")
    parser.add_argument("--top-errors", type=int, default=50, help="Number of incorrect items to print")
    parser.add_argument("--key-mode", choices=["auto", "id", "criterion"], default="auto", help="Comparison key: id, criterion, or auto fallback from id to criterion")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    for path in (args.baseline_file, args.model_file):
        if not os.path.exists(path):
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 1

    baseline = load_file(args.baseline_file)
    model = load_file(args.model_file)
    report = compare_catalog(baseline, model, key_mode=args.key_mode)
    print_report(report, top_errors=max(args.top_errors, 0))

    if args.out:
        write_json_report(report, args.out)
        print(f"JSON report written to: {args.out}")

    if args.errors_csv:
        write_errors_csv(report, args.errors_csv)
        print(f"Error CSV written to: {args.errors_csv}")

    # Non-zero exit code only for syntax errors or no overlap.
    if report["syntax_errors"]["baseline"] or report["syntax_errors"]["model"]:
        return 2
    if report["coverage"]["common_items"] == 0:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
