#!/usr/bin/env python3
"""
compare_answers.py
------------------
Compares an expert-validated baseline file against a model answer file.
Both files may be JSON or JSONL format.

Usage:
    python compare_answers.py <baseline_file> <model_file>

Steps performed:
    1. Syntax validation of both files
    2. Field-level comparison (answer_idx excluded)
    3. answer_idx accuracy metric
    4. Optional log file output (asks before saving)
"""

import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------------------------
# Keys that are intentionally excluded from field comparison
# ---------------------------------------------------------------------------
SKIP_COMPARISON_KEYS = {
    "answer_idx",   # handled separately in Step 3
    "_validation",  # only present in validated baseline
    "__line__",     # internal tracking field added by this script
}


# ---------------------------------------------------------------------------
# File loading helpers
# ---------------------------------------------------------------------------

def detect_format(filepath: str) -> str:
    """Return 'jsonl' or 'json' based on file extension."""
    return "jsonl" if Path(filepath).suffix.lower() == ".jsonl" else "json"


def find_id_line(raw_lines: list[str], item_id: str) -> int | None:
    """
    Scan raw lines for the approximate line number where an id value appears.
    Looks for   "id": "<item_id>"   pattern.
    """
    pattern = re.compile(r'"id"\s*:\s*"' + re.escape(item_id) + r'"')
    for i, line in enumerate(raw_lines, start=1):
        if pattern.search(line):
            return i
    return None


