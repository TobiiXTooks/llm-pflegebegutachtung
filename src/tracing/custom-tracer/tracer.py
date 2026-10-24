import os
import json
import time
import uuid
import hashlib
import requests
from datetime import datetime, timezone
from config import OPENROUTER_API_KEY, TRACES_DIR, FILES_DIR, DEFAULT_MODEL

os.makedirs(TRACES_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)


def _render_template(template: str, variables: dict) -> str:
    for key, value in variables.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template


def _store_file(file_path: str) -> dict:
    with open(file_path, "rb") as f:
        content = f.read()
    checksum = hashlib.sha256(content).hexdigest()
    dest = os.path.join(FILES_DIR, checksum)
    if not os.path.exists(dest):
        with open(dest, "wb") as f:
            f.write(content)
    return {
        "original_filename": os.path.basename(file_path),
        "checksum": checksum,
        "size_bytes": len(content)
    }


def _write_trace(trace: dict):
    filename = f"{trace['timestamp'].replace(':', '-').replace('.', '-')}_{trace['trace_id']}.json"
    path = os.path.join(TRACES_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False, sort_keys=True)
    print(f"Trace written to {path}")


class Conversation:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.conversation_id = str(uuid.uuid4())
        self.model = model
        self.messages = []
        self.turn_count = 0

    def turn(
        self,
        prompt_template: str,
        variables: dict = {},
        file_paths: list = [],
        model: str = None
    ) -> str:
        model = model or self.model
        self.turn_count += 1
        rendered = _render_template(prompt_template, variables)

        # Handle attachments
        attachments = [_store_file(fp) for fp in file_paths]

        # Build message history
        self.messages.append({"role": "user", "content": rendered})

        # Call OpenRouter
        start = time.time()
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": self.messages
            }
        )
        latency_ms = round((time.time() - start) * 1000, 2)

        data = response.json()
        print(data)
        assistant_message = data["choices"][0]["message"]["content"]

        # Add assistant response to history
        self.messages.append({"role": "assistant", "content": assistant_message})

        # Build trace
        trace = {
            "trace_id": data["id"],
            "conversation_id": self.conversation_id,
            "turn": self.turn_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": data["model"],
            "provider": data.get("provider"),
            "prompt_template": prompt_template,
            "variables": variables,
            "prompt_rendered": rendered,
            "messages": self.messages[:-1],  # history sent to model
            "response": assistant_message,
            "finish_reason": data["choices"][0]["finish_reason"],
            "input_tokens": data["usage"]["prompt_tokens"],
            "output_tokens": data["usage"]["completion_tokens"],
            "total_tokens": data["usage"]["total_tokens"],
            "cost_usd": data["usage"]["cost"],
            "latency_ms": latency_ms,
            "attachments": attachments,
            "trace_version": "1.0"
        }

        _write_trace(trace)
        return assistant_message


def single_turn(
    prompt_template: str,
    variables: dict = {},
    file_paths: list = [],
    model: str = DEFAULT_MODEL
) -> str:
    conv = Conversation(model=model)
    return conv.turn(prompt_template, variables, file_paths)
