"""Project-wide environment handling for PflegeBench.

This module is intentionally small and dependency-light.  It centralizes .env
loading and runtime checks so legacy GUI/trace scripts do not crash at import
time on Windows, macOS or Linux.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv

from .paths import PROJECT_ROOT

ENV_FILE = PROJECT_ROOT / ".env"
ENV_EXAMPLE_FILE = PROJECT_ROOT / ".env.example"


def load_project_env() -> None:
    """Load .env from the repository root if it exists.

    The current working directory is intentionally ignored.  This makes behavior
    identical whether the user starts a command from PowerShell, Terminal, an
    IDE, or through ``python -m pflegebench``.
    """

    load_dotenv(ENV_FILE, override=False)


def get_env(name: str, default: str | None = None) -> str | None:
    """Return one environment variable after loading the project .env."""

    load_project_env()
    value = os.getenv(name, default)
    if value is not None and value.strip() == "":
        return default
    return value


def missing_env(names: Iterable[str]) -> list[str]:
    """Return configured variable names that are not set or are empty."""

    load_project_env()
    return [name for name in names if not os.getenv(name)]


def require_env(name: str, purpose: str) -> str:
    """Return a required variable or raise a user-facing RuntimeError."""

    value = get_env(name)
    if value:
        return value

    example_hint = ""
    if ENV_EXAMPLE_FILE.exists():
        example_hint = f"\nVorlage: {ENV_EXAMPLE_FILE}"

    raise RuntimeError(
        f"Fehlende Umgebungsvariable: {name}\n"
        f"Benötigt für: {purpose}\n"
        f"Lege im Projektordner eine .env-Datei an oder setze die Variable im System.{example_hint}\n"
        f"Beispiel unter Windows PowerShell:\n"
        f"  Copy-Item .env.example .env\n"
        f"  notepad .env"
    )


def require_openrouter_api_key() -> str:
    """Return OPENROUTER_API_KEY or raise a clear runtime error."""

    return require_env("OPENROUTER_API_KEY", "OpenRouter-Modellaufrufe")


def langfuse_configured() -> bool:
    """Return True if the minimum Langfuse credential set is present."""

    return not missing_env(["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"])


def openrouter_configured() -> bool:
    """Return True if OpenRouter can be used."""

    return not missing_env(["OPENROUTER_API_KEY"])
