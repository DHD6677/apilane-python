from __future__ import annotations

from ._base_resource import _Resource, _AsyncResource
from ..types import Model, ModelList


class Models:
    def __init__(self, client: _Resource) -> None:
        self._client = client

    def list(self) -> ModelList:
        return self._client._request("GET", "/models", cast_type=ModelList)

    def retrieve(self, model: str) -> Model:
        return self._client._request("GET", f"/models/{model}", cast_type=Model)


class AsyncModels:
    def __init__(self, client: _AsyncResource) -> None:
        self._client = client

    async def list(self) -> ModelList:
        return await self._client._request("GET", "/models", cast_type=ModelList)

    async def retrieve(self, model: str) -> Model:
        return await self._client._request("GET", f"/models/{model}", cast_type=Model)
