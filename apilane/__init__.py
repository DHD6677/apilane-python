"""apilane — Official Python SDK.

The cheapest way to call GPT-4o, Claude, and DeepSeek.
Pay per call from $2. Crypto accepted.

Quickstart::

    from apilane import Apilane

    client = Apilane(api_key="sk-...")
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}],
    )
    print(resp.choices[0].message.content)
"""
from .client import Apilane, AsyncApilane
from .types import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
    Choice,
    Model,
    ModelList,
)
from ._exceptions import (
    ApilaneError,
    APIError,
    APIStatusError,
    APIConnectionError,
    AuthenticationError,
    RateLimitError,
)

from ._version import __version__
__all__ = [
    "Apilane",
    "AsyncApilane",
    "ChatCompletion",
    "ChatCompletionChunk",
    "ChatCompletionMessage",
    "Choice",
    "Model",
    "ModelList",
    "ApilaneError",
    "APIError",
    "APIStatusError",
    "APIConnectionError",
    "AuthenticationError",
    "RateLimitError",
]

DEFAULT_BASE_URL = "https://api.apilane.one/v1"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2
