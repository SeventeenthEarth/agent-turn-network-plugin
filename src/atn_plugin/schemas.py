"""Hermes tool schemas for fake/injected ATN plugin surfaces."""

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
    "council.drop",
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
COUNCIL_HAND_RAISE_COMMAND: Final = "council.hand_raise"
COUNCIL_DROP_COMMAND: Final = "council.drop"
ARGUE_CLAIM_KINDS: Final[tuple[str, ...]] = (
    "observation",
    "requirement",
    "risk",
    "decision_frame",
    "evidence",
    "open_question",
    "proposal",
)
ARGUE_STANCES: Final[tuple[str, ...]] = (
    "support",
    "challenge",
    "refine",
    "extend",
    "synthesize",
    "question",
    "risk_addition",
    "decision_frame",
)
ARGUE_CONTRIBUTION_TYPES: Final[tuple[str, ...]] = (*ARGUE_STANCES, "new_axis")
ARGUE_CLAIM_SCHEMA: Final[dict[str, object]] = {
    "type": "object",
    "properties": {
        "claim_id": {"type": "string", "minLength": 1},
        "summary": {"type": "string", "minLength": 1},
        "kind": {"type": "string", "enum": list(ARGUE_CLAIM_KINDS)},
    },
    "required": ["claim_id", "summary"],
    "additionalProperties": True,
}
ARGUE_STANCE_LINK_SCHEMA: Final[dict[str, object]] = {
    "type": "object",
    "properties": {
        "target_event_id": {"type": "string", "minLength": 1},
        "target_claim_id": {"type": "string", "minLength": 1},
        "stance": {"type": "string", "enum": list(ARGUE_STANCES)},
        "rationale": {"type": "string", "minLength": 1},
    },
    "required": ["target_event_id", "stance"],
    "additionalProperties": True,
}
ARGUE_SPEECH_PAYLOAD_PROPERTIES: Final[dict[str, object]] = {
    "claims": {
        "type": "array",
        "items": ARGUE_CLAIM_SCHEMA,
        "description": "ARGUE claims preserved verbatim for daemon validation.",
    },
    "stance_links": {
        "type": "array",
        "items": ARGUE_STANCE_LINK_SCHEMA,
        "description": "ARGUE relation links; relation authority over legacy display hints.",
    },
    "contribution_type": {
        "type": "string",
        "enum": list(ARGUE_CONTRIBUTION_TYPES),
    },
    "new_axis_reason": {"type": ["string", "null"], "minLength": 1},
    "evidence": {
        "type": "array",
        "items": {"type": "object"},
        "description": "ARGUE evidence array preserved for daemon/control semantics.",
    },
    "responds_to_event_id": {
        "type": "string",
        "minLength": 1,
        "description": "Legacy display hint only; never overrides stance_links.",
    },
}
ARGUE_HAND_RAISE_TARGET_LINK_PROPERTIES: Final[dict[str, object]] = {
    "intent": {
        "type": "string",
        "minLength": 1,
        "description": (
            "Required unless reason is supplied; daemon derives selected-runner "
            "stance_assignment from hand_raise intent first."
        ),
    },
    "reason": {
        "type": "string",
        "minLength": 1,
        "description": (
            "Required unless intent is supplied; daemon derives selected-runner "
            "stance_assignment from reason when intent is absent."
        ),
    },
    "target_links": {
        "type": "array",
        "items": ARGUE_STANCE_LINK_SCHEMA,
        "description": "Preferred ARGUE hand-raise targets preserved verbatim.",
    },
    "target_event_ids": {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
        "description": "Legacy display hints only; not an ARGUE validation authority.",
    },
    "target_claim_ids": {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
        "description": "Legacy display hints only; not an ARGUE validation authority.",
    },
}
DELIVERY_EVIDENCE_COMMANDS: Final[tuple[str, ...]] = (
    "delegate.escalation_delivered",
    "delegate.escalation_delivery_failed",
)

