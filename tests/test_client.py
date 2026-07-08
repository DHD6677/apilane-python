from __future__ import annotations

import json
from typing import Any, Dict, List

import httpx
import pytest

import apilane
from apilane import Apilane, AsyncApilane
from apilane._exceptions import (
    APIError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
)


def _make_response(status_code: int, json_body: Any = None, text: str = "") -> httpx.Response:
    request = httpx.Request("POST", "https://api.apilane.one/v1/chat/completions")
    if json_body is not None:
        content = json.dumps(json_body).encode("utf-8")
        headers = {"content-type": "application/json"}
    else:
        content = text.encode("utf-8")
        headers = {"content-type": "text/plain"}
    return httpx.Response(status_code, content=content, headers=headers, request=request)


class _MockTransport(httpx.BaseTransport):
    def __init__(self, responses: List[httpx.Response]):
        self.responses = list(responses)
        self.calls: List[httpx.Request] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        if not self.responses:
            return _make_response(500, {"error": {"message": "no mock left"}})
        return self.responses.pop(0)


def _client(transport: _MockTransport, **kwargs: Any) -> Apilane:
    http_client = httpx.Client(transport=transport)
    return Apilane(api_key="sk-test", http_client=http_client, max_retries=0, **kwargs)


def test_init_requires_api_key():
    import os
    os.environ.pop("APILANE_API_KEY", None)
    with pytest.raises(ValueError, match="api_key"):
        Apilane()


def test_init_reads_env_var(monkeypatch):
    monkeypatch.setenv("APILANE_API_KEY", "sk-from-env")
    c = Apilane()
    assert c.api_key == "sk-from-env"


def test_default_base_url():
    transport = _MockTransport([])
    c = _client(transport)
    assert c.base_url == "https://api.apilane.one/v1"


def test_chat_completion_create_basic():
    payload = {
        "id": "chatcmpl-1",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
    }
    transport = _MockTransport([_make_response(200, payload)])
    c = _client(transport)
    resp = c.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hi"}],
    )
    assert isinstance(resp, apilane.ChatCompletion)
    assert resp.choices[0].message.content == "Hello!"
    assert resp.usage.total_tokens == 8

    sent = transport.calls[0]
    assert sent.method == "POST"
    assert str(sent.url) == "https://api.apilane.one/v1/chat/completions"
    assert sent.headers["authorization"] == "Bearer sk-test"
    body = json.loads(sent.content)
    assert body["model"] == "gpt-4o"
    assert body["messages"] == [{"role": "user", "content": "Hi"}]
    assert body["stream"] is False


def test_chat_completion_create_optional_params():
    payload = {
        "id": "x", "object": "chat.completion", "created": 1, "model": "gpt-4o",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
    }
    transport = _MockTransport([_make_response(200, payload)])
    c = _client(transport)
    c.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hi"}],
        temperature=0.5,
        top_p=0.9,
        max_tokens=128,
        stop=["END"],
        user="u-1",
    )
    body = json.loads(transport.calls[0].content)
    assert body["temperature"] == 0.5
    assert body["max_tokens"] == 128
    assert body["stop"] == ["END"]
    assert body["user"] == "u-1"


def test_chat_completion_create_omits_none_optional():
    payload = {
        "id": "x", "object": "chat.completion", "created": 1, "model": "m",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
    }
    transport = _MockTransport([_make_response(200, payload)])
    c = _client(transport)
    c.chat.completions.create(model="m", messages=[{"role": "user", "content": "Hi"}])
    body = json.loads(transport.calls[0].content)
    assert "temperature" not in body
    assert "max_tokens" not in body
    assert "tools" not in body


def test_chat_completion_create_vision_multimodal():
    payload = {
        "id": "x", "object": "chat.completion", "created": 1, "model": "gpt-4o",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "A cat"}, "finish_reason": "stop"}],
    }
    transport = _MockTransport([_make_response(200, payload)])
    c = _client(transport)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "https://example.com/cat.png"}},
            ],
        }
    ]
    resp = c.chat.completions.create(model="gpt-4o", messages=messages)
    body = json.loads(transport.calls[0].content)
    assert body["messages"] == messages
    assert resp.choices[0].message.content == "A cat"


