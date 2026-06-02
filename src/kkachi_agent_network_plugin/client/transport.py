"""Explicit daemon transport boundary.

Only injected/fake transports are provided here.  There is intentionally no
localhost, subprocess, Hermes, Discord, auth, token, or gateway fallback.
"""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Protocol

from ..errors import DaemonTransportError
from ..protocol import JsonObject


class DaemonTransport(Protocol):
    """Protocol implemented by explicit fake/injected daemon transports."""

    def request(self, operation: str, body: JsonObject | None = None) -> JsonObject:
        """Return a JSON object response for a daemon operation."""


class StaticDaemonTransport:
    """Deterministic fake transport for unit/integration tests.

    Responses may be static JSON objects or callables that inspect the request.
    The class records every request so tests can prove no hidden fallback was
    attempted.
    """

    def __init__(
        self,
        responses: dict[str, JsonObject | Callable[[JsonObject | None], JsonObject]],
        *,
        label: str = "fake-daemon",
    ) -> None:
        self.responses = dict(responses)
        self.label = label
        self.requests: list[tuple[str, JsonObject | None]] = []

    def request(self, operation: str, body: JsonObject | None = None) -> JsonObject:
        self.requests.append((operation, body))
        response = self.responses.get(operation)
        if response is None:
            raise DaemonTransportError(f"fake daemon has no response for operation: {operation}")
        if callable(response):
            return response(body)
        return deepcopy(response)


__all__ = ["DaemonTransport", "StaticDaemonTransport"]
