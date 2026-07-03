from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, cast

import pytest

from atn_plugin.client import DaemonClient, StaticDaemonTransport
from atn_plugin.client.daemon import (
    OP_COMMAND_SUBMIT,
    OP_DIAGNOSTICS_READ,
    OP_STATUS_READ,
    OP_STREAM_ACK,
    OP_STREAM_TAIL,
    OP_VERSION_READ,
)
from atn_plugin.protocol import JsonObject
from atn_plugin.tools import (
    handle_compatibility_diagnostics,
    handle_council_command,
    handle_daemon_status,
    handle_delegate_action,
    handle_delegate_new,
    handle_delivery_evidence,
    handle_discussion_activation_plan,
    handle_stream_ack,
    handle_stream_tail,
    handle_surface_render_projection,
)

BASE_STATUS: JsonObject = {
    "protocol_version": "atn-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "status": "fake-ready",
    "feature_groups": ["version.read", "command_envelope", "structured_error"],
    "live_readiness": False,
}
BASE_VERSION_WITH_STREAM: JsonObject = {
    "protocol_version": "atn-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": ["version.read", "command_envelope", "structured_error", "stream_frame"],
    "live_readiness": False,
}
BASE_VERSION_WITH_STREAM_ACK: JsonObject = {
    **BASE_VERSION_WITH_STREAM,
    "feature_groups": [
        "version.read",
        "command_envelope",
        "structured_error",
        "stream_frame",
        "stream.ack",
    ],
}
BASE_VERSION_WITHOUT_STREAM: JsonObject = {
    "protocol_version": "atn-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": ["version.read", "command_envelope", "structured_error"],
    "live_readiness": False,
}
BASE_VERSION_WITH_CNDIS: JsonObject = {
    "protocol_version": "atn-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": [
        "version.read",
        "command_envelope",
        "structured_error",
        "delivery_evidence",
        "council.lifecycle",
    ],
    "live_readiness": False,
}
BASE_VERSION_WITHOUT_CNDIS: JsonObject = {
    "protocol_version": "atn-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": ["version.read", "command_envelope", "structured_error"],
    "live_readiness": False,
}
BASE_FRAME: JsonObject = {
    "cursor": "cur_000000000012_evt_01HV",
    "is_replay": False,
    "sequence": 12,
    "schema_version": 1,
    "event": {
        "schema_version": 1,
        "event_id": "evt_01HV",
        "session_id": "sess-1",
        "type": "hand_raise_requested",
        "from": "agent-mod",
        "to": ["agent-1"],
        "payload": {"gateway_token": "do-not-leak", "turn": 5},
        "details": {"note": "ok"},
    },
}
BASE_STREAM_TAIL: JsonObject = {
    "protocol_version": "atn-protocol-v1alpha0",
    "frames": [BASE_FRAME],
    "next_cursor": "cur_next",
}
BASE_DIAGNOSTICS: JsonObject = {
    "protocol_version": "atn-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "live_readiness": False,
    "checks": [
        {
            "name": "structured_error",
            "ok": True,
            "details": {"gateway_token": "do-not-leak"},
        }
    ],
}
BASE_COMMAND_SUCCESS: JsonObject = {
    "ok": True,
    "command_id": "cmd-1",
    "event_id": "evt-1",
    "session_id": "sess-1",
    "request_id": "req-1",
}
BASE_STREAM_ACK_SUCCESS: JsonObject = {
    "ok": True,
    "command_id": "cmd-ack-1",
    "event_id": "evt-ack-1",
    "session_id": "sess-1",
    "request_id": "plugin-live-stream-ack",
    "deduplicated": False,
}


def factory_for(responses: dict[str, JsonObject]) -> Callable[[], DaemonClient]:
    typed_responses = cast(
        dict[str, JsonObject | Callable[[JsonObject | None], JsonObject]],
        responses,
    )
    return lambda: DaemonClient(StaticDaemonTransport(typed_responses))


def factory_for_transport(transport: StaticDaemonTransport) -> Callable[[], DaemonClient]:
    return lambda: DaemonClient(transport)


def decode(payload: str) -> dict[str, Any]:
    decoded = json.loads(payload)
    assert isinstance(decoded, dict)
    return decoded


def test_daemon_status_handler_returns_json_success_from_explicit_fake_client() -> None:
    result = decode(
        handle_daemon_status({}, client_factory=factory_for({OP_STATUS_READ: BASE_STATUS}))
    )

    assert result == {
        "ok": True,
        "tool": "atn_daemon_status",
        "protocol_version": "atn-protocol-v1alpha0",
        "live_readiness": False,
        "data": {
            "daemon_version": "0.0.0-fake",
            "status": "fake-ready",
            "feature_groups": ["version.read", "command_envelope", "structured_error"],
        },
    }


def test_compatibility_diagnostics_handler_returns_redacted_json_success() -> None:
    result = decode(
        handle_compatibility_diagnostics(
            {"session_id": "sess-1"},
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )

    assert result == {
        "ok": True,
        "tool": "atn_compatibility_diagnostics",
        "protocol_version": "atn-protocol-v1alpha0",
        "live_readiness": False,
        "data": {
            "daemon_version": "0.0.0-fake",
            "checks": [
                {
                    "name": "structured_error",
                    "ok": True,
                    "message": None,
                    "details": {"gateway_token": "[REDACTED]"},
                    "error": None,
                }
            ],
        },
    }


def test_stream_tail_handler_returns_redacted_json_success_from_explicit_fake_client() -> None:
    result = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1", "since_cursor": "cur_prev", "limit": 1},
            client_factory=factory_for(
                {OP_VERSION_READ: BASE_VERSION_WITH_STREAM, OP_STREAM_TAIL: BASE_STREAM_TAIL}
            ),
        )
    )

    assert result == {
        "ok": True,
        "tool": "atn_stream_tail",
        "protocol_version": "atn-protocol-v1alpha0",
        "live_readiness": False,
        "data": {
            "frames": [
                {
                    "cursor": "cur_000000000012_evt_01HV",
                    "is_replay": False,
                    "sequence": 12,
                    "schema_version": 1,
                    "event": {
                        "schema_version": 1,
                        "event_id": "evt_01HV",
                        "session_id": "sess-1",
                        "type": "hand_raise_requested",
                        "from": "agent-mod",
                        "to": ["agent-1"],
                        "payload": {"gateway_token": "[REDACTED]", "turn": 5},
                        "details": {"note": "ok"},
                    },
                }
            ],
            "next_cursor": "cur_next",
        },
    }


def test_handlers_fail_closed_without_client_factory() -> None:
    status = decode(handle_daemon_status({}))
    diagnostics = decode(handle_compatibility_diagnostics({}))
    stream_tail = decode(handle_stream_tail({"session_id": "sess-1", "member": "agent-1"}))

    assert status["ok"] is False
    assert status["tool"] == "atn_daemon_status"
    assert status["error"]["category"] == "unavailable"
    assert "client factory" in status["error"]["message"]
    assert diagnostics["ok"] is False
    assert diagnostics["error"]["category"] == "unavailable"
    assert stream_tail["ok"] is False
    assert stream_tail["tool"] == "atn_stream_tail"
    assert stream_tail["error"]["category"] == "unavailable"


def test_surface_render_projection_handler_returns_local_projection_success() -> None:
    result = decode(
        handle_surface_render_projection(
            {
                "projection": {
                    "schema_version": 1,
                    "session_id": "sess-surface",
                    "events": [
                        {
                            "cursor": "cur_000000000001_evt_session",
                            "event": {
                                "event_id": "evt-session",
                                "session_id": "sess-surface",
                                "type": "session_created",
                                "payload": {"surface": {"kind": "local_fixture"}},
                            },
                        }
                    ],
                }
            }
        )
    )

    assert result == {
        "ok": True,
        "tool": "atn_surface_render_projection",
        "live_readiness": False,
        "data": {
            "local_projection": {
                "schema_version": 1,
                "session_id": "sess-surface",
                "order_authority": "daemon_cursor",
                "source_event_count": 1,
                "live_readiness": False,
                "rows": [
                    {
                        "cursor": "cur_000000000001_evt_session",
                        "order": 1,
                        "event_id": "evt-session",
                        "type": "session_created",
                        "target": "session",
                        "status": "created",
                        "evidence": {
                            "surface": {"kind": "local_fixture"},
                            "linked_authority": None,
                        },
                    }
                ],
                "visible_transcript": [
                    {
                        "kind": "header",
                        "label": "[ATN]",
                        "text": "[ATN]\nCouncil session opened.",
                    }
                ],
                "audit_log": [
                    {
                        "cursor": "cur_000000000001_evt_session",
                        "order": 1,
                        "event_id": "evt-session",
                        "type": "session_created",
                        "target": "session",
                        "status": "created",
                        "evidence": {
                            "surface": {"kind": "local_fixture"},
                            "linked_authority": None,
                        },
                    }
                ],
            }
        },
    }


