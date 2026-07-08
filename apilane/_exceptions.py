from __future__ import annotations

from typing import Any, Optional

import httpx


class ApilaneError(Exception):
    pass


class APIError(ApilaneError):
    def __init__(self, message: str, *, request: Optional[httpx.Request] = None) -> None:
        super().__init__(message)
        self.request = request


class APIStatusError(APIError):
    def __init__(
        self,
        message: str,
        *,
        response: httpx.Response,
        body: Any = None,
    ) -> None:
        super().__init__(message, request=response.request)
        self.response = response
        self.status_code = response.status_code
        self.body = body


class APIConnectionError(APIError):
    def __init__(self, message: str = "Connection error", *, request: Optional[httpx.Request] = None) -> None:
        super().__init__(message, request=request)


class AuthenticationError(APIStatusError):
    pass


class RateLimitError(APIStatusError):
    pass


class BadRequestError(APIStatusError):
    pass


def _status_to_error(
    response: httpx.Response,
    *,
    body: Any,
) -> APIStatusError:
    message = ""
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            message = err.get("message", "")
        elif isinstance(err, str):
            message = err
        if not message:
            message = body.get("message", "")
    if not message:
        message = f"HTTP {response.status_code}"

    status = response.status_code
    if status == 401:
        return AuthenticationError(message, response=response, body=body)
    if status == 429:
        return RateLimitError(message, response=response, body=body)
    if 400 <= status < 500:
        return BadRequestError(message, response=response, body=body)
    return APIStatusError(message, response=response, body=body)
