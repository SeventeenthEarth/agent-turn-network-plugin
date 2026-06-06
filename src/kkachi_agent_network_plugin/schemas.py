"""Hermes tool schemas for fake/injected KAN plugin surfaces."""

from __future__ import annotations

from typing import Final

from .protocol import STREAM_TAIL_FRAME_LIMIT

DELEGATE_NEW_COMMAND: Final = "delegate.new"
DELEGATE_ACTION_COMMANDS: Final[tuple[str, ...]] = (
    "delegate.ack",
    "delegate.message",
    "delegate.clarify",
    "delegate.answer_clarification",
    "delegate.update",
    "delegate.request_update",
    "delegate.submit",
    "delegate.review",
    "delegate.review_question",
    "delegate.review_answer",
    "delegate.review_submit",
    "delegate.revise",
    "delegate.accept",
    "delegate.escalate",
    "delegate.escalation_flush",
    "delegate.resolve_escalation",
    "delegate.escalation_delivered",
    "delegate.escalation_delivery_failed",
)

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

KAN_STREAM_TAIL: Final[dict[str, object]] = {
    "name": "kan_stream_tail",
    "description": (
        "Read-only KAN stream tail through an explicit fake/injected daemon client. "
        "Requires stream_frame compatibility from the injected transport and fails closed "
        "without live daemon, Hermes, Discord, auth, token, gateway, socket, or CLI fallback."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": "KAN session identifier whose retained stream tail should be read.",
            },
            "member": {
                "type": "string",
                "minLength": 1,
                "description": "Member or agent stream partition to read.",
            },
            "since_cursor": {
                "type": "string",
                "minLength": 1,
                "description": "Optional exclusive cursor for incremental tail reads.",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": STREAM_TAIL_FRAME_LIMIT,
                "default": 100,
                "description": "Maximum frames to return from the injected daemon response.",
            },
        },
        "required": ["session_id", "member"],
        "additionalProperties": False,
    },
}

KAN_DELEGATE_NEW: Final[dict[str, object]] = {
    "name": "kan_delegate_new",
    "description": (
        "Submit a delegate.new command envelope through an explicit fake/injected daemon "
        "client. The caller must supply request_id and idempotency_key; the plugin does "
        "not generate IDs, dedupe locally, own lifecycle state, or fall back to live "
        "daemon, Hermes, Discord, auth, token, gateway, socket, or CLI resources."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": "KAN session identifier for the delegation.",
            },
            "moderator": {
                "type": "string",
                "minLength": 1,
                "description": "Delegation moderator/member identifier.",
            },
            "assignee": {
                "type": "string",
                "minLength": 1,
                "description": "Delegation assignee/member identifier.",
            },
            "title": {
                "type": "string",
                "minLength": 1,
                "description": "Short delegation title.",
            },
            "task": {
                "type": "string",
                "minLength": 1,
                "description": "Delegated task instructions.",
            },
            "context": {
                "type": "object",
                "description": "JSON object context passed opaquely to the daemon.",
            },
            "participants": {
                "type": "array",
                "description": "Participant descriptors passed opaquely to the daemon.",
            },
            "acceptance": {
                "type": "array",
                "description": "Acceptance criteria passed opaquely to the daemon.",
            },
            "expected_outputs": {
                "type": "array",
                "description": "Expected output descriptors passed opaquely to the daemon.",
            },
            "limits": {
                "type": "object",
                "description": "Delegation limits passed opaquely to the daemon.",
            },
            "request_id": {
                "type": "string",
                "minLength": 1,
                "description": "Caller-supplied request identifier; never generated by plugin.",
            },
            "idempotency_key": {
                "type": "string",
                "minLength": 1,
                "description": (
                    "Caller-supplied idempotency key; never generated or cached locally."
                ),
            },
        },
        "required": [
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
        ],
        "additionalProperties": False,
    },
}

KAN_DELEGATE_ACTION: Final[dict[str, object]] = {
    "name": "kan_delegate_action",
    "description": (
        "Submit one exact implemented delegate.* action/review/delivery command through "
        "an explicit fake/injected daemon client. Rejects delegate.request, top-level "
        "review, and any command outside the closed enum before transport. The top-level "
        "session_id is deterministically written into payload.session_id before submit."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": (
                    "KAN session identifier; overrides/sets payload.session_id before submit."
                ),
            },
            "command": {
                "type": "string",
                "enum": list(DELEGATE_ACTION_COMMANDS),
                "description": "Exact implemented delegate.* command to submit.",
            },
            "request_id": {
                "type": "string",
                "minLength": 1,
                "description": "Caller-supplied request identifier; never generated by plugin.",
            },
            "idempotency_key": {
                "type": "string",
                "minLength": 1,
                "description": (
                    "Caller-supplied idempotency key; never generated or cached locally."
                ),
            },
            "payload": {
                "type": "object",
                "description": (
                    "Opaque JSON object for daemon-side validation; payload.session_id is "
                    "overridden by the top-level session_id."
                ),
            },
        },
        "required": ["session_id", "command", "request_id", "idempotency_key", "payload"],
        "additionalProperties": False,
    },
}

KAN_TOOL_SCHEMAS: Final[tuple[dict[str, object], ...]] = (
    KAN_DAEMON_STATUS,
    KAN_COMPATIBILITY_DIAGNOSTICS,
    KAN_STREAM_TAIL,
    KAN_DELEGATE_NEW,
    KAN_DELEGATE_ACTION,
)


def tool_names() -> tuple[str, ...]:
    """Return tool names in registration order."""

    return tuple(str(schema["name"]) for schema in KAN_TOOL_SCHEMAS)


__all__ = [
    "DELEGATE_ACTION_COMMANDS",
    "DELEGATE_NEW_COMMAND",
    "KAN_COMPATIBILITY_DIAGNOSTICS",
    "KAN_DAEMON_STATUS",
    "KAN_DELEGATE_ACTION",
    "KAN_DELEGATE_NEW",
    "KAN_STREAM_TAIL",
    "KAN_TOOL_SCHEMAS",
    "tool_names",
]
