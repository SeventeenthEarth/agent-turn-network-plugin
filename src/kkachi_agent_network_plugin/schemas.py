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
COUNCIL_COMMANDS: Final[tuple[str, ...]] = (
    "council.new",
    "council.request_attendance",
    "council.attend",
    "council.lock_agenda",
    "council.prepare",
    "council.ready",
    "council.prepared_partial",
    "council.poll",
    "council.hand_raise",
    "council.grant",
    "council.speak",
    "council.intervene",
    "council.propose",
    "council.revise",
    "council.request_vote",
    "council.vote",
    "council.finalize",
    "council.unresolved",
)
COUNCIL_SPEAK_COMMAND: Final = "council.speak"
DELIVERY_EVIDENCE_COMMANDS: Final[tuple[str, ...]] = (
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

KAN_STREAM_ACK: Final[dict[str, object]] = {
    "name": "kan_stream_ack",
    "description": (
        "Submit a KAN stream ack through an explicit fake/injected daemon client. "
        "The caller supplies command_id as the daemon idempotency key; the plugin "
        "does not dedupe locally or fall back to live daemon discovery, Hermes, "
        "Discord, auth, token, gateway, localhost/TCP, socket discovery, or CLI."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": "KAN session identifier whose stream cursor should be acknowledged.",
            },
            "member": {
                "type": "string",
                "minLength": 1,
                "description": "Member or agent stream partition acknowledging the cursor.",
            },
            "cursor": {
                "type": "string",
                "minLength": 1,
                "description": "Stream cursor being acknowledged.",
            },
            "command_id": {
                "type": "string",
                "minLength": 1,
                "description": "Caller-supplied idempotent acknowledgement command identifier.",
            },
        },
        "required": ["session_id", "member", "cursor", "command_id"],
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

KAN_COUNCIL_COMMAND: Final[dict[str, object]] = {
    "name": "kan_council_command",
    "description": (
        "Submit one exact implemented council.* lifecycle command through an explicit "
        "fake/injected daemon client. The plugin probes council.lifecycle with injected "
        "version.read before command.submit, preserves caller-supplied request_id and "
        "idempotency_key, and owns no council lifecycle, consensus, log, cursor, lock, "
        "or dedupe state."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "enum": list(COUNCIL_COMMANDS),
                "description": "Exact implemented council.* command to submit.",
            },
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": (
                    "Authoritative council session identifier; overrides/sets "
                    "payload.session_id before submit."
                ),
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
                    "Caller-supplied idempotency key; never generated, cached, or deduped "
                    "by the plugin."
                ),
            },
            "payload": {
                "type": "object",
                "description": (
                    "Opaque daemon-owned command params. payload.command_id is required; "
                    "command-specific fields are validated before transport."
                ),
            },
        },
        "required": ["command", "session_id", "request_id", "idempotency_key", "payload"],
        "additionalProperties": False,
    },
}

KAN_DELIVERY_EVIDENCE: Final[dict[str, object]] = {
    "name": "kan_delivery_evidence",
    "description": (
        "Submit a delivery-evidence command through an explicit fake/injected daemon "
        "client. The plugin probes delivery_evidence with injected version.read before "
        "command.submit, preserves caller-supplied request_id and idempotency_key, and "
        "owns no delivery evidence state or transitions."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "enum": list(DELIVERY_EVIDENCE_COMMANDS),
                "description": "Exact delivery-evidence command to submit.",
            },
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": (
                    "Authoritative delegation session identifier; overrides/sets "
                    "payload.session_id before submit."
                ),
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
                    "Caller-supplied idempotency key; never generated, cached, or deduped "
                    "by the plugin."
                ),
            },
            "payload": {
                "type": "object",
                "description": (
                    "Opaque daemon-owned delivery params. payload.escalation and "
                    "payload.command_id are required; command-specific fields are "
                    "validated before transport."
                ),
            },
        },
        "required": ["command", "session_id", "request_id", "idempotency_key", "payload"],
        "additionalProperties": False,
    },
}

