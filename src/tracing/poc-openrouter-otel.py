from __future__ import annotations

import sys
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pflegebench.env import require_openrouter_api_key

OPENROUTER_API_KEY = require_openrouter_api_key()
MODEL = "openai/gpt-4o-mini"  # cheap model for testing

# Step 1 — Send a prompt
response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "Say hello in one sentence."}
        ],
    },
    timeout=120,
)

completion = response.json()
print("=== COMPLETION RESPONSE ===")
print(completion)

# Step 2 — Query the generation endpoint
generation_id = completion["id"]

# Small delay — generation endpoint needs a moment to populate
time.sleep(10)

generation = requests.get(
    url=f"https://openrouter.ai/api/v1/generation?id={generation_id}",
    headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
    timeout=120,
)

print("\n=== GENERATION RESPONSE ===")
print(generation.json())
