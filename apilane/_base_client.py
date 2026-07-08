from __future__ import annotations

import json as _json
from typing import Any, Dict, Iterator, AsyncIterator, Mapping, Optional, Union

import httpx

from ._exceptions import (
    APIConnectionError,
    APIStatusError,
    _status_to_error,
)
from ._version import __version__

DEFAULT_BASE_URL = "https://api.apilane.one/v1"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2

_RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504}


class _BaseClient:
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        import os

        if api_key is None:
            api_key = os.environ.get("APILANE_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing API key. Pass `api_key=...` or set APILANE_API_KEY env var."
            )
        self.api_key = api_key
        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        self._default_headers = dict(default_headers or {})
        self._default_query = dict(default_query or {})
        self._client = http_client

    def _build_headers(self, *, stream: bool) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"apilane-python/{__version__}",
            "Accept": "text/event-stream" if stream else "application/json",
        }
        headers.update(self._default_headers)
        return headers

    def _build_url(self, path: str) -> str:
        base = self.base_url.rstrip("/")
        if not path.startswith("/"):
            path = "/" + path
        return base + path

    @staticmethod
    def _serialize_body(body: Any) -> Optional[bytes]:
        if body is None:
            return None
        if isinstance(body, bytes):
            return body
        if hasattr(body, "model_dump"):
            body = body.model_dump(exclude_none=True)
        return _json.dumps(body).encode("utf-8")

    @staticmethod
    def _parse_body(resp: httpx.Response) -> Any:
        if not resp.content:
            return None
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def _should_retry(self, status_code: int) -> bool:
        return status_code in _RETRY_STATUS

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    def _get_async_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    def _prepare_request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        body: Any = None,
        stream: bool = False,
    ) -> httpx.Request:
        url = self._build_url(path)
        headers = self._build_headers(stream=stream)
        merged_query: Dict[str, Any] = dict(self._default_query)
        if params:
            merged_query.update(params)
        content = self._serialize_body(body) if body is not None else None
        if content is not None:
            headers.setdefault("Content-Type", "application/json")
        return httpx.Request(
            method=method,
            url=url,
            params=merged_query or None,
            content=content,
            headers=headers,
        )


class _SyncClient(_BaseClient):
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        body: Any = None,
        cast_type: Optional[type] = None,
        stream: bool = False,
    ) -> Any:
        client = self._get_client()
        request = self._prepare_request(method, path, params=params, body=body, stream=stream)

        attempts = 0
        while True:
            attempts += 1
            try:
                response = client.send(request, stream=stream)
            except httpx.HTTPError as exc:
                if attempts > self.max_retries:
                    raise APIConnectionError(str(exc), request=request) from exc
                continue

            if stream and 200 <= response.status_code < 300:
                return response

            body_obj = self._parse_body(response)
            if 200 <= response.status_code < 300:
                if cast_type is None or body_obj is None:
                    return body_obj
                if hasattr(cast_type, "model_validate"):
                    return cast_type.model_validate(body_obj)
                return body_obj

            if self._should_retry(response.status_code) and attempts <= self.max_retries:
                response.close()
                continue
            raise _status_to_error(response, body=body_obj)

    def _stream_sse(
        self,
        method: str,
        path: str,
        *,
        body: Any,
        cast_type: type,
    ) -> Iterator[Any]:
        response = self._request(method, path, body=body, stream=True, cast_type=None)
        try:
            for line in response.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                payload = line[len("data: "):]
                if payload == "[DONE]":
                    break
                try:
                    obj = _json.loads(payload)
                except ValueError:
                    continue
                yield cast_type.model_validate(obj)
        finally:
            response.close()


class _AsyncClient(_BaseClient):
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        body: Any = None,
        cast_type: Optional[type] = None,
        stream: bool = False,
    ) -> Any:
        client = self._get_async_client()
        request = self._prepare_request(method, path, params=params, body=body, stream=stream)

        attempts = 0
        while True:
            attempts += 1
            try:
                response = await client.send(request, stream=stream)
            except httpx.HTTPError as exc:
                if attempts > self.max_retries:
                    raise APIConnectionError(str(exc), request=request) from exc
                continue

            if stream and 200 <= response.status_code < 300:
                return response

            body_obj = self._parse_body(response)
            if 200 <= response.status_code < 300:
                if cast_type is None or body_obj is None:
                    return body_obj
                if hasattr(cast_type, "model_validate"):
                    return cast_type.model_validate(body_obj)
                return body_obj

            if self._should_retry(response.status_code) and attempts <= self.max_retries:
                await response.aclose()
                continue
            raise _status_to_error(response, body=body_obj)

    async def _stream_sse(
        self,
        method: str,
        path: str,
        *,
        body: Any,
        cast_type: type,
    ) -> AsyncIterator[Any]:
        response = await self._request(method, path, body=body, stream=True, cast_type=None)
        try:
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                payload = line[len("data: "):]
                if payload == "[DONE]":
                    break
                try:
                    obj = _json.loads(payload)
                except ValueError:
                    continue
                yield cast_type.model_validate(obj)
        finally:
            await response.aclose()