KAN_SELECTED_PARTICIPANT_RESPONSE: Final[dict[str, object]] = {
    "name": "kan_selected_participant_response",
    "description": (
        "Submit a selected participant response as canonical council.speak through an "
        "explicit fake/injected or configured live daemon client, mapping the caller's "
        "participant_response.message into the daemon-owned speech payload, then acknowledge "
        "the selected stream cursor. The plugin preserves all caller-supplied IDs and "
        "fails closed before transport on role substitution or member mismatches."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": "Authoritative council session identifier.",
            },
            "selected_member": {
                "type": "string",
                "minLength": 1,
                "description": "Member selected by the speaker_selected stream frame.",
            },
            "speaker_selected_frame": {
                "type": "object",
                "description": "speaker_selected stream frame containing cursor and event payload.",
                "properties": {
                    "cursor": {"type": "string", "minLength": 1},
                    "event": {
                        "type": "object",
                        "properties": {
                            "event_id": {"type": "string", "minLength": 1},
                            "session_id": {"type": "string", "minLength": 1},
                            "type": {"type": "string", "const": "speaker_selected"},
                            "to": {
                                "type": "array",
                                "minItems": 1,
                                "maxItems": 1,
                                "items": {"type": "string", "minLength": 1},
                            },
                            "payload": {
                                "type": "object",
                                "properties": {
                                    "member": {"type": "string", "minLength": 1},
                                    "turn": {"type": ["integer", "string", "null"]},
                                },
                                "additionalProperties": True,
                            },
                        },
                        "required": ["event_id", "session_id", "type", "to", "payload"],
                        "additionalProperties": True,
                    },
                },
                "required": ["cursor", "event"],
                "additionalProperties": True,
            },
            "participant_response": {
                "type": "object",
                "description": (
                    "Control MEMBR evidence response; source must be control_membr_evidence, "
                    "member must match selected_member, and role_substitution must be false."
                ),
                "properties": {
                    "source": {"type": "string", "const": "control_membr_evidence"},
                    "member": {"type": "string", "minLength": 1},
                    "message": {"type": "string", "minLength": 1},
                    "role_substitution": {"type": "boolean", "const": False},
                    "runner": {
                        "type": "object",
                        "properties": {
                            "invocation_id": {"type": "string", "minLength": 1},
                            "started_event_id": {"type": "string", "minLength": 1},
                            "terminal_event_id": {"type": "string", "minLength": 1},
                            "terminal_event_type": {
                                "type": "string",
                                "const": "participant_response",
                            },
                            "adapter_kind": {"type": "string", "const": "hermes-agent"},
                            "wrapper_binding_evidence": {"type": "string", "minLength": 1},
                        },
                        "required": [
                            "invocation_id",
                            "started_event_id",
                            "terminal_event_id",
                            "terminal_event_type",
                            "adapter_kind",
                            "wrapper_binding_evidence",
                        ],
                        "additionalProperties": True,
                    },
                },
                "required": [
                    "source",
                    "member",
                    "message",
                    "role_substitution",
                    "runner",
                ],
                "additionalProperties": True,
            },
            "command_id": {
                "type": "string",
                "minLength": 1,
                "description": "Caller-supplied council.speak command identifier.",
            },
            "request_id": {
                "type": "string",
                "minLength": 1,
                "description": "Caller-supplied council.speak request identifier.",
            },
            "idempotency_key": {
                "type": "string",
                "minLength": 1,
                "description": "Caller-supplied council.speak idempotency key.",
            },
            "ack_command_id": {
                "type": "string",
                "minLength": 1,
                "description": "Caller-supplied stream ack command identifier.",
            },
        },
        "required": [
            "session_id",
            "selected_member",
            "speaker_selected_frame",
            "participant_response",
            "command_id",
            "request_id",
            "idempotency_key",
            "ack_command_id",
        ],
        "additionalProperties": False,
    },
}

