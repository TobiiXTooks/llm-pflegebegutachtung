# PflegeBench — LLM Conversation Tracker

Track multi-turn LLM conversations via OpenRouter, traced in Langfuse, exported to JSON for reproducibility and peer review.

## Setup

```bash
pip install langfuse requests python-dotenv
```

Create a `.env` file in the project folder:

```
OPENROUTER_API_KEY=...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Add `.env` to `.gitignore` — never commit API keys. Use `.env.example` with empty values as a template for collaborators.

## Usage

```bash
python conversation.py --model <openrouter-model-id>
```

The model ID must be an exact OpenRouter slug. Find available models at https://openrouter.ai/models.

Examples:
```bash
python conversation.py --model google/gemini-2.5-pro-preview
python conversation.py --model anthropic/claude-sonnet-4-5
python conversation.py --model meta-llama/llama-3.3-70b-instruct
```

## Slash Commands

| Command | Effect |
|---|---|
| `/pdf <url>` | Queue a PDF (cloudflare-ai engine, free) to attach to your next message |
| `/pdf <url> mistral-ocr` | Queue a PDF with Mistral OCR engine ($2 / 1000 pages, better for complex PDFs) |
| `/pdf <url> native` | Queue a PDF using the model's native file support (if available) |
| `/new` | End current conversation, export it, start a new one (same model) |
| `/model <id>` | End current conversation, export it, start a new one with a different model |
| `/done` | End current conversation, export it, exit the script |
| `/help` | Show available commands |

### PDF attachment flow

`/pdf` queues the file — nothing is sent yet. The input prompt changes to show the attachment is pending:

```
You [guideline.pdf, cloudflare-ai]: Summarize section 3 on risk assessment
```

The PDF is bundled with your next message and the queue clears. If the API call fails the PDF is automatically re-queued so you can retry without re-typing the URL.

## Output

Each finished conversation is fetched from Langfuse and saved to `traces/`:

```
traces/
└── 20250529T142301Z_google_gemini-2.5-pro-preview_a1b2c3d4.json
```

Filename format: `<UTC-timestamp>_<model-slug>_<trace-id-prefix>.json`

The JSON contains the full Langfuse trace and all observations (one per turn):

```json
{
  "trace": { ... },
  "observations": [
    { "name": "turn-1", "type": "GENERATION", "input": "...", "output": "...", "usage": { ... } },
    { "name": "turn-2", ... }
  ]
}
```

Commit the `traces/` folder to Git as a scientific record of how synthetic data was generated.

## Data Model

```
Root span (one per conversation)
├── metadata: project, model, started_at
├── Generation: turn-1  ← full message history sent, model response, token usage
├── Generation: turn-2
└── ...
```

One conversation = one model = one trace = one JSON file.

## Project Structure

```
pflegebench/
├── config.py          # API keys, constants, retry settings
├── conversation.py    # Main script
├── traces/            # Auto-created, JSON exports land here (commit to Git)
├── .env               # API keys — never commit
└── .env.example       # Empty template for collaborators
```