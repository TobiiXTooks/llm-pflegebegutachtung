"""Small process/browser helpers for cross-platform workflow execution."""

from __future__ import annotations

import os
import subprocess
import webbrowser
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .paths import PROJECT_ROOT, python_executable


def merged_env(extra: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return a child-process environment with UTF-8 defaults."""

    env = dict(os.environ)
    env.setdefault("PYTHONUTF8", "1")
    if extra:
        env.update(extra)
    return env


def run_command(
    args: Iterable[str | Path],
    cwd: Path = PROJECT_ROOT,
    allowed_exit_codes: Sequence[int] = (0,),
    quiet: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a command without invoking a shell.

    The command is passed as a list, so paths with spaces work on Windows and no
    shell-specific quoting is required. ``allowed_exit_codes`` can be used for
    tools that intentionally return a special non-zero code after still writing
    a useful report.
    """

    command = [str(arg) for arg in args]
    result = subprocess.run(
        command,
        cwd=str(cwd),
        env=merged_env(),
        text=True,
        stdout=subprocess.PIPE if quiet else None,
        stderr=subprocess.STDOUT if quiet else None,
    )
    if result.returncode not in allowed_exit_codes:
        if quiet and result.stdout:
            print(result.stdout)
        raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout)
    return result


def run_python(
    args: Iterable[str | Path],
    cwd: Path = PROJECT_ROOT,
    allowed_exit_codes: Sequence[int] = (0,),
    quiet: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a Python module or script with the current interpreter."""

    return run_command([python_executable(), *args], cwd=cwd, allowed_exit_codes=allowed_exit_codes, quiet=quiet)


def open_in_browser(path_or_url: str | Path) -> None:
    """Open a local file or URL with the OS default browser."""

    value = str(path_or_url)
    if value.startswith(("http://", "https://", "file://")):
        webbrowser.open(value)
        return
    webbrowser.open(Path(value).resolve().as_uri())