KAN_DISCORD_SEND_MESSAGE: Final[dict[str, object]] = {
    "name": "kan_discord_send_message",
    "description": (
        "Send a Discord message only through an explicit injected send_message callable. "
        "Requires a dedicated test target and fails closed without sender injection; it "
        "does not read environment variables, discover Hermes/Discord state, register "
        "slash commands, or record daemon delivery evidence by itself."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "minLength": 1,
                "description": "Message body supplied by the caller; never generated by plugin.",
            },
            "target": {
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["discord"],
                        "default": "discord",
                        "description": "Must be discord.",
                    },
                    "channel_id": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Dedicated Discord test channel ID evidence pointer.",
                    },
                    "thread_id": {
                        "type": "string",
                        "minLength": 1,
                        "description": (
                            "Optional dedicated Discord test thread ID evidence pointer."
                        ),
                    },
                    "dedicated_test_target": {
                        "type": "boolean",
                        "const": True,
                        "description": "Must be true; current/active user targets are rejected.",
                    },
                    "label": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Visible test label required for every successful send.",
                    },
                    "cleanup_hint": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Cleanup guidance required for every successful send.",
                    },
                    "live_opt_in": {
                        "type": "boolean",
                        "default": False,
                        "description": "Explicit live Discord opt-in marker; false by default.",
                    },
                },
                "required": ["channel_id", "dedicated_test_target", "label", "cleanup_hint"],
                "additionalProperties": False,
            },
        },
        "required": ["content", "target"],
        "additionalProperties": False,
    },
}

KAN_SURFACE_RENDER_PROJECTION: Final[dict[str, object]] = {
    "name": "kan_surface_render_projection",
    "description": (
        "Render explicit daemon/control projection event JSON into separated clean "
        "visible transcript rows, audit rows, and evidence pointers. This pure tool "
        "performs no daemon reads, Discord reads or sends, environment reads, lifecycle "
        "transitions, provider/profile/auth mutation, or CLI fallback; visible IDs remain "
        "display/evidence pointers only."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "projection": {
                "type": "object",
                "description": (
                    "Explicit local daemon/control projection input with schema_version=1, "
                    "session_id, and cursor/order-authoritative events."
                ),
                "properties": {
                    "schema_version": {"type": "integer", "const": 1},
                    "session_id": {"type": "string", "minLength": 1},
                    "require_terminal_closeout": {
                        "type": "boolean",
                        "description": (
                            "When true, fail closed unless a terminal outcome has posted "
                            "visible closeout evidence matching the terminal event."
                        ),
                    },
                    "events": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": (
                            "Daemon/control events or stream frames. Each item must carry "
                            "a daemon cursor and either event.order or a parseable cur_000... "
                            "cursor; supported event types are session_created, "
                            "speaker_selected, speech, draft_conclusion, "
                            "consensus_vote_requested, consensus_vote, council_finalized, "
                            "council_unresolved, and session_cancelled."
                        ),
                    },
                },
                "required": ["schema_version", "session_id", "events"],
                "additionalProperties": True,
            }
        },
        "required": ["projection"],
        "additionalProperties": False,
    },
}

KAN_TOOL_SCHEMAS: Final[tuple[dict[str, object], ...]] = (
    KAN_DAEMON_STATUS,
    KAN_COMPATIBILITY_DIAGNOSTICS,
    KAN_STREAM_TAIL,
    KAN_STREAM_ACK,
    KAN_DELEGATE_NEW,
    KAN_DELEGATE_ACTION,
    KAN_COUNCIL_COMMAND,
    KAN_SELECTED_PARTICIPANT_RESPONSE,
    KAN_DELIVERY_EVIDENCE,
    KAN_SURFACE_RENDER_PROJECTION,
    KAN_DISCORD_SEND_MESSAGE,
)


def tool_names() -> tuple[str, ...]:
    """Return tool names in registration order."""

    return tuple(str(schema["name"]) for schema in KAN_TOOL_SCHEMAS)


__all__ = [
    "COUNCIL_COMMANDS",
    "COUNCIL_SPEAK_COMMAND",
    "DELIVERY_EVIDENCE_COMMANDS",
    "DELEGATE_ACTION_COMMANDS",
    "DELEGATE_NEW_COMMAND",
    "KAN_COMPATIBILITY_DIAGNOSTICS",
    "KAN_COUNCIL_COMMAND",
    "KAN_DAEMON_STATUS",
    "KAN_DELEGATE_ACTION",
    "KAN_DELEGATE_NEW",
    "KAN_DELIVERY_EVIDENCE",
    "KAN_DISCORD_SEND_MESSAGE",
    "KAN_SELECTED_PARTICIPANT_RESPONSE",
    "KAN_STREAM_ACK",
    "KAN_STREAM_TAIL",
    "KAN_TOOL_SCHEMAS",
    "tool_names",
]
