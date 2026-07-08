from __future__ import annotations

from typing import Optional, Mapping

import httpx

from ._base_client import _SyncClient, _AsyncClient
from .resources.chat import Chat, AsyncChat
from .resources.models import Models, AsyncModels


class Apilane(_SyncClient):
    """Synchronous apilane client.

    Example::

        from apilane import Apilane
        client = Apilane(api_key="sk-...")
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hi"}],
        )
    """
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
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
        )
        self.chat = Chat(self)
        self.models = Models(self)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()

    def __enter__(self) -> "Apilane":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


class AsyncApilane(_AsyncClient):
    """Asynchronous apilane client.

    Example::

        import asyncio
        from apilane import AsyncApilane
        async def main():
            client = AsyncApilane(api_key="sk-...")
            resp = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hi"}],
            )
            print(resp.choices[0].message.content)
            await client.close()
        asyncio.run(main())
    """
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
        )
        self.chat = AsyncChat(self)
        self.models = AsyncModels(self)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncApilane":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
