"""Repository path helpers used by all workflow commands.

All paths are built with :class:`pathlib.Path` and are therefore portable across
Windows, macOS and Linux. No command in the workflow layer depends on POSIX-only
syntax, shell quoting, or path separators.
"""

from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
BENCHMARK_DIR = DATA_DIR / "benchmark"
DOCS_DIR = PROJECT_ROOT / "docs"
REPORTS_DIR = PROJECT_ROOT / "reports"
LEGACY_SRC_DIR = PROJECT_ROOT / "src"


def resolve_repo_path(path: str | Path) -> Path:
    """Resolve a user-supplied path relative to the repository root.

    Absolute paths are returned unchanged. Relative paths are interpreted from
    the project root, not from the current terminal directory. This keeps command
    behavior stable on all operating systems and from all shells.
    """

    value = Path(path).expanduser()
    if value.is_absolute():
        return value
    return PROJECT_ROOT / value


def python_executable() -> str:
    """Return the exact interpreter that is currently running the workflow."""

    return sys.executable
