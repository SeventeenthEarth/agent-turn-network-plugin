from __future__ import annotations

from atn_plugin import schemas
from atn_plugin.protocol import STREAM_TAIL_FRAME_LIMIT


def test_schemas_expose_only_authorized_fake_injected_tools() -> None:
    assert schemas.tool_names() == (
        "atn_daemon_status",
        "atn_compatibility_diagnostics",
        "atn_stream_tail",
        "atn_stream_ack",
        "atn_delegate_new",
        "atn_delegate_action",
        "atn_council_command",
        "atn_selected_participant_response",
        "atn_delivery_evidence",
        "atn_surface_render_projection",
        "atn_discussion_activation_plan",
        "atn_discord_send_message",
    )
    assert [schema["name"] for schema in schemas.ATN_TOOL_SCHEMAS] == list(schemas.tool_names())
    assert all(not name.startswith("kan_") for name in schemas.tool_names())
    assert "delegate.request" not in schemas.DELEGATE_ACTION_COMMANDS
    assert "review" not in schemas.DELEGATE_ACTION_COMMANDS


def test_daemon_status_schema_has_no_arguments_and_no_write_claims() -> None:
    schema = schemas.ATN_DAEMON_STATUS

    assert schema["name"] == "atn_daemon_status"
    assert "read-only" in str(schema["description"]).lower()
    assert "command.submit" not in str(schema["description"]).lower()
    assert schema["parameters"] == {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }


def test_compatibility_diagnostics_schema_accepts_optional_session_id_only() -> None:
    schema = schemas.ATN_COMPATIBILITY_DIAGNOSTICS

    assert schema["name"] == "atn_compatibility_diagnostics"
    assert "diagnostics" in str(schema["description"]).lower()
    assert schema["parameters"] == {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": "Optional ATN session identifier for scoped diagnostics.",
            }
        },
        "additionalProperties": False,
    }


def test_stream_tail_schema_requires_session_and_member_with_bounded_optional_cursor() -> None:
    schema = schemas.ATN_STREAM_TAIL

    assert schema["name"] == "atn_stream_tail"
    assert "stream tail" in str(schema["description"]).lower()
    assert schema["parameters"] == {
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
    }


def test_stream_ack_schema_requires_cursor_and_command_id() -> None:
    schema = schemas.ATN_STREAM_ACK

    assert schema["name"] == "atn_stream_ack"
    assert "stream ack" in str(schema["description"]).lower()
    assert schema["parameters"] == {
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
    }


def test_hplug2_does_not_expose_deferred_session_status_schema() -> None:
    assert "atn_session_status" not in schemas.tool_names()
    assert "kan_session_status" not in schemas.tool_names()


def test_argue_schema_fragments_expose_council_argument_graph_fields() -> None:
    assert schemas.ARGUE_CLAIM_KINDS == (
        "observation",
        "requirement",
        "risk",
        "decision_frame",
        "evidence",
        "open_question",
        "proposal",
    )
    assert schemas.ARGUE_STANCES == (
        "support",
        "challenge",
        "refine",
        "extend",
        "synthesize",
        "question",
        "risk_addition",
        "decision_frame",
    )
    assert (*schemas.ARGUE_STANCES, "new_axis") == schemas.ARGUE_CONTRIBUTION_TYPES

    speech_fields = schemas.ARGUE_SPEECH_PAYLOAD_PROPERTIES
    assert set(speech_fields) == {
        "claims",
        "stance_links",
        "contribution_type",
        "new_axis_reason",
        "evidence",
        "responds_to_event_id",
    }
    assert speech_fields["claims"]["items"] == schemas.ARGUE_CLAIM_SCHEMA
    assert speech_fields["stance_links"]["items"] == schemas.ARGUE_STANCE_LINK_SCHEMA
    assert "display hint" in str(speech_fields["responds_to_event_id"]["description"])
    assert "target_links" in schemas.ARGUE_HAND_RAISE_TARGET_LINK_PROPERTIES


def test_council_command_schema_documents_argue_payload_preservation() -> None:
    schema = schemas.ATN_COUNCIL_COMMAND
    payload_schema = schema["parameters"]["properties"]["payload"]
    nested_payload = payload_schema["properties"]["payload"]

    assert "ARGUE fields" in str(payload_schema["description"])
    assert (
        nested_payload["properties"]["claims"] == schemas.ARGUE_SPEECH_PAYLOAD_PROPERTIES["claims"]
    )
    assert (
        nested_payload["properties"]["stance_links"]
        == schemas.ARGUE_SPEECH_PAYLOAD_PROPERTIES["stance_links"]
    )
    assert (
        nested_payload["properties"]["target_links"]
        == schemas.ARGUE_HAND_RAISE_TARGET_LINK_PROPERTIES["target_links"]
    )
    assert nested_payload["additionalProperties"] is True