def test_surface_render_projection_handler_fails_closed_for_bad_projection() -> None:
    result = decode(
        handle_surface_render_projection(
            {
                "projection": {
                    "schema_version": 1,
                    "session_id": "sess-surface",
                    "events": [
                        {
                            "cursor": "cur_000000000001_evt_speech",
                            "event": {
                                "event_id": "evt-speech",
                                "session_id": "sess-surface",
                                "type": "speech",
                                "from": "agent-1",
                                "payload": {"turn": 1, "speech": "no grant"},
                            },
                        }
                    ],
                }
            }
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_surface_render_projection"
    assert result["live_readiness"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "floor_grant_missing_or_mismatched",
        "retryable": False,
    }


def test_discussion_activation_plan_handler_returns_local_doctor_report() -> None:
    result = decode(
        handle_discussion_activation_plan(
            {
                "plan": {
                    "schema_version": 1,
                    "task_id": "plugin/RUNFIX-006",
                    "control_dependency": {
                        "task_id": "control/RUNFIX-005",
                        "status": "completed/local-control",
                        "evidence_ref": "control-runfix-005",
                    },
                    "plugin_install": {
                        "installed": True,
                        "enabled": True,
                        "tool_names": ["atn_discussion_activation_plan"],
                    },
                    "control_daemon": {
                        "mode": "explicit",
                        "socket_or_config_ref": "socket-config",
                        "compatibility_ref": "version-read",
                    },
                    "participant_profiles": [
                        {
                            "profile": "macho",
                            "tools_visible": True,
                            "bot_to_bot_enabled": False,
                        }
                    ],
                    "discord_parent_channel": {
                        "channel_id": "parent-123",
                        "allow_list_inheritance_proven": True,
                        "proof_source": "gateway_parent_allow_list_inheritance",
                        "proof_ref": "parent-proof",
                    },
                    "planned_changes": ["dry-run only"],
                    "rollback": {"steps": ["revert dry-run config"]},
                    "verification_commands": ["make test-prepare"],
                    "approval_gates": ["explicit apply approval"],
                }
            }
        )
    )

    assert result["ok"] is True
    assert result["tool"] == "atn_discussion_activation_plan"
    assert result["live_readiness"] is False
    assert result["data"]["status"] == "ready_for_approval"
    assert result["data"]["behavior_task_id"] == "plugin/RUNFIX-007"
    assert result["data"]["allow_list_targets"] == ["macho"]
    assert result["data"]["evidence_labels"]["selected_runner_pass"] == "unproven"


def test_discussion_activation_plan_handler_accepts_newfix006_review_pending() -> None:
    result = decode(
        handle_discussion_activation_plan(
            {
                "plan": {
                    "schema_version": 1,
                    "task_id": "plugin/NEWFIX-006",
                    "control_dependency": {
                        "task_id": "control/RUNFIX-005",
                        "status": "completed/local-control",
                        "evidence_ref": "control-runfix-005",
                    },
                    "plugin_install": {
                        "installed": True,
                        "enabled": True,
                        "tool_names": ["atn_discussion_activation_plan"],
                    },
                    "control_daemon": {
                        "mode": "explicit",
                        "socket_or_config_ref": "socket-config",
                        "compatibility_ref": "version-read",
                    },
                    "participant_profiles": [
                        {"profile": "macho", "tools_visible": True, "bot_to_bot_enabled": False},
                        {"profile": "seohwang", "tools_visible": True, "bot_to_bot_enabled": False},
                    ],
                    "discord_parent_channel": {
                        "channel_id": "parent-123",
                        "allow_list_inheritance_proven": True,
                        "proof_source": "gateway_parent_allow_list_inheritance",
                        "proof_ref": "parent-proof",
                    },
                    "planned_changes": ["local proof only"],
                    "rollback": {"steps": ["revert local proof fixtures"]},
                    "verification_commands": ["make test-prepare"],
                    "approval_gates": ["explicit apply approval"],
                    "request_context": {
                        "source": "discord_thread",
                        "chat_id": "chat-123",
                        "thread_id": "thread-456",
                    },
                    "visible_surface_readiness": {
                        "surface_bound": True,
                        "parent_channel_id": "parent-123",
                        "thread_id": "thread-456",
                        "observed_chat_id": "chat-123",
                        "observed_thread_id": "thread-456",
                        "exact_origin_binding": True,
                        "origin_binding_evidence_ref": "discord/thread-origin-proof",
                        "turn_posting_strategy": "selected_speaker_profile_send",
                        "turn_delivery_probe_ref": "discord/thread-turn-probe",
                        "visible_closeout_probe_ref": "discord/thread-closeout-probe",
                        "real_profile_gateway_replies": True,
                        "cli_actor_speech_only": False,
                        "max_discussion_turns": 3,
                        "participant_count": 2,
                        "visible_turns_expected": 7,
                        "visible_turns_posted": 7,
                    },
                    "daemon_registry_membership": {
                        "registry_loaded": True,
                        "selected_moderator_principal": "macho",
                        "evidence_ref": "control/registry/show",
                        "participants": [
                            {
                                "principal": "macho",
                                "in_loaded_registry": True,
                                "mapping_unambiguous": True,
                                "planned_reconcile": False,
                                "wrapper_resolves": True,
                                "enabled": True,
                            },
                            {
                                "principal": "seohwang",
                                "in_loaded_registry": True,
                                "mapping_unambiguous": True,
                                "planned_reconcile": False,
                                "wrapper_resolves": True,
                                "enabled": True,
                            },
                        ],
                    },
                    "selected_runner_prompt_evidence": {
                        "task_id": "control/NEWFIX-004",
                        "status": "implementation_complete/review_pending",
                        "evidence_ref": "control/status/newfix-004",
                        "result": "pass",
                        "prompt_context_sha256": "prompt-sha-256",
                        "own_history_source_event_ids": ["evt-own-1"],
                    },
                    "selected_runner_timeout_evidence": {
                        "task_id": "control/NEWFIX-005",
                        "status": "implementation_complete/review_pending",
                        "evidence_ref": "control/status/newfix-005",
                        "policy_required": True,
                        "configured_timeout_sec": 120,
                        "effective_timeout_sec": 120,
                        "approved_alternative": False,
                        "approval_basis": None,
                        "compliant": True,
                        "drift_blocked": False,
                    },
                }
            }
        )
    )

    assert result["ok"] is True
    assert result["tool"] == "atn_discussion_activation_plan"
    assert result["live_readiness"] is False
    assert result["data"]["task_id"] == "plugin/NEWFIX-006"
    assert result["data"]["behavior_task_id"] == "plugin/NEWFIX-006"
    assert result["data"]["start_status"] == "ready_to_start"
    assert result["data"]["status"] == "ready_to_start"
    assert result["data"]["selected_runner_prompt_evidence_report"]["status"] == "proven"
    assert result["data"]["selected_runner_timeout_evidence_report"]["status"] == "proven"
    assert (
        result["data"]["selected_runner_prompt_evidence_report"]["control_dependency"][
            "accepted_for_start"
        ]
        is True
    )
    assert (
        result["data"]["selected_runner_timeout_evidence_report"]["control_dependency"][
            "accepted_for_start"
        ]
        is True
    )


def test_discussion_activation_plan_handler_exposes_runfix3_live_thread_report() -> None:
    result = decode(
        handle_discussion_activation_plan(
            {
                "plan": {
                    "schema_version": 1,
                    "task_id": "plugin/RUNFIX3-003",
                    "control_dependency": {
                        "task_id": "control/RUNFIX-005",
                        "status": "completed/local-control",
                        "evidence_ref": "control-runfix-005",
                    },
                    "plugin_install": {
                        "installed": True,
                        "enabled": True,
                        "tool_names": ["atn_discussion_activation_plan"],
                    },
                    "control_daemon": {
                        "mode": "explicit",
                        "socket_or_config_ref": "socket-config",
                        "compatibility_ref": "version-read",
                    },
                    "participant_profiles": [
                        {
                            "profile": "macho",
                            "tools_visible": True,
                            "bot_to_bot_enabled": False,
                        },
                        {
                            "profile": "seohwang",
                            "tools_visible": True,
                            "bot_to_bot_enabled": False,
                        },
                    ],
                    "discord_parent_channel": {
                        "channel_id": "parent-123",
                        "allow_list_inheritance_proven": True,
                        "proof_source": "gateway_parent_allow_list_inheritance",
                        "proof_ref": "parent-proof",
                    },
                    "planned_changes": ["local proof only"],
                    "rollback": {"steps": ["revert local proof fixtures"]},
                    "verification_commands": ["make test-prepare"],
                    "approval_gates": ["explicit apply approval"],
                    "operator_evidence": {
                        "runner": {
                            "speaker_selected_event_id": "evt_select_1",
                            "selected_member": "macho",
                            "runner_invocation_started_ref": "runner/run-1/invocation-started",
                        },
                        "canonical_speech": {
                            "speaker_selected_event_id": "evt_select_1",
                            "speech_event_id": "evt_speech_1",
                            "speaker": "macho",
                        },
                        "participant_response": {
                            "speech": (
                                "We should keep the pilot blocked until canonical "
                                "speech linkage is proven."
                            ),
                            "claims": [
                                {
                                    "claim_id": "T03.C1",
                                    "summary": "Canonical speech linkage gates pilot acceptance.",
                                    "kind": "requirement",
                                }
                            ],
                            "stance_links": [
                                {
                                    "target_event_id": "evt_speech_0",
                                    "target_claim_id": "T01.C1",
                                    "stance": "support",
                                    "rationale": (
                                        "The prior traceability requirement remains "
                                        "the acceptance axis."
                                    ),
                                }
                            ],
                            "contribution_type": "support",
                            "new_axis_reason": None,
                            "evidence": [{"kind": "runner_log", "ref": "runner/run-1/speech-link"}],
                        },
                        "fallback_disclosure": {
                            "fallback_profile_pass": True,
                            "evidence_ref": "manual/profile-diagnostic-reply",
                            "missing_evidence": ["visible delivery evidence"],
                        },
                        "discussion_quality": {
                            "quality_mode": "quality_required",
                            "local_context_sufficient": True,
                            "prior_claims": [
                                {
                                    "event_id": "evt_speech_0",
                                    "claim_id": "T01.C1",
                                    "speaker": "seohwang",
                                    "summary": "Prior traceability remains the acceptance axis.",
                                    "available_stances": [
                                        "support",
                                        "challenge",
                                        "refine",
                                        "synthesize",
                                    ],
                                }
                            ],
                            "turns": [
                                {
                                    "speech_event_id": "evt_speech_1",
                                    "is_opening_speech": False,
                                    "participant_response": {
                                        "speech": (
                                            "We should keep the pilot blocked until "
                                            "canonical speech linkage is proven."
                                        ),
                                        "claims": [
                                            {
                                                "claim_id": "T03.C1",
                                                "summary": (
                                                    "Canonical speech linkage gates "
                                                    "pilot acceptance."
                                                ),
                                                "kind": "requirement",
                                            }
                                        ],
                                        "stance_links": [
                                            {
                                                "target_event_id": "evt_speech_0",
                                                "target_claim_id": "T01.C1",
                                                "stance": "support",
                                                "rationale": (
                                                    "The prior traceability requirement "
                                                    "remains the acceptance axis."
                                                ),
                                            }
                                        ],
                                        "contribution_type": "support",
                                        "new_axis_reason": None,
                                        "evidence": [
                                            {
                                                "kind": "runner_log",
                                                "ref": "runner/run-1/speech-link",
                                            }
                                        ],
                                    },
                                }
                            ],
                        },
                    },
                    "daemon_registry_membership": {
                        "registry_loaded": True,
                        "selected_moderator_principal": "macho",
                        "evidence_ref": "control/registry/show",
                        "participants": [
                            {
                                "principal": "macho",
                                "in_loaded_registry": True,
                                "mapping_unambiguous": True,
                                "planned_reconcile": False,
                                "wrapper_resolves": True,
                                "enabled": True,
                            },
                            {
                                "principal": "seohwang",
                                "in_loaded_registry": True,
                                "mapping_unambiguous": True,
                                "planned_reconcile": False,
                                "wrapper_resolves": True,
                                "enabled": True,
                            },
                        ],
                    },
                    "request_context": {
                        "source": "discord_thread",
                        "chat_id": "chat-123",
                        "thread_id": "thread-456",
                    },
                    "visible_surface_readiness": {
                        "surface_bound": True,
                        "parent_channel_id": "parent-123",
                        "thread_id": "thread-456",
                        "observed_chat_id": "chat-123",
                        "observed_thread_id": "thread-456",
                        "exact_origin_binding": True,
                        "origin_binding_evidence_ref": "discord/thread-origin-proof",
                        "turn_posting_strategy": "selected_speaker_profile_send",
                        "turn_delivery_probe_ref": "discord/thread-turn-probe",
                        "visible_closeout_probe_ref": "discord/thread-closeout-probe",
                        "real_profile_gateway_replies": True,
                        "cli_actor_speech_only": False,
                        "max_discussion_turns": 3,
                        "participant_count": 2,
                        "visible_turns_expected": 7,
                        "visible_turns_posted": 7,
                    },
                    "runfix3_live_thread_proof": {
                        "selected_runner": {
                            "selected_member": "macho",
                            "speaker_selected_event_id": "evt_select_1",
                            "runner_invocation_started_ref": "control/runner-started-1",
                            "runner_invocation_succeeded_ref": "control/runner-succeeded-1",
                            "speech_event_id": "evt_speech_1",
                            "delivery_target_match": True,
                            "evidence_ref": "control/selected-runner-proof-turn-1",
                        },
                        "participant_closeout": {
                            "participant_closeout_pass": True,
                            "rows": [
                                {
                                    "participant": "macho",
                                    "closeout_turn": 4,
                                    "speech_event_id": "evt_closeout_macho",
                                    "delivery_target_match": True,
                                    "evidence_ref": "plugin/surface/closeout-macho",
                                },
                                {
                                    "participant": "seohwang",
                                    "closeout_turn": 5,
                                    "speech_event_id": "evt_closeout_seohwang",
                                    "delivery_target_match": True,
                                    "evidence_ref": "plugin/surface/closeout-seohwang",
                                },
                            ],
                            "evidence_ref": "plugin/surface/participant-closeouts",
                        },
                        "moderator_synthesis": {
                            "moderator_synthesis_pass": True,
                            "speech_event_id": "evt_synthesis_1",
                            "delivery_target_match": True,
                            "evidence_ref": "plugin/surface/moderator-synthesis",
                        },
                        "delivery_targets": {
                            "delivery_target_pass": True,
                            "rows": [
                                {
                                    "turn": 0,
                                    "speaker_selected_event_id": "evt_select_opening",
                                    "speech_event_id": "evt_opening_1",
                                    "expected_delivery_target": "chat-123:thread-456",
                                    "posted_delivery_target": "chat-123:thread-456",
                                    "evidence_ref": "plugin/surface/delivery-target-opening",
                                },
                                {
                                    "turn": 1,
                                    "speaker_selected_event_id": "evt_select_1",
                                    "speech_event_id": "evt_speech_1",
                                    "expected_delivery_target": "chat-123:thread-456",
                                    "posted_delivery_target": "chat-123:thread-456",
                                    "evidence_ref": "plugin/surface/delivery-target-turn-1",
                                },
                                {
                                    "turn": 2,
                                    "speaker_selected_event_id": "evt_select_2",
                                    "speech_event_id": "evt_speech_2",
                                    "expected_delivery_target": "chat-123:thread-456",
                                    "posted_delivery_target": "chat-123:thread-456",
                                    "evidence_ref": "plugin/surface/delivery-target-turn-2",
                                },
                                {
                                    "turn": 3,
                                    "speaker_selected_event_id": "evt_select_3",
                                    "speech_event_id": "evt_speech_3",
                                    "expected_delivery_target": "chat-123:thread-456",
                                    "posted_delivery_target": "chat-123:thread-456",
                                    "evidence_ref": "plugin/surface/delivery-target-turn-3",
                                },
                                {
                                    "turn": 4,
                                    "speaker_selected_event_id": "evt_select_closeout_macho",
                                    "speech_event_id": "evt_closeout_macho",
                                    "expected_delivery_target": "chat-123:thread-456",
                                    "posted_delivery_target": "chat-123:thread-456",
                                    "evidence_ref": "plugin/surface/delivery-target-closeout-macho",
                                },
                                {
                                    "turn": 5,
                                    "speaker_selected_event_id": "evt_select_closeout_seohwang",
                                    "speech_event_id": "evt_closeout_seohwang",
                                    "expected_delivery_target": "chat-123:thread-456",
                                    "posted_delivery_target": "chat-123:thread-456",
                                    "evidence_ref": (
                                        "plugin/surface/delivery-target-closeout-seohwang"
                                    ),
                                },
                                {
                                    "turn": 6,
                                    "speaker_selected_event_id": "evt_select_synthesis",
                                    "speech_event_id": "evt_synthesis_1",
                                    "expected_delivery_target": "chat-123:thread-456",
                                    "posted_delivery_target": "chat-123:thread-456",
                                    "evidence_ref": "plugin/surface/delivery-target-synthesis",
                                },
                            ],
                            "evidence_ref": "plugin/surface/delivery-targets",
                        },
                        "prompt_envelope": {
                            "prompt_envelope_pass": True,
                            "content_audit_separated": True,
                            "control_metadata_leaked": False,
                            "evidence_ref": "plugin/surface/prompt-envelope",
                        },
                        "dialogue_mode": {
                            "dialogue_mode_pass": True,
                            "participant_to_participant": True,
                            "moderator_substitute_turns": False,
                            "evidence_ref": "plugin/surface/dialogue-mode",
                        },
                        "drift": {
                            "status": "repair_forward",
                            "drift_detected": True,
                            "repaired_forward": True,
                            "unresolved_closeout": False,
                            "evidence_ref": "plugin/surface/drift-status",
                        },
                        "final_fail_closed": {
                            "final_fail_closed_pass": True,
                            "final_status": "repair_forward",
                            "fail_closed": True,
                            "evidence_ref": "plugin/surface/fail-closed-final",
                        },
                    },
                }
            }
        )
    )

    assert result["ok"] is True
    assert result["tool"] == "atn_discussion_activation_plan"
    assert result["live_readiness"] is False
    assert result["data"]["status"] == "ready_to_start"
    assert result["data"]["start_status"] == "ready_to_start"
    assert result["data"]["runfix3_acceptance_status"] == "proven"
    assert result["data"]["behavior_task_id"] == "plugin/RUNFIX3-003"
    assert result["data"]["visible_surface_readiness_report"]["exact_origin_binding_proven"] is True
    assert result["data"]["visible_surface_readiness_report"]["visible_turn_count_proven"] is True
    assert result["data"]["integrated_discussion_proof_report"]["status"] == "not_required"
    assert result["data"]["runfix3_live_thread_proof_report"]["status"] == "proven"
    assert (
        result["data"]["runfix3_live_thread_proof_report"]["selected_runner_proof"]["status"]
        == "proven"
    )
    assert (
        result["data"]["runfix3_live_thread_proof_report"]["participant_closeout_coverage"][
            "status"
        ]
        == "proven"
    )
    assert (
        result["data"]["runfix3_live_thread_proof_report"]["moderator_synthesis_coverage"]["status"]
        == "proven"
    )


def test_diagnostics_handler_rejects_invalid_session_id_before_transport() -> None:
    result = decode(
        handle_compatibility_diagnostics(
            {"session_id": ""},
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "session_id must be a non-empty string when present",
        "retryable": False,
    }


def test_stream_tail_handler_rejects_invalid_args_before_transport() -> None:
    factory = factory_for(
        {OP_VERSION_READ: BASE_VERSION_WITH_STREAM, OP_STREAM_TAIL: BASE_STREAM_TAIL}
    )

    missing_member = decode(handle_stream_tail({"session_id": "sess-1"}, client_factory=factory))
    empty_cursor = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1", "since_cursor": ""},
            client_factory=factory,
        )
    )
    bad_limit = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1", "limit": 1001},
            client_factory=factory,
        )
    )

    assert missing_member["ok"] is False
    assert missing_member["error"] == {
        "category": "validation",
        "message": "member must be a non-empty string",
        "retryable": False,
    }
    assert empty_cursor["ok"] is False
    assert empty_cursor["error"]["category"] == "validation"
    assert bad_limit["ok"] is False
    assert bad_limit["error"] == {
        "category": "validation",
        "message": "limit must be between 1 and 1000",
        "retryable": False,
    }


