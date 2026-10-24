from __future__ import annotations

import sys
from pathlib import Path

# Allow this legacy script folder to be executed directly without requiring the
# user to manually set PYTHONPATH. The canonical entry point remains
# ``python -m pflegebench trace``.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pflegebench.env import get_env, load_project_env, require_openrouter_api_key

load_project_env()

# Optional at import time. Runtime calls must use require_openrouter_api_key().
OPENROUTER_API_KEY = get_env("OPENROUTER_API_KEY")

# Traces are stored beside this tracing tool, independent of the shell cwd.
TRACES_DIR = str(Path(__file__).resolve().parent / "traces")

FETCH_MAX_RETRIES = 10
FETCH_RETRY_DELAY_SECONDS = 3
PROJECT_NAME = "PflegeBench"
