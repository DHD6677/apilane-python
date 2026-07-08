# apilane — Python SDK

[![PyPI](https://img.shields.io/badge/pypi-coming--soon-yellow)](https://pypi.org/project/apilane/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-21%2F21%20passing-brightgreen)](tests/)

**The cheapest way to call GPT-4o, Claude, and DeepSeek. Pay per call from $2. Crypto accepted.**

This is the official Python client for [apilane](https://apilane.one) — a unified LLM API gateway that gives you one API key, one `base_url`, and access to every major model at a fraction of the official price.

```bash
pip install apilane
```

```python
from apilane import Apilane

client = Apilane(api_key="sk-...")
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(resp.choices[0].message.content)
```

That's it. Same interface as the official `openai` SDK — switch by changing the import and the `api_key`.

---

## Why apilane?

| What | Why it matters |
|------|----------------|
| **One key, every model** | GPT-4o, Claude, DeepSeek, GLM, Kimi — same client, same code. |
| **1/10 to 1/60 official price** | Pay per call from $2. Same response, audited upstream. |
| **Crypto billing** | USDT (TRC20/BSC/ERC20) and BTC. No card required. |
| **Open-source client** | This SDK is on GitHub — read every line, no hidden data exfiltration. |
| **Drop-in for `openai` SDK** | Same method names. Migrate in 60 seconds. |

---

## Quickstart

### 1. Install

```bash
pip install apilane
```

Requires Python 3.9 or later. Two dependencies only: `httpx` and `pydantic`.

### 2. Get an API key

Sign up at [apilane.one](https://apilane.one), top up with USDT or BTC, and create a key in the dashboard. New accounts start with a $2 minimum.

### 3. Make your first call

```python
import os
from apilane import Apilane

client = Apilane(api_key=os.environ["APILANE_API_KEY"])

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Say hi in one short sentence."}],
)
print(resp.choices[0].message.content)
print("Tokens used:", resp.usage.total_tokens)
```

### 4. Or use any other model — same code

```python
# Claude
client.chat.completions.create(model="claude-3-5-sonnet", messages=...)

# DeepSeek
client.chat.completions.create(model="deepseek-chat", messages=...)

# GLM
client.chat.completions.create(model="glm-4-plus", messages=...)
```

List everything available:

```python
models = client.models.list()
for m in models.data:
    print(m.id)
```

---

## Examples

### 1. Basic chat

```python
from apilane import Apilane

client = Apilane(api_key="sk-...")

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
    temperature=0.2,
    max_tokens=100,
)
print(resp.choices[0].message.content)
```

See [`examples/01_chat.py`](examples/01_chat.py).

### 2. Streaming responses (SSE)

```python
from apilane import Apilane

client = Apilane(api_key="sk-...")

stream = client.chat.completions.create(
    model="claude-3-5-sonnet",
    messages=[{"role": "user", "content": "Write a haiku about programming."}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()
```

See [`examples/02_stream.py`](examples/02_stream.py).

### 3. Vision (multimodal)

```python
from apilane import Apilane

client = Apilane(api_key="sk-...")

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image? Be brief."},
            {
                "type": "image_url",
                "image_url": {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/640px-Cat03.jpg"},
            },
        ],
    }
]

resp = client.chat.completions.create(model="gpt-4o", messages=messages)
print(resp.choices[0].message.content)
```

See [`examples/03_vision.py`](examples/03_vision.py). Works with any vision-capable model — `gpt-4o`, `claude-3-5-sonnet`, `glm-4v-plus`, etc.

### 4. Tool calling (function calling)

```python
import json
from apilane import Apilane

client = Apilane(api_key="sk-...")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["city"],
            },
        },
    }
]

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto",
)

msg = resp.choices[0].message
if msg.tool_calls:
    call = msg.tool_calls[0]
    args = json.loads(call.function.arguments)
    print("Model wants to call:", call.function.name, "with", args)
    # ... your function here ...
else:
    print(msg.content)
```

See [`examples/04_tool_call.py`](examples/04_tool_call.py).

### 5. Batch (async, many calls concurrently)

```python
import asyncio
from apilane import AsyncApilane

async def main():
    async with AsyncApilane(api_key="sk-...") as client:
        prompts = [
            "Translate 'hello' to French.",
            "Translate 'hello' to Japanese.",
            "Translate 'hello' to Spanish.",
        ]
        tasks = [
            client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": p}],
                max_tokens=30,
            )
            for p in prompts
        ]
        results = await asyncio.gather(*tasks)
        for prompt, r in zip(prompts, results):
            print(f"{prompt} -> {r.choices[0].message.content}")

asyncio.run(main())
```

See [`examples/05_batch.py`](examples/05_batch.py).

---

## API reference

### `Apilane(api_key=None, base_url=None, timeout=None, max_retries=2, ...)`

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_key` | `$APILANE_API_KEY` | Your apilane key. Falls back to env var. |
| `base_url` | `https://api.apilane.one/v1` | Override for self-hosted or testing. |
| `timeout` | `60.0` | Per-request timeout in seconds. |
| `max_retries` | `2` | Retries on 408/409/429/5xx. |
| `default_headers` | `None` | Extra headers sent on every request. |
| `default_query` | `None` | Extra query params sent on every request. |
| `http_client` | `None` | Inject your own `httpx.Client` (e.g. for proxies). |

Async equivalent: `AsyncApilane` — same params, all methods are `async`.

### `client.chat.completions.create(...)`

Mirrors the OpenAI Chat Completions API. Supports `model`, `messages`, `stream`, `temperature`, `top_p`, `max_tokens`, `tools`, `tool_choice`, `stop`, `n`, `presence_penalty`, `frequency_penalty`, `user`, and any other provider-specific fields via `**kwargs`.

Returns a [`ChatCompletion`](#types) or an iterator (sync) / async iterator (async) of `ChatCompletionChunk` when `stream=True`.

### `client.models.list()`

Returns a `ModelList` of all models your key can use.

### `client.models.retrieve(model: str)`

Returns a single `Model` by id.

### Types

- `ChatCompletion` / `ChatCompletionChunk` — pydantic models with `id`, `model`, `choices`, `usage`, `system_fingerprint`.
- `Choice` — `index`, `message` (or `delta` for chunks), `finish_reason`.
- `ChatCompletionMessage` — `role`, `content`, `tool_calls`, `tool_call_id`, `refusal`.
- `Model` — `id`, `object`, `created`, `owned_by`.
- `ModelList` — `object`, `data: list[Model]`.

### Exceptions

| Class | Status |
|-------|--------|
| `apilane.ApilaneError` | Base. |
| `apilane.APIError` | Any non-success response. |
| `apilane.AuthenticationError` | 401. |
| `apilane.RateLimitError` | 429. |
| `apilane.BadRequestError` | 4xx. |
| `apilane.APIStatusError` | 5xx or unknown. |
| `apilane.APIConnectionError` | Network failure (after all retries). |

All status errors expose `.status_code`, `.response`, `.body`, `.request`.

---

## Environment variables

| Variable | Equivalent |
|----------|------------|
| `APILANE_API_KEY` | `Apilane(api_key=...)` |

---

## Migrating from `openai`

```diff
-from openai import OpenAI
+from apilane import Apilane

-client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
+client = Apilane(api_key=os.environ["APILANE_API_KEY"])

 resp = client.chat.completions.create(model="gpt-4o", messages=[...])
```

The interface is intentionally identical. The only changes are: the import name, the class name, and the `api_key` value. Everything else — methods, parameters, return types — stays the same.

---

## Development

```bash
git clone https://github.com/apilane/apilane-python
cd apilane-python
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest tests/ -v
```

All tests use mocked `httpx` transports — no network calls, no real API keys needed.

---

## License

MIT — see [LICENSE](LICENSE).

## Links

- Website: https://apilane.one
- Docs: https://apilane.one/docs
- Pricing: https://apilane.one/pricing
- Status: https://stats.uptimerobot.com/dFPmjei6XoV/
- Issues: https://github.com/apilane/apilane-python/issues
