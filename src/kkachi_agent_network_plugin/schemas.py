"""Hermes tool schemas for HPLUG-1 read-only plugin surfaces."""

from __future__ import annotations

from typing import Final

KAN_DAEMON_STATUS: Final[dict[str, object]] = {
    "name": "kan_daemon_status",
    "description": (
        "Read-only KAN daemon status through an explicit fake/injected daemon client. "
        "Fails closed when no client is injected; performs no write, live daemon discovery, "
        "Hermes, Discord, auth, token, or gateway fallback."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
}

KAN_COMPATIBILITY_DIAGNOSTICS: Final[dict[str, object]] = {
    "name": "kan_compatibility_diagnostics",
    "description": (
        "Read-only KAN compatibility diagnostics through an explicit fake/injected daemon "
        "client. Returns redacted diagnostic checks and fails closed without live fallback."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": "Optional KAN session identifier for scoped diagnostics.",
            }
        },
        "additionalProperties": False,
    },
}

KAN_TOOL_SCHEMAS: Final[tuple[dict[str, object], ...]] = (
    KAN_DAEMON_STATUS,
    KAN_COMPATIBILITY_DIAGNOSTICS,
)


def tool_names() -> tuple[str, ...]:
    """Return HPLUG-1 tool names in registration order."""

    return tuple(str(schema["name"]) for schema in KAN_TOOL_SCHEMAS)


__all__ = [
    "KAN_COMPATIBILITY_DIAGNOSTICS",
    "KAN_DAEMON_STATUS",
    "KAN_TOOL_SCHEMAS",
    "tool_names",
]