ATN_DAEMON_STATUS: Final[dict[str, object]] = {
    "name": "atn_daemon_status",
    "description": (
        "Read-only ATN daemon status through an explicit fake/injected daemon client. "
        "Fails closed when no client is injected; performs no write, live daemon discovery, "
        "Hermes, Discord, auth, token, or gateway fallback."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
}

ATN_COMPATIBILITY_DIAGNOSTICS: Final[dict[str, object]] = {
    "name": "atn_compatibility_diagnostics",
    "description": (
        "Read-only ATN compatibility diagnostics through an explicit fake/injected daemon "
        "client. Returns redacted diagnostic checks and fails closed without live fallback."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": "Optional ATN session identifier for scoped diagnostics.",
            }
        },
        "additionalProperties": False,
    },
}

ATN_STREAM_TAIL: Final[dict[str, object]] = {
    "name": "atn_stream_tail",
    "description": (
        "Read-only ATN stream tail through an explicit fake/injected daemon client. "
        "Requires stream_frame compatibility from the injected transport and fails closed "
        "without live daemon, Hermes, Discord, auth, token, gateway, socket, or CLI fallback."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": "ATN session identifier whose retained stream tail should be read.",
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

ATN_STREAM_ACK: Final[dict[str, object]] = {
    "name": "atn_stream_ack",
    "description": (
        "Submit a ATN stream ack through an explicit fake/injected daemon client. "
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
                "description": "ATN session identifier whose stream cursor should be acknowledged.",
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

ATN_DELEGATE_NEW: Final[dict[str, object]] = {
    "name": "atn_delegate_new",
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
                "description": "ATN session identifier for the delegation.",
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

ATN_DELEGATE_ACTION: Final[dict[str, object]] = {
    "name": "atn_delegate_action",
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
                    "ATN session identifier; overrides/sets payload.session_id before submit."
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

ATN_COUNCIL_COMMAND: Final[dict[str, object]] = {
    "name": "atn_council_command",
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
                    "Daemon-owned command params. payload.command_id is required; "
                    "command-specific fields are validated before transport. "
                    "For council.new, payload must explicitly declare output intent: "
                    "live_visible_thread with Discord surface/request_context evidence, "
                    "or a supported non-visible/local-daemon-only requested_output_mode "
                    "with explicit_non_visible_override=true and non-empty override_reason. "
                    "Turn-bearing council.poll/council.hand_raise/council.drop/"
                    "council.grant/council.speak payloads require payload.turn and reject "
                    "legacy payload.round. For manual council.drop, payload.payload.reason "
                    "and payload.payload.request_event_id are required; caller/plugin "
                    "auto=true drops are rejected because timeout auto-drops are daemon-owned. "
                    "For council.speak and council.hand_raise, ARGUE fields are "
                    "preserved without inferring state from legacy pointers."
                ),
                "properties": {
                    "command_id": {"type": "string", "minLength": 1},
                    "actor": {"type": "string", "minLength": 1},
                    "payload": {
                        "type": "object",
                        "properties": {
                            **ARGUE_SPEECH_PAYLOAD_PROPERTIES,
                            **ARGUE_HAND_RAISE_TARGET_LINK_PROPERTIES,
                        },
                        "additionalProperties": True,
                    },
                },
                "additionalProperties": True,
            },
        },
        "required": ["command", "session_id", "request_id", "idempotency_key", "payload"],
        "additionalProperties": False,
    },
}

ATN_DELIVERY_EVIDENCE: Final[dict[str, object]] = {
    "name": "atn_delivery_evidence",
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

ATN_SELECTED_PARTICIPANT_RESPONSE: Final[dict[str, object]] = {
    "name": "atn_selected_participant_response",
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
                    **ARGUE_SPEECH_PAYLOAD_PROPERTIES,
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
            "caller_validation_context": {
                "type": "object",
                "description": (
                    "Optional caller-provided, non-authoritative selected/projection context "
                    "used only for deterministic local fail-closed checks. The plugin does "
                    "not infer lifecycle state from this field or store it. In "
                    "quality_required mode, non-opening speeches with sufficient local "
                    "context must include a stance_links[] entry that validates against "
                    "caller_validation_context.prior_claims by event_id and, when present, "
                    "claim_id, or contribution_type=new_axis with a non-empty "
                    "new_axis_reason. responds_to_event_id, prose, keywords, Discord "
                    "order, Hermes messages, and display hints are not relation authority."
                ),
                "properties": {
                    "quality_mode": {
                        "type": "string",
                        "enum": ["default", "quality_warn", "quality_required"],
                    },
                    "local_context_sufficient": {"type": "boolean"},
                    "is_opening_speech": {"type": "boolean"},
                    "selected_member": {"type": "string", "minLength": 1},
                    "selected_event_id": {"type": "string", "minLength": 1},
                    "selected_cursor": {"type": "string", "minLength": 1},
                    "prior_claims": {
                        "type": "array",
                        "description": (
                            "Compact prior claim graph targets supplied by the caller. "
                            "Only event_id and claim_id are local validation authority; "
                            "speaker, summary, and available_stances are prompt guidance "
                            "only and never satisfy relation validity by themselves."
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "event_id": {
                                    "type": "string",
                                    "minLength": 1,
                                    "description": (
                                        "Prior speech/event id accepted as local relation "
                                        "target authority."
                                    ),
                                },
                                "claim_id": {
                                    "type": "string",
                                    "minLength": 1,
                                    "description": (
                                        "Optional prior claim id; stance_links[] must match "
                                        "it when supplied."
                                    ),
                                },
                                "speaker": {
                                    "type": "string",
                                    "minLength": 1,
                                    "description": (
                                        "Prompt guidance only; not local validation authority."
                                    ),
                                },
                                "summary": {
                                    "type": "string",
                                    "minLength": 1,
                                    "description": (
                                        "Prompt guidance only; not local validation authority."
                                    ),
                                },
                                "available_stances": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": (
                                        "Prompt guidance only; not local validation authority."
                                    ),
                                },
                            },
                            "required": ["event_id"],
                            "additionalProperties": True,
                        },
                    },
                },
                "additionalProperties": False,
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

ATN_DISCORD_SEND_MESSAGE: Final[dict[str, object]] = {
    "name": "atn_discord_send_message",
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

ATN_SURFACE_RENDER_PROJECTION: Final[dict[str, object]] = {
    "name": "atn_surface_render_projection",
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

ATN_DISCUSSION_ACTIVATION_PLAN: Final[dict[str, object]] = {
    "name": "atn_discussion_activation_plan",
    "description": (
        "Build a deterministic pure/local ATN discussion activation "
        "planner/doctor report from explicit caller-provided evidence only. The "
        "tool performs no environment reads, socket discovery, daemon startup, "
        "CLI fallback, Discord/Hermes/profile/gateway inspection, or provider/"
        "auth/token/model mutation, and always keeps live readiness false."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "plan": {
                "type": "object",
                "description": (
                    "Explicit activation planning evidence with schema_version=1, "
                    "ATN task evidence, historical control/RUNFIX dependency labels, "
                    "ATN plugin tool visibility, "
                    "explicit daemon/socket/config evidence, participant profiles, "
                    "parent-channel allow-list inheritance proof, planned changes, "
                    "rollback, verification commands, approval gates, and separated "
                    "evidence labels, optional live-visible surface readiness, "
                    "optional integrated discussion proof evidence, and optional "
                    "RUNFIX3 live-thread proof evidence."
                ),
                "properties": {
                    "schema_version": {"type": "integer", "const": 1},
                    "task_id": {
                        "type": "string",
                        "enum": [
                            "plugin/RUNFIX-006",
                            "plugin/RUNFIX-007",
                            "plugin/RUNFIX-008",
                            "plugin/RUNFIX-010",
                            "plugin/RUNFIX-012",
                            "plugin/RUNFIX-015",
                            "plugin/RUNFIX-017",
                            "plugin/RUNFIX-019",
                            "plugin/RUNFIX2-005",
                            "plugin/RUNFIX3-003",
                            "plugin/NEWFIX-006",
                            "plugin/ATN-005",
                            "plugin/LVCOR-005",
                        ],
                    },
                    "control_dependency": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit control dependency completion evidence. "
                            "RUNFIX-006/007/008/010/015/017 require control/RUNFIX-005; "
                            "RUNFIX-012 requires control/RUNFIX-011 local participant-runtime "
                            "readiness proof; NEWFIX-006 keeps this field as historical activation-"
                            "planner evidence while its authoritative NEWFIX start-gate "
                            "proof lives in "
                            "selected_runner_prompt_evidence and selected_runner_timeout_evidence; "
                            "RUNFIX-019 requires control/RUNFIX-018 registry reconciliation proof; "
                            "ATN-005 preserves those IDs as historical dependency labels."
                        ),
                    },
                    "plugin_install": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit installed/enabled/plugin tool visibility evidence."
                        ),
                    },
                    "control_daemon": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit daemon socket/config and compatibility evidence; "
                            "discovery is unsupported."
                        ),
                    },
                    "participant_profiles": {
                        "type": "array",
                        "items": {"type": "object", "additionalProperties": True},
                        "description": (
                            "Candidate profile rows with explicit effective_hermes "
                            "profile visibility evidence. Historical effective_discord or "
                            "tools_visible/bot_to_bot_enabled fields remain compatibility "
                            "input only, not public aliases. Unknowns block; bot-to-bot "
                            "enabled profiles are excluded by default."
                        ),
                    },
                    "discord_parent_channel": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Selected parent-channel plan with explicit allow-list "
                            "inheritance proof from the Hermes/gateway, not thread-only, "
                            "current-channel, or manual profile evidence."
                        ),
                    },
                    "planned_changes": {"type": "array", "items": {"type": "string"}},
                    "rollback": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": "Rollback plan containing steps.",
                    },
                    "verification_commands": {"type": "array", "items": {"type": "string"}},
                    "approval_gates": {"type": "array", "items": {"type": "string"}},
                    "operator_blockers": {"type": "array", "items": {"type": "object"}},
                    "operator_evidence": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit RUNFIX-008/RUNFIX-010 operator evidence for "
                            "participant ARGUE "
                            "response fields, ARGUE counts, runner evidence, canonical "
                            "speaker_selected -> speech linkage, fallback disclosure, and "
                            "RUNFIX-017 discussion-quality evidence. In quality_required, "
                            "the first non-opening orphan speech blocks "
                            "discussion_quality_pass; repeated orphan counts are diagnostics "
                            "only and do not synthesize stance_links[]. Missing or ambiguous "
                            "evidence remains unproven/blocked."
                        ),
                    },
                    "daemon_registry_membership": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit loaded daemon registry membership or planned reconcile "
                            "evidence for the selected moderator and participants. Missing "
                            "principals require planned_reconcile=true, mapping_unambiguous=true, "
                            "and wrapper_resolves=true; loaded principals require enabled=true "
                            "and explicit evidence_ref; ambiguous or disabled principals block "
                            "live-visible activation. Use moderator or "
                            "selected_moderator_principal when the moderator is not also "
                            "a participant row."
                        ),
                    },
                    "request_context": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Operator request source and output mode. Discord-origin requests "
                            "require live_visible_thread as the default user-facing surface. "
                            "Non-visible modes such as artifact_only, "
                            "daemon_cli_actor_speech, transcript/export-only/"
                            "transcript_export_only, activation_planning_only, or "
                            "local-daemon-only/local_daemon_only discussion require "
                            "explicit_non_visible_override=true with override_reason."
                        ),
                    },
                    "visible_surface_readiness": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "RUNFIX-010 live visible thread preflight evidence and "
                            "RUNFIX3-003 visible-surface proof input: exact origin binding, "
                            "surface binding, turn-posting probe, visible closeout probe, "
                            "real profile/gateway replies, non-CLI-actor speech path, and "
                            "expected/posted visible turn counts."
                        ),
                    },
                    "participant_runtime_readiness": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit-only RUNFIX-012 participant runtime readiness input "
                            "from control/RUNFIX-011 diagnostics. It must report "
                            "subscriber presence, cursor ack freshness, heartbeat "
                            "freshness, attendance/preparation terminal evidence, "
                            "selected-runner readiness/prerequisites, and visible-surface "
                            "proof as a separate evidence class. Gateway-only, "
                            "transcript/export-only, parent-channel-fallback-only, and "
                            "manual/fallback-profile-only evidence is diagnostic and "
                            "must not imply live_readiness or production readiness."
                        ),
                    },
                    "visible_author_guard": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit-only RUNFIX-015 pre-council.new visible author guard "
                            "input/report evidence. Required for plugin/RUNFIX-015. It must "
                            "include guard_surface=pre_council_new_activation_plan, "
                            "profile_author_probes with profile, expected_author_source "
                            "(registry_snapshot or approved_profile_author_map), "
                            "expected_author_id or approved absence reason, observed bot id, "
                            "observed username, source_env, posting_path, same-path probe "
                            "evidence ref/message id/surface/posting_path, explicit "
                            "shared/default author negative proof, env_precedence_proof order "
                            "and per-key source, per-turn Discord message id/member/profile "
                            "author/posting_path/speech_event_id linkage, and final result "
                            "fields separating lifecycle, visible turns posted, real "
                            "profile/gateway replies, selected-runner labels, and "
                            "shared/default author fallback status. Generic Discord send, "
                            "transcript/export, daemon CLI actor speech, manual profile reply, "
                            "parent-channel fallback, or raw message id alone must not satisfy "
                            "the guard. The planner reports blockers only and does not claim "
                            "runtime enforcement or live readiness."
                        ),
                    },
                    "integrated_discussion_proof": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit-only plugin/RUNFIX2-005 integrated proof input. "
                            "When task_id is plugin/RUNFIX2-005, it must separately prove "
                            "lifecycle_pass, selected_runner_pass with runner invocation "
                            "success plus canonical linked speech for the selected member, "
                            "participant_runtime_ready_at_turns using grant/turn-time rows, "
                            "visible turn count as max_discussion_turns + participant_count + 2, "
                            "visible_surface_pass, clean_transcript_pass, visible_closeout_pass, "
                            "diagnostic-only fallback_profile_pass, optional "
                            "discussion_quality_pass, and final_labels that do not collapse "
                            "those axes. Manual/fallback/profile, transcript/export, "
                            "delivery-only, gateway-only, or current-only evidence cannot "
                            "satisfy selected-runner, runtime, visible-surface, "
                            "clean-transcript, or closeout proof."
                        ),
                    },
                    "runfix3_live_thread_proof": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit-only plugin/RUNFIX3-003 live-thread proof input. "
                            "When task_id is plugin/RUNFIX3-003, "
                            "visible_surface_readiness_report owns exact origin binding plus "
                            "expected/posted visible-turn fields, while "
                            "runfix3_live_thread_proof_report owns separate RUNFIX3 acceptance "
                            "axes for selected-runner proof, participant closeout coverage, "
                            "moderator synthesis coverage, per-turn delivery target rows plus "
                            "aggregate delivery-target proof, prompt envelope proof, dialogue "
                            "mode proof, drift status, and fail-closed final status. The top-"
                            "level report separates start_status from overall status so "
                            "ready_to_start cannot be mistaken for RUNFIX3 acceptance. "
                            "selected_runner_pass remains evidence-derived only, live_readiness "
                            "stays false, and the planner does not invent control enforcement "
                            "semantics."
                        ),
                    },
                    "lvcor_full_shape_acceptance_proof": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit-only plugin/LVCOR-005 full-shape one-pass acceptance "
                            "proof input. When task_id is plugin/LVCOR-005, it must cite completed "
                            "LVCOR-001 through LVCOR-004 dependency rows plus scenario_rows for "
                            "both 15/4/21 and 5/2/9. finalized_success_candidate rows must keep "
                            "expected_visible_turns equal to max_discussion_turns + "
                            "participant_count + 2, prove posted or accepted visible-turn count "
                            "equality, keep runnerless/manual selected turns at zero, prove full "
                            "participant closeout coverage, and use "
                            "terminal_synthesis_turn = max_discussion_turns + "
                            "participant_count + 1 with terminal_phase=finalized. "
                            "unresolved_terminal_blocked rows are blocker-path "
                            "evidence only and must not satisfy one-pass success labels. "
                            "live_readiness still stays false."
                        ),
                    },
                    "selected_runner_prompt_evidence": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit-only plugin/NEWFIX-006 prompt own-history proof input from "
                            "control/NEWFIX-004. For Discord-origin live_visible_thread requests, "
                            "it must carry the control task/status/evidence ref, result, prompt "
                            "hash, and distinguishable selected-member own-history source ids. "
                            "Review-pending control status is provisional only and does not unlock "
                            "ready_to_start by itself."
                        ),
                    },
                    "selected_runner_timeout_evidence": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": (
                            "Explicit-only plugin/NEWFIX-006 timeout-policy proof input from "
                            "control/NEWFIX-005. For Discord-origin live_visible_thread requests, "
                            "it must prove dispatch_timeout_sec=120 or an explicitly approved "
                            "alternative, preserve the raw control status/evidence ref, and keep "
                            "review-pending control status provisional rather than "
                            "start-authorizing."
                        ),
                    },
                    "evidence_labels": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "lifecycle_pass": {},
                            "fallback_profile_pass": {},
                            "selected_runner_pass": {},
                            "visible_surface_pass": {},
                            "discussion_quality_pass": {},
                        },
                        "description": (
                            "Evidence labels remain separate and default to unproven "
                            "unless explicit evidence is supplied."
                        ),
                    },
                },
                "required": [
                    "schema_version",
                    "task_id",
                    "control_dependency",
                    "plugin_install",
                    "control_daemon",
                    "participant_profiles",
                    "discord_parent_channel",
                    "planned_changes",
                    "rollback",
                    "verification_commands",
                    "approval_gates",
                ],
                "additionalProperties": False,
            }
        },
        "required": ["plan"],
        "additionalProperties": False,
    },
}

