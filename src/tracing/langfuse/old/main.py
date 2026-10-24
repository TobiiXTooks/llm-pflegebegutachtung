import os
import json
import time
from langfuse import get_client
from langfuse_tracer import single_turn, Conversation

os.makedirs("traces", exist_ok=True)

langfuse = get_client()


def export_trace(trace_id: str):
    # Langfuse needs a moment to process before querying
    time.sleep(5)

    observations = langfuse.api.observations.get_many(
        trace_id=trace_id,
        fields="core,basic,usage"
    )

    trace = {
        "trace_id": trace_id,
        "observations": [o.dict() for o in observations.data]
    }

    path = f"traces/{trace_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False, sort_keys=True)

    print(f"Trace exported to {path}")


# Single turn
response, trace_id = single_turn(
    prompt_template="Translate to French: {{text}}",
    variables={"text": "Hello, how are you?"}
)
print(response)

langfuse.flush()
export_trace(trace_id)

# Multi turn
conv = Conversation(session_id="test-session-001")

conv.turn(
    prompt_template="My name is {{name}}.",
    variables={"name": "Alex"}
)
response, trace_id = conv.turn(
    prompt_template="{{question}}",
    variables={"question": "What is my name?"}
)
print(response)

langfuse.flush()
export_trace(trace_id)