def test_chat_completion_create_tool_call():
    payload = {
        "id": "x", "object": "chat.completion", "created": 1, "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "get_weather", "arguments": '{"city":"SF"}'},
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
    }
    transport = _MockTransport([_make_response(200, payload)])
    c = _client(transport)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather",
                "parameters": {"type": "object", "properties": {"city": {"type": "string"}}},
            },
        }
    ]
    resp = c.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Weather in SF?"}],
        tools=tools,
    )
    assert resp.choices[0].finish_reason == "tool_calls"
    assert resp.choices[0].message.tool_calls[0].function.name == "get_weather"
    body = json.loads(transport.calls[0].content)
    assert body["tools"] == tools


def test_chat_completion_create_stream_sse():
    lines = [
        'data: {"id":"c1","object":"chat.completion.chunk","created":1,"model":"gpt-4o","choices":[{"index":0,"delta":{"role":"assistant","content":"Hel"}}]}',
        'data: {"id":"c1","object":"chat.completion.chunk","created":1,"model":"gpt-4o","choices":[{"index":0,"delta":{"content":"lo"}}]}',
        'data: {"id":"c1","object":"chat.completion.chunk","created":1,"model":"gpt-4o","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}',
        "data: [DONE]",
    ]
    request = httpx.Request("POST", "https://api.apilane.one/v1/chat/completions")
    response = httpx.Response(
        200,
        content=("\n".join(lines) + "\n").encode("utf-8"),
        headers={"content-type": "text/event-stream"},
        request=request,
    )
    transport = _MockTransport([response])
    c = _client(transport)
    stream = c.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hi"}],
        stream=True,
    )
    chunks = list(stream)
    assert len(chunks) == 3
    assert chunks[0].choices[0].delta.content == "Hel"
    assert chunks[1].choices[0].delta.content == "lo"
    assert chunks[2].choices[0].finish_reason == "stop"

    sent = transport.calls[0]
    assert sent.headers["accept"] == "text/event-stream"
    body = json.loads(sent.content)
    assert body["stream"] is True


def test_models_list():
    payload = {
        "object": "list",
        "data": [
            {"id": "gpt-4o", "object": "model", "created": 0, "owned_by": "openai"},
            {"id": "claude-3-5-sonnet", "object": "model", "created": 0, "owned_by": "anthropic"},
        ],
    }
    transport = _MockTransport([_make_response(200, payload)])
    c = _client(transport)
    models = c.models.list()
    assert isinstance(models, apilane.ModelList)
    assert [m.id for m in models.data] == ["gpt-4o", "claude-3-5-sonnet"]
    assert transport.calls[0].method == "GET"
    assert str(transport.calls[0].url) == "https://api.apilane.one/v1/models"


def test_models_retrieve():
    payload = {"id": "gpt-4o", "object": "model", "created": 0, "owned_by": "openai"}
    transport = _MockTransport([_make_response(200, payload)])
    c = _client(transport)
    m = c.models.retrieve("gpt-4o")
    assert m.id == "gpt-4o"
    assert str(transport.calls[0].url) == "https://api.apilane.one/v1/models/gpt-4o"


def test_authentication_error_401():
    transport = _MockTransport([_make_response(401, {"error": {"message": "bad key"}})])
    c = _client(transport)
    with pytest.raises(AuthenticationError) as exc:
        c.chat.completions.create(model="m", messages=[{"role": "user", "content": "x"}])
    assert exc.value.status_code == 401
    assert "bad key" in str(exc.value)


def test_rate_limit_error_429():
    transport = _MockTransport([_make_response(429, {"error": {"message": "slow down"}})])
    c = _client(transport)
    with pytest.raises(RateLimitError):
        c.models.list()


