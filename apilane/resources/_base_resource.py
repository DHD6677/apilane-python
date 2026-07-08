from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._base_client import _SyncClient, _AsyncClient


class _Resource:
    def __init__(self, client: "_SyncClient") -> None:
        self._client = client
        self._request = client._request
        self._stream_sse = client._stream_sse


class _AsyncResource:
    def __init__(self, client: "_AsyncClient") -> None:
        self._client = client
        self._request = client._request
        self._stream_sse = client._stream_sse
