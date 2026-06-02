"""Protocol constants and import-safe daemon protocol models.

This module intentionally contains no network, daemon, Hermes, Discord, auth,
token, or gateway initialization.  It only validates and serializes local data
structures used by injected transports and fake-daemon tests.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final, cast

SUPPORTED_PROTOCOL_VERSION: Final = "kan-protocol-v1alpha0"
COMMAND_ENVELOPE_VERSION: Final = "kan-command-envelope-v1alpha0"
CLIENT_NAME: Final = "kkachi-agent-network-plugin"
CLIENT_VERSION: Final = "0.1.0"
REQUIRED_FEATURE_GROUPS: Final[tuple[str, ...]] = (
    "version_features",
    "command_envelope",
    "structured_error",
)
STREAM_FRAME_FEATURE_GROUP: Final = "stream_frame"
STREAM_REQUIRED_FEATURE_GROUPS: Final[tuple[str, ...]] = (
    *REQUIRED_FEATURE_GROUPS,
    STREAM_FRAME_FEATURE_GROUP,
)
STREAM_EVENT_SCHEMA_VERSION: Final = 1
STREAM_FRAME_SCHEMA_VERSION: Final = 1
STREAM_TAIL_FRAME_LIMIT: Final = 1000
DIAGNOSTIC_CHECK_LIMIT: Final = 128

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


class ProtocolValidationError(ValueError):
    """Raised when local protocol data cannot be represented safely."""


def _validate_json_value(value: object, *, label: str) -> None:
    if value is None or isinstance(value, bool | int | str):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ProtocolValidationError(f"{label} floats must be finite")
        return
    if isinstance(value, list):
        for item in value:
            _validate_json_value(item, label=label)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ProtocolValidationError(f"{label} keys must be strings")
            _validate_json_value(item, label=label)
        return
    raise ProtocolValidationError(f"{label} must contain only JSON-compatible values")


def canonical_json(value: Mapping[str, JsonValue]) -> str:
    """Return deterministic JSON for protocol payloads.

    The canonical form is stable across runs for later hashing/signing layers.
    It deliberately performs no implicit UUID/time generation.
    """

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def require_json_object(value: Mapping[str, object], *, label: str) -> JsonObject:
    """Validate that a mapping contains only JSON-compatible values."""

    for key, item in value.items():
        if not isinstance(key, str):
            raise ProtocolValidationError(f"{label} keys must be strings")
        _validate_json_value(item, label=label)
    candidate = dict(value)
    try:
        encoded = json.dumps(candidate, ensure_ascii=False, sort_keys=True, allow_nan=False)
        decoded = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ProtocolValidationError(f"{label} must be JSON serializable") from exc
    if not isinstance(decoded, dict):  # defensive; json round-trip should preserve dict root.
        raise ProtocolValidationError(f"{label} must be a JSON object")
    for key in decoded:
        if not isinstance(key, str):
            raise ProtocolValidationError(f"{label} keys must be strings")
    return cast(JsonObject, decoded)


def require_non_empty_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProtocolValidationError(f"{label} must be a non-empty string")
    return value


@dataclass(frozen=True)
class ClientMetadata:
    """Metadata included with command envelopes.

    The transport label is caller supplied so fake/injected transports remain
    explicit and no live daemon endpoint is inferred.
    """

    name: str = CLIENT_NAME
    version: str = CLIENT_VERSION
    transport: str = "injected"

    def to_mapping(self) -> JsonObject:
        return {
            "name": require_non_empty_string(self.name, label="client metadata name"),
            "version": require_non_empty_string(self.version, label="client metadata version"),
            "transport": require_non_empty_string(
                self.transport, label="client metadata transport"
            ),
        }


@dataclass(frozen=True)
class CommandEnvelope:
    """Deterministic command envelope sent through an injected daemon transport."""

    command: str
    payload: Mapping[str, object]
    request_id: str
    idempotency_key: str
    client_metadata: ClientMetadata = ClientMetadata()
    protocol_version: str = SUPPORTED_PROTOCOL_VERSION
    envelope_version: str = COMMAND_ENVELOPE_VERSION

    def to_mapping(self) -> JsonObject:
        protocol_version = require_non_empty_string(self.protocol_version, label="protocol version")
        if protocol_version != SUPPORTED_PROTOCOL_VERSION:
            raise ProtocolValidationError(
                f"unsupported protocol version: {protocol_version} != {SUPPORTED_PROTOCOL_VERSION}"
            )
        envelope_version = require_non_empty_string(self.envelope_version, label="envelope version")
        if envelope_version != COMMAND_ENVELOPE_VERSION:
            raise ProtocolValidationError(
                f"unsupported envelope version: {envelope_version} != {COMMAND_ENVELOPE_VERSION}"
            )
        return {
            "protocol_version": protocol_version,
            "envelope_version": envelope_version,
            "command": require_non_empty_string(self.command, label="command"),
            "payload": require_json_object(self.payload, label="payload"),
            "request_id": require_non_empty_string(self.request_id, label="request id"),
            "idempotency_key": require_non_empty_string(
                self.idempotency_key, label="idempotency key"
            ),
            "client_metadata": self.client_metadata.to_mapping(),
        }

    def canonical_json(self) -> str:
        return canonical_json(self.to_mapping())


@dataclass(frozen=True)
class DaemonVersion:
    protocol_version: str
    daemon_version: str
    feature_groups: tuple[str, ...]
    live_readiness: bool


@dataclass(frozen=True)
class DaemonStatus:
    protocol_version: str
    daemon_version: str
    status: str
    feature_groups: tuple[str, ...]
    live_readiness: bool


@dataclass(frozen=True)
class CommandResult:
    command_id: str
    event_id: str | None
    session_id: str | None
    request_id: str | None


@dataclass(frozen=True)
class StreamEvent:
    schema_version: int
    event_id: str
    session_id: str
    type: str
    sender: str
    recipients: tuple[str, ...]
    payload: JsonObject
    details: JsonObject | None = None


@dataclass(frozen=True)
class StreamFrame:
    cursor: str
    is_replay: bool
    event: StreamEvent
    sequence: int | None = None
    schema_version: int | None = None


@dataclass(frozen=True)
class StreamTail:
    protocol_version: str
    frames: tuple[StreamFrame, ...]
    next_cursor: str | None = None


@dataclass(frozen=True)
class DiagnosticCheck:
    name: str
    ok: bool
    message: str | None = None
    details: JsonObject | None = None
    error: object | None = None


@dataclass(frozen=True)
class DaemonDiagnostics:
    protocol_version: str
    daemon_version: str
    live_readiness: bool
    checks: tuple[DiagnosticCheck, ...]


__all__ = [
    "CLIENT_NAME",
    "CLIENT_VERSION",
    "COMMAND_ENVELOPE_VERSION",
    "CommandEnvelope",
    "CommandResult",
    "DIAGNOSTIC_CHECK_LIMIT",
    "DaemonStatus",
    "DaemonDiagnostics",
    "DaemonVersion",
    "DiagnosticCheck",
    "JsonObject",
    "JsonValue",
    "ProtocolValidationError",
    "REQUIRED_FEATURE_GROUPS",
    "STREAM_EVENT_SCHEMA_VERSION",
    "STREAM_FRAME_FEATURE_GROUP",
    "STREAM_FRAME_SCHEMA_VERSION",
    "STREAM_REQUIRED_FEATURE_GROUPS",
    "STREAM_TAIL_FRAME_LIMIT",
    "SUPPORTED_PROTOCOL_VERSION",
    "StreamEvent",
    "StreamFrame",
    "StreamTail",
    "canonical_json",
]
