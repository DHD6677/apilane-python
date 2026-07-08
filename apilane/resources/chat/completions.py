from __future__ import annotations

from typing import Any, Dict, Iterator, AsyncIterator, List, Optional, Union

from .._base_resource import _Resource, _AsyncResource
from ...types import ChatCompletion, ChatCompletionChunk


class Completions:
    def __init__(self, client: _Resource) -> None:
        self._client = client

    def create(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        stop: Optional[Union[str, List[str]]] = None,
        n: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        user: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        body: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        for k, v in (
            ("temperature", temperature),
            ("top_p", top_p),
            ("max_tokens", max_tokens),
            ("tools", tools),
            ("tool_choice", tool_choice),
            ("stop", stop),
            ("n", n),
            ("presence_penalty", presence_penalty),
            ("frequency_penalty", frequency_penalty),
            ("user", user),
        ):
            if v is not None:
                body[k] = v
        body.update(kwargs)

        if stream:
            return self._client._stream_sse(
                "POST", "/chat/completions", body=body, cast_type=ChatCompletionChunk
            )
        return self._client._request(
            "POST", "/chat/completions", body=body, cast_type=ChatCompletion
        )


class AsyncCompletions:
    def __init__(self, client: _AsyncResource) -> None:
        self._client = client

    async def create(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        stop: Optional[Union[str, List[str]]] = None,
        n: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        user: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        body: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        for k, v in (
            ("temperature", temperature),
            ("top_p", top_p),
            ("max_tokens", max_tokens),
            ("tools", tools),
            ("tool_choice", tool_choice),
            ("stop", stop),
            ("n", n),
            ("presence_penalty", presence_penalty),
            ("frequency_penalty", frequency_penalty),
            ("user", user),
        ):
            if v is not None:
                body[k] = v
        body.update(kwargs)

        if stream:
            return self._client._stream_sse(
                "POST", "/chat/completions", body=body, cast_type=ChatCompletionChunk
            )
        return await self._client._request(
            "POST", "/chat/completions", body=body, cast_type=ChatCompletion
        )
