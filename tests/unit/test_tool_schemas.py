from __future__ import annotations

from kkachi_agent_network_plugin import schemas
from kkachi_agent_network_plugin.protocol import STREAM_TAIL_FRAME_LIMIT


def test_schemas_expose_only_authorized_fake_injected_tools() -> None:
    assert schemas.tool_names() == (
        "kan_daemon_status",
        "kan_compatibility_diagnostics",
        "kan_stream_tail",
        "kan_delegate_new",
        "kan_delegate_action",
        "kan_council_command",
        "kan_delivery_evidence",
        "kan_discord_send_message",
    )
    assert [schema["name"] for schema in schemas.KAN_TOOL_SCHEMAS] == list(schemas.tool_names())
    assert "delegate.request" not in schemas.DELEGATE_ACTION_COMMANDS
    assert "review" not in schemas.DELEGATE_ACTION_COMMANDS


def test_daemon_status_schema_has_no_arguments_and_no_write_claims() -> None:
    schema = schemas.KAN_DAEMON_STATUS

    assert schema["name"] == "kan_daemon_status"
    assert "read-only" in str(schema["description"]).lower()
    assert "command.submit" not in str(schema["description"]).lower()
    assert schema["parameters"] == {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }


def test_compatibility_diagnostics_schema_accepts_optional_session_id_only() -> None:
    schema = schemas.KAN_COMPATIBILITY_DIAGNOSTICS

    assert schema["name"] == "kan_compatibility_diagnostics"
    assert "diagnostics" in str(schema["description"]).lower()
    assert schema["parameters"] == {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": "Optional KAN session identifier for scoped diagnostics.",
            }
        },
        "additionalProperties": False,
    }


def test_stream_tail_schema_requires_session_and_member_with_bounded_optional_cursor() -> None:
    schema = schemas.KAN_STREAM_TAIL

    assert schema["name"] == "kan_stream_tail"
    assert "stream tail" in str(schema["description"]).lower()
    assert schema["parameters"] == {
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
    }


def test_hplug2_does_not_expose_deferred_session_status_schema() -> None:
    assert "kan_session_status" not in schemas.tool_names()


def test_delegate_new_schema_requires_explicit_metadata_and_creation_fields() -> None:
    schema = schemas.KAN_DELEGATE_NEW

    assert schema["name"] == "kan_delegate_new"
    assert "delegate.new" in str(schema["description"])
    assert schema["parameters"] == {
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
    }


def test_delegate_action_schema_uses_closed_implemented_delegate_enum() -> None:
    schema = schemas.KAN_DELEGATE_ACTION

    assert schema["name"] == "kan_delegate_action"
    assert schema["parameters"] == {
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
                "enum": list(schemas.DELEGATE_ACTION_COMMANDS),
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
    }
    assert schemas.DELEGATE_ACTION_COMMANDS == (
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


def test_cndis_tool_schemas_use_closed_control_command_enums() -> None:
    assert schemas.COUNCIL_COMMANDS == (
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
    assert schemas.DELIVERY_EVIDENCE_COMMANDS == (
        "delegate.escalation_delivered",
        "delegate.escalation_delivery_failed",
    )
    assert schemas.KAN_COUNCIL_COMMAND["parameters"] == {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "enum": list(schemas.COUNCIL_COMMANDS),
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
    }
    assert schemas.KAN_DELIVERY_EVIDENCE["parameters"] == {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "enum": list(schemas.DELIVERY_EVIDENCE_COMMANDS),
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
    }


def test_discord_send_message_schema_is_injected_only_and_target_gated() -> None:
    schema = schemas.KAN_DISCORD_SEND_MESSAGE

    assert schema["name"] == "kan_discord_send_message"
    description = str(schema["description"])
    assert "explicit injected send_message" in description
    assert "fails closed without sender injection" in description
    assert "slash commands" in description
    assert schema["parameters"] == {
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
    }