def test_handlers_reject_non_object_args_without_raising() -> None:
    status = decode(
        handle_daemon_status(
            [],
            client_factory=factory_for({OP_STATUS_READ: BASE_STATUS}),
        )
    )
    diagnostics = decode(
        handle_compatibility_diagnostics(
            [],
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )
    stream_tail = decode(
        handle_stream_tail(
            [],
            client_factory=factory_for(
                {OP_VERSION_READ: BASE_VERSION_WITH_STREAM, OP_STREAM_TAIL: BASE_STREAM_TAIL}
            ),
        )
    )

    assert status["ok"] is False
    assert status["error"]["category"] == "validation"
    assert diagnostics["ok"] is False
    assert diagnostics["error"]["category"] == "validation"
    assert stream_tail["ok"] is False
    assert stream_tail["error"]["category"] == "validation"


def test_handlers_reject_unknown_args_before_transport() -> None:
    status = decode(
        handle_daemon_status(
            {"unexpected": "x"},
            client_factory=factory_for({OP_STATUS_READ: BASE_STATUS}),
        )
    )
    diagnostics = decode(
        handle_compatibility_diagnostics(
            {"unexpected": "x"},
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )
    stream_tail = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1", "unexpected": "x"},
            client_factory=factory_for(
                {OP_VERSION_READ: BASE_VERSION_WITH_STREAM, OP_STREAM_TAIL: BASE_STREAM_TAIL}
            ),
        )
    )

    assert status["ok"] is False
    assert status["error"] == {
        "category": "validation",
        "message": "unsupported tool args: unexpected",
        "retryable": False,
    }
    assert diagnostics["ok"] is False
    assert diagnostics["error"] == {
        "category": "validation",
        "message": "unsupported tool args: unexpected",
        "retryable": False,
    }
    assert stream_tail["ok"] is False
    assert stream_tail["error"] == {
        "category": "validation",
        "message": "unsupported tool args: unexpected",
        "retryable": False,
    }


