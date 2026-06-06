"""JSON-string Hermes handlers for fake/injected KAN plugin tools."""

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
    CommandResult,
    DaemonDiagnostics,
    DaemonStatus,
    DiagnosticCheck,
    JsonObject,
    JsonValue,
    ProtocolValidationError,
    StreamEvent,
    StreamFrame,
    StreamTail,
    require_json_object,
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


def handle_delegate_new(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Submit a delegate.new envelope as a JSON string or fail closed."""

    tool = "kan_delegate_new"
    try:
        payload = _coerce_args(
            args,
            allowed_keys=frozenset(
                {
                    "session_id",
                    "moderator",
                    "assignee",
                    "title",
                    "task",
                    "context",
                    "participants",
                    "acceptance",
                    "expected_outputs",
                    "limits",
                    "request_id",
                    "idempotency_key",
                }
            ),
        )
        command_payload: JsonObject = {
            "session_id": _required_string(payload.get("session_id"), label="session_id"),
            "moderator": _required_string(payload.get("moderator"), label="moderator"),
            "assignee": _required_string(payload.get("assignee"), label="assignee"),
            "title": _required_string(payload.get("title"), label="title"),
            "task": _required_string(payload.get("task"), label="task"),
            "context": _required_json_object(payload.get("context"), label="context"),
            "participants": _required_json_array(payload.get("participants"), label="participants"),
            "acceptance": _required_json_array(payload.get("acceptance"), label="acceptance"),
            "expected_outputs": _required_json_array(
                payload.get("expected_outputs"), label="expected_outputs"
            ),
            "limits": _required_json_object(payload.get("limits"), label="limits"),
        }
        request_id = _required_string(payload.get("request_id"), label="request_id")
        idempotency_key = _required_string(payload.get("idempotency_key"), label="idempotency_key")
        return _submit_command(
            tool=tool,
            client_factory=client_factory,
            command=schemas.DELEGATE_NEW_COMMAND,
            payload=command_payload,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def handle_delegate_action(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Submit an exact delegate.* action envelope as JSON or fail closed."""

    tool = "kan_delegate_action"
    try:
        payload = _coerce_args(
            args,
            allowed_keys=frozenset(
                {"session_id", "command", "request_id", "idempotency_key", "payload"}
            ),
        )
        session_id = _required_string(payload.get("session_id"), label="session_id")
        command = _required_string(payload.get("command"), label="command")
        if command not in schemas.DELEGATE_ACTION_COMMANDS:
            raise ValueError(f"unsupported delegate action command: {command}")
        request_id = _required_string(payload.get("request_id"), label="request_id")
        idempotency_key = _required_string(payload.get("idempotency_key"), label="idempotency_key")
        command_payload = _required_json_object(payload.get("payload"), label="payload")
        # Deterministic normalization rule: the top-level session_id is authoritative
        # and always overwrites/sets payload.session_id before the envelope is submitted.
        command_payload = {**command_payload, "session_id": session_id}

        return _submit_command(
            tool=tool,
            client_factory=client_factory,
            command=command,
            payload=command_payload,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def register_tools(
    ctx: ToolRegistrationContext,
    *,
    client_factory: ClientFactory | None = None,
) -> None:
    """Register fake/injected KAN tools with a Hermes plugin context."""

    def daemon_status_handler(args: object | None = None) -> str:
        return handle_daemon_status(args, client_factory=client_factory)

    def compatibility_diagnostics_handler(args: object | None = None) -> str:
        return handle_compatibility_diagnostics(args, client_factory=client_factory)

    def stream_tail_handler(args: object | None = None) -> str:
        return handle_stream_tail(args, client_factory=client_factory)

    def delegate_new_handler(args: object | None = None) -> str:
        return handle_delegate_new(args, client_factory=client_factory)

    def delegate_action_handler(args: object | None = None) -> str:
        return handle_delegate_action(args, client_factory=client_factory)

    registrations: tuple[tuple[str, dict[str, object], Callable[[object | None], str]], ...]
    registrations = (
        ("kan_daemon_status", schemas.KAN_DAEMON_STATUS, daemon_status_handler),
        (
            "kan_compatibility_diagnostics",
            schemas.KAN_COMPATIBILITY_DIAGNOSTICS,
            compatibility_diagnostics_handler,
        ),
        ("kan_stream_tail", schemas.KAN_STREAM_TAIL, stream_tail_handler),
        ("kan_delegate_new", schemas.KAN_DELEGATE_NEW, delegate_new_handler),
        ("kan_delegate_action", schemas.KAN_DELEGATE_ACTION, delegate_action_handler),
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


def _required_json_object(value: object, *, label: str) -> JsonObject:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object")
    try:
        return require_json_object(value, label=label)
    except ProtocolValidationError as exc:
        raise ValueError(str(exc)) from exc


def _required_json_array(value: object, *, label: str) -> list[JsonValue]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array")
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
        decoded = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must contain only JSON-compatible values") from exc
    if not isinstance(decoded, list):
        raise ValueError(f"{label} must be a JSON array")
    return cast(list[JsonValue], decoded)


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


def _submit_command(
    *,
    tool: str,
    client_factory: ClientFactory | None,
    command: str,
    payload: JsonObject,
    request_id: str,
    idempotency_key: str,
) -> str:
    client = _require_client(client_factory)
    envelope = client.build_command_envelope(
        command=command,
        payload=payload,
        request_id=request_id,
        idempotency_key=idempotency_key,
    )
    return _json_command_success(tool, client.submit_command(envelope))


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


def _json_command_success(tool: str, result: CommandResult) -> str:
    data: JsonObject = {"command_id": result.command_id}
    if result.event_id is not None:
        data["event_id"] = result.event_id
    if result.session_id is not None:
        data["session_id"] = result.session_id
    if result.request_id is not None:
        data["request_id"] = result.request_id
    return _dumps(
        {
            "ok": True,
            "tool": tool,
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
    "handle_delegate_action",
    "handle_delegate_new",
    "handle_stream_tail",
    "register_tools",
]