def test_bad_request_400():
    transport = _MockTransport([_make_response(400, {"error": {"message": "bad input"}})])
    c = _client(transport)
    with pytest.raises(BadRequestError):
        c.chat.completions.create(model="m", messages=[])


def test_server_error_500_not_retried_when_disabled():
    transport = _MockTransport([_make_response(500, {"error": {"message": "boom"}})])
    c = _client(transport)
    with pytest.raises(APIStatusError) as exc:
        c.models.list()
    assert exc.value.status_code == 500
    assert len(transport.calls) == 1


def test_retry_then_success():
    transport = _MockTransport([
        _make_response(500, {"error": {"message": "transient"}}),
        _make_response(200, {
            "id": "x", "object": "chat.completion", "created": 1, "model": "m",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
        }),
    ])
    http_client = httpx.Client(transport=transport)
    c = Apilane(api_key="sk-test", http_client=http_client, max_retries=2)
    resp = c.chat.completions.create(model="m", messages=[{"role": "user", "content": "Hi"}])
    assert resp.choices[0].message.content == "ok"
    assert len(transport.calls) == 2


def test_custom_base_url():
    transport = _MockTransport([_make_response(200, {"object": "list", "data": []})])
    c = _client(transport, base_url="https://custom.example.com/v1")
    c.models.list()
    assert str(transport.calls[0].url).startswith("https://custom.example.com/v1/models")


def test_default_headers_and_query():
    transport = _MockTransport([_make_response(200, {"object": "list", "data": []})])
    http_client = httpx.Client(transport=transport)
    c = Apilane(
        api_key="sk-test",
        http_client=http_client,
        max_retries=0,
        default_headers={"X-Foo": "bar"},
        default_query={"app": "test"},
    )
    c.models.list()
    sent = transport.calls[0]
    assert sent.headers["x-foo"] == "bar"
    assert sent.url.params["app"] == "test"


def test_close_releases_http_client():
    transport = _MockTransport([_make_response(200, {"object": "list", "data": []})])
    http_client = httpx.Client(transport=transport)
    c = Apilane(api_key="sk-test", http_client=http_client, max_retries=0)
    c.close()
    with pytest.raises(RuntimeError):
        c.models.list()


@pytest.mark.asyncio
async def test_async_chat_completion():
    payload = {
        "id": "x", "object": "chat.completion", "created": 1, "model": "m",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "hi"}, "finish_reason": "stop"}],
    }

    class _ATransport(httpx.AsyncBaseTransport):
        def __init__(self):
            self.calls = []
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            self.calls.append(request)
            return _make_response(200, payload)

    transport = _ATransport()
    http_client = httpx.AsyncClient(transport=transport)
    c = AsyncApilane(api_key="sk-test", http_client=http_client, max_retries=0)
    try:
        resp = await c.chat.completions.create(model="m", messages=[{"role": "user", "content": "Hi"}])
        assert resp.choices[0].message.content == "hi"
        assert str(transport.calls[0].url) == "https://api.apilane.one/v1/chat/completions"
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_async_stream():
    def _payload(content: str) -> bytes:
        return (
            f"data: {{\"id\":\"c1\",\"object\":\"chat.completion.chunk\",\"created\":1,\"model\":\"m\",\"choices\":[{{\"index\":0,\"delta\":{{\"content\":\"{content}\"}}}}]}}\n\n"
        ).encode("utf-8")

    body = b""
    for s in ["Hel", "lo", ""]:
        body += _payload(s)
    body += b"data: [DONE]\n\n"

    class _AStreamTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                content=body,
                headers={"content-type": "text/event-stream"},
                request=request,
            )

    transport = _AStreamTransport()
    http_client = httpx.AsyncClient(transport=transport)
    c = AsyncApilane(api_key="sk-test", http_client=http_client, max_retries=0)
    try:
        stream = await c.chat.completions.create(model="m", messages=[{"role": "user", "content": "x"}], stream=True)
        out = []
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                out.append(chunk.choices[0].delta.content)
        assert "".join(out) == "Hello"
    finally:
        await c.close()