def test_stream_tail_handler_requires_stream_feature_before_tail_operation() -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITHOUT_STREAM, OP_STREAM_TAIL: BASE_STREAM_TAIL}
    )

    result = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1"},
            client_factory=lambda: DaemonClient(transport),
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "compatibility"
    assert transport.requests == [(OP_VERSION_READ, {"protocol_version": "atn-protocol-v1alpha0"})]


def test_stream_ack_handler_submits_ack_after_stream_feature_probe() -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_STREAM_ACK, OP_STREAM_ACK: BASE_STREAM_ACK_SUCCESS}
    )

    result = decode(
        handle_stream_ack(
            {
                "session_id": "sess-1",
                "member": "agent-1",
                "cursor": "cur_000000000012_evt_01HV",
                "command_id": "cmd-ack-1",
            },
            client_factory=factory_for_transport(transport),
        )
    )

    assert result == {
        "ok": True,
        "tool": "atn_stream_ack",
        "live_readiness": False,
        "data": {
            "command_id": "cmd-ack-1",
            "event_id": "evt-ack-1",
            "session_id": "sess-1",
            "request_id": "plugin-live-stream-ack",
            "deduplicated": False,
        },
    }
    assert transport.requests == [
        (OP_VERSION_READ, {"protocol_version": "atn-protocol-v1alpha0"}),
        (
            OP_STREAM_ACK,
            {
                "protocol_version": "atn-protocol-v1alpha0",
                "session_id": "sess-1",
                "member": "agent-1",
                "cursor": "cur_000000000012_evt_01HV",
                "command_id": "cmd-ack-1",
            },
        ),
    ]


