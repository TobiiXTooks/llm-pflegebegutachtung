"""
PflegeBench — multi-turn LLM conversation tracker
Usage: python conversation.py --model <openrouter-model-id>
Example: python conversation.py --model google/gemini-2.5-pro
"""

import argparse
import json
import os
import sys
import time
from contextlib import nullcontext
from datetime import UTC, datetime
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import requests as http
from langfuse import get_client, propagate_attributes as _langfuse_propagate_attributes
from pflegebench.env import langfuse_configured

from config import (
    FETCH_MAX_RETRIES,
    FETCH_RETRY_DELAY_SECONDS,
    require_openrouter_api_key,
    PROJECT_NAME,
    TRACES_DIR,
)

# ---------------------------------------------------------------------------
# Langfuse client
# ---------------------------------------------------------------------------


class _NoOpObservation:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def update(self, *args, **kwargs):
        return None


class _NoOpLangfuseClient:
    def start_as_current_observation(self, *args, **kwargs):
        return _NoOpObservation()

    def get_current_trace_id(self):
        return "local-no-langfuse"

    def flush(self):
        return None


def _get_langfuse_client():
    if not langfuse_configured():
        return _NoOpLangfuseClient()
    try:
        return get_client()
    except Exception:
        return _NoOpLangfuseClient()


def propagate_attributes(*args, **kwargs):
    if not langfuse_configured():
        return nullcontext()
    return _langfuse_propagate_attributes(*args, **kwargs)


langfuse = _get_langfuse_client()

# ---------------------------------------------------------------------------
# OpenRouter — single raw requests session for all calls
# Avoids OpenAI SDK mangling non-standard fields like 'plugins'
# ---------------------------------------------------------------------------

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_ENGINES = {"cloudflare-ai", "mistral-ocr", "native"}
DEFAULT_ENGINE = "cloudflare-ai"