def test_selected_participant_response_schema_accepts_explicit_argue_fields() -> None:
    schema_properties = schemas.ATN_SELECTED_PARTICIPANT_RESPONSE["parameters"]["properties"]
    participant_response = schema_properties["participant_response"]
    properties = participant_response["properties"]

    for field in (
        "claims",
        "stance_links",
        "contribution_type",
        "new_axis_reason",
        "evidence",
        "responds_to_event_id",
    ):
        assert field in properties
    assert properties["claims"] == schemas.ARGUE_SPEECH_PAYLOAD_PROPERTIES["claims"]
    assert properties["evidence"] == schemas.ARGUE_SPEECH_PAYLOAD_PROPERTIES["evidence"]
    caller_context = schema_properties["caller_validation_context"]
    assert "non-authoritative" in str(caller_context["description"])
    assert "event_id and, when present, claim_id" in str(caller_context["description"])
    assert "responds_to_event_id" in str(caller_context["description"])
    assert caller_context["properties"]["quality_mode"]["enum"] == [
        "default",
        "quality_warn",
        "quality_required",
    ]
    prior_claims = caller_context["properties"]["prior_claims"]
    assert "Compact prior claim graph targets" in prior_claims["description"]
    assert (
        "Only event_id and claim_id are local validation authority" in prior_claims["description"]
    )
    prior_claim_properties = prior_claims["items"]["properties"]
    assert set(prior_claim_properties) == {
        "event_id",
        "claim_id",
        "speaker",
        "summary",
        "available_stances",
    }
    assert "Prompt guidance only" in prior_claim_properties["speaker"]["description"]
    assert "Prompt guidance only" in prior_claim_properties["summary"]["description"]
    assert "Prompt guidance only" in prior_claim_properties["available_stances"]["description"]


def test_surface_render_projection_schema_is_pure_local_projection_tool() -> None:
    schema = schemas.ATN_SURFACE_RENDER_PROJECTION

    assert schema["name"] == "atn_surface_render_projection"
    description = str(schema["description"]).lower()
    assert "pure" in description
    assert "no daemon reads" in description
    assert "cli fallback" in description
    assert schema["parameters"] == {
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
    }


