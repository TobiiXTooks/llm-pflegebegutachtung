from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pflegebench.env import get_env, load_project_env

load_project_env()

OPENROUTER_API_KEY = get_env("OPENROUTER_API_KEY")
TRACES_DIR = str(Path(__file__).resolve().parent / "traces")
FILES_DIR = str(Path(__file__).resolve().parent / "files")
DEFAULT_MODEL = "openai/gpt-4o-mini"