def load_file(filepath: str) -> tuple[list[dict], list[dict], list[str]]:
    """
    Load a JSON or JSONL file.

    Returns
    -------
    items        : list of parsed dicts (with '__line__' injected)
    syntax_errors: list of error detail dicts
    raw_lines    : original lines (for line-number lookups)
    """
    fmt = detect_format(filepath)
    items: list[dict] = []
    errors: list[dict] = []

    with open(filepath, "r", encoding="utf-8") as fh:
        raw = fh.read()

    raw_lines = raw.splitlines()

    if fmt == "jsonl":
        # ---- JSONL: one JSON object per non-empty line ----
        for lineno, line in enumerate(raw_lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
                obj["__line__"] = lineno
                items.append(obj)
            except json.JSONDecodeError as exc:
                errors.append({
                    "line": lineno,
                    "col": exc.colno,
                    "message": exc.msg,
                    "snippet": stripped[:100],
                })

    else:
        # ---- JSON: single object or array ----
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                data = [data]
            if not isinstance(data, list):
                errors.append({
                    "line": 1, "col": 1,
                    "message": "Top-level JSON is neither an object nor an array.",
                    "snippet": raw[:100],
                })
            else:
                for obj in data:
                    if isinstance(obj, dict):
                        item_id = obj.get("id", "")
                        obj["__line__"] = find_id_line(raw_lines, item_id) if item_id else None
                        items.append(obj)
        except json.JSONDecodeError as exc:
            errors.append({
                "line": exc.lineno,
                "col": exc.colno,
                "message": exc.msg,
                "snippet": raw_lines[exc.lineno - 1][:100] if exc.lineno <= len(raw_lines) else "",
            })

    return items, errors, raw_lines


# ---------------------------------------------------------------------------
# Comparison helpers
# ---------------------------------------------------------------------------

def diff_items(baseline: dict, model: dict) -> list[dict]:
    """
    Return a list of field-level differences between two items.
    Keys in SKIP_COMPARISON_KEYS and internal '__*' keys are ignored.
    """
    all_keys = (set(baseline.keys()) | set(model.keys())) - SKIP_COMPARISON_KEYS
    all_keys = {k for k in all_keys if not k.startswith("__")}

    diffs = []
    for key in sorted(all_keys):
        b_val = baseline.get(key, "<missing>")
        m_val = model.get(key, "<missing>")
        if b_val != m_val:
            diffs.append({"key": key, "baseline": b_val, "model": m_val})
    return diffs


def compute_accuracy(baseline_items: list[dict], model_items: list[dict]) -> dict:
    """
    Compare answer_idx for every id that exists in both files.
    Returns a summary dict including per-item detail.
    """
    b_map = {item["id"]: item for item in baseline_items if "id" in item}
    m_map = {item["id"]: item for item in model_items if "id" in item}

    common_ids = sorted(set(b_map) & set(m_map))
    results = []
    correct = 0

    for item_id in common_ids:
        b_ans = b_map[item_id].get("answer_idx")
        m_ans = m_map[item_id].get("answer_idx")
        is_correct = b_ans == m_ans
        if is_correct:
            correct += 1
        results.append({
            "id": item_id,
            "baseline_answer_idx": b_ans,
            "model_answer_idx": m_ans,
            "correct": is_correct,
        })

    total = len(common_ids)
    return {
        "accuracy": round(correct / total, 4) if total else 0.0,
        "correct": correct,
        "total": total,
        "details": results,
    }


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

W = 72  # output width

def section(title: str, char: str = "=") -> None:
    print(f"\n{char * W}")
    print(f"  {title}")
    print(f"{char * W}")


def fmt_val(value, max_len: int = 72) -> str:
    """Compact single-line representation of any value."""
    s = json.dumps(value, ensure_ascii=False)
    if len(s) > max_len:
        s = s[:max_len - 3] + "..."
    return s


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python compare_answers.py <baseline_file> <model_file>")
        sys.exit(1)

    baseline_path, model_path = sys.argv[1], sys.argv[2]

    for p in (baseline_path, model_path):
        if not os.path.exists(p):
            print(f"Error: File not found — {p}")
            sys.exit(1)

    # Master log dict — populated throughout the script
    log = {
        "timestamp": datetime.now().isoformat(),
        "baseline_file": baseline_path,
        "model_file": model_path,
        "syntax_errors": {"baseline": [], "model": []},
        "id_coverage": {},
        "field_differences": [],
        "accuracy": {},
    }

    # ------------------------------------------------------------------ #
    # STEP 1 — SYNTAX VALIDATION                                          #
    # ------------------------------------------------------------------ #
    section("STEP 1 — SYNTAX VALIDATION")
    print(f"  Baseline : {baseline_path}  [{detect_format(baseline_path).upper()}]")
    print(f"  Model    : {model_path}  [{detect_format(model_path).upper()}]")

    baseline_items, baseline_errors, _ = load_file(baseline_path)
    model_items,    model_errors,    _ = load_file(model_path)

    log["syntax_errors"]["baseline"] = baseline_errors
    log["syntax_errors"]["model"]    = model_errors

    def report_errors(label: str, errors: list[dict], item_count: int) -> None:
        if not errors:
            print(f"\n  ✓  {label}: no syntax errors  ({item_count} item(s) loaded)")
        else:
            print(f"\n  ✗  {label}: {len(errors)} syntax error(s)  "
                  f"({item_count} item(s) loaded before first error)")
            for e in errors:
                print(f"       Line {e['line']}, col {e['col']} — {e['message']}")
                if e.get("snippet"):
                    print(f"         → {e['snippet']}")

    report_errors("Baseline", baseline_errors, len(baseline_items))
    report_errors("Model   ", model_errors,    len(model_items))

    if baseline_errors or model_errors:
        print("\n  ⚠  Fix syntax errors before relying on comparison results.")

    # ------------------------------------------------------------------ #
    # STEP 2 — FIELD COMPARISON  (answer_idx excluded)                   #
    # ------------------------------------------------------------------ #
    section("STEP 2 — FIELD COMPARISON  (answer_idx excluded)")

    b_map = {item["id"]: item for item in baseline_items if "id" in item}
    m_map = {item["id"]: item for item in model_items  if "id" in item}

    only_baseline = sorted(set(b_map) - set(m_map))
    only_model    = sorted(set(m_map) - set(b_map))
    common_ids    = sorted(set(b_map) & set(m_map))

    coverage = {
        "total_baseline": len(b_map),
        "total_model":    len(m_map),
        "common":         len(common_ids),
        "only_in_baseline": only_baseline,
        "only_in_model":    only_model,
    }
    log["id_coverage"] = coverage

    print(f"\n  Baseline items : {len(b_map)}")
    print(f"  Model items    : {len(m_map)}")
    print(f"  Common IDs     : {len(common_ids)}")

    if only_baseline:
        print(f"\n  ⚠  IDs only in baseline ({len(only_baseline)}): "
              + ", ".join(only_baseline))
    if only_model:
        print(f"\n  ⚠  IDs only in model ({len(only_model)}): "
              + ", ".join(only_model))

    all_field_diffs = []

    for item_id in common_ids:
        b_item = b_map[item_id]
        m_item = m_map[item_id]
        diffs  = diff_items(b_item, m_item)

        if diffs:
            line_tag = (f"line ~{m_item['__line__']}"
                        if m_item.get("__line__") else "line unknown")
            print(f"\n  ✗  [{item_id}]  ({line_tag})")
            for d in diffs:
                print(f"       key  '{d['key']}'")
                print(f"         baseline : {fmt_val(d['baseline'])}")
                print(f"         model    : {fmt_val(d['model'])}")

            all_field_diffs.append({
                "id":          item_id,
                "model_line":  m_item.get("__line__"),
                "differences": diffs,
            })

    log["field_differences"] = all_field_diffs

    if not all_field_diffs:
        print(f"\n  ✓  All {len(common_ids)} common item(s) are field-identical "
              f"(answer_idx excluded).")
    else:
        print(f"\n  Summary: {len(all_field_diffs)} / {len(common_ids)} item(s) "
              f"have field differences.")

    # ------------------------------------------------------------------ #
    # STEP 3 — ANSWER_IDX ACCURACY                                        #
    # ------------------------------------------------------------------ #
    section("STEP 3 — ANSWER_IDX ACCURACY")

    acc = compute_accuracy(baseline_items, model_items)
    log["accuracy"] = acc

    print(f"\n  Accuracy : {acc['accuracy']:.4f}   "
          f"({acc['correct']} correct / {acc['total']} compared)")

    wrong = [r for r in acc["details"] if not r["correct"]]
    if wrong:
        print(f"\n  Incorrect predictions ({len(wrong)}):")
        for r in wrong:
            print(f"       [{r['id']}]  "
                  f"baseline={r['baseline_answer_idx']}  "
                  f"model={r['model_answer_idx']}")
    elif acc["total"] > 0:
        print("  ✓  All answer_idx values match!")
    else:
        print("  ⚠  No common IDs to compare.")

    # ------------------------------------------------------------------ #
    # SAVE LOG                                                            #
    # ------------------------------------------------------------------ #
    section("SAVE LOG", char="-")
    try:
        answer = input("\n  Save comparison log to a JSON file? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"

    if answer == "y":
        default_name = (
            f"comparison_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        try:
            filename = input(f"  Filename [{default_name}]: ").strip() or default_name
        except (EOFError, KeyboardInterrupt):
            filename = default_name

        with open(filename, "w", encoding="utf-8") as fh:
            json.dump(log, fh, indent=2, ensure_ascii=False)
        print(f"\n  ✓  Log saved → {filename}")
    else:
        print("\n  Log not saved.")

    print()


if __name__ == "__main__":
    main()