def test_stream_ack_handler_requires_stream_ack_feature_before_ack_operation() -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_STREAM, OP_STREAM_ACK: BASE_STREAM_ACK_SUCCESS}
    )

    result = decode(
        handle_stream_ack(
            {
                "session_id": "sess-1",
                "member": "agent-1",
                "cursor": "cur_000000000012_evt_01HV",
                "command_id": "cmd-ack-1",
            },
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_stream_ack"
    assert result["error"]["category"] == "compatibility"
    assert "stream.ack" in result["error"]["message"]
    assert transport.requests == [(OP_VERSION_READ, {"protocol_version": "atn-protocol-v1alpha0"})]


@pytest.mark.parametrize("field", ["session_id", "member", "cursor", "command_id"])
def test_stream_ack_handler_rejects_missing_required_args_before_transport(field: str) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    args: dict[str, object] = {
        "session_id": "sess-1",
        "member": "agent-1",
        "cursor": "cur_000000000012_evt_01HV",
        "command_id": "cmd-ack-1",
    }
    del args[field]

    result = decode(handle_stream_ack(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["tool"] == "atn_stream_ack"
    assert result["error"] == {
        "category": "validation",
        "message": f"{field} must be a non-empty string",
        "retryable": False,
    }
    assert client_factory_called is False


def test_stream_ack_duplicate_command_id_is_sent_twice_without_local_dedupe() -> None:
    responses = iter(
        (
            BASE_STREAM_ACK_SUCCESS,
            {**BASE_STREAM_ACK_SUCCESS, "event_id": "evt-ack-2", "deduplicated": True},
        )
    )

    def ack(_: JsonObject | None) -> JsonObject:
        return next(responses)

    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_STREAM_ACK, OP_STREAM_ACK: ack}
    )
    args = {
        "session_id": "sess-1",
        "member": "agent-1",
        "cursor": "cur_000000000012_evt_01HV",
        "command_id": "cmd-ack-1",
    }

    first = decode(handle_stream_ack(args, client_factory=factory_for_transport(transport)))
    second = decode(handle_stream_ack(args, client_factory=factory_for_transport(transport)))

    assert first["data"]["deduplicated"] is False
    assert second["data"]["deduplicated"] is True
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_STREAM_ACK,
        OP_VERSION_READ,
        OP_STREAM_ACK,
    ]
    assert transport.requests[1][1] == transport.requests[3][1]


def test_handler_malformed_daemon_payload_fails_closed_as_protocol_error() -> None:
    result = decode(
        handle_daemon_status(
            {},
            client_factory=factory_for({OP_STATUS_READ: {"protocol_version": "wrong"}}),
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "compatibility"
    assert result["live_readiness"] is False


def test_stream_tail_handler_malformed_stream_payload_fails_closed() -> None:
    result = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1"},
            client_factory=factory_for(
                {
                    OP_VERSION_READ: BASE_VERSION_WITH_STREAM,
                    OP_STREAM_TAIL: {"protocol_version": "atn-protocol-v1alpha0", "frames": ["[]"]},
                }
            ),
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "protocol"
    assert result["live_readiness"] is False


def test_delegate_new_submits_delegate_new_envelope_with_caller_metadata() -> None:
    transport = StaticDaemonTransport({OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS})

    result = decode(
        handle_delegate_new(
            {
                "session_id": "sess-1",
                "moderator": "agent-mod",
                "assignee": "agent-impl",
                "title": "Implement DELRV-1",
                "task": "Add fake command envelope tools",
                "context": {"run_id": "run-1"},
                "participants": [{"id": "agent-mod"}, {"id": "agent-impl"}],
                "acceptance": ["tests pass"],
                "expected_outputs": ["summary"],
                "limits": {"no_live": True},
                "request_id": "req-1",
                "idempotency_key": "idem-1",
            },
            client_factory=factory_for_transport(transport),
        )
    )

    assert result == {
        "ok": True,
        "tool": "atn_delegate_new",
        "live_readiness": False,
        "data": {
            "command_id": "cmd-1",
            "event_id": "evt-1",
            "session_id": "sess-1",
            "request_id": "req-1",
        },
    }
    assert transport.requests == [
        (
            OP_COMMAND_SUBMIT,
            {
                "protocol_version": "atn-protocol-v1alpha0",
                "envelope_version": "kan-command-envelope-v1alpha0",
                "command": "delegate.new",
                "payload": {
                    "session_id": "sess-1",
                    "moderator": "agent-mod",
                    "assignee": "agent-impl",
                    "title": "Implement DELRV-1",
                    "task": "Add fake command envelope tools",
                    "context": {"run_id": "run-1"},
                    "participants": [{"id": "agent-mod"}, {"id": "agent-impl"}],
                    "acceptance": ["tests pass"],
                    "expected_outputs": ["summary"],
                    "limits": {"no_live": True},
                },
                "request_id": "req-1",
                "idempotency_key": "idem-1",
                "client_metadata": {
                    "name": "atn-plugin",
                    "version": "0.1.0",
                    "transport": "injected",
                },
            },
        )
    ]


@pytest.mark.parametrize(
    ("field", "bad_value", "message"),
    [
        ("context", {"nested": object()}, "context must contain only JSON-compatible values"),
        ("limits", {"nested": object()}, "limits must contain only JSON-compatible values"),
        (
            "participants",
            [{"nested": object()}],
            "participants must contain only JSON-compatible values",
        ),
        ("acceptance", [object()], "acceptance must contain only JSON-compatible values"),
        (
            "expected_outputs",
            [{"nested": object()}],
            "expected_outputs must contain only JSON-compatible values",
        ),
    ],
)
def test_delegate_new_rejects_nested_non_json_values_before_transport(
    field: str,
    bad_value: object,
    message: str,
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    args: dict[str, object] = {
        "session_id": "sess-1",
        "moderator": "agent-mod",
        "assignee": "agent-impl",
        "title": "Implement DELRV-1",
        "task": "Add fake command envelope tools",
        "context": {"run_id": "run-1"},
        "participants": [{"id": "agent-mod"}, {"id": "agent-impl"}],
        "acceptance": ["tests pass"],
        "expected_outputs": ["summary"],
        "limits": {"no_live": True},
        "request_id": "req-1",
        "idempotency_key": "idem-1",
    }
    args[field] = bad_value

    result = decode(handle_delegate_new(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["tool"] == "atn_delegate_new"
    assert result["error"] == {
        "category": "validation",
        "message": message,
        "retryable": False,
    }
    assert client_factory_called is False


@pytest.mark.parametrize(
    "command",
    ["delegate.review", "delegate.review_submit", "delegate.escalation_delivered"],
)
def test_delegate_action_submits_representative_closed_enum_commands(command: str) -> None:
    transport = StaticDaemonTransport({OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS})

    result = decode(
        handle_delegate_action(
            {
                "session_id": "sess-top",
                "command": command,
                "request_id": "req-1",
                "idempotency_key": "idem-1",
                "payload": {
                    "session_id": "payload-session-is-overridden",
                    "body": {"ok": True},
                },
            },
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is True
    operation, body = transport.requests[0]
    assert operation == OP_COMMAND_SUBMIT
    assert body is not None
    assert body["command"] == command
    assert body["request_id"] == "req-1"
    assert body["idempotency_key"] == "idem-1"
    assert body["payload"] == {"session_id": "sess-top", "body": {"ok": True}}


@pytest.mark.parametrize("command", ["delegate.request", "review", "delegate.unknown"])
def test_delegate_action_rejects_commands_outside_closed_enum_before_transport(
    command: str,
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    result = decode(
        handle_delegate_action(
            {
                "session_id": "sess-1",
                "command": command,
                "request_id": "req-1",
                "idempotency_key": "idem-1",
                "payload": {},
            },
            client_factory=client_factory,
        )
    )

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": f"unsupported delegate action command: {command}",
        "retryable": False,
    }
    assert client_factory_called is False


@pytest.mark.parametrize("idempotency_value", ["", None])
def test_delegate_action_rejects_missing_or_empty_idempotency_before_transport(
    idempotency_value: object,
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    base_args: dict[str, object] = {
        "session_id": "sess-1",
        "command": "delegate.review",
        "request_id": "req-1",
        "idempotency_key": "idem-1",
        "payload": {},
    }
    if idempotency_value is None:
        del base_args["idempotency_key"]
    else:
        base_args["idempotency_key"] = idempotency_value

    result = decode(handle_delegate_action(base_args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["error"]["category"] == "validation"
    assert result["error"]["message"] == "idempotency_key must be a non-empty string"
    assert client_factory_called is False


def test_delegate_action_preserves_structured_daemon_conflict_error() -> None:
    transport = StaticDaemonTransport(
        {
            OP_COMMAND_SUBMIT: {
                "ok": False,
                "error": {
                    "category": "conflict",
                    "message": "duplicate idempotency key",
                    "retryable": True,
                    "command_id": "cmd-old",
                    "session_id": "sess-1",
                    "request_id": "req-1",
                    "diagnostics": {"duplicate": True},
                },
            }
        }
    )

    result = decode(
        handle_delegate_action(
            {
                "session_id": "sess-1",
                "command": "delegate.review",
                "request_id": "req-1",
                "idempotency_key": "idem-1",
                "payload": {},
            },
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_delegate_action"
    assert result["error"] == {
        "category": "conflict",
        "message": "duplicate idempotency key",
        "retryable": True,
        "command_id": "cmd-old",
        "session_id": "sess-1",
        "request_id": "req-1",
        "diagnostics": {"duplicate": True},
    }


def test_delegate_new_malformed_daemon_response_fails_closed_as_protocol_error() -> None:
    result = decode(
        handle_delegate_new(
            {
                "session_id": "sess-1",
                "moderator": "agent-mod",
                "assignee": "agent-impl",
                "title": "Implement DELRV-1",
                "task": "Add fake command envelope tools",
                "context": {},
                "participants": [],
                "acceptance": [],
                "expected_outputs": [],
                "limits": {},
                "request_id": "req-1",
                "idempotency_key": "idem-1",
            },
            client_factory=factory_for({OP_COMMAND_SUBMIT: {"ok": True}}),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_delegate_new"
    assert result["error"]["category"] == "protocol"
    assert result["live_readiness"] is False


def test_delegate_handlers_fail_closed_without_client_factory() -> None:
    delegate_new = decode(
        handle_delegate_new(
            {
                "session_id": "sess-1",
                "moderator": "agent-mod",
                "assignee": "agent-impl",
                "title": "Implement DELRV-1",
                "task": "Add fake command envelope tools",
                "context": {},
                "participants": [],
                "acceptance": [],
                "expected_outputs": [],
                "limits": {},
                "request_id": "req-1",
                "idempotency_key": "idem-1",
            }
        )
    )
    delegate_action = decode(
        handle_delegate_action(
            {
                "session_id": "sess-1",
                "command": "delegate.review",
                "request_id": "req-1",
                "idempotency_key": "idem-1",
                "payload": {},
            }
        )
    )

    assert delegate_new["ok"] is False
    assert delegate_new["error"]["category"] == "unavailable"
    assert delegate_action["ok"] is False
    assert delegate_action["tool"] == "atn_delegate_action"
    assert delegate_action["error"]["category"] == "unavailable"


def _council_args(command: str, payload: JsonObject | None = None) -> JsonObject:
    if payload is None:
        payload = {
            "actor": "agent-mod",
            "command_id": f"cmd-{command.replace('.', '-')}",
            "payload": {"note": "ok"},
        }
    return {
        "session_id": "sess-council",
        "command": command,
        "request_id": f"req-{command.replace('.', '-')}",
        "idempotency_key": "idem-shared",
        "payload": payload,
    }


def _delivery_args(command: str, payload: JsonObject | None = None) -> JsonObject:
    if payload is None and command == "delegate.escalation_delivered":
        payload = {
            "escalation": "evt-escalation",
            "delivery_target": "origin",
            "platform": "hermes",
            "message_ref": "msg-1",
            "command_id": "cmd-delivered",
        }
    if payload is None:
        payload = {
            "escalation": "evt-escalation",
            "target": "telegram",
            "reason": "unreachable",
            "will_retry_targets": ["origin"],
            "command_id": "cmd-failed",
        }
    return {
        "session_id": "sess-delegate",
        "command": command,
        "request_id": f"req-{command.replace('.', '-')}",
        "idempotency_key": "idem-delivery",
        "payload": payload,
    }


TURN_BEARING_COUNCIL_CASES = (
    (
        "council.poll",
        "agent-mod",
        {"turn": 1, "research_timeout_sec": 600},
    ),
    (
        "council.hand_raise",
        "agent-1",
        {
            "turn": 2,
            "intent": "support",
            "reason": "The static fixture handoff is complete.",
        },
    ),
    (
        "council.grant",
        "agent-mod",
        {"turn": 3, "member": "agent-1", "selection_mode": "moderator_direct"},
    ),
    (
        "council.speak",
        "agent-1",
        {"turn": 4, "speech": "Canonical turn-bearing payloads must use turn."},
    ),
)


@pytest.mark.parametrize(
    ("command", "actor", "command_payload"),
    [
        ("council.attend", "agent-1", {"availability": "present"}),
        ("council.ready", "agent-1", {"summary": "ready"}),
        ("council.prepared_partial", "agent-2", {"summary": "partial", "blocked": True}),
        ("council.vote", "agent-2", {"choice": "approve"}),
    ],
)
def test_council_participant_commands_submit_after_feature_probe(
    command: str, actor: str, command_payload: JsonObject
) -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )
    command_id = f"cmd-{command.replace('.', '-')}"
    payload: JsonObject = {
        "actor": actor,
        "command_id": command_id,
        "payload": command_payload,
    }

    result = decode(
        handle_council_command(
            _council_args(command, payload),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is True
    assert transport.requests[0] == (
        OP_VERSION_READ,
        {"protocol_version": "atn-protocol-v1alpha0"},
    )
    operation, body = transport.requests[1]
    assert operation == OP_COMMAND_SUBMIT
    assert body is not None
    assert body["command"] == command
    assert body["request_id"] == f"req-{command.replace('.', '-')}"
    assert body["idempotency_key"] == "idem-shared"
    assert body["payload"] == {
        "session_id": "sess-council",
        "actor": actor,
        "command_id": command_id,
        "payload": command_payload,
    }


@pytest.mark.parametrize(
    ("command", "payload"),
    [
        (
            "council.new",
            {
                "session_id": "payload-session-is-overridden",
                "moderator": "agent-mod",
                "members": ["agent-1", "agent-2"],
                "title": "Static council",
                "request_context": {
                    "source": "discord_thread",
                    "requested_output_mode": "live_visible_thread",
                    "visible_output_required": True,
                },
                "surface": {
                    "kind": "discord_thread",
                    "platform": "discord",
                    "thread_id": "thread-1",
                },
                "event_id": "evt-council",
                "command_id": "cmd-council-new",
            },
        ),
        (
            "council.finalize",
            {"actor": "agent-mod", "command_id": "cmd-finalize", "payload": {"done": True}},
        ),
    ],
)
def test_council_moderator_commands_submit_after_feature_probe(
    command: str, payload: JsonObject
) -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )

    result = decode(
        handle_council_command(
            _council_args(command, payload),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is True
    operation, body = transport.requests[1]
    assert operation == OP_COMMAND_SUBMIT
    assert body is not None
    assert body["command"] == command
    assert cast(JsonObject, body["payload"])["session_id"] == "sess-council"


@pytest.mark.parametrize(
    ("command", "actor", "nested_payload"),
    TURN_BEARING_COUNCIL_CASES,
)
def test_council_turn_bearing_commands_preserve_turn_and_ids_without_round(
    command: str, actor: str, nested_payload: JsonObject
) -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )
    payload: JsonObject = {
        "actor": actor,
        "command_id": f"cmd-preserve-{command.replace('.', '-')}",
        "payload": nested_payload,
    }
    args = _council_args(command, payload)
    args["request_id"] = f"req-preserve-{command.replace('.', '-')}"
    args["idempotency_key"] = f"idem-preserve-{command.replace('.', '-')}"

    result = decode(
        handle_council_command(
            args,
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is True
    submitted = transport.requests[1][1]
    assert submitted is not None
    assert submitted["request_id"] == args["request_id"]
    assert submitted["idempotency_key"] == args["idempotency_key"]
    submitted_payload = cast(JsonObject, submitted["payload"])
    assert submitted_payload["command_id"] == payload["command_id"]
    assert submitted_payload["session_id"] == args["session_id"]
    daemon_payload = cast(JsonObject, submitted_payload["payload"])
    assert daemon_payload["turn"] == nested_payload["turn"]
    assert "round" not in daemon_payload


@pytest.mark.parametrize(
    ("command", "actor", "nested_payload"),
    TURN_BEARING_COUNCIL_CASES,
)
def test_council_turn_bearing_legacy_round_fails_closed_before_transport(
    command: str, actor: str, nested_payload: JsonObject
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    payload: JsonObject = {
        "actor": actor,
        "command_id": f"cmd-round-{command.replace('.', '-')}",
        "payload": {**nested_payload, "round": nested_payload["turn"]},
    }

    result = decode(
        handle_council_command(_council_args(command, payload), client_factory=client_factory)
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_council_command"
    assert result["error"]["category"] == "validation"
    assert (
        result["error"]["message"]
        == "payload.payload.round is unsupported for turn-bearing council commands; "
        "use payload.payload.turn"
    )
    assert client_factory_called is False


@pytest.mark.parametrize(
    ("command", "actor", "nested_payload"),
    TURN_BEARING_COUNCIL_CASES,
)
def test_council_turn_bearing_missing_turn_fails_closed_before_transport(
    command: str, actor: str, nested_payload: JsonObject
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    payload_without_turn = dict(nested_payload)
    payload_without_turn.pop("turn")
    payload: JsonObject = {
        "actor": actor,
        "command_id": f"cmd-missing-turn-{command.replace('.', '-')}",
        "payload": payload_without_turn,
    }

    result = decode(
        handle_council_command(_council_args(command, payload), client_factory=client_factory)
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_council_command"
    assert result["error"]["category"] == "validation"
    assert (
        result["error"]["message"]
        == "payload.payload.turn is required for turn-bearing council commands"
    )
    assert client_factory_called is False


@pytest.mark.parametrize("bad_turn", ["", True, {"turn": 1}])
def test_council_turn_bearing_invalid_turn_fails_closed_before_transport(
    bad_turn: object,
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    payload: JsonObject = {
        "actor": "agent-mod",
        "command_id": "cmd-invalid-turn",
        "payload": cast(JsonObject, {"turn": bad_turn, "research_timeout_sec": 600}),
    }

    result = decode(
        handle_council_command(
            _council_args("council.poll", payload), client_factory=client_factory
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_council_command"
    assert result["error"]["category"] == "validation"
    assert (
        result["error"]["message"]
        == "payload.payload.turn must be a non-empty string or integer for "
        "turn-bearing council commands"
    )
    assert client_factory_called is False


def test_council_hand_raise_requires_intent_or_reason_before_submit() -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )

    result = decode(
        handle_council_command(
            _council_args(
                "council.hand_raise",
                {
                    "actor": "agent-1",
                    "command_id": "cmd-hand-raise-missing-stance",
                    "payload": {"turn": 2, "topic": "risk"},
                },
            ),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_council_command"
    assert result["error"]["category"] == "validation"
    assert "intent or reason" in result["error"]["message"]
    assert transport.requests == []


def test_council_new_fails_closed_without_output_intent_before_submit() -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )
    result = decode(
        handle_council_command(
            _council_args(
                "council.new",
                {
                    "moderator": "agent-mod",
                    "members": ["agent-1", "agent-2"],
                    "title": "Undeclared local daemon bypass",
                    "request_context": {"source": "discord_thread"},
                    "surface": {
                        "kind": "discord_thread",
                        "platform": "discord",
                        "thread_id": "thread-1",
                    },
                    "event_id": "evt-council",
                    "command_id": "cmd-council-new",
                },
            ),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_council_command"
    assert result["error"]["category"] == "validation"
    assert "requested_output_mode" in result["error"]["message"]
    assert transport.requests == []


def test_council_new_explicit_non_visible_override_submits_without_surface() -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )
    payload: JsonObject = {
        "moderator": "agent-mod",
        "members": ["agent-1", "agent-2"],
        "title": "Explicit local diagnostics",
        "request_context": {
            "source": "operator",
            "requested_output_mode": "local-daemon-only",
            "explicit_non_visible_override": True,
            "override_reason": "주군 explicitly requested local-daemon-only diagnostics.",
        },
        "event_id": "evt-council-local-only",
        "command_id": "cmd-council-local-only",
    }

    result = decode(
        handle_council_command(
            _council_args("council.new", payload),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is True
    operation, body = transport.requests[1]
    assert operation == OP_COMMAND_SUBMIT
    assert body is not None
    assert body["command"] == "council.new"
    submitted_context = cast(JsonObject, cast(JsonObject, body["payload"])["request_context"])
    assert submitted_context == {
        "source": "operator",
        "requested_output_mode": "activation_planning_only",
        "explicit_non_visible_override": True,
        "override_reason": "주군 explicitly requested local-daemon-only diagnostics.",
    }


def test_council_new_output_mode_alias_is_canonicalized_before_submit() -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )
    payload: JsonObject = {
        "moderator": "agent-mod",
        "members": ["agent-1", "agent-2"],
        "title": "Explicit local diagnostics alias",
        "request_context": {
            "source": "operator",
            "output_mode": "local-daemon-only",
            "explicit_non_visible_override": True,
            "override_reason": "주군 explicitly requested local-daemon-only diagnostics.",
        },
        "event_id": "evt-council-local-only-alias",
        "command_id": "cmd-council-local-only-alias",
    }

    result = decode(
        handle_council_command(
            _council_args("council.new", payload),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is True
    submitted = transport.requests[1][1]
    assert submitted is not None
    submitted_payload = cast(JsonObject, submitted["payload"])
    submitted_context = cast(JsonObject, submitted_payload["request_context"])
    assert submitted_context["requested_output_mode"] == "activation_planning_only"
    assert "output_mode" not in submitted_context
    assert "requested_output" not in submitted_context


def test_council_new_conflicting_output_intent_fails_before_submit() -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )
    payload: JsonObject = {
        "moderator": "agent-mod",
        "members": ["agent-1", "agent-2"],
        "title": "Conflicting local diagnostics",
        "explicit_non_visible_override": False,
        "request_context": {
            "source": "operator",
            "requested_output_mode": "local-daemon-only",
            "explicit_non_visible_override": True,
            "override_reason": "주군 explicitly requested local-daemon-only diagnostics.",
        },
        "event_id": "evt-council-conflict",
        "command_id": "cmd-council-conflict",
    }

    result = decode(
        handle_council_command(
            _council_args("council.new", payload),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "validation"
    assert "must not conflict" in result["error"]["message"]
    assert transport.requests == []


def test_council_new_conflicting_output_mode_alias_fails_before_submit() -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )
    payload: JsonObject = {
        "moderator": "agent-mod",
        "members": ["agent-1", "agent-2"],
        "title": "Conflicting output mode aliases",
        "requested_output_mode": "live_visible_thread",
        "surface": {
            "kind": "discord_thread",
            "platform": "discord",
            "thread_id": "thread-conflict-alias",
        },
        "request_context": {
            "source": "discord_thread",
            "output_mode": "local-daemon-only",
        },
        "event_id": "evt-council-conflict-alias",
        "command_id": "cmd-council-conflict-alias",
    }

    result = decode(
        handle_council_command(
            _council_args("council.new", payload),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "validation"
    assert "output-mode aliases" in result["error"]["message"]
    assert transport.requests == []


@pytest.mark.parametrize(
    "command",
    ["delegate.escalation_delivered", "delegate.escalation_delivery_failed"],
)
def test_delivery_evidence_submits_after_feature_probe(command: str) -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )

    result = decode(
        handle_delivery_evidence(
            _delivery_args(command),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is True
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
    ]
    submitted = transport.requests[1][1]
    assert submitted is not None
    assert submitted["command"] == command
    assert submitted["request_id"] == f"req-{command.replace('.', '-')}"
    assert submitted["idempotency_key"] == "idem-delivery"
    assert cast(JsonObject, submitted["payload"])["session_id"] == "sess-delegate"


@pytest.mark.parametrize(
    ("handler", "args", "missing_feature"),
    [
        (
            handle_council_command,
            _council_args("council.ready"),
            "council.lifecycle",
        ),
        (
            handle_delivery_evidence,
            _delivery_args("delegate.escalation_delivered"),
            "delivery_evidence",
        ),
    ],
)
def test_cndis_handlers_fail_compatibility_before_submit_when_feature_missing(
    handler: Callable[..., str], args: JsonObject, missing_feature: str
) -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITHOUT_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )

    result = decode(handler(args, client_factory=factory_for_transport(transport)))

    assert result["ok"] is False
    assert result["error"]["category"] == "compatibility"
    assert missing_feature in result["error"]["message"]
    assert transport.requests == [(OP_VERSION_READ, {"protocol_version": "atn-protocol-v1alpha0"})]


@pytest.mark.parametrize(
    ("handler", "args", "message"),
    [
        (
            handle_council_command,
            _council_args("council.unknown"),
            "unsupported council command: council.unknown",
        ),
        (
            handle_council_command,
            _council_args("council.ready", {"actor": "agent-1", "payload": {}}),
            "payload.command_id must be a non-empty string",
        ),
        (
            handle_council_command,
            _council_args("council.new", {"command_id": "cmd"}),
            "payload.moderator must be a non-empty string",
        ),
        (
            handle_delivery_evidence,
            _delivery_args("delegate.unknown", {}),
            "unsupported delivery evidence command: delegate.unknown",
        ),
        (
            handle_delivery_evidence,
            _delivery_args("delegate.escalation_delivered", {"command_id": "cmd"}),
            "payload.escalation must be a non-empty string",
        ),
        (
            handle_delivery_evidence,
            _delivery_args(
                "delegate.escalation_delivery_failed",
                {"escalation": "evt", "command_id": "cmd"},
            ),
            "payload.target must be a non-empty string",
        ),
    ],
)
def test_cndis_handlers_reject_invalid_args_before_transport(
    handler: Callable[..., str], args: JsonObject, message: str
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    result = decode(handler(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["error"] == {"category": "validation", "message": message, "retryable": False}
    assert client_factory_called is False


def test_cndis_duplicate_idempotency_key_is_sent_twice_without_local_dedupe() -> None:
    responses = iter((BASE_COMMAND_SUCCESS, {**BASE_COMMAND_SUCCESS, "event_id": "evt-2"}))

    def submit(_: JsonObject | None) -> JsonObject:
        return next(responses)

    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: submit}
    )

    first = decode(
        handle_council_command(
            _council_args("council.ready"), client_factory=factory_for_transport(transport)
        )
    )
    second = decode(
        handle_council_command(
            _council_args("council.ready"), client_factory=factory_for_transport(transport)
        )
    )

    assert first["ok"] is True
    assert second["ok"] is True
    submit_bodies = [
        body for operation, body in transport.requests if operation == OP_COMMAND_SUBMIT
    ]
    assert len(submit_bodies) == 2
    assert submit_bodies[0] is not None
    assert submit_bodies[1] is not None
    assert submit_bodies[0]["idempotency_key"] == submit_bodies[1]["idempotency_key"]


def test_cndis_handler_preserves_structured_daemon_error_after_feature_probe() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_CNDIS,
            OP_COMMAND_SUBMIT: {
                "ok": False,
                "error": {
                    "category": "validation",
                    "message": "only the council moderator may perform this action",
                    "retryable": False,
                    "request_id": "req-council-ready",
                },
            },
        }
    )

    result = decode(
        handle_council_command(
            _council_args("council.ready"), client_factory=factory_for_transport(transport)
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_council_command"
    assert result["error"] == {
        "category": "validation",
        "message": "only the council moderator may perform this action",
        "retryable": False,
        "request_id": "req-council-ready",
    }


def test_cndis_malformed_daemon_response_fails_closed_after_feature_probe() -> None:
    result = decode(
        handle_delivery_evidence(
            _delivery_args("delegate.escalation_delivered"),
            client_factory=factory_for(
                {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: {"ok": True}}
            ),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_delivery_evidence"
    assert result["error"]["category"] == "protocol"


def _discord_tool_args(target: JsonObject | None = None) -> JsonObject:
    return {
        "content": "CNDIS-2 isolated Discord helper smoke",
        "target": target
        or {
            "channel_id": "discord-test-channel-123",
            "thread_id": "discord-test-thread-456",
            "dedicated_test_target": True,
            "label": "[Kkachi CNDIS-2 isolated E2E]",
            "cleanup_hint": "Delete CNDIS-2 helper test messages.",
        },
    }


def test_discord_send_message_handler_fails_closed_without_sender() -> None:
    from atn_plugin.tools import handle_discord_send_message

    result = decode(handle_discord_send_message(_discord_tool_args()))

    assert result["ok"] is False
    assert result["tool"] == "atn_discord_send_message"
    assert result["live_readiness"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "explicit Discord send_message sender is required; no live Discord fallback",
        "retryable": False,
    }


def test_discord_send_message_handler_rejects_missing_target_before_sender() -> None:
    from atn_plugin.discord_surface import (
        DiscordMessageResult,
        DiscordMessageTarget,
    )
    from atn_plugin.tools import handle_discord_send_message

    sender_called = False

    def sender(*, target: DiscordMessageTarget, content: str) -> DiscordMessageResult:
        nonlocal sender_called
        sender_called = True
        _ = (target, content)
        return DiscordMessageResult(message_id="msg-1", channel_id="discord-test-channel-123")

    result = decode(handle_discord_send_message({"content": "hello"}, send_message=sender))

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "target must be a JSON object",
        "retryable": False,
    }
    assert sender_called is False


def test_discord_send_message_handler_rejects_active_target_before_sender() -> None:
    from atn_plugin.discord_surface import (
        DiscordMessageResult,
        DiscordMessageTarget,
    )
    from atn_plugin.tools import handle_discord_send_message

    sender_called = False

    def sender(*, target: DiscordMessageTarget, content: str) -> DiscordMessageResult:
        nonlocal sender_called
        sender_called = True
        _ = (target, content)
        return DiscordMessageResult(message_id="msg-1", channel_id=target.channel_id)

    result = decode(
        handle_discord_send_message(
            _discord_tool_args(
                {
                    "channel_id": "current-thread",
                    "dedicated_test_target": True,
                    "label": "[Kkachi CNDIS-2 isolated E2E]",
                    "cleanup_hint": "Delete CNDIS-2 helper test messages.",
                }
            ),
            send_message=sender,
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "validation"
    assert "current or active Discord targets" in result["error"]["message"]
    assert sender_called is False


def test_discord_send_message_handler_calls_fake_sender_once_on_valid_target() -> None:
    from atn_plugin.discord_surface import (
        DiscordMessageResult,
        DiscordMessageTarget,
    )
    from atn_plugin.tools import handle_discord_send_message

    calls: list[tuple[DiscordMessageTarget, str]] = []

    def sender(*, target: DiscordMessageTarget, content: str) -> DiscordMessageResult:
        calls.append((target, content))
        return DiscordMessageResult(
            message_id="msg-1",
            channel_id=target.channel_id,
            thread_id=target.thread_id,
            message_ref="discord://discord-test-channel-123/discord-test-thread-456/msg-1",
            label=target.label,
            cleanup_hint=target.cleanup_hint,
        )

    result = decode(handle_discord_send_message(_discord_tool_args(), send_message=sender))

    assert result == {
        "ok": True,
        "tool": "atn_discord_send_message",
        "live_readiness": False,
        "data": {
            "message_id": "msg-1",
            "channel_id": "discord-test-channel-123",
            "thread_id": "discord-test-thread-456",
            "message_ref": "discord://discord-test-channel-123/discord-test-thread-456/msg-1",
            "label": "[Kkachi CNDIS-2 isolated E2E]",
            "cleanup_hint": "Delete CNDIS-2 helper test messages.",
        },
    }
    assert len(calls) == 1
    assert calls[0][1] == "CNDIS-2 isolated Discord helper smoke"