HELP_TEXT = """
┌──────────────────────────────────────────────────────────────┐
│  PflegeBench slash commands                                  │
│                                                              │
│  /pdf <url>                attach PDF (cloudflare-ai, free)  │
│  /pdf <url> mistral-ocr    attach PDF with mistral-ocr       │
│  /pdf <url> native         attach PDF with native engine     │
│  /new                      end conversation, start new one   │
│  /model <id>               end conversation, switch model,   │
│                            start new conversation            │
│  /done                     end conversation, exit script     │
│  /help                     show this message                 │
└──────────────────────────────────────────────────────────────┘
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_separator(label: str = ""):
    width = 60
    if label:
        pad = (width - len(label) - 2) // 2
        print("\n" + "─" * pad + f" {label} " + "─" * pad + "\n")
    else:
        print("\n" + "─" * width + "\n")


def fetch_trace_with_retry(trace_id: str) -> dict:
    """Poll Langfuse until the trace is available, then return it as a dict."""
    if not langfuse_configured():
        print("  Langfuse is not configured — skipping remote trace export")
        return {}
    print("  Waiting for Langfuse to ingest trace", end="", flush=True)
    for _ in range(FETCH_MAX_RETRIES):
        try:
            trace = langfuse.api.trace.get(trace_id)
            observations = langfuse.api.observations.get_many(
                trace_id=trace_id,
                fields="core,basic,usage",
                limit=100,
            )
            print(" ✓")
            return {
                "trace": trace.dict(),
                "observations": [o.dict() for o in observations.data],
            }
        except Exception:
            print(".", end="", flush=True)
            time.sleep(FETCH_RETRY_DELAY_SECONDS)

    print(" ✗ (timed out)")
    return {}


def save_trace_to_file(trace_data: dict, trace_id: str, model: str):
    """Write trace JSON to the traces/ folder."""
    os.makedirs(TRACES_DIR, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    model_slug = model.replace("/", "_").replace(":", "_")
    filename = f"{timestamp}_{model_slug}_{trace_id[:8]}.json"
    filepath = os.path.join(TRACES_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, indent=2, default=str)
    print(f"  Saved → traces/{filename}")
    return filepath


# ---------------------------------------------------------------------------
# OpenRouter API call
# Always uses raw requests so payload structure is exact.
# Per OpenRouter docs (Python example): messages + optional plugins at top level.
# PDF URL is passed as file_data (string URL, not base64).
# ---------------------------------------------------------------------------

def call_model(model: str, messages: list, pdf_engine: str | None = None) -> tuple[str, int, int]:
    """
    Call OpenRouter. If pdf_engine is set, adds the plugins parameter.
    Returns (content, input_tokens, output_tokens).
    """
    payload: dict = {
        "model": model,
        "messages": messages,
    }

    if pdf_engine is not None:
        payload["plugins"] = [
            {
                "id": "file-parser",
                "pdf": {"engine": pdf_engine},
            }
        ]

    api_key = require_openrouter_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = http.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload))

    data = resp.json()

    if "error" in data:
        raise RuntimeError(f"OpenRouter error {resp.status_code}: {data['error'].get('message', str(data['error']))}")

    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return (
        content,
        usage.get("prompt_tokens", 0),
        usage.get("completion_tokens", 0),
    )


def build_user_message(text: str, queued_pdf: dict | None) -> dict:
    """
    Build a user message. If a PDF is queued, use the structured file content
    block as shown in OpenRouter docs. file_data accepts a URL string directly.
    """
    if queued_pdf:
        return {
            "role": "user",
            "content": [
                {"type": "text", "text": text},
                {
                    "type": "file",
                    "file": {
                        "filename": queued_pdf["filename"],
                        "file_data": queued_pdf["url"],   # plain URL per OpenRouter docs
                    },
                },
            ],
        }
    return {"role": "user", "content": text}


# ---------------------------------------------------------------------------
# Core conversation loop
# ---------------------------------------------------------------------------

def run_conversation(model: str):
    """
    Run a single multi-turn conversation with the given model.
    Returns the slash command that ended it: 'new', 'model:<id>', or 'done'.
    """
    messages = []
    turn_number = 0
    queued_pdf: dict | None = None  # {url, filename, engine}

    print_separator(f"New conversation · {model}")
    print("  Type /help for commands\n")

    # Outer span = the full conversation trace
    # Per Langfuse docs: start_as_current_observation with no as_type = span (root)
    with langfuse.start_as_current_observation(
        name=f"{PROJECT_NAME}-conversation",
        input={"model": model},
    ) as root_span:
        trace_id = langfuse.get_current_trace_id()

        # propagate_attributes: pushes metadata/tags to all child observations
        # Per docs: accepts user_id, session_id, tags, metadata, version, release
        with propagate_attributes(
            tags=[PROJECT_NAME],
            metadata={
                "model": model,
                "started_at": datetime.now(UTC).isoformat(),
            },
        ):
            exit_command = "done"

            while True:
                # Show PDF hint in prompt if one is queued
                if queued_pdf:
                    prompt = f"You [{queued_pdf['filename']}, {queued_pdf['engine']}]: "
                else:
                    prompt = "You: "

                try:
                    user_input = input(prompt).strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n  Interrupted — finishing conversation.")
                    exit_command = "done"
                    break

                # ── Slash commands ──────────────────────────────────────────
                if user_input.startswith("/"):
                    parts = user_input.split(maxsplit=2)
                    cmd = parts[0].lower()

                    if cmd == "/help":
                        print(HELP_TEXT)
                        continue

                    elif cmd == "/pdf":
                        if len(parts) < 2 or not parts[1].strip():
                            print("  Usage: /pdf <url> [mistral-ocr|native]")
                            continue
                        url = parts[1].strip()
                        engine = DEFAULT_ENGINE
                        if len(parts) == 3:
                            requested = parts[2].strip().lower()
                            if requested not in VALID_ENGINES:
                                print(f"  Unknown engine '{requested}'. Valid: {', '.join(sorted(VALID_ENGINES))}")
                                continue
                            engine = requested
                        filename = url.rstrip("/").split("/")[-1]
                        if not filename.lower().endswith(".pdf"):
                            filename += ".pdf"
                        queued_pdf = {"url": url, "filename": filename, "engine": engine}
                        print(f"  [{filename}, {engine}]")
                        continue

                    elif cmd == "/new":
                        exit_command = "new"
                        break

                    elif cmd == "/done":
                        exit_command = "done"
                        break

                    elif cmd == "/model":
                        if len(parts) < 2 or not parts[1].strip():
                            print("  Usage: /model <openrouter-model-id>")
                            continue
                        exit_command = f"model:{parts[1].strip()}"
                        break

                    else:
                        print(f"  Unknown command '{cmd}'. Type /help for options.")
                        continue

                # ── Normal turn ─────────────────────────────────────────────
                if not user_input:
                    continue

                turn_number += 1
                attached_pdf = queued_pdf
                queued_pdf = None

                user_message = build_user_message(user_input, attached_pdf)
                messages.append(user_message)

                # Per Langfuse docs: nested generation inside root span
                with langfuse.start_as_current_observation(
                    as_type="generation",
                    name=f"turn-{turn_number}",
                    model=model,
                    input=messages,
                ) as gen:
                    try:
                        content, input_tok, output_tok = call_model(
                            model=model,
                            messages=messages,
                            pdf_engine=attached_pdf["engine"] if attached_pdf else None,
                        )
                        gen.update(
                            output=content,
                            usage_details={
                                "input": input_tok,
                                "output": output_tok,
                            },
                        )
                    except Exception as e:
                        print(f"\n  ⚠ API error: {e}\n")
                        messages.pop()
                        turn_number -= 1
                        queued_pdf = attached_pdf  # re-queue for retry
                        continue

                messages.append({"role": "assistant", "content": content})
                print(f"\nModel: {content}\n")

        root_span.update(output={"turns": turn_number})

    # ── Export ───────────────────────────────────────────────────────────────
    if turn_number > 0:
        print_separator("Exporting")
        langfuse.flush()
        trace_data = fetch_trace_with_retry(trace_id)
        if trace_data:
            save_trace_to_file(trace_data, trace_id, model)
    else:
        print("  (empty conversation — nothing exported)")

    return exit_command


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="PflegeBench — tracked LLM conversation via OpenRouter"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="OpenRouter model ID, e.g. google/gemini-2.5-pro",
    )
    args = parser.parse_args()
    current_model = args.model

    print(f"\n  PflegeBench · starting with model: {current_model}")
    print("  Type /help at any time for commands\n")

    while True:
        result = run_conversation(current_model)
        if result == "done":
            print("\n  Goodbye.\n")
            break
        elif result == "new":
            continue
        elif result.startswith("model:"):
            current_model = result.split(":", 1)[1]
            print(f"\n  Switching to model: {current_model}")


if __name__ == "__main__":
    main()