from __future__ import annotations

from .._base_resource import _Resource, _AsyncResource
from .completions import Completions, AsyncCompletions


class Chat:
    def __init__(self, client: _Resource) -> None:
        self.completions = Completions(client)


class AsyncChat:
    def __init__(self, client: _AsyncResource) -> None:
        self.completions = AsyncCompletions(client)
