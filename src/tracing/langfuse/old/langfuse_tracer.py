import os
import time
import requests
from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = "openai/gpt-4o-mini"

langfuse = get_client()


def _render_template(template: str, variables: dict) -> str:
    for key, value in variables.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template


def _call_openrouter(messages: list, model: str) -> tuple:
    start = time.time()
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={"model": model, "messages": messages}
    )
    latency_ms = round((time.time() - start) * 1000, 2)
    data = response.json()
    return data, latency_ms


class Conversation:
    def __init__(self, model: str = DEFAULT_MODEL, session_id: str = None):
        self.model = model
        self.messages = []
        self.turn_count = 0
        self.session_id = session_id

    def turn(
        self,
        prompt_template: str,
        variables: dict = {},
        model: str = None
    ) -> tuple:
        model = model or self.model
        self.turn_count += 1
        rendered = _render_template(prompt_template, variables)
        self.messages.append({"role": "user", "content": rendered})

        trace_id = None

        # One Langfuse trace per turn, linked by session_id
        with langfuse.start_as_current_observation(
            as_type="span",
            name=f"conversation-turn-{self.turn_count}",
            session_id=self.session_id,
            input=self.messages[:-1],
            metadata={
                "prompt_template": prompt_template,
                "variables": variables,
                "prompt_rendered": rendered,
                "turn": self.turn_count
            }
        ) as span:

            trace_id = span.trace_id

            # Nested generation for the actual LLM call
            with langfuse.start_as_current_observation(
                as_type="generation",
                name="openrouter-call",
                model=model,
                input=self.messages
            ) as generation:

                data, latency_ms = _call_openrouter(self.messages, model)
                assistant_message = data["choices"][0]["message"]["content"]

                generation.update(
                    output=assistant_message,
                    usage={
                        "input": data["usage"]["prompt_tokens"],
                        "output": data["usage"]["completion_tokens"],
                        "total": data["usage"]["total_tokens"]
                    },
                    metadata={
                        "provider": data.get("provider"),
                        "finish_reason": data["choices"][0]["finish_reason"],
                        "latency_ms": latency_ms,
                        "cost_usd": data["usage"]["cost"]
                    }
                )

            span.update(output=assistant_message)

        self.messages.append({"role": "assistant", "content": assistant_message})
        return assistant_message, trace_id


def single_turn(
    prompt_template: str,
    variables: dict = {},
    model: str = DEFAULT_MODEL
) -> tuple:
    conv = Conversation(model=model)
    return conv.turn(prompt_template, variables)