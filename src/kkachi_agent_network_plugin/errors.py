"""Fail-closed daemon error decoding with redaction."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from .protocol import JsonObject, JsonValue, ProtocolValidationError, require_json_object

ERROR_CATEGORIES: Final[frozenset[str]] = frozenset(
    {
        "validation",
        "conflict",
        "not_found",
        "permission",
        "internal",
        "protocol",
        "unavailable",
        "unsupported",
    }
)
SENSITIVE_KEY_FRAGMENTS: Final[tuple[str, ...]] = (
    "token",
    "secret",
    "password",
    "authorization",
    "api_key",
    "apikey",
    "gateway",
)
SENSITIVE_VALUE_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"Bearer\s+[^\s]+", re.IGNORECASE),
    re.compile(r"(discord|hermes|gateway)[-_ ]?(token|secret)\s*[:=]\s*[^\s,;]+", re.IGNORECASE),
)
REDACTED: Final = "[REDACTED]"


class DaemonClientError(Exception):
    """Base class for DAEMN-1 client failures."""


class DaemonTransportError(DaemonClientError):
    """Raised when an injected transport fails locally."""


class DaemonProtocolError(DaemonClientError):
    """Raised when daemon/fake-daemon data is malformed or unsupported."""


class DaemonCompatibilityError(DaemonProtocolError):
    """Raised when daemon/manifest compatibility checks fail closed."""


@dataclass(frozen=True)
class DaemonErrorDetails:
    category: str
    message: str
    command_id: str | None = None
    event_id: str | None = None
    session_id: str | None = None
    request_id: str | None = None
    retryable: bool = False
    diagnostics: JsonObject | None = None

    def to_mapping(self) -> JsonObject:
        value: JsonObject = {
            "category": self.category,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.command_id is not None:
            value["command_id"] = self.command_id
        if self.event_id is not None:
            value["event_id"] = self.event_id
        if self.session_id is not None:
            value["session_id"] = self.session_id
        if self.request_id is not None:
            value["request_id"] = self.request_id
        if self.diagnostics is not None:
            value["diagnostics"] = self.diagnostics
        return value


class DaemonCommandError(DaemonClientError):
    """Raised for structured daemon command failures."""

    def __init__(self, details: DaemonErrorDetails) -> None:
        super().__init__(f"{details.category}: {details.message}")
        self.details = details


def _string_or_none(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise DaemonProtocolError(f"daemon error {label} must be a non-empty string when present")
    return value


def _redact_string(value: str) -> str:
    redacted = value
    for pattern in SENSITIVE_VALUE_PATTERNS:
        redacted = pattern.sub(REDACTED, redacted)
    return redacted


def redact_sensitive(value: JsonValue, *, parent_key: str = "") -> JsonValue:
    """Recursively redact token/secret-like diagnostics."""

    lowered = parent_key.lower()
    if any(fragment in lowered for fragment in SENSITIVE_KEY_FRAGMENTS):
        return REDACTED
    if isinstance(value, str):
        return _redact_string(value)
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    if isinstance(value, dict):
        return {key: redact_sensitive(child, parent_key=key) for key, child in value.items()}
    return value


def decode_daemon_error(value: Mapping[str, object]) -> DaemonErrorDetails:
    """Decode a structured daemon error or fail closed as a protocol error."""

    category = value.get("category")
    if not isinstance(category, str) or not category:
        raise DaemonProtocolError("daemon error missing non-empty category")
    if category not in ERROR_CATEGORIES:
        raise DaemonProtocolError(f"unsupported daemon error category: {category}")

    message = value.get("message")
    if not isinstance(message, str) or not message:
        raise DaemonProtocolError("daemon error missing non-empty message")

    retryable = value.get("retryable", False)
    if not isinstance(retryable, bool):
        raise DaemonProtocolError("daemon error retryable must be a boolean")

    raw_diagnostics = value.get("diagnostics")
    diagnostics: JsonObject | None = None
    if raw_diagnostics is not None:
        if not isinstance(raw_diagnostics, Mapping):
            raise DaemonProtocolError("daemon error diagnostics must be an object when present")
        try:
            diagnostics = require_json_object(raw_diagnostics, label="daemon error diagnostics")
        except ProtocolValidationError as exc:
            raise DaemonProtocolError(str(exc)) from exc
        redacted = redact_sensitive(diagnostics)
        if not isinstance(redacted, dict):  # defensive: object input redacts to object output.
            raise DaemonProtocolError("daemon error diagnostics redaction produced malformed data")
        diagnostics = redacted

    return DaemonErrorDetails(
        category=category,
        message=_redact_string(message),
        command_id=_string_or_none(value.get("command_id"), label="command_id"),
        event_id=_string_or_none(value.get("event_id"), label="event_id"),
        session_id=_string_or_none(value.get("session_id"), label="session_id"),
        request_id=_string_or_none(value.get("request_id"), label="request_id"),
        retryable=retryable,
        diagnostics=diagnostics,
    )


__all__ = [
    "DaemonClientError",
    "DaemonCommandError",
    "DaemonCompatibilityError",
    "DaemonErrorDetails",
    "DaemonProtocolError",
    "DaemonTransportError",
    "decode_daemon_error",
    "redact_sensitive",
]
