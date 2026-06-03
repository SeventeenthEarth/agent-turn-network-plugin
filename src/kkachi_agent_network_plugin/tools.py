"""JSON-string Hermes handlers for HPLUG-1 read-only tools."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Final, Protocol

from . import schemas
from .client import DaemonClient
from .errors import (
    DaemonCommandError,
    DaemonCompatibilityError,
    DaemonErrorDetails,
    DaemonProtocolError,
    DaemonTransportError,
    redact_sensitive,
)
from .protocol import DaemonDiagnostics, DaemonStatus, DiagnosticCheck, JsonObject, JsonValue

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


def register_tools(
    ctx: ToolRegistrationContext,
    *,
    client_factory: ClientFactory | None = None,
) -> None:
    """Register HPLUG-1 read-only tools with a Hermes plugin context."""

    def daemon_status_handler(args: object | None = None) -> str:
        return handle_daemon_status(args, client_factory=client_factory)

    def compatibility_diagnostics_handler(args: object | None = None) -> str:
        return handle_compatibility_diagnostics(args, client_factory=client_factory)

    registrations: tuple[tuple[str, dict[str, object], Callable[[object | None], str]], ...]
    registrations = (
        ("kan_daemon_status", schemas.KAN_DAEMON_STATUS, daemon_status_handler),
        (
            "kan_compatibility_diagnostics",
            schemas.KAN_COMPATIBILITY_DIAGNOSTICS,
            compatibility_diagnostics_handler,
        ),
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


def _optional_string(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string when present")
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
    if isinstance(exc, DaemonCommandError):
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
    "register_tools",
]
