"""File matching rules for validated and non-validated benchmark outputs."""

from __future__ import annotations

import re
from pathlib import Path

VALID_DATA_SUFFIXES = {".json", ".jsonl"}


def is_data_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VALID_DATA_SUFFIXES


def normalized_benchmark_stem(path: Path) -> str:
    """Return a stable comparison key for benchmark filenames.

    Examples:
    - ``example_v.json`` -> ``example``
    - ``example_export_v.json`` -> ``example``
    - ``example_validated.jsonl`` -> ``example``

    The extension is ignored, so ``.json`` and ``.jsonl`` can still be matched.
    """

    stem = path.stem
    for suffix in ("_export_v", "_validated", "_v"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return stem


def safe_report_name(value: str) -> str:
    """Return a filesystem-safe report basename."""

    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return value.strip("._-") or "comparison"
