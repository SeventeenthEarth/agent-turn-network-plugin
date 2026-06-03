"""JSON-string Hermes handlers for HPLUG-2 read-only tools."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Final, Protocol, cast

from . import schemas
from .client import DaemonClient
from .errors import (
    DaemonCommandError,
    DaemonCompatibilityError,
    DaemonErrorDetails,
    DaemonProtocolError,
    DaemonStreamError,
    DaemonTransportError,
    redact_sensitive,
)
from .protocol import (
    STREAM_TAIL_FRAME_LIMIT,
    DaemonDiagnostics,
    DaemonStatus,
    DiagnosticCheck,
    JsonObject,
    JsonValue,
    StreamEvent,
    StreamFrame,
    StreamTail,
)

ClientFactory = Callable[[], DaemonClient]
TOOLSET: Final = "kkachi_agent_network"


class ToolRegistrationContext(Protocol):
    def register_tool(self, **kwargs: object) -> None: ...


def handle_daemon_status(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Return daemon status as a JSON string or a fail-closed JSON error."""

    try:
        _ = _coerce_args(args, allowed_keys=frozenset())
        client = _require_client(client_factory)
        status = client.read_status()
        return _json_success("kan_daemon_status", status, _status_data(status))
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error("kan_daemon_status", exc)