def test_discussion_activation_plan_schema_is_pure_local_doctor_tool() -> None:
    schema = schemas.ATN_DISCUSSION_ACTIVATION_PLAN

    assert schema["name"] == "atn_discussion_activation_plan"
    description = str(schema["description"]).lower()
    assert "pure/local" in description
    assert "atn discussion activation" in description
    assert "explicit caller-provided evidence only" in description
    assert "live readiness false" in description
    assert "cli fallback" in description
    plan_schema = schema["parameters"]["properties"]["plan"]
    assert plan_schema["required"] == [
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
    ]
    assert plan_schema["additionalProperties"] is False
    assert plan_schema["properties"]["task_id"] == {
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
    }
    assert (
        "ATN-005 preserves those IDs"
        in plan_schema["properties"]["control_dependency"]["description"]
    )
    participant_profiles = plan_schema["properties"]["participant_profiles"]
    assert "effective_hermes" in participant_profiles["description"]
    assert "not public aliases" in participant_profiles["description"]
    operator_evidence = plan_schema["properties"]["operator_evidence"]
    assert "ARGUE counts" in operator_evidence["description"]
    assert "speaker_selected -> speech linkage" in operator_evidence["description"]
    assert "fallback disclosure" in operator_evidence["description"]
    assert "RUNFIX-017 discussion-quality evidence" in operator_evidence["description"]
    assert "discussion_quality_pass" in operator_evidence["description"]
    assert "do not synthesize stance_links[]" in operator_evidence["description"]
    request_context = plan_schema["properties"]["request_context"]
    assert "live_visible_thread" in request_context["description"]
    visible_readiness = plan_schema["properties"]["visible_surface_readiness"]
    assert "exact origin binding" in visible_readiness["description"]
    assert "real profile/gateway replies" in visible_readiness["description"]
    assert "expected/posted visible turn counts" in visible_readiness["description"]
    runtime_readiness = plan_schema["properties"]["participant_runtime_readiness"]
    assert "control/RUNFIX-011" in runtime_readiness["description"]
    assert "subscriber presence" in runtime_readiness["description"]
    assert "cursor ack freshness" in runtime_readiness["description"]
    assert "manual/fallback-profile-only" in runtime_readiness["description"]
    prompt_evidence = plan_schema["properties"]["selected_runner_prompt_evidence"]
    assert "plugin/NEWFIX-006" in prompt_evidence["description"]
    assert "control/NEWFIX-004" in prompt_evidence["description"]
    assert "own-history source ids" in prompt_evidence["description"]
    timeout_evidence = plan_schema["properties"]["selected_runner_timeout_evidence"]
    assert "plugin/NEWFIX-006" in timeout_evidence["description"]
    assert "control/NEWFIX-005" in timeout_evidence["description"]
    assert "dispatch_timeout_sec=120" in timeout_evidence["description"]
    visible_author_guard = plan_schema["properties"]["visible_author_guard"]
    assert "pre-council.new visible author guard" in visible_author_guard["description"]
    assert "expected_author_source" in visible_author_guard["description"]
    assert "env_precedence_proof order" in visible_author_guard["description"]
    assert "speech_event_id" in visible_author_guard["description"]
    assert "does not claim runtime enforcement" in visible_author_guard["description"]
    integrated_proof = plan_schema["properties"]["integrated_discussion_proof"]
    assert "plugin/RUNFIX2-005" in integrated_proof["description"]
    assert "participant_runtime_ready_at_turns" in integrated_proof["description"]
    assert "max_discussion_turns + participant_count + 2" in integrated_proof["description"]
    assert "Manual/fallback/profile" in integrated_proof["description"]
    assert "final_labels" in integrated_proof["description"]
    runfix3_live_thread_proof = plan_schema["properties"]["runfix3_live_thread_proof"]
    assert "plugin/RUNFIX3-003" in runfix3_live_thread_proof["description"]
    assert "participant closeout" in runfix3_live_thread_proof["description"]
    assert "moderator synthesis" in runfix3_live_thread_proof["description"]
    assert "delivery target" in runfix3_live_thread_proof["description"]
    assert "prompt envelope" in runfix3_live_thread_proof["description"]
    assert "dialogue mode" in runfix3_live_thread_proof["description"]
    assert "drift" in runfix3_live_thread_proof["description"]
    assert "fail-closed final status" in runfix3_live_thread_proof["description"]
    lvcor_proof = plan_schema["properties"]["lvcor_full_shape_acceptance_proof"]
    assert "plugin/LVCOR-005" in lvcor_proof["description"]
    assert "15/4/21" in lvcor_proof["description"]
    assert "5/2/9" in lvcor_proof["description"]
    assert "runnerless/manual selected turns at zero" in lvcor_proof["description"]
    assert "unresolved_terminal_blocked" in lvcor_proof["description"]
    evidence_labels = plan_schema["properties"]["evidence_labels"]
    assert set(evidence_labels["properties"]) == {
        "lifecycle_pass",
        "fallback_profile_pass",
        "selected_runner_pass",
        "visible_surface_pass",
        "discussion_quality_pass",
    }


def test_delegate_new_schema_requires_explicit_metadata_and_creation_fields() -> None:
    schema = schemas.ATN_DELEGATE_NEW

    assert schema["name"] == "atn_delegate_new"
    assert "delegate.new" in str(schema["description"])
    assert schema["parameters"] == {
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
    }


def test_delegate_action_schema_uses_closed_implemented_delegate_enum() -> None:
    schema = schemas.ATN_DELEGATE_ACTION

    assert schema["name"] == "atn_delegate_action"
    assert schema["parameters"] == {
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
    assert schemas.DELIVERY_EVIDENCE_COMMANDS == (
        "delegate.escalation_delivered",
        "delegate.escalation_delivery_failed",
    )
    council_parameters = schemas.ATN_COUNCIL_COMMAND["parameters"]
    assert council_parameters["required"] == [
        "command",
        "session_id",
        "request_id",
        "idempotency_key",
        "payload",
    ]
    assert council_parameters["additionalProperties"] is False
    assert council_parameters["properties"]["command"]["enum"] == list(schemas.COUNCIL_COMMANDS)
    assert council_parameters["properties"]["payload"]["type"] == "object"
    assert council_parameters["properties"]["payload"]["additionalProperties"] is True
    assert schemas.ATN_DELIVERY_EVIDENCE["parameters"] == {
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
    schema = schemas.ATN_DISCORD_SEND_MESSAGE

    assert schema["name"] == "atn_discord_send_message"
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
