"""Exception types raised by the Kamino client."""

from __future__ import annotations

from typing import Optional


class KaminoError(Exception):
    """Base class for all errors raised by ``kamino-py``."""


class KaminoAPIError(KaminoError):
    """Raised when the Kamino API returns a non-success HTTP status.

    Attributes:
        status_code: The HTTP status code returned by the API.
        response_text: The raw response body, when available.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


__all__ = ["KaminoAPIError", "KaminoError"]