def handle_compatibility_diagnostics(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Return compatibility diagnostics as a JSON string or fail closed."""

    try:
        payload = _coerce_args(args, allowed_keys=frozenset({"session_id"}))
        session_id = _optional_string(payload.get("session_id"), label="session_id")
        client = _require_client(client_factory)
        diagnostics = client.read_diagnostics(session_id=session_id)
        return _json_success(
            "kan_compatibility_diagnostics",
            diagnostics,
            _diagnostics_data(diagnostics),
        )
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error("kan_compatibility_diagnostics", exc)


def handle_stream_tail(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Return retained stream tail frames as a JSON string or fail closed."""

    try:
        payload = _coerce_args(
            args,
            allowed_keys=frozenset({"session_id", "member", "since_cursor", "limit"}),
        )
        session_id = _required_string(payload.get("session_id"), label="session_id")
        member = _required_string(payload.get("member"), label="member")
        since_cursor = _optional_string(payload.get("since_cursor"), label="since_cursor")
        limit = _optional_limit(payload.get("limit"))
        client = _require_client(client_factory)
        stream_tail = client.read_stream_tail(
            session_id=session_id,
            member=member,
            since_cursor=since_cursor,
            limit=limit,
        )
        return _json_stream_success("kan_stream_tail", stream_tail, _stream_tail_data(stream_tail))
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error("kan_stream_tail", exc)


def register_tools(
    ctx: ToolRegistrationContext,
    *,
    client_factory: ClientFactory | None = None,
) -> None:
    """Register HPLUG-2 read-only tools with a Hermes plugin context."""

    def daemon_status_handler(args: object | None = None) -> str:
        return handle_daemon_status(args, client_factory=client_factory)

    def compatibility_diagnostics_handler(args: object | None = None) -> str:
        return handle_compatibility_diagnostics(args, client_factory=client_factory)

    def stream_tail_handler(args: object | None = None) -> str:
        return handle_stream_tail(args, client_factory=client_factory)

    registrations: tuple[tuple[str, dict[str, object], Callable[[object | None], str]], ...]
    registrations = (
        ("kan_daemon_status", schemas.KAN_DAEMON_STATUS, daemon_status_handler),
        (
            "kan_compatibility_diagnostics",
            schemas.KAN_COMPATIBILITY_DIAGNOSTICS,
            compatibility_diagnostics_handler,
        ),
        ("kan_stream_tail", schemas.KAN_STREAM_TAIL, stream_tail_handler),
    )
    for name, schema, handler in registrations:
        ctx.register_tool(
            name=name,
            toolset=TOOLSET,
            schema=schema,
            handler=handler,
        )


def _coerce_args(args: object | None, *, allowed_keys: frozenset[str]) -> Mapping[str, object]:
    if args is None:
        return {}
    if not isinstance(args, Mapping):
        raise ValueError("tool args must be an object")
    unknown_keys = sorted(str(key) for key in args if key not in allowed_keys)
    if unknown_keys:
        raise ValueError(f"unsupported tool args: {', '.join(unknown_keys)}")
    return args


def _required_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _optional_string(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string when present")
    return value


def _optional_limit(value: object) -> int:
    if value is None:
        return 100
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("limit must be an integer when present")
    if value < 1 or value > STREAM_TAIL_FRAME_LIMIT:
        raise ValueError(f"limit must be between 1 and {STREAM_TAIL_FRAME_LIMIT}")
    return value


def _require_client(client_factory: ClientFactory | None) -> DaemonClient:
    if client_factory is None:
        raise DaemonTransportError(
            "explicit daemon client factory is required; no live daemon/Hermes/Discord fallback"
        )
    return client_factory()


def _status_data(status: DaemonStatus) -> JsonObject:
    return {
        "daemon_version": status.daemon_version,
        "status": status.status,
        "feature_groups": list(status.feature_groups),
    }


def _diagnostics_data(diagnostics: DaemonDiagnostics) -> JsonObject:
    return {
        "daemon_version": diagnostics.daemon_version,
        "checks": [_diagnostic_check_data(check) for check in diagnostics.checks],
    }


def _diagnostic_check_data(check: DiagnosticCheck) -> JsonObject:
    return {
        "name": check.name,
        "ok": check.ok,
        "message": check.message,
        "details": check.details,
        "error": check.error.to_mapping() if isinstance(check.error, DaemonErrorDetails) else None,
    }


def _stream_tail_data(stream_tail: StreamTail) -> JsonObject:
    return {
        "frames": [_stream_frame_data(frame) for frame in stream_tail.frames],
        "next_cursor": stream_tail.next_cursor,
    }


def _stream_frame_data(frame: StreamFrame) -> JsonObject:
    return {
        "cursor": frame.cursor,
        "is_replay": frame.is_replay,
        "sequence": frame.sequence,
        "schema_version": frame.schema_version,
        "event": _stream_event_data(frame.event),
    }


def _stream_event_data(event: StreamEvent) -> JsonObject:
    payload = redact_sensitive(event.payload)
    details = redact_sensitive(event.details) if event.details is not None else None
    return {
        "schema_version": event.schema_version,
        "event_id": event.event_id,
        "session_id": event.session_id,
        "type": event.type,
        "from": event.sender,
        "to": list(event.recipients),
        "payload": cast(JsonObject, payload),
        "details": cast(JsonObject | None, details),
    }


def _json_success(tool: str, source: DaemonStatus | DaemonDiagnostics, data: JsonObject) -> str:
    return _dumps(
        {
            "ok": True,
            "tool": tool,
            "protocol_version": source.protocol_version,
            "live_readiness": source.live_readiness,
            "data": data,
        }
    )


def _json_stream_success(tool: str, source: StreamTail, data: JsonObject) -> str:
    return _dumps(
        {
            "ok": True,
            "tool": tool,
            "protocol_version": source.protocol_version,
            # StreamTail carries no live-readiness field in the current fake/injected-only
            # contract. Future live daemon support must source this from version.read.
            "live_readiness": False,
            "data": data,
        }
    )


def _json_error(tool: str, exc: Exception) -> str:
    live_readiness = False
    return _dumps(
        {
            "ok": False,
            "tool": tool,
            "live_readiness": live_readiness,
            "error": _error_data(exc),
        }
    )


def _error_data(exc: Exception) -> JsonObject:
    if isinstance(exc, DaemonCommandError | DaemonStreamError):
        return exc.details.to_mapping()
    if isinstance(exc, DaemonCompatibilityError):
        return _simple_error("compatibility", str(exc))
    if isinstance(exc, DaemonProtocolError):
        return _simple_error("protocol", str(exc))
    if isinstance(exc, DaemonTransportError):
        return _simple_error("unavailable", str(exc))
    if isinstance(exc, ValueError):
        return _simple_error("validation", str(exc))
    return _simple_error("internal", "internal plugin handler error")


def _simple_error(category: str, message: str) -> JsonObject:
    redacted = redact_sensitive(message)
    if not isinstance(redacted, str):
        redacted = "handler error"
    return {"category": category, "message": redacted, "retryable": False}


def _dumps(value: Mapping[str, JsonValue]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


__all__ = [
    "TOOLSET",
    "handle_compatibility_diagnostics",
    "handle_daemon_status",
    "handle_stream_tail",
    "register_tools",
]