ATN_TOOL_SCHEMAS: Final[tuple[dict[str, object], ...]] = (
    ATN_DAEMON_STATUS,
    ATN_COMPATIBILITY_DIAGNOSTICS,
    ATN_STREAM_TAIL,
    ATN_STREAM_ACK,
    ATN_DELEGATE_NEW,
    ATN_DELEGATE_ACTION,
    ATN_COUNCIL_COMMAND,
    ATN_SELECTED_PARTICIPANT_RESPONSE,
    ATN_DELIVERY_EVIDENCE,
    ATN_SURFACE_RENDER_PROJECTION,
    ATN_DISCUSSION_ACTIVATION_PLAN,
    ATN_DISCORD_SEND_MESSAGE,
)


def tool_names() -> tuple[str, ...]:
    """Return tool names in registration order."""

    return tuple(str(schema["name"]) for schema in ATN_TOOL_SCHEMAS)


__all__ = [
    "ARGUE_CLAIM_KINDS",
    "ARGUE_CLAIM_SCHEMA",
    "ARGUE_CONTRIBUTION_TYPES",
    "ARGUE_HAND_RAISE_TARGET_LINK_PROPERTIES",
    "ARGUE_SPEECH_PAYLOAD_PROPERTIES",
    "ARGUE_STANCES",
    "ARGUE_STANCE_LINK_SCHEMA",
    "COUNCIL_COMMANDS",
    "COUNCIL_DROP_COMMAND",
    "COUNCIL_HAND_RAISE_COMMAND",
    "COUNCIL_SPEAK_COMMAND",
    "DELIVERY_EVIDENCE_COMMANDS",
    "DELEGATE_ACTION_COMMANDS",
    "DELEGATE_NEW_COMMAND",
    "ATN_COMPATIBILITY_DIAGNOSTICS",
    "ATN_COUNCIL_COMMAND",
    "ATN_DAEMON_STATUS",
    "ATN_DELEGATE_ACTION",
    "ATN_DELEGATE_NEW",
    "ATN_DELIVERY_EVIDENCE",
    "ATN_DISCUSSION_ACTIVATION_PLAN",
    "ATN_DISCORD_SEND_MESSAGE",
    "ATN_SELECTED_PARTICIPANT_RESPONSE",
    "ATN_STREAM_ACK",
    "ATN_STREAM_TAIL",
    "ATN_TOOL_SCHEMAS",
    "tool_names",
]
