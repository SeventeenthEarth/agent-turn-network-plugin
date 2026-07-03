from __future__ import annotations

import json

import pytest

from atn_plugin.activation_planner import build_discussion_activation_plan
from atn_plugin.tools import handle_discussion_activation_plan


def complete_plan() -> dict[str, object]:
    return {
        "schema_version": 1,
        "task_id": "plugin/RUNFIX-007",
        "control_dependency": {
            "task_id": "control/RUNFIX-005",
            "status": "completed/local-control",
            "evidence_ref": "control/docs/runfix-005-closeout.md",
        },
        "plugin_install": {
            "installed": True,
            "enabled": True,
            "tool_names": [
                "atn_daemon_status",
                "atn_discussion_activation_plan",
            ],
            "evidence_ref": "plugin-load-smoke",
        },
        "control_daemon": {
            "mode": "explicit",
            "socket_or_config_ref": "config.yaml live_transport.unix_socket_path",
            "compatibility_ref": "version.read feature_groups",
        },
        "participant_profiles": [
            {
                "profile": "macho",
                "effective_hermes": {
                    "tools_visible": True,
                    "bot_to_bot_enabled": False,
                    "evidence_ref": "profile/macho/effective-hermes",
                },
            },
            {
                "profile": "seohwang",
                "tools_visible": True,
                "bot_to_bot_enabled": True,
                "evidence_ref": "profile/seohwang/bot-to-bot-enabled",
            },
        ],
        "discord_parent_channel": {
            "channel_id": "parent-123",
            "allow_list_inheritance_proven": True,
            "proof_source": "gateway_parent_allow_list_inheritance",
            "proof_ref": "gateway/parent-inheritance-proof",
        },
        "planned_changes": ["dry-run allow-list for eligible profiles only"],
        "rollback": {"steps": ["remove dry-run allow-list changes"]},
        "verification_commands": [
            "make test-prepare",
            "make check-core-contract",
        ],
        "approval_gates": ["explicit live-local apply approval"],
        "operator_blockers": [],
        "evidence_labels": {
            "lifecycle_pass": "runfix-005 status projection",
        },
    }


def daemon_registry_membership(
    *,
    in_loaded_registry: bool = True,
    planned_reconcile: bool = False,
    mapping_unambiguous: bool = True,
    wrapper_resolves: bool = True,
    enabled: bool | None = True,
    evidence_ref: str | None = "control/registry/show",
) -> dict[str, object]:
    row: dict[str, object] = {
        "principal": "macho",
        "in_loaded_registry": in_loaded_registry,
        "mapping_unambiguous": mapping_unambiguous,
        "planned_reconcile": planned_reconcile,
        "wrapper_resolves": wrapper_resolves,
    }
    if enabled is not None:
        row["enabled"] = enabled
    membership: dict[str, object] = {
        "registry_loaded": True,
        "selected_moderator_principal": "macho",
        "participants": [row],
    }
    if evidence_ref is not None:
        membership["evidence_ref"] = evidence_ref
    return membership


def visible_author_guard_sample() -> dict[str, object]:
    return {
        "guard_surface": "pre_council_new_activation_plan",
        "runtime_enforcement": False,
        "profile_author_probes": [
            {
                "profile": "macho",
                "expected_author_source": "registry_snapshot",
                "expected_author_id": "bot-macho",
                "observed_bot_id": "bot-macho",
                "observed_username": "Macho",
                "source_env": "profile:macho/.env",
                "posting_path": "discord.gateway.profile_send",
                "same_path_probe": {
                    "evidence_ref": "probe/macho/same-path",
                    "message_id": "msg-probe-macho",
                    "surface": "discord_thread",
                    "posting_path": "discord.gateway.profile_send",
                },
                "shared_default_author": False,
                "shared_default_negative_proof_ref": "env/macho/no-shared-default",
                "profile_local_override_present": True,
            }
        ],
        "env_precedence_proof": {
            "order": ["shared_default", "default", "profile_local"],
            "per_key_source": [
                {
                    "profile": "macho",
                    "key": "DISCORD_BOT_ID",
                    "source": "profile_local",
                    "value_ref": "profile:macho/.env#DISCORD_BOT_ID",
                }
            ],
            "final_author_source": "profile_local",
        },
        "per_turn_visible_evidence": [
            {
                "discord_message_id": "msg-turn-1",
                "selected_member": "macho",
                "profile_author_id": "bot-macho",
                "posting_path": "discord.gateway.profile_send",
                "speech_event_id": "evt_speech_1",
            }
        ],
        "final_result": {
            "lifecycle": "pre_session_blocker_check_only",
            "visible_turns_posted": 1,
            "real_profile_gateway_replies": True,
            "selected_runner_labels": ["selected_runner_pass"],
            "shared_default_author_fallback_status": "none",
        },
    }


def complete_runfix_008_plan() -> dict[str, object]:
    plan = complete_plan()
    plan["task_id"] = "plugin/RUNFIX-008"
    plan["daemon_registry_membership"] = daemon_registry_membership()
    plan["operator_evidence"] = {
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
            "speech": "We should keep the pilot blocked until canonical speech linkage is proven.",
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
                    "rationale": "The prior traceability requirement remains the acceptance axis.",
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
    }
    plan["evidence_labels"] = {
        "lifecycle_pass": "runfix-005 status projection",
        "fallback_profile_pass": "manual/profile-diagnostic-reply",
        "selected_runner_pass": "runner/run-1/invocation-started",
        "visible_surface_pass": "unproven",
        "discussion_quality_pass": "argue counts present",
    }
    return plan


def complete_runfix_012_plan() -> dict[str, object]:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-012"
    plan["control_dependency"] = {
        "task_id": "control/RUNFIX-011",
        "status": "local implementation proof",
        "evidence_ref": "control/docs/roadmap.md#runfix-011",
    }
    plan["participant_runtime_readiness"] = {
        "source_mode": "explicit",
        "subscriber": {
            "subscriber": True,
            "fresh": True,
            "evidence_ref": "control/runtime/subscriber-presence",
        },
        "cursor_ack": {
            "fresh": True,
            "evidence_ref": "control/runtime/cursor-ack-fresh",
        },
        "heartbeat": {
            "fresh": True,
            "evidence_ref": "control/runtime/heartbeat-fresh",
        },
        "attendance": {
            "terminal_success": True,
            "terminal_status": "success",
            "fresh": True,
            "evidence_ref": "control/runtime/attendance-success",
        },
        "preparation": {
            "terminal_success": True,
            "terminal_status": "success",
            "fresh": True,
            "evidence_ref": "control/runtime/preparation-success",
        },
        "selected_runner": {
            "ready": True,
            "prerequisites_met": True,
            "fresh": True,
            "evidence_ref": "control/runtime/selected-runner-ready",
        },
        "visible_surface": {
            "proven": True,
            "fresh": True,
            "evidence_ref": "plugin/runtime/visible-surface-proof",
        },
    }
    return plan


def complete_hun_008_plan() -> dict[str, object]:
    plan = complete_runfix_012_plan()
    plan["task_id"] = "plugin/ATN-005"
    return plan


def complete_prior_task_plan(task_id: str) -> dict[str, object]:
    if task_id == "plugin/ATN-005":
        return complete_hun_008_plan()
    if task_id == "plugin/RUNFIX-017":
        return complete_runfix_017_plan()
    if task_id == "plugin/RUNFIX3-003":
        return complete_runfix3_003_plan()
    if task_id in {"plugin/RUNFIX-008", "plugin/RUNFIX-010"}:
        return complete_runfix_008_plan()
    return complete_plan()


def complete_runfix_017_plan() -> dict[str, object]:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-017"
    operator_evidence = plan["operator_evidence"]
    assert isinstance(operator_evidence, dict)
    operator_evidence["discussion_quality"] = {
        "quality_mode": "quality_required",
        "local_context_sufficient": True,
        "prior_claims": [
            {
                "event_id": "evt_speech_0",
                "claim_id": "T01.C1",
                "speaker": "seohwang",
                "summary": "Prior traceability remains the acceptance axis.",
                "available_stances": ["support", "challenge", "refine", "synthesize"],
            }
        ],
        "turns": [
            {
                "speech_event_id": "evt_speech_1",
                "is_opening_speech": False,
                "participant_response": operator_evidence["participant_response"],
            }
        ],
    }
    plan["evidence_labels"] = {
        "lifecycle_pass": "runfix-005 status projection",
        "fallback_profile_pass": "manual/profile-diagnostic-reply",
        "selected_runner_pass": "runner/run-1/invocation-started",
        "visible_surface_pass": "unproven",
        "discussion_quality_pass": "argue quality evidence",
    }
    return plan


def complete_runfix2_005_plan() -> dict[str, object]:
    plan = complete_runfix_017_plan()
    plan["task_id"] = "plugin/RUNFIX2-005"
    plan["integrated_discussion_proof"] = {
        "lifecycle": {
            "lifecycle_pass": True,
            "evidence_ref": "control/export/session-finalized.json",
        },
        "selected_runner": {
            "selected_member": "macho",
            "speaker_selected_event_id": "evt_select_1",
            "runner_invocation_started_ref": "control/events/runner-started",
            "runner_invocation_succeeded": True,
            "runner_invocation_succeeded_ref": "control/events/runner-succeeded",
        },
        "canonical_speech": {
            "speaker_selected_event_id": "evt_select_1",
            "speech_event_id": "evt_speech_1",
            "speaker": "macho",
            "evidence_ref": "control/events/speech-linkage",
        },
        "grant_turn_runtime_readiness": [
            {
                "turn": 1,
                "speaker_selected_event_id": "evt_select_1",
                "subscriber_present": True,
                "cursor_ack_fresh": True,
                "heartbeat_fresh": True,
                "attendance_terminal_success": True,
                "preparation_terminal_success": True,
                "selected_runner_prerequisites_met": True,
                "fresh": True,
                "evidence_ref": "control/runtime/grant-turn-1",
            }
        ],
        "visible_turns": {
            "max_discussion_turns": 3,
            "participant_count": 2,
            "expected_visible_turns": 7,
            "visible_turns_posted": 7,
            "evidence_ref": "control/export/summary_turn_accounting",
        },
        "visible_surface": {
            "visible_surface_pass": True,
            "evidence_ref": "plugin/surface/posted-turns",
        },
        "clean_transcript": {
            "clean_transcript_pass": True,
            "evidence_ref": "plugin/surface/clean-transcript",
            "audit_ids_in_visible_text": False,
        },
        "visible_closeout": {
            "visible_closeout_pass": True,
            "evidence_ref": "plugin/surface/visible-closeout",
        },
        "fallback_profile": {
            "fallback_profile_pass": True,
            "evidence_ref": "manual/profile-diagnostic",
            "missing_evidence": ["none; diagnostic sample only"],
        },
        "discussion_quality": {
            "discussion_quality_pass": True,
            "evidence_ref": "control/status/discussion-quality",
        },
        "final_labels": {
            "lifecycle_pass": {
                "pass": True,
                "evidence_ref": "control/export/session-finalized.json",
            },
            "selected_runner_pass": {
                "pass": True,
                "evidence_ref": "control/events/runner-succeeded",
            },
            "participant_runtime_ready_at_turns": {
                "pass": True,
                "evidence_ref": "control/runtime/grant-turn-1",
            },
            "visible_surface_pass": {
                "pass": True,
                "evidence_ref": "plugin/surface/posted-turns",
            },
            "clean_transcript_pass": {
                "pass": True,
                "evidence_ref": "plugin/surface/clean-transcript",
            },
            "visible_closeout_pass": {
                "pass": True,
                "evidence_ref": "plugin/surface/visible-closeout",
            },
            "fallback_profile_pass": {
                "pass": True,
                "evidence_ref": "manual/profile-diagnostic",
            },
            "discussion_quality_pass": {
                "pass": True,
                "evidence_ref": "control/status/discussion-quality",
            },
        },
    }
    return plan


def complete_runfix3_003_plan() -> dict[str, object]:
    plan = complete_runfix_017_plan()
    plan["task_id"] = "plugin/RUNFIX3-003"
    plan["request_context"] = {
        "source": "discord_thread",
        "chat_id": "chat-123",
        "thread_id": "thread-456",
    }
    participant_profiles = plan["participant_profiles"]
    assert isinstance(participant_profiles, list)
    second_profile = participant_profiles[1]
    assert isinstance(second_profile, dict)
    second_profile["bot_to_bot_enabled"] = False

    plan["visible_surface_readiness"] = {
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
        "evidence_ref": "discord/thread-visible-proof",
    }
    plan["daemon_registry_membership"] = {
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
    }
    plan["runfix3_live_thread_proof"] = {
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
                    "evidence_ref": "plugin/surface/delivery-target-closeout-seohwang",
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
    }
    return plan


def complete_lvcor_005_plan() -> dict[str, object]:
    plan = complete_runfix_017_plan()
    plan["task_id"] = "plugin/LVCOR-005"
    plan["participant_profiles"] = [
        {
            "profile": "macho",
            "effective_hermes": {
                "tools_visible": True,
                "bot_to_bot_enabled": False,
                "evidence_ref": "profile/macho/effective-hermes",
            },
        },
        {
            "profile": "seohwang",
            "effective_hermes": {
                "tools_visible": True,
                "bot_to_bot_enabled": False,
                "evidence_ref": "profile/seohwang/effective-hermes",
            },
        },
        {
            "profile": "jonghoe",
            "effective_hermes": {
                "tools_visible": True,
                "bot_to_bot_enabled": False,
                "evidence_ref": "profile/jonghoe/effective-hermes",
            },
        },
        {
            "profile": "manchong",
            "effective_hermes": {
                "tools_visible": True,
                "bot_to_bot_enabled": False,
                "evidence_ref": "profile/manchong/effective-hermes",
            },
        },
    ]
    plan["lvcor_full_shape_acceptance_proof"] = {
        "dependency_rows": [
            {
                "task_id": "control/LVCOR-001",
                "status": "completed/control-local",
                "evidence_ref": "control/lvcor-001/final-report.md",
            },
            {
                "task_id": "control/LVCOR-002",
                "status": "completed/control-local",
                "evidence_ref": "control/lvcor-002/final-report.md",
            },
            {
                "task_id": "control/LVCOR-003",
                "status": "completed/control-local",
                "evidence_ref": "control/lvcor-003/final-report.md",
            },
            {
                "task_id": "plugin/LVCOR-004",
                "status": "completed/local-proof",
                "evidence_ref": "plugin/lvcor-004/final-report.md",
            },
        ],
        "scenario_rows": [
            {
                "scenario_id": "lvcor-15-4-21",
                "acceptance_label": "finalized_success_candidate",
                "max_discussion_turns": 15,
                "participant_count": 4,
                "expected_visible_turns": 21,
                "accepted_visible_turns": 21,
                "visible_turn_count_proven": True,
                "discussion_turns_completed": 15,
                "opening_turn": 0,
                "opening_turn_proven": True,
                "participant_closeout_count": 4,
                "participant_closeout_complete": True,
                "terminal_synthesis_turn": 20,
                "terminal_phase": "finalized",
                "moderator_synthesis_proven": True,
                "runnerless_manual_selected_turn_count": 0,
                "evidence_ref": "plugin/lvcor-005/15-4-21",
            },
            {
                "scenario_id": "lvcor-5-2-9",
                "acceptance_label": "finalized_success_candidate",
                "max_discussion_turns": 5,
                "participant_count": 2,
                "expected_visible_turns": 9,
                "posted_visible_turns": 9,
                "visible_turn_count_proven": True,
                "discussion_turns_completed": 5,
                "opening_turn": 0,
                "opening_turn_proven": True,
                "participant_closeout_count": 2,
                "participant_closeout_complete": True,
                "terminal_synthesis_turn": 8,
                "terminal_phase": "finalized",
                "moderator_synthesis_proven": True,
                "runnerless_manual_selected_turn_count": 0,
                "evidence_ref": "plugin/lvcor-005/5-2-9",
            },
        ],
    }
    return plan


def complete_newfix_006_plan(
    *,
    prompt_status: str = "implementation_complete/review_pending",
    timeout_status: str = "implementation_complete/review_pending",
    configured_timeout_sec: int = 120,
    effective_timeout_sec: int = 120,
    approved_alternative: bool = False,
    approval_basis: str | None = None,
    drift_blocked: bool = False,
) -> dict[str, object]:
    plan = complete_runfix3_003_plan()
    plan["task_id"] = "plugin/NEWFIX-006"
    plan["selected_runner_prompt_evidence"] = {
        "task_id": "control/NEWFIX-004",
        "status": prompt_status,
        "evidence_ref": "control/status/newfix-004",
        "result": "pass",
        "prompt_context_sha256": "prompt-sha-256",
        "own_history_source_event_ids": ["evt-own-1", "evt-own-2"],
    }
    plan["selected_runner_timeout_evidence"] = {
        "task_id": "control/NEWFIX-005",
        "status": timeout_status,
        "evidence_ref": "control/status/newfix-005",
        "policy_required": True,
        "configured_timeout_sec": configured_timeout_sec,
        "effective_timeout_sec": effective_timeout_sec,
        "approved_alternative": approved_alternative,
        "approval_basis": approval_basis,
        "compliant": True,
        "drift_blocked": drift_blocked,
    }
    return plan


def complete_runfix_015_plan() -> dict[str, object]:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-015"
    plan["visible_author_guard"] = {
        "guard_surface": "pre_council_new_activation_plan",
        "runtime_enforcement": False,
        "profile_author_probes": [
            {
                "profile": "macho",
                "expected_author_source": "registry_snapshot",
                "expected_author_id": "bot-macho",
                "observed_bot_id": "bot-macho",
                "observed_username": "Macho",
                "source_env": "profile:macho/.env",
                "posting_path": "discord.gateway.profile_send",
                "same_path_probe": {
                    "evidence_ref": "probe/macho/same-path",
                    "message_id": "msg-probe-macho",
                    "surface": "discord_thread",
                    "posting_path": "discord.gateway.profile_send",
                },
                "shared_default_author": False,
                "shared_default_negative_proof_ref": "env/macho/no-shared-default",
                "profile_local_override_present": True,
            }
        ],
        "env_precedence_proof": {
            "order": ["shared_default", "default", "profile_local"],
            "per_key_source": [
                {
                    "profile": "macho",
                    "key": "DISCORD_BOT_ID",
                    "source": "profile_local",
                    "value_ref": "profile:macho/.env#DISCORD_BOT_ID",
                }
            ],
            "final_author_source": "profile_local",
        },
        "per_turn_visible_evidence": [
            {
                "discord_message_id": "msg-turn-1",
                "selected_member": "macho",
                "profile_author_id": "bot-macho",
                "posting_path": "discord.gateway.profile_send",
                "speech_event_id": "evt_speech_1",
            }
        ],
        "final_result": {
            "lifecycle": "pre_session_blocker_check_only",
            "visible_turns_posted": 1,
            "real_profile_gateway_replies": True,
            "selected_runner_labels": ["selected_runner_pass"],
            "shared_default_author_fallback_status": "none",
        },
    }
    return plan


def test_complete_dry_run_is_ready_for_approval_without_live_readiness() -> None:
    report = build_discussion_activation_plan(complete_plan())

    assert report["status"] == "ready_for_approval"
    assert report["task_id"] == "plugin/RUNFIX-007"
    assert report["behavior_task_id"] == "plugin/RUNFIX-007"
    assert report["live_readiness"] is False
    assert report["eligible_profiles"] == [
        {
            "profile": "macho",
            "reason": "effective_hermes_tools_visible_and_bot_to_bot_disabled",
            "evidence_ref": "profile/macho/effective-hermes",
        }
    ]
    assert report["excluded_profiles"] == [
        {
            "profile": "seohwang",
            "reason": "bot_to_bot_enabled",
            "evidence_ref": "profile/seohwang/bot-to-bot-enabled",
            "remediation": (
                "Disable bot-to-bot replies for this profile or omit it from the "
                "ATN discussion allow-list."
            ),
        }
    ]
    assert report["blocked_profiles"] == []
    assert report["allow_list_targets"] == ["macho"]
    assert report["profile_remediation"] == {
        "excluded": report["excluded_profiles"],
        "blocked": [],
    }
    assert report["parent_channel_plan"] == {
        "channel_id": "parent-123",
        "allow_list_inheritance_proven": True,
        "proof_ref": "gateway/parent-inheritance-proof",
        "proof_source": "gateway_parent_allow_list_inheritance",
        "thread_allow_list_behavior_proven": True,
        "remediation": (
            "Provide explicit Hermes/gateway proof that parent-channel allow-list "
            "inheritance covers newly created discussion threads."
        ),
    }
    assert report["blockers"] == []
    assert report["dry_run_actions"] == ["dry-run allow-list for eligible profiles only"]
    assert report["rollback"] == ["remove dry-run allow-list changes"]
    assert report["verification_commands"] == ["make test-prepare", "make check-core-contract"]
    assert report["required_approvals"] == ["explicit live-local apply approval"]
    assert report["evidence_labels"] == {
        "lifecycle_pass": "runfix-005 status projection",
        "fallback_profile_pass": "unproven",
        "selected_runner_pass": "unproven",
        "visible_surface_pass": "unproven",
        "discussion_quality_pass": "unproven",
    }
    assert {item["fallback"] for item in report["fallback_audit"]} == {
        "hidden_plugin_to_cli_subprocess_fallback",
        "current_hermes_or_discord_inference",
        "manual_profile_replies_as_full_atn_success",
        "daemon_startup_or_discovery",
        "profile_gateway_provider_auth_token_model_mutation",
        "codex_exec",
        "generic_openai_sdk",
        "raw_app_server_transport",
        "kab_native_codex",
    }
    assert all(item["allowed"] is False for item in report["fallback_audit"])
    assert report["participant_argue_response_template"]["required_fields"] == [
        "speech",
        "claims[]",
        "stance_links[]",
        "contribution_type",
        "new_axis_reason",
    ]
    assert report["operator_evidence_report"]["runner_evidence"]["status"] == "unproven"
    assert report["activation_evidence_model_report"] == {
        "task_id": "plugin/ATN-005",
        "public_tool_name": "atn_discussion_activation_plan",
        "legacy_public_aliases_allowed": False,
        "historical_dependency_labels": [
            "control/RUNFIX-005",
            "control/RUNFIX-011",
            "control/RUNFIX-018",
        ],
        "readiness_axes": {
            "plugin_install_tool_visibility": "plugin_install",
            "daemon_socket_config_compatibility": "control_daemon",
            "profile_gateway_visibility": "participant_profiles",
            "visible_surface_readiness": "visible_surface_readiness_report",
            "selected_runner_runtime_proof": "participant_runtime_readiness_report",
            "final_live_readiness_claim": "live_readiness_false",
        },
        "local_proof_only": True,
        "live_readiness": False,
    }


def test_legacy_kan_activation_tool_name_does_not_satisfy_visibility() -> None:
    plan = complete_plan()
    install = plan["plugin_install"]
    assert isinstance(install, dict)
    install["tool_names"] = ["kan_discussion_activation_plan"]

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert {
        "code": "activation_tool_visibility_missing",
        "owner": "plugin",
        "message": "atn_discussion_activation_plan must be visible in plugin_install.tool_names.",
    } in report["blockers"]


def test_runfix_006_task_id_remains_accepted_with_runfix_007_behavior_label() -> None:
    plan = complete_plan()
    plan["task_id"] = "plugin/RUNFIX-006"

    report = build_discussion_activation_plan(plan)

    assert report["task_id"] == "plugin/RUNFIX-006"
    assert report["behavior_task_id"] == "plugin/RUNFIX-007"
    assert report["status"] == "ready_for_approval"


def test_runfix_010_defaults_to_live_visible_and_blocks_without_surface_evidence() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan.pop("request_context", None)
    plan.pop("visible_surface_readiness", None)

    report = build_discussion_activation_plan(plan)

    assert report["requested_output_mode"] == "live_visible_thread"
    assert report["status"] == "blocked"
    assert report["start_status"] == "blocked"
    blockers = report["blockers"]
    assert isinstance(blockers, list)
    assert any(
        isinstance(blocker, dict) and blocker["code"] == "visible_surface_readiness_missing"
        for blocker in blockers
    )


def test_discord_origin_activation_planning_only_requires_explicit_non_visible_override() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {
        "source": "discord_thread",
        "requested_output_mode": "activation_planning_only",
    }

    report = build_discussion_activation_plan(plan)

    assert report["requested_output_mode"] == "activation_planning_only"
    assert report["status"] == "blocked"
    blockers = report["blockers"]
    assert isinstance(blockers, list)
    assert any(
        isinstance(blocker, dict) and blocker["code"] == "non_visible_output_override_missing"
        for blocker in blockers
    )


def test_whitespace_override_reason_does_not_satisfy_non_visible_override() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {
        "source": "discord_thread",
        "requested_output_mode": "activation_planning_only",
        "explicit_non_visible_override": True,
        "override_reason": "   ",
    }

    report = build_discussion_activation_plan(plan)

    assert report["requested_output_mode"] == "activation_planning_only"
    assert report["status"] == "blocked"
    readiness_report = report["visible_surface_readiness_report"]
    assert isinstance(readiness_report, dict)
    assert readiness_report["override_reason"] is None
    blockers = report["blockers"]
    assert isinstance(blockers, list)
    assert any(
        isinstance(blocker, dict) and blocker["code"] == "non_visible_output_override_missing"
        for blocker in blockers
    )


def test_explicit_local_daemon_override_keeps_non_visible_mode_diagnostic_only() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {
        "source": "discord_thread",
        "requested_output_mode": "activation_planning_only",
        "explicit_non_visible_override": True,
        "override_reason": "주군 explicitly requested a local-daemon-only diagnostic rehearsal.",
    }

    report = build_discussion_activation_plan(plan)

    assert report["requested_output_mode"] == "activation_planning_only"
    readiness_report = report["visible_surface_readiness_report"]
    assert isinstance(readiness_report, dict)
    assert readiness_report["explicit_non_visible_override"] is True
    assert report["status"] == "ready_for_approval"
    assert report["start_authority"] == "explicit_operator_approval_required"


@pytest.mark.parametrize(
    ("requested_mode", "canonical_mode"),
    [
        ("artifact_only", "artifact_only"),
        ("daemon_cli_actor_speech", "daemon_cli_actor_speech"),
        ("transcript/export-only", "artifact_only"),
        ("transcript_export_only", "artifact_only"),
        ("local-daemon-only", "activation_planning_only"),
        ("local_daemon_only", "activation_planning_only"),
    ],
)
def test_explicit_non_visible_override_reason_is_sufficient_for_supported_modes(
    requested_mode: str, canonical_mode: str
) -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {
        "source": "discord_thread",
        "requested_output_mode": requested_mode,
        "explicit_non_visible_override": True,
        "override_reason": f"주군 explicitly requested {requested_mode} diagnostic output.",
    }

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "ready_for_approval"
    assert report["requested_output_mode"] == canonical_mode
    blockers = report["blockers"]
    assert isinstance(blockers, list)
    assert not any(
        isinstance(blocker, dict) and blocker["code"] == "artifact_only_confirmation_missing"
        for blocker in blockers
    )


@pytest.mark.parametrize(
    "task_id",
    [
        "plugin/RUNFIX-006",
        "plugin/RUNFIX-007",
        "plugin/RUNFIX-008",
        "plugin/RUNFIX-010",
        "plugin/RUNFIX-017",
        "plugin/ATN-005",
    ],
)
def test_prior_runfix_task_ids_remain_accepted(task_id: str) -> None:
    plan = complete_prior_task_plan(task_id)
    plan["task_id"] = task_id
    if task_id == "plugin/RUNFIX-010":
        plan["request_context"] = {
            "source": "operator",
            "requested_output_mode": "activation_planning_only",
            "explicit_non_visible_override": True,
            "override_reason": "주군 explicitly requested local-only activation planning proof.",
        }

    report = build_discussion_activation_plan(plan)

    assert report["task_id"] == task_id
    assert report["status"] == "ready_for_approval"
    assert report["live_readiness"] is False


def test_hun_008_is_local_proof_only_even_for_discord_origin_request() -> None:
    plan = complete_hun_008_plan()
    plan["request_context"] = {"source": "discord_thread"}

    report = build_discussion_activation_plan(plan)

    assert report["task_id"] == "plugin/ATN-005"
    assert report["behavior_task_id"] == "plugin/ATN-005"
    assert report["status"] == "ready_for_approval"
    assert report["start_authority"] == "explicit_operator_approval_required"
    assert report["live_readiness"] is False
    assert report["requested_output_mode"] == "live_visible_thread"
    assert report["visible_surface_readiness_report"]["ready"] is False
    assert report["participant_runtime_readiness_report"]["ready"] is True
    assert report["activation_evidence_model_report"]["legacy_public_aliases_allowed"] is False


@pytest.mark.parametrize(
    ("task_id", "status"),
    [
        ("control/RUNFIX-005", "completed/local-control"),
        ("control/RUNFIX-011", "local implementation proof"),
        ("control/RUNFIX-018", "local-control"),
    ],
)
def test_hun_008_control_dependency_accepts_historical_labels(task_id: str, status: str) -> None:
    plan = complete_hun_008_plan()
    plan["control_dependency"] = {
        "task_id": task_id,
        "status": status,
        "evidence_ref": f"control/docs/roadmap.md#{task_id.removeprefix('control/')}",
    }

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "ready_for_approval"
    assert report["behavior_task_id"] == "plugin/ATN-005"
    assert report["live_readiness"] is False
    assert task_id in report["activation_evidence_model_report"]["historical_dependency_labels"]


@pytest.mark.parametrize(
    ("control_dependency", "blocker_code"),
    [
        (None, "control_dependency_missing"),
        (
            {
                "task_id": "control/RUNFIX-999",
                "status": "local-control",
                "evidence_ref": "control/docs/roadmap.md#runfix-999",
            },
            "control_dependency_task_mismatch",
        ),
        (
            {
                "task_id": "control/RUNFIX-018",
                "status": "planned",
                "evidence_ref": "control/docs/roadmap.md#runfix-018",
            },
            "control_dependency_not_completed",
        ),
        (
            {
                "task_id": "control/RUNFIX-018",
                "status": "local-control",
            },
            "control_dependency_evidence_missing",
        ),
        (
            {
                "task_id": "control/RUNFIX-018",
                "status": "local-control",
                "evidence_ref": "",
            },
            "control_dependency_evidence_missing",
        ),
    ],
)
def test_hun_008_control_dependency_invalid_evidence_fails_closed(
    control_dependency: object, blocker_code: str
) -> None:
    plan = complete_hun_008_plan()
    if control_dependency is None:
        plan.pop("control_dependency")
    else:
        plan["control_dependency"] = control_dependency

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["live_readiness"] is False
    assert any(blocker["code"] == blocker_code for blocker in report["blockers"])


def test_runfix_017_exposes_prior_claim_targets_and_quality_report() -> None:
    report = build_discussion_activation_plan(complete_runfix_017_plan())

    assert report["status"] == "ready_for_approval"
    assert report["task_id"] == "plugin/RUNFIX-017"
    assert report["behavior_task_id"] == "plugin/RUNFIX-017"
    assert report["live_readiness"] is False
    targets = report["participant_argue_response_template"]["prior_claim_graph_targets"]
    assert targets["required_authority_fields"] == ["event_id"]
    assert targets["optional_authority_fields"] == ["claim_id"]
    assert targets["prompt_guidance_fields"] == ["speaker", "summary", "available_stances"]
    assert "responds_to_event_id" in targets["validation_rule"]
    assert report["operator_evidence_report"]["runfix_task_id"] == "plugin/RUNFIX-017"
    discussion_quality = report["operator_evidence_report"]["discussion_quality"]
    assert discussion_quality["status"] == "proven"
    assert discussion_quality["discussion_quality_pass"] is True
    assert discussion_quality["valid_stance_link_count"] == 1
    assert discussion_quality["orphan_speech_count"] == 0
    assert report["evidence_labels"]["lifecycle_pass"] == "runfix-005 status projection"
    assert report["evidence_labels"]["discussion_quality_pass"] == "argue quality evidence"


def test_runfix2_005_complete_integrated_proof_is_ready_without_live_readiness() -> None:
    report = build_discussion_activation_plan(complete_runfix2_005_plan())

    assert report["status"] == "ready_for_approval"
    assert report["task_id"] == "plugin/RUNFIX2-005"
    assert report["behavior_task_id"] == "plugin/RUNFIX2-005"
    assert report["live_readiness"] is False
    proof = report["integrated_discussion_proof_report"]
    assert proof["status"] == "proven"
    assert proof["lifecycle_pass"]["status"] == "proven"
    assert proof["selected_runner_pass"]["status"] == "proven"
    assert proof["selected_runner_pass"]["canonical_speech"]["status"] == "proven"
    assert proof["participant_runtime_ready_at_turns"]["status"] == "proven"
    assert proof["visible_turn_count"] == {
        "status": "proven",
        "max_discussion_turns": 3,
        "participant_count": 2,
        "expected_visible_turns": 7,
        "visible_turns_posted": 7,
        "evidence_ref": "control/export/summary_turn_accounting",
    }
    assert proof["visible_surface_pass"]["status"] == "proven"
    assert proof["clean_transcript_pass"]["status"] == "proven"
    assert proof["visible_closeout_pass"]["status"] == "proven"
    assert proof["fallback_profile_pass"]["status"] == "diagnostic_only"
    assert proof["fallback_profile_pass"]["full_atn_success"] is False
    assert proof["discussion_quality_pass"]["status"] == "proven"
    assert proof["final_labels"]["status"] == "proven"


def test_runfix3_003_complete_live_thread_proof_is_ready_without_live_readiness() -> None:
    report = build_discussion_activation_plan(complete_runfix3_003_plan())

    assert report["status"] == "ready_to_start"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "proven"
    assert report["task_id"] == "plugin/RUNFIX3-003"
    assert report["behavior_task_id"] == "plugin/RUNFIX3-003"
    assert report["live_readiness"] is False
    assert report["visible_surface_readiness_report"]["exact_origin_binding_proven"] is True
    assert report["visible_surface_readiness_report"]["visible_turn_count_proven"] is True
    assert report["integrated_discussion_proof_report"]["status"] == "not_required"
    proof = report["runfix3_live_thread_proof_report"]
    assert proof["status"] == "proven"
    assert proof["selected_runner_proof"] == {
        "status": "proven",
        "selected_member": "macho",
        "speaker_selected_event_id": "evt_select_1",
        "runner_invocation_started_ref": "control/runner-started-1",
        "runner_invocation_succeeded_ref": "control/runner-succeeded-1",
        "speech_event_id": "evt_speech_1",
        "delivery_target_match": True,
        "evidence_ref": "control/selected-runner-proof-turn-1",
    }
    assert proof["participant_closeout_coverage"] == {
        "status": "proven",
        "expected_participants": ["macho", "seohwang"],
        "closed_out_participants": ["macho", "seohwang"],
        "missing_participants": [],
        "evidence_ref": "plugin/surface/participant-closeouts",
    }
    assert proof["moderator_synthesis_coverage"] == {
        "status": "proven",
        "synthesis_posted": True,
        "evidence_ref": "plugin/surface/moderator-synthesis",
    }
    assert proof["delivery_target_proof"]["status"] == "proven"
    assert proof["delivery_target_proof"]["aggregate_match"] is True
    assert proof["delivery_target_proof"]["evidence_ref"] == "plugin/surface/delivery-targets"
    assert all(row["match"] is True for row in proof["delivery_target_rows"])
    assert proof["prompt_envelope_proof"] == {
        "status": "proven",
        "content_audit_separated": True,
        "control_metadata_leaked": False,
        "evidence_ref": "plugin/surface/prompt-envelope",
    }
    assert proof["dialogue_mode_proof"] == {
        "status": "proven",
        "participant_to_participant": True,
        "moderator_substitute_turns": False,
        "evidence_ref": "plugin/surface/dialogue-mode",
    }
    assert proof["drift_status"] == {
        "status": "proven",
        "drift_detected": True,
        "repaired_forward": True,
        "unresolved_closeout": False,
        "evidence_ref": "plugin/surface/drift-status",
    }
    assert proof["fail_closed_final_status"] == {
        "status": "proven",
        "final_status": "repair_forward",
        "fail_closed": True,
        "evidence_ref": "plugin/surface/fail-closed-final",
    }


def test_lvcor_005_full_shape_acceptance_proof_requires_both_success_shapes() -> None:
    report = build_discussion_activation_plan(complete_lvcor_005_plan())

    assert report["status"] == "ready_for_approval"
    assert report["start_status"] == "ready_for_approval"
    assert report["task_id"] == "plugin/LVCOR-005"
    assert report["behavior_task_id"] == "plugin/LVCOR-005"
    assert report["live_readiness"] is False
    proof = report["lvcor_full_shape_acceptance_proof_report"]
    assert proof["status"] == "proven"
    assert proof["label_statuses"]["finalized_success_candidate"] == {
        "status": "proven",
        "covered_shapes": ["15/4/21", "5/2/9"],
        "missing_shapes": [],
    }
    assert proof["label_statuses"]["unresolved_terminal_blocked"] == {
        "status": "not_supplied",
        "scenario_ids": [],
    }


def test_lvcor_005_missing_5_2_9_shape_fails_closed() -> None:
    plan = complete_lvcor_005_plan()
    proof = plan["lvcor_full_shape_acceptance_proof"]
    assert isinstance(proof, dict)
    rows = proof["scenario_rows"]
    assert isinstance(rows, list)
    rows.pop()

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["lvcor_full_shape_acceptance_proof_report"]["status"] == "blocked"
    assert any(blocker["code"] == "lvcor_required_shape_missing" for blocker in report["blockers"])


def test_lvcor_005_hard_coded_t20_assumption_for_5_2_fails_closed() -> None:
    plan = complete_lvcor_005_plan()
    proof = plan["lvcor_full_shape_acceptance_proof"]
    assert isinstance(proof, dict)
    rows = proof["scenario_rows"]
    assert isinstance(rows, list)
    second_row = rows[1]
    assert isinstance(second_row, dict)
    second_row["terminal_synthesis_turn"] = 20

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert (
        report["lvcor_full_shape_acceptance_proof_report"]["required_shapes"][1]["status"]
        == "missing"
    )
    assert any(
        blocker["code"] == "lvcor_terminal_synthesis_turn_mismatch"
        for blocker in report["blockers"]
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("posted_visible_turns", 8),
        ("visible_turn_count_proven", False),
    ],
)
def test_lvcor_005_visible_turn_count_mismatch_or_unproven_fails_closed(
    field: str, value: object
) -> None:
    plan = complete_lvcor_005_plan()
    proof = plan["lvcor_full_shape_acceptance_proof"]
    assert isinstance(proof, dict)
    rows = proof["scenario_rows"]
    assert isinstance(rows, list)
    second_row = rows[1]
    assert isinstance(second_row, dict)
    second_row.pop("accepted_visible_turns", None)
    second_row[field] = value

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "lvcor_visible_turn_count_unproven" for blocker in report["blockers"]
    )


def test_lvcor_005_runnerless_manual_selected_turns_nonzero_fails_closed() -> None:
    plan = complete_lvcor_005_plan()
    proof = plan["lvcor_full_shape_acceptance_proof"]
    assert isinstance(proof, dict)
    rows = proof["scenario_rows"]
    assert isinstance(rows, list)
    first_row = rows[0]
    assert isinstance(first_row, dict)
    first_row["runnerless_manual_selected_turn_count"] = 1

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "lvcor_runnerless_manual_selected_turns_nonzero"
        for blocker in report["blockers"]
    )


def test_lvcor_005_participant_closeout_incomplete_fails_closed() -> None:
    plan = complete_lvcor_005_plan()
    proof = plan["lvcor_full_shape_acceptance_proof"]
    assert isinstance(proof, dict)
    rows = proof["scenario_rows"]
    assert isinstance(rows, list)
    first_row = rows[0]
    assert isinstance(first_row, dict)
    first_row["participant_closeout_count"] = 3

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "lvcor_participant_closeout_incomplete" for blocker in report["blockers"]
    )


def test_lvcor_005_unresolved_terminal_cannot_claim_success_like_label() -> None:
    plan = complete_lvcor_005_plan()
    proof = plan["lvcor_full_shape_acceptance_proof"]
    assert isinstance(proof, dict)
    rows = proof["scenario_rows"]
    assert isinstance(rows, list)
    second_row = rows[1]
    assert isinstance(second_row, dict)
    second_row["terminal_phase"] = "unresolved"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert (
        report["lvcor_full_shape_acceptance_proof_report"]["label_statuses"][
            "finalized_success_candidate"
        ]["status"]
        == "blocked"
    )
    assert any(
        blocker["code"] == "lvcor_success_terminal_phase_invalid" for blocker in report["blockers"]
    )


def test_newfix_006_review_pending_evidence_stays_blocked_before_closeout() -> None:
    report = build_discussion_activation_plan(complete_newfix_006_plan())

    assert report["task_id"] == "plugin/NEWFIX-006"
    assert report["behavior_task_id"] == "plugin/NEWFIX-006"
    assert report["start_status"] == "blocked"
    assert report["status"] == "blocked"
    assert report["live_readiness"] is False
    prompt_report = report["selected_runner_prompt_evidence_report"]
    timeout_report = report["selected_runner_timeout_evidence_report"]
    assert prompt_report["status"] == "proven"
    assert timeout_report["status"] == "proven"
    assert (
        prompt_report["control_dependency"]["dependency_status"]
        == "implementation_complete/review_pending"
    )
    assert (
        timeout_report["control_dependency"]["dependency_status"]
        == "implementation_complete/review_pending"
    )
    assert {blocker["code"] for blocker in report["blockers"]} >= {
        "newfix_prompt_review_closeout_pending",
        "newfix_timeout_review_closeout_pending",
    }


def test_newfix_006_completed_control_evidence_can_be_ready_to_start() -> None:
    report = build_discussion_activation_plan(
        complete_newfix_006_plan(prompt_status="completed", timeout_status="completed")
    )

    assert report["task_id"] == "plugin/NEWFIX-006"
    assert report["behavior_task_id"] == "plugin/NEWFIX-006"
    assert report["start_status"] == "ready_to_start"
    assert report["status"] == "ready_to_start"
    assert report["live_readiness"] is False
    assert report["visible_surface_readiness_report"]["ready"] is True
    assert report["daemon_registry_membership_report"]["required"] is True
    assert report["daemon_registry_membership_report"]["ready"] is True
    assert report["selected_runner_prompt_evidence_report"]["status"] == "proven"
    assert report["selected_runner_timeout_evidence_report"]["status"] == "proven"
    assert (
        report["selected_runner_prompt_evidence_report"]["control_dependency"]["accepted_for_start"]
        is True
    )
    assert (
        report["selected_runner_timeout_evidence_report"]["control_dependency"][
            "accepted_for_start"
        ]
        is True
    )


def test_newfix_006_missing_visible_surface_readiness_blocks() -> None:
    plan = complete_newfix_006_plan(prompt_status="completed", timeout_status="completed")
    plan.pop("visible_surface_readiness", None)

    report = build_discussion_activation_plan(plan)

    assert report["start_status"] == "blocked"
    assert report["status"] == "blocked"
    assert report["visible_surface_readiness_report"]["ready"] is False
    assert any(
        blocker["code"] == "visible_surface_readiness_missing" for blocker in report["blockers"]
    )


def test_newfix_006_missing_daemon_registry_membership_blocks() -> None:
    plan = complete_newfix_006_plan(prompt_status="completed", timeout_status="completed")
    plan.pop("daemon_registry_membership", None)

    report = build_discussion_activation_plan(plan)

    assert report["start_status"] == "blocked"
    assert report["status"] == "blocked"
    assert report["daemon_registry_membership_report"]["required"] is True
    assert report["daemon_registry_membership_report"]["ready"] is False
    assert any(
        blocker["code"] == "daemon_registry_membership_missing" for blocker in report["blockers"]
    )


def test_newfix_006_missing_own_history_source_ids_blocks() -> None:
    plan = complete_newfix_006_plan()
    prompt = plan["selected_runner_prompt_evidence"]
    assert isinstance(prompt, dict)
    prompt["own_history_source_event_ids"] = []

    report = build_discussion_activation_plan(plan)

    assert report["start_status"] == "blocked"
    assert report["selected_runner_prompt_evidence_report"]["status"] == "blocked"
    assert any(
        blocker["code"] == "newfix_prompt_own_history_missing" for blocker in report["blockers"]
    )


def test_newfix_006_prompt_result_blocked_blocks() -> None:
    plan = complete_newfix_006_plan(prompt_status="completed", timeout_status="completed")
    prompt = plan["selected_runner_prompt_evidence"]
    assert isinstance(prompt, dict)
    prompt["result"] = "blocked"

    report = build_discussion_activation_plan(plan)

    assert report["start_status"] == "blocked"
    assert report["selected_runner_prompt_evidence_report"]["status"] == "blocked"
    assert any(
        blocker["code"] == "newfix_prompt_evidence_blocked" for blocker in report["blockers"]
    )


def test_newfix_006_wrong_prompt_control_task_id_blocks() -> None:
    plan = complete_newfix_006_plan(prompt_status="completed", timeout_status="completed")
    prompt = plan["selected_runner_prompt_evidence"]
    assert isinstance(prompt, dict)
    prompt["task_id"] = "control/RUNFIX-005"

    report = build_discussion_activation_plan(plan)

    assert report["start_status"] == "blocked"
    assert report["selected_runner_prompt_evidence_report"]["status"] == "blocked"
    assert any(
        blocker["code"] == "newfix_prompt_control_dependency_unproven"
        for blocker in report["blockers"]
    )


def test_newfix_006_missing_timeout_evidence_blocks() -> None:
    plan = complete_newfix_006_plan()
    plan.pop("selected_runner_timeout_evidence", None)

    report = build_discussion_activation_plan(plan)

    assert report["start_status"] == "blocked"
    assert report["selected_runner_timeout_evidence_report"]["status"] == "blocked"
    assert any(
        blocker["code"] == "newfix_timeout_evidence_missing" for blocker in report["blockers"]
    )


def test_newfix_006_default_timeout_30_blocks() -> None:
    report = build_discussion_activation_plan(
        complete_newfix_006_plan(configured_timeout_sec=30, effective_timeout_sec=30)
    )

    assert report["start_status"] == "blocked"
    assert report["selected_runner_timeout_evidence_report"]["status"] == "blocked"
    assert any(blocker["code"] == "newfix_timeout_policy_invalid" for blocker in report["blockers"])


def test_newfix_006_approved_alternative_requires_approval_basis() -> None:
    report = build_discussion_activation_plan(
        complete_newfix_006_plan(
            configured_timeout_sec=90,
            effective_timeout_sec=90,
            approved_alternative=True,
            approval_basis=None,
        )
    )

    assert report["start_status"] == "blocked"
    assert report["selected_runner_timeout_evidence_report"]["status"] == "blocked"
    assert any(blocker["code"] == "newfix_timeout_policy_invalid" for blocker in report["blockers"])


def test_newfix_006_approved_alternative_requires_matching_timeout_values() -> None:
    report = build_discussion_activation_plan(
        complete_newfix_006_plan(
            prompt_status="completed",
            timeout_status="completed",
            configured_timeout_sec=90,
            effective_timeout_sec=30,
            approved_alternative=True,
            approval_basis="approved by operator",
        )
    )

    assert report["start_status"] == "blocked"
    assert report["selected_runner_timeout_evidence_report"]["status"] == "blocked"
    assert any(blocker["code"] == "newfix_timeout_policy_invalid" for blocker in report["blockers"])


def test_newfix_006_approved_alternative_requires_positive_timeout_value() -> None:
    report = build_discussion_activation_plan(
        complete_newfix_006_plan(
            prompt_status="completed",
            timeout_status="completed",
            configured_timeout_sec=0,
            effective_timeout_sec=0,
            approved_alternative=True,
            approval_basis="approved by operator",
        )
    )

    assert report["start_status"] == "blocked"
    assert report["selected_runner_timeout_evidence_report"]["status"] == "blocked"
    assert any(blocker["code"] == "newfix_timeout_policy_invalid" for blocker in report["blockers"])


def test_newfix_006_timeout_policy_blocked_flag_blocks() -> None:
    plan = complete_newfix_006_plan(prompt_status="completed", timeout_status="completed")
    timeout = plan["selected_runner_timeout_evidence"]
    assert isinstance(timeout, dict)
    timeout["selected_runner_timeout_policy_blocked"] = True

    report = build_discussion_activation_plan(plan)

    assert report["start_status"] == "blocked"
    assert report["selected_runner_timeout_evidence_report"]["status"] == "blocked"
    assert report["selected_runner_timeout_evidence_report"]["drift_blocked"] is True
    assert any(blocker["code"] == "newfix_timeout_drift_blocked" for blocker in report["blockers"])


def test_newfix_006_wrong_timeout_control_task_id_blocks() -> None:
    plan = complete_newfix_006_plan(prompt_status="completed", timeout_status="completed")
    timeout = plan["selected_runner_timeout_evidence"]
    assert isinstance(timeout, dict)
    timeout["task_id"] = "control/NEWFIX-004"

    report = build_discussion_activation_plan(plan)

    assert report["start_status"] == "blocked"
    assert report["selected_runner_timeout_evidence_report"]["status"] == "blocked"
    assert any(
        blocker["code"] == "newfix_timeout_control_dependency_unproven"
        for blocker in report["blockers"]
    )


def test_newfix_006_manual_bridge_mode_blocks() -> None:
    plan = complete_newfix_006_plan(prompt_status="completed", timeout_status="completed")
    plan["request_context"] = {
        "source": "discord_thread",
        "requested_output_mode": "manual_bridge",
        "explicit_non_visible_override": True,
        "override_reason": "manual bridge diagnostic",
    }

    report = build_discussion_activation_plan(plan)

    assert report["requested_output_mode"] == "manual_bridge"
    assert report["start_status"] == "blocked"
    assert report["status"] == "blocked"
    assert report["visible_surface_readiness_report"]["ready"] is False
    assert any(
        blocker["code"] == "requested_output_mode_unsupported" for blocker in report["blockers"]
    )


def test_newfix_006_artifact_only_override_does_not_claim_ready_to_start() -> None:
    plan = complete_newfix_006_plan(prompt_status="completed", timeout_status="completed")
    plan["request_context"] = {
        "source": "discord_thread",
        "requested_output_mode": "artifact_only",
        "explicit_non_visible_override": True,
        "override_reason": "Operator requested diagnostic artifact-only output.",
    }
    plan.pop("visible_surface_readiness", None)

    report = build_discussion_activation_plan(plan)

    assert report["requested_output_mode"] == "artifact_only"
    assert report["start_status"] == "ready_for_approval"
    assert report["status"] == "ready_for_approval"
    assert report["visible_surface_readiness_report"]["ready"] is True
    assert report["selected_runner_prompt_evidence_report"]["status"] == "not_required"
    assert report["selected_runner_timeout_evidence_report"]["status"] == "not_required"


def test_runfix3_003_wrong_exact_origin_binding_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    readiness = plan["visible_surface_readiness"]
    assert isinstance(readiness, dict)
    readiness["observed_thread_id"] = "thread-wrong"
    readiness["exact_origin_binding"] = False

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["visible_surface_readiness_report"]["exact_origin_binding_proven"] is False
    assert any(
        blocker["code"] == "live_visible_surface_not_ready" for blocker in report["blockers"]
    )


def test_runfix3_003_exact_origin_flag_still_requires_matching_observed_target() -> None:
    plan = complete_runfix3_003_plan()
    readiness = plan["visible_surface_readiness"]
    assert isinstance(readiness, dict)
    readiness["observed_thread_id"] = "thread-wrong"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["visible_surface_readiness_report"]["exact_origin_binding_status"] == "mismatched"
    assert report["visible_surface_readiness_report"]["exact_origin_binding_proven"] is False
    assert any(
        blocker["code"] == "live_visible_surface_not_ready" for blocker in report["blockers"]
    )


def test_runfix3_003_exact_origin_flag_without_ids_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    request_context = plan["request_context"]
    readiness = plan["visible_surface_readiness"]
    assert isinstance(request_context, dict)
    assert isinstance(readiness, dict)
    request_context.pop("chat_id")
    request_context.pop("thread_id")
    readiness.pop("observed_chat_id")
    readiness.pop("observed_thread_id")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["visible_surface_readiness_report"]["exact_origin_binding_status"] == "unproven"
    assert report["visible_surface_readiness_report"]["exact_origin_binding_proven"] is False
    assert any(
        blocker["code"] == "live_visible_surface_not_ready" for blocker in report["blockers"]
    )


def test_runfix3_003_visible_turn_formula_mismatch_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    readiness = plan["visible_surface_readiness"]
    assert isinstance(readiness, dict)
    readiness["visible_turns_expected"] = 6
    readiness["visible_turns_posted"] = 6

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert report["visible_surface_readiness_report"]["visible_turn_count_proven"] is False
    assert report["runfix3_live_thread_proof_report"]["status"] == "blocked"
    assert any(
        blocker["code"] == "runfix3_visible_turn_count_unproven" for blocker in report["blockers"]
    )


def test_runfix3_003_missing_formula_inputs_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    readiness = plan["visible_surface_readiness"]
    assert isinstance(readiness, dict)
    readiness.pop("max_discussion_turns")
    readiness.pop("participant_count")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert report["visible_surface_readiness_report"]["visible_turn_count_proven"] is False
    assert report["runfix3_live_thread_proof_report"]["status"] == "blocked"
    assert any(
        blocker["code"] == "runfix3_visible_turn_count_unproven" for blocker in report["blockers"]
    )


def test_runfix3_003_missing_live_thread_proof_does_not_block_start() -> None:
    plan = complete_runfix3_003_plan()
    plan.pop("runfix3_live_thread_proof")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert report["runfix3_live_thread_proof_report"]["status"] == "blocked"
    assert any(
        blocker["code"] == "runfix3_live_thread_proof_missing" for blocker in report["blockers"]
    )


def test_runfix3_003_live_thread_acceptance_applies_to_operator_source() -> None:
    plan = complete_runfix3_003_plan()
    plan["request_context"] = {"source": "operator"}
    plan.pop("runfix3_live_thread_proof")

    report = build_discussion_activation_plan(plan)

    assert report["requested_output_mode"] == "live_visible_thread"
    assert report["start_status"] == "blocked"
    assert report["status"] == "blocked"
    assert report["runfix3_acceptance_status"] == "blocked"
    proof_report = report["runfix3_live_thread_proof_report"]
    assert isinstance(proof_report, dict)
    assert proof_report["status"] == "blocked"


def test_runfix3_003_missing_selected_runner_proof_blocks_acceptance_only() -> None:
    plan = complete_runfix3_003_plan()
    proof = plan["runfix3_live_thread_proof"]
    assert isinstance(proof, dict)
    proof.pop("selected_runner")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert (
        report["runfix3_live_thread_proof_report"]["selected_runner_proof"]["status"] == "blocked"
    )
    assert any(
        blocker["code"] == "runfix3_selected_runner_proof_missing" for blocker in report["blockers"]
    )


def test_runfix3_003_artifact_only_mode_does_not_require_live_thread_proof() -> None:
    plan = complete_runfix3_003_plan()
    plan["request_context"] = {
        "source": "discord_thread",
        "requested_output_mode": "artifact_only",
        "artifact_only_confirmed": True,
        "explicit_non_visible_override": True,
        "override_reason": "주군 explicitly requested artifact-only RUNFIX3 diagnostic output.",
    }
    plan.pop("visible_surface_readiness")
    plan.pop("runfix3_live_thread_proof")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "ready_for_approval"
    assert report["start_status"] == "ready_for_approval"
    assert report["runfix3_acceptance_status"] == "not_required"
    assert report["runfix3_live_thread_proof_report"]["status"] == "not_required"


def test_runfix3_003_missing_visible_author_guard_does_not_block_start() -> None:
    report = build_discussion_activation_plan(complete_runfix3_003_plan())

    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "proven"
    assert report["status"] == "ready_to_start"
    assert report["visible_author_guard_report"]["status"] == "not_required"


def test_runfix3_003_missing_registry_membership_blocks_ready_to_start() -> None:
    plan = complete_runfix3_003_plan()
    plan.pop("daemon_registry_membership")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "daemon_registry_membership_missing" for blocker in report["blockers"]
    )


def test_runfix3_003_missing_participant_profiles_returns_structured_blocker() -> None:
    plan = complete_runfix3_003_plan()
    plan.pop("participant_profiles")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["runfix3_live_thread_proof_report"]["status"] == "blocked"
    assert any(blocker["code"] == "participant_profiles_missing" for blocker in report["blockers"])


def test_runfix3_003_excluded_requested_roster_blocks_start() -> None:
    plan = complete_runfix3_003_plan()
    participant_profiles = plan["participant_profiles"]
    assert isinstance(participant_profiles, list)
    second_profile = participant_profiles[1]
    assert isinstance(second_profile, dict)
    second_profile["bot_to_bot_enabled"] = True

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["excluded_profiles"][0]["profile"] == "seohwang"


def test_runfix3_003_partial_delivery_coverage_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    proof = plan["runfix3_live_thread_proof"]
    assert isinstance(proof, dict)
    delivery_targets = proof["delivery_targets"]
    assert isinstance(delivery_targets, dict)
    rows = delivery_targets["rows"]
    assert isinstance(rows, list)
    delivery_targets["rows"] = rows[:4]

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert (
        report["runfix3_live_thread_proof_report"]["delivery_target_proof"]["aggregate_match"]
        is False
    )
    assert any(
        blocker["code"] == "runfix3_delivery_target_mismatch" for blocker in report["blockers"]
    )


def test_runfix3_003_missing_participant_closeout_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    proof = plan["runfix3_live_thread_proof"]
    assert isinstance(proof, dict)
    closeout = proof["participant_closeout"]
    assert isinstance(closeout, dict)
    rows = closeout["rows"]
    assert isinstance(rows, list)
    closeout["participant_closeout_pass"] = False
    closeout["rows"] = rows[:1]

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert report["runfix3_live_thread_proof_report"]["participant_closeout_coverage"][
        "status"
    ] in {
        "blocked",
        "unproven",
    }
    assert any(
        blocker["code"] == "runfix3_participant_closeout_unproven" for blocker in report["blockers"]
    )


def test_runfix3_003_missing_moderator_synthesis_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    proof = plan["runfix3_live_thread_proof"]
    assert isinstance(proof, dict)
    proof.pop("moderator_synthesis")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert report["runfix3_live_thread_proof_report"]["moderator_synthesis_coverage"]["status"] in {
        "blocked",
        "unproven",
    }
    assert any(
        blocker["code"] == "runfix3_moderator_synthesis_coverage_missing"
        for blocker in report["blockers"]
    )


def test_runfix3_003_parent_channel_fallback_remains_startable_when_approved() -> None:
    plan = complete_runfix3_003_plan()
    readiness = plan["visible_surface_readiness"]
    assert isinstance(readiness, dict)
    readiness.pop("thread_id")
    readiness.pop("observed_chat_id")
    readiness.pop("observed_thread_id")
    readiness["mode"] = "parent_channel_fallback"
    readiness["parent_channel_id"] = "chat-123"
    readiness["fallback_reason"] = "thread posting unsupported"
    readiness["exact_origin_binding"] = False

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert (
        report["visible_surface_readiness_report"]["exact_origin_binding_status"]
        == "parent_channel_fallback"
    )
    assert report["visible_surface_readiness_report"]["exact_origin_binding_proven"] is True


def test_runfix3_003_parent_channel_fallback_with_wrong_observed_target_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    readiness = plan["visible_surface_readiness"]
    assert isinstance(readiness, dict)
    readiness.pop("thread_id")
    readiness["mode"] = "parent_channel_fallback"
    readiness["parent_channel_id"] = "chat-123"
    readiness["fallback_reason"] = "thread posting unsupported"
    readiness["exact_origin_binding"] = False
    readiness["observed_chat_id"] = "wrong-chat"
    readiness["observed_thread_id"] = "thread-wrong"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["visible_surface_readiness_report"]["exact_origin_binding_status"] == "mismatched"
    assert report["visible_surface_readiness_report"]["exact_origin_binding_proven"] is False
    assert any(
        blocker["code"] == "live_visible_surface_not_ready" for blocker in report["blockers"]
    )


def test_runfix3_003_delivery_target_mismatch_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    proof = plan["runfix3_live_thread_proof"]
    assert isinstance(proof, dict)
    delivery_targets = proof["delivery_targets"]
    assert isinstance(delivery_targets, dict)
    rows = delivery_targets["rows"]
    assert isinstance(rows, list)
    first_row = rows[0]
    assert isinstance(first_row, dict)
    delivery_targets["delivery_target_pass"] = False
    first_row["posted_delivery_target"] = "chat-123:thread-wrong"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert (
        report["runfix3_live_thread_proof_report"]["delivery_target_proof"]["aggregate_match"]
        is False
    )
    assert any(
        blocker["code"] == "runfix3_delivery_target_mismatch" for blocker in report["blockers"]
    )


def test_runfix3_003_delivery_target_flag_does_not_override_string_mismatch() -> None:
    plan = complete_runfix3_003_plan()
    proof = plan["runfix3_live_thread_proof"]
    assert isinstance(proof, dict)
    delivery_targets = proof["delivery_targets"]
    assert isinstance(delivery_targets, dict)
    rows = delivery_targets["rows"]
    assert isinstance(rows, list)
    first_row = rows[0]
    assert isinstance(first_row, dict)
    first_row["delivery_target_match"] = True
    first_row["posted_delivery_target"] = "chat-123:thread-wrong"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert (
        report["runfix3_live_thread_proof_report"]["delivery_target_proof"]["aggregate_match"]
        is False
    )
    assert any(
        blocker["code"] == "runfix3_delivery_target_mismatch" for blocker in report["blockers"]
    )


def test_runfix3_003_self_matching_wrong_delivery_target_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    proof = plan["runfix3_live_thread_proof"]
    assert isinstance(proof, dict)
    delivery_targets = proof["delivery_targets"]
    assert isinstance(delivery_targets, dict)
    rows = delivery_targets["rows"]
    assert isinstance(rows, list)
    first_row = rows[0]
    assert isinstance(first_row, dict)
    first_row["expected_delivery_target"] = "wrong-chat:wrong-thread"
    first_row["posted_delivery_target"] = "wrong-chat:wrong-thread"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert (
        report["runfix3_live_thread_proof_report"]["delivery_target_proof"]["aggregate_match"]
        is False
    )
    assert any(
        blocker["code"] == "runfix3_delivery_target_mismatch" for blocker in report["blockers"]
    )


def test_runfix3_003_prompt_envelope_leakage_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    proof = plan["runfix3_live_thread_proof"]
    assert isinstance(proof, dict)
    prompt_envelope = proof["prompt_envelope"]
    assert isinstance(prompt_envelope, dict)
    prompt_envelope["prompt_envelope_pass"] = False
    prompt_envelope["content_audit_separated"] = False
    prompt_envelope["control_metadata_leaked"] = True

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert report["runfix3_live_thread_proof_report"]["prompt_envelope_proof"] == {
        "status": "blocked",
        "content_audit_separated": False,
        "control_metadata_leaked": True,
        "evidence_ref": "plugin/surface/prompt-envelope",
    }
    assert any(
        blocker["code"] == "runfix3_prompt_envelope_unproven" for blocker in report["blockers"]
    )


def test_runfix3_003_non_dialogue_prose_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    proof = plan["runfix3_live_thread_proof"]
    assert isinstance(proof, dict)
    dialogue_mode = proof["dialogue_mode"]
    assert isinstance(dialogue_mode, dict)
    dialogue_mode["dialogue_mode_pass"] = False
    dialogue_mode["participant_to_participant"] = False
    dialogue_mode["moderator_substitute_turns"] = True

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert report["runfix3_live_thread_proof_report"]["dialogue_mode_proof"] == {
        "status": "blocked",
        "participant_to_participant": False,
        "moderator_substitute_turns": True,
        "evidence_ref": "plugin/surface/dialogue-mode",
    }
    assert any(
        blocker["code"] == "runfix3_dialogue_mode_unproven" for blocker in report["blockers"]
    )


def test_runfix3_003_unresolved_drift_fails_closed() -> None:
    plan = complete_runfix3_003_plan()
    proof = plan["runfix3_live_thread_proof"]
    assert isinstance(proof, dict)
    drift = proof["drift"]
    assert isinstance(drift, dict)
    final_fail_closed = proof["final_fail_closed"]
    assert isinstance(final_fail_closed, dict)
    drift["status"] = "unresolved"
    drift["repaired_forward"] = False
    drift["unresolved_closeout"] = True
    final_fail_closed["final_fail_closed_pass"] = False
    final_fail_closed["final_status"] = "unresolved"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["start_status"] == "ready_to_start"
    assert report["runfix3_acceptance_status"] == "blocked"
    assert report["runfix3_live_thread_proof_report"]["drift_status"] == {
        "status": "blocked",
        "drift_detected": True,
        "repaired_forward": False,
        "unresolved_closeout": True,
        "evidence_ref": "plugin/surface/drift-status",
    }
    assert report["runfix3_live_thread_proof_report"]["fail_closed_final_status"] == {
        "status": "blocked",
        "final_status": "unresolved",
        "fail_closed": True,
        "evidence_ref": "plugin/surface/fail-closed-final",
    }
    assert any(blocker["code"] == "runfix3_drift_unproven" for blocker in report["blockers"])


def test_runfix2_005_missing_integrated_proof_fails_closed() -> None:
    plan = complete_runfix2_005_plan()
    plan.pop("integrated_discussion_proof")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["integrated_discussion_proof_report"]["status"] == "blocked"
    assert any(
        blocker["code"] == "integrated_discussion_proof_missing" for blocker in report["blockers"]
    )


def test_runfix2_005_runner_started_only_fails_closed() -> None:
    plan = complete_runfix2_005_plan()
    proof = plan["integrated_discussion_proof"]
    assert isinstance(proof, dict)
    runner = proof["selected_runner"]
    assert isinstance(runner, dict)
    runner.pop("runner_invocation_succeeded_ref")
    runner["runner_invocation_succeeded"] = False

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert (
        report["integrated_discussion_proof_report"]["selected_runner_pass"]["status"] == "blocked"
    )
    assert any(
        blocker["code"] == "integrated_selected_runner_started_only"
        for blocker in report["blockers"]
    )


def test_runfix2_005_runner_success_ref_without_explicit_success_true_fails_closed() -> None:
    plan = complete_runfix2_005_plan()
    proof = plan["integrated_discussion_proof"]
    assert isinstance(proof, dict)
    runner = proof["selected_runner"]
    assert isinstance(runner, dict)
    runner.pop("runner_invocation_succeeded")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert (
        report["integrated_discussion_proof_report"]["selected_runner_pass"]["status"] == "blocked"
    )
    assert any(
        blocker["code"] == "integrated_selected_runner_started_only"
        for blocker in report["blockers"]
    )


@pytest.mark.parametrize(
    ("proof_key", "evidence_kind", "expected_code"),
    [
        ("selected_runner", "fallback/manual", "integrated_selected_runner_substituted"),
        (
            "grant_turn_runtime_readiness",
            "manual/fallback-profile-only",
            "integrated_runtime_turn_substituted",
        ),
        (
            "visible_surface",
            "transcript/export-only",
            "integrated_visible_surface_unproven_substituted",
        ),
        ("clean_transcript", "gateway-only", "integrated_clean_transcript_unproven_substituted"),
        ("visible_closeout", "delivery-only", "integrated_visible_closeout_unproven_substituted"),
    ],
)
def test_runfix2_005_natural_evidence_kind_substitutions_fail_closed(
    proof_key: str,
    evidence_kind: str,
    expected_code: str,
) -> None:
    plan = complete_runfix2_005_plan()
    proof = plan["integrated_discussion_proof"]
    assert isinstance(proof, dict)
    target = proof[proof_key]
    if proof_key == "grant_turn_runtime_readiness":
        assert isinstance(target, list)
        row = target[0]
        assert isinstance(row, dict)
        row["evidence_kind"] = evidence_kind
    else:
        assert isinstance(target, dict)
        target["evidence_kind"] = evidence_kind

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(blocker["code"] == expected_code for blocker in report["blockers"])


def test_runfix2_005_durable_runner_failure_and_fallback_do_not_repair_pass() -> None:
    plan = complete_runfix2_005_plan()
    proof = plan["integrated_discussion_proof"]
    assert isinstance(proof, dict)
    runner = proof["selected_runner"]
    assert isinstance(runner, dict)
    runner.pop("runner_invocation_succeeded_ref")
    runner["durable_runner_failure_ref"] = "control/events/runner-failed"
    runner["manual_profile_only"] = True

    report = build_discussion_activation_plan(plan)

    selected_runner = report["integrated_discussion_proof_report"]["selected_runner_pass"]
    assert report["status"] == "blocked"
    assert selected_runner["status"] == "blocked"
    assert selected_runner["canonical_speech"]["status"] == "proven"
    assert report["integrated_discussion_proof_report"]["fallback_profile_pass"]["status"] == (
        "diagnostic_only"
    )
    assert any(
        blocker["code"] == "integrated_selected_runner_substituted"
        for blocker in report["blockers"]
    )
    assert any(
        blocker["code"] == "integrated_selected_runner_durable_failure"
        for blocker in report["blockers"]
    )


def test_runfix2_005_missing_canonical_speech_linkage_fails_closed() -> None:
    plan = complete_runfix2_005_plan()
    proof = plan["integrated_discussion_proof"]
    assert isinstance(proof, dict)
    canonical = proof["canonical_speech"]
    assert isinstance(canonical, dict)
    canonical["speaker_selected_event_id"] = "evt_other"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert (
        report["integrated_discussion_proof_report"]["selected_runner_pass"]["canonical_speech"][
            "status"
        ]
        == "blocked"
    )
    assert any(
        blocker["code"] == "integrated_canonical_speech_unlinked" for blocker in report["blockers"]
    )


def test_runfix2_005_missing_or_stale_per_turn_runtime_readiness_fails_closed() -> None:
    plan = complete_runfix2_005_plan()
    proof = plan["integrated_discussion_proof"]
    assert isinstance(proof, dict)
    runtime_rows = proof["grant_turn_runtime_readiness"]
    assert isinstance(runtime_rows, list)
    row = runtime_rows[0]
    assert isinstance(row, dict)
    row["heartbeat_fresh"] = False
    row["current_only"] = True

    report = build_discussion_activation_plan(plan)

    runtime_report = report["integrated_discussion_proof_report"][
        "participant_runtime_ready_at_turns"
    ]
    assert report["status"] == "blocked"
    assert runtime_report["status"] == "unproven"
    assert runtime_report["turns"][0]["status"] == "blocked"
    assert any(
        blocker["code"] == "integrated_runtime_current_only" for blocker in report["blockers"]
    )
    assert any(
        blocker["code"] == "integrated_runtime_turn_unproven" for blocker in report["blockers"]
    )


def test_runfix2_005_visible_turn_count_mismatch_fails_closed() -> None:
    plan = complete_runfix2_005_plan()
    proof = plan["integrated_discussion_proof"]
    assert isinstance(proof, dict)
    visible_turns = proof["visible_turns"]
    assert isinstance(visible_turns, dict)
    visible_turns["visible_turns_posted"] = 6

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["integrated_discussion_proof_report"]["visible_turn_count"]["status"] == (
        "unproven"
    )
    assert any(
        blocker["code"] == "integrated_visible_turn_count_mismatch"
        for blocker in report["blockers"]
    )


def test_runfix2_005_clean_transcript_and_closeout_proof_fail_closed() -> None:
    plan = complete_runfix2_005_plan()
    proof = plan["integrated_discussion_proof"]
    assert isinstance(proof, dict)
    clean = proof["clean_transcript"]
    closeout = proof["visible_closeout"]
    assert isinstance(clean, dict)
    assert isinstance(closeout, dict)
    clean["audit_ids_in_visible_text"] = True
    closeout.pop("evidence_ref")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["integrated_discussion_proof_report"]["clean_transcript_pass"]["status"] == (
        "blocked"
    )
    assert report["integrated_discussion_proof_report"]["visible_closeout_pass"]["status"] == (
        "blocked"
    )
    assert any(
        blocker["code"] == "integrated_clean_transcript_audit_ids_visible"
        for blocker in report["blockers"]
    )
    assert any(
        blocker["code"] == "integrated_visible_closeout_unproven" for blocker in report["blockers"]
    )


def test_runfix2_005_collapsed_or_missing_final_labels_fail_closed() -> None:
    plan = complete_runfix2_005_plan()
    proof = plan["integrated_discussion_proof"]
    assert isinstance(proof, dict)
    labels = proof["final_labels"]
    assert isinstance(labels, dict)
    labels["collapsed"] = True
    labels.pop("selected_runner_pass")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["integrated_discussion_proof_report"]["final_labels"]["status"] == "blocked"
    assert any(
        blocker["code"] == "integrated_final_labels_collapsed" for blocker in report["blockers"]
    )
    assert any(
        blocker["code"] == "integrated_final_label_selected_runner_pass_missing"
        for blocker in report["blockers"]
    )


def test_runfix_017_missing_operator_evidence_reports_runfix_017_blocker() -> None:
    plan = complete_plan()
    plan["task_id"] = "plugin/RUNFIX-017"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["operator_evidence_report"]["runfix_task_id"] == "plugin/RUNFIX-017"
    assert {
        "code": "operator_evidence_missing",
        "owner": "operator",
        "message": (
            "plugin/RUNFIX-017 requires explicit runner, ARGUE, canonical "
            "speech-link, and discussion_quality evidence."
        ),
    } in report["blockers"]


def test_runfix_017_requires_explicit_discussion_quality_evidence() -> None:
    plan = complete_runfix_017_plan()
    operator_evidence = plan["operator_evidence"]
    assert isinstance(operator_evidence, dict)
    operator_evidence.pop("discussion_quality")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    discussion_quality = report["operator_evidence_report"]["discussion_quality"]
    assert discussion_quality["status"] == "blocked"
    assert discussion_quality["discussion_quality_pass"] is False
    assert {
        "code": "discussion_quality_evidence_missing",
        "owner": "participant",
        "message": "plugin/RUNFIX-017 requires explicit discussion_quality evidence.",
    } in report["blockers"]


def test_runfix_017_quality_required_orphan_blocks_discussion_quality() -> None:
    plan = complete_runfix_017_plan()
    operator_evidence = plan["operator_evidence"]
    assert isinstance(operator_evidence, dict)
    discussion_quality = operator_evidence["discussion_quality"]
    assert isinstance(discussion_quality, dict)
    discussion_quality["turns"] = [
        {
            "speech_event_id": "evt_speech_orphan",
            "is_opening_speech": False,
            "participant_response": {
                "speech": "This speaks near the topic but does not link to prior claims.",
                "claims": [{"claim_id": "T04.C1", "summary": "The response is orphaned."}],
                "stance_links": [],
                "contribution_type": "support",
                "new_axis_reason": None,
                "evidence": [],
            },
        }
    ]

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    discussion_report = report["operator_evidence_report"]["discussion_quality"]
    assert discussion_report["status"] == "blocked"
    assert discussion_report["discussion_quality_pass"] is False
    assert discussion_report["first_orphan_speech_event_id"] == "evt_speech_orphan"
    assert discussion_report["orphan_speech_count"] == 1
    assert {
        "code": "discussion_quality_orphan_speech",
        "owner": "participant",
        "message": (
            "quality_required evidence has a non-opening speech without a valid "
            "prior-target stance_links[] entry or justified new_axis."
        ),
    } in report["blockers"]


def test_runfix_017_quality_required_ignores_guidance_and_legacy_hints() -> None:
    plan = complete_runfix_017_plan()
    operator_evidence = plan["operator_evidence"]
    assert isinstance(operator_evidence, dict)
    discussion_quality = operator_evidence["discussion_quality"]
    assert isinstance(discussion_quality, dict)
    discussion_quality["turns"] = [
        {
            "speech_event_id": "evt_speech_guidance_only",
            "is_opening_speech": False,
            "participant_response": {
                "speech": (
                    "I support seohwang's prior traceability summary and keyword "
                    "references, but no machine relation is supplied."
                ),
                "claims": [{"claim_id": "T04.C1", "summary": "Guidance is not relation."}],
                "stance_links": [],
                "contribution_type": "support",
                "responds_to_event_id": "evt_speech_0",
                "speaker": "seohwang",
                "summary": "Prior traceability remains the acceptance axis.",
                "available_stances": ["support"],
                "keywords": ["support", "traceability"],
            },
        }
    ]

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    discussion_report = report["operator_evidence_report"]["discussion_quality"]
    assert discussion_report["status"] == "blocked"
    assert discussion_report["valid_stance_link_count"] == 0
    assert discussion_report["orphan_speech_count"] == 1
    assert discussion_report["synthetic_links_created"] is False


def test_runfix_017_repeated_orphans_are_diagnostics_not_synthesized_links() -> None:
    plan = complete_runfix_017_plan()
    operator_evidence = plan["operator_evidence"]
    assert isinstance(operator_evidence, dict)
    discussion_quality = operator_evidence["discussion_quality"]
    assert isinstance(discussion_quality, dict)
    discussion_quality["turns"] = [
        {
            "speech_event_id": "evt_speech_orphan_1",
            "is_opening_speech": False,
            "participant_response": {
                "speech": "First orphan.",
                "claims": [{"claim_id": "T04.C1", "summary": "First orphan."}],
                "stance_links": [],
                "contribution_type": "support",
            },
        },
        {
            "speech_event_id": "evt_speech_orphan_2",
            "is_opening_speech": False,
            "participant_response": {
                "speech": "Second orphan.",
                "claims": [{"claim_id": "T05.C1", "summary": "Second orphan."}],
                "stance_links": [
                    {
                        "target_event_id": "evt_unknown",
                        "target_claim_id": "T99.C1",
                        "stance": "support",
                    }
                ],
                "contribution_type": "support",
            },
        },
    ]

    report = build_discussion_activation_plan(plan)

    discussion_report = report["operator_evidence_report"]["discussion_quality"]
    assert discussion_report["orphan_speech_count"] == 2
    assert discussion_report["repeated_orphan_count"] == 1
    assert discussion_report["valid_stance_link_count"] == 0
    assert discussion_report["synthetic_links_created"] is False
    assert {
        "code": "stance_links_not_validated_against_prior_claims",
        "speech_event_id": "evt_speech_orphan_2",
        "turn_index": 1,
        "synthetic_link_created": False,
    } in discussion_report["diagnostics"]


def test_runfix_017_quality_warn_orphan_is_warning_only() -> None:
    plan = complete_runfix_017_plan()
    operator_evidence = plan["operator_evidence"]
    assert isinstance(operator_evidence, dict)
    discussion_quality = operator_evidence["discussion_quality"]
    assert isinstance(discussion_quality, dict)
    discussion_quality["quality_mode"] = "quality_warn"
    discussion_quality["turns"] = [
        {
            "speech_event_id": "evt_speech_warn",
            "is_opening_speech": False,
            "participant_response": {
                "speech": "Warning-only orphan.",
                "claims": [{"claim_id": "T04.C1", "summary": "Warning-only orphan."}],
                "stance_links": [],
                "contribution_type": "support",
            },
        }
    ]

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "ready_for_approval"
    discussion_report = report["operator_evidence_report"]["discussion_quality"]
    assert discussion_report["status"] == "warning"
    assert discussion_report["discussion_quality_pass"] is True
    assert discussion_report["orphan_speech_count"] == 1


def test_runfix_008_exposes_operator_argue_and_fallback_evidence() -> None:
    report = build_discussion_activation_plan(complete_runfix_008_plan())

    assert report["status"] == "ready_for_approval"
    assert report["task_id"] == "plugin/RUNFIX-008"
    assert report["behavior_task_id"] == "plugin/RUNFIX-008"
    assert report["live_readiness"] is False
    operator_evidence = report["operator_evidence_report"]
    assert operator_evidence["runner_evidence"] == {
        "status": "proven",
        "speaker_selected_event_id": "evt_select_1",
        "selected_member": "macho",
        "runner_invocation_started_ref": "runner/run-1/invocation-started",
        "durable_runner_failure_ref": None,
    }
    assert operator_evidence["canonical_speaker_selected_to_speech"] == {
        "status": "proven",
        "linked": True,
        "speaker_selected_event_id": "evt_select_1",
        "speech_event_id": "evt_speech_1",
        "speaker": "macho",
    }
    assert operator_evidence["participant_response"] == {
        "status": "proven",
        "speech": "We should keep the pilot blocked until canonical speech linkage is proven.",
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
                "rationale": "The prior traceability requirement remains the acceptance axis.",
            }
        ],
        "contribution_type": "support",
        "new_axis_reason": None,
        "evidence": [{"kind": "runner_log", "ref": "runner/run-1/speech-link"}],
    }
    assert operator_evidence["argue_counts"] == {
        "status": "proven",
        "speech_present": True,
        "claims": 1,
        "stance_links": 1,
        "new_axis": 0,
        "evidence": 1,
        "contribution_types": {"support": 1},
    }
    assert operator_evidence["fallback_disclosure"] == {
        "status": "diagnostic_only",
        "label": "fallback_profile_pass",
        "full_atn_success": False,
        "evidence_ref": "manual/profile-diagnostic-reply",
        "missing_evidence": ["visible delivery evidence"],
    }
    assert report["evidence_labels"]["selected_runner_pass"] == "runner/run-1/invocation-started"
    assert report["evidence_labels"]["fallback_profile_pass"] == "manual/profile-diagnostic-reply"


def test_runfix_008_missing_operator_evidence_fails_closed() -> None:
    plan = complete_plan()
    plan["task_id"] = "plugin/RUNFIX-008"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["live_readiness"] is False
    assert report["operator_evidence_report"]["runner_evidence"]["status"] == "unproven"
    assert report["operator_evidence_report"]["argue_counts"]["status"] == "unproven"
    assert (
        report["operator_evidence_report"]["canonical_speaker_selected_to_speech"]["status"]
        == "unproven"
    )
    assert {
        "code": "operator_evidence_missing",
        "owner": "operator",
        "message": (
            "plugin/RUNFIX-008 requires explicit runner, ARGUE, and canonical speech-link evidence."
        ),
    } in report["blockers"]


def test_runfix_008_ambiguous_canonical_link_fails_closed() -> None:
    plan = complete_runfix_008_plan()
    plan["operator_evidence"]["canonical_speech"]["speaker_selected_event_id"] = "evt_other"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert (
        report["operator_evidence_report"]["canonical_speaker_selected_to_speech"]["linked"]
        is False
    )
    assert {
        "code": "canonical_speech_link_unproven",
        "owner": "control/plugin",
        "message": (
            "speaker_selected_event_id must link to a speech_event_id for the "
            "selected member and participant speech evidence."
        ),
    } in report["blockers"]


def test_discord_origin_runfix_010_defaults_to_live_visible_blocks_without_surface() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {"source": "discord_thread"}
    plan.pop("visible_surface_readiness", None)

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["behavior_task_id"] == "plugin/RUNFIX-010"
    assert report["requested_output_mode"] == "live_visible_thread"
    assert report["visible_surface_readiness_report"] == {
        "requested_output_mode": "live_visible_thread",
        "request_source": "discord_thread",
        "explicit_non_visible_override": False,
        "override_reason": None,
        "exact_origin_binding_status": "unproven",
        "exact_origin_binding_proven": False,
        "requested_chat_id": None,
        "requested_thread_id": None,
        "observed_chat_id": None,
        "observed_thread_id": None,
        "origin_binding_evidence_ref": None,
        "approved_delivery_target": None,
        "surface_bound": False,
        "turn_delivery_proven": False,
        "visible_closeout_proven": False,
        "real_profile_gateway_replies": False,
        "cli_actor_speech_only": False,
        "visible_turns_expected": 0,
        "visible_turns_posted": 0,
        "visible_turns_formula_expected": None,
        "visible_turn_count_proven": False,
        "ready": False,
    }

    assert {
        "code": "visible_surface_readiness_missing",
        "owner": "operator/Hermes-gateway",
        "message": (
            "Discord-origin ATN council requests default to live visible thread output; "
            "provide surface binding, turn-posting, profile/gateway reply, and closeout evidence "
            "or record an explicit non-visible override_reason before creating the session."
        ),
    } in report["blockers"]


def test_runfix_010_transcript_export_only_confirmation_is_accepted() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {
        "source": "discord_thread",
        "requested_output_mode": "transcript/export-only",
        "artifact_only_confirmed": True,
        "explicit_non_visible_override": True,
        "override_reason": "주군 explicitly requested transcript/export-only diagnostic output.",
    }

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "ready_for_approval"
    assert report["requested_output_mode"] == "artifact_only"


def test_runfix_010_accepts_unambiguous_registry_reconcile_plan() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {"source": "discord_thread"}
    plan["visible_surface_readiness"] = {
        "surface_bound": True,
        "parent_channel_id": "parent-123",
        "thread_id": "thread-456",
        "turn_posting_strategy": "selected_speaker_profile_send",
        "turn_delivery_probe_ref": "discord/thread-turn-probe",
        "visible_closeout_probe_ref": "discord/thread-closeout-probe",
        "real_profile_gateway_replies": True,
        "cli_actor_speech_only": False,
        "visible_turns_expected": 15,
        "visible_turns_posted": 15,
        "evidence_ref": "discord/thread-visible-proof",
    }
    plan["daemon_registry_membership"] = daemon_registry_membership(
        in_loaded_registry=False,
        planned_reconcile=True,
        mapping_unambiguous=True,
        wrapper_resolves=True,
    )

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "ready_to_start"
    assert report["additional_operator_approval_required"] is False
    registry_report = report["daemon_registry_membership_report"]
    assert isinstance(registry_report, dict)
    assert registry_report["planned_reconcile"] == ["macho"]


def test_runfix_010_blocks_ambiguous_registry_principal_mapping() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {"source": "discord_thread"}
    plan["visible_surface_readiness"] = {
        "surface_bound": True,
        "parent_channel_id": "parent-123",
        "thread_id": "thread-456",
        "turn_posting_strategy": "selected_speaker_profile_send",
        "turn_delivery_probe_ref": "discord/thread-turn-probe",
        "visible_closeout_probe_ref": "discord/thread-closeout-probe",
        "real_profile_gateway_replies": True,
        "cli_actor_speech_only": False,
        "visible_turns_expected": 15,
        "visible_turns_posted": 15,
        "evidence_ref": "discord/thread-visible-proof",
    }
    plan["daemon_registry_membership"] = daemon_registry_membership(
        in_loaded_registry=False,
        planned_reconcile=True,
        mapping_unambiguous=False,
        wrapper_resolves=True,
    )

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    blockers = report["blockers"]
    assert isinstance(blockers, list)
    assert {
        "code": "daemon_registry_principal_ambiguous",
        "owner": "control/operator",
        "message": "principal macho mapping is not explicitly unambiguous.",
    } in blockers


def test_runfix_010_blocks_missing_registry_evidence_ref() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {"source": "discord_thread"}
    plan["visible_surface_readiness"] = {
        "surface_bound": True,
        "parent_channel_id": "parent-123",
        "thread_id": "thread-456",
        "turn_posting_strategy": "selected_speaker_profile_send",
        "turn_delivery_probe_ref": "discord/thread-turn-probe",
        "visible_closeout_probe_ref": "discord/thread-closeout-probe",
        "real_profile_gateway_replies": True,
        "cli_actor_speech_only": False,
        "visible_turns_expected": 15,
        "visible_turns_posted": 15,
        "evidence_ref": "discord/thread-visible-proof",
    }
    plan["daemon_registry_membership"] = daemon_registry_membership(evidence_ref=None)

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "daemon_registry_evidence_ref_missing" for blocker in report["blockers"]
    )


def test_runfix_010_blocks_loaded_registry_principal_without_enabled_true() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {"source": "discord_thread"}
    plan["visible_surface_readiness"] = {
        "surface_bound": True,
        "parent_channel_id": "parent-123",
        "thread_id": "thread-456",
        "turn_posting_strategy": "selected_speaker_profile_send",
        "turn_delivery_probe_ref": "discord/thread-turn-probe",
        "visible_closeout_probe_ref": "discord/thread-closeout-probe",
        "real_profile_gateway_replies": True,
        "cli_actor_speech_only": False,
        "visible_turns_expected": 15,
        "visible_turns_posted": 15,
        "evidence_ref": "discord/thread-visible-proof",
    }
    plan["daemon_registry_membership"] = daemon_registry_membership(enabled=None)

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "daemon_registry_principal_not_enabled" for blocker in report["blockers"]
    )


def test_runfix_010_checks_selected_moderator_when_not_participant() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {"source": "discord_thread"}
    plan["visible_surface_readiness"] = {
        "surface_bound": True,
        "parent_channel_id": "parent-123",
        "thread_id": "thread-456",
        "turn_posting_strategy": "selected_speaker_profile_send",
        "turn_delivery_probe_ref": "discord/thread-turn-probe",
        "visible_closeout_probe_ref": "discord/thread-closeout-probe",
        "real_profile_gateway_replies": True,
        "cli_actor_speech_only": False,
        "visible_turns_expected": 15,
        "visible_turns_posted": 15,
        "evidence_ref": "discord/thread-visible-proof",
    }
    plan["daemon_registry_membership"] = daemon_registry_membership()
    cast_membership = plan["daemon_registry_membership"]
    assert isinstance(cast_membership, dict)
    cast_membership["selected_moderator_principal"] = "moderator-only"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "daemon_registry_required_principal_missing"
        and "moderator-only" in blocker["message"]
        for blocker in report["blockers"]
    )


def test_runfix_019_requires_control_runfix_018_and_registry_membership() -> None:
    plan = complete_plan()
    plan["task_id"] = "plugin/RUNFIX-019"
    plan["control_dependency"] = {
        "task_id": "control/RUNFIX-018",
        "status": "local implementation proof",
        "evidence_ref": "control/docs/roadmap.md#runfix-018",
    }
    plan["daemon_registry_membership"] = daemon_registry_membership()

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "ready_for_approval"
    assert report["behavior_task_id"] == "plugin/RUNFIX-019"
    registry_report = report["daemon_registry_membership_report"]
    assert isinstance(registry_report, dict)
    assert registry_report["required"] is True
    assert registry_report["ready"] is True


def test_runfix_010_live_visible_ready_requires_real_profile_gateway_and_not_cli_actor_only() -> (
    None
):
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {"source": "discord_thread"}
    plan["visible_surface_readiness"] = {
        "surface_bound": True,
        "parent_channel_id": "parent-123",
        "thread_id": "thread-456",
        "turn_posting_strategy": "selected_speaker_profile_send",
        "turn_delivery_probe_ref": "discord/thread-turn-probe",
        "visible_closeout_probe_ref": "discord/thread-closeout-probe",
        "real_profile_gateway_replies": True,
        "cli_actor_speech_only": False,
        "visible_turns_expected": 15,
        "visible_turns_posted": 15,
    }

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "ready_to_start"
    assert report["additional_operator_approval_required"] is False
    assert report["start_authority"] == "discord_request_authorizes_live_visible_thread"
    assert report["requested_output_mode"] == "live_visible_thread"
    assert report["visible_surface_readiness_report"]["ready"] is True
    assert report["visible_surface_readiness_report"]["surface_bound"] is True
    assert report["visible_surface_readiness_report"]["turn_delivery_proven"] is True
    registry_report = report["daemon_registry_membership_report"]
    assert isinstance(registry_report, dict)
    assert registry_report["ready"] is True
    assert registry_report["present"] == ["macho"]
    assert report["final_report_contract"] == {
        "lifecycle": "ATN lifecycle finalized true/false from daemon/control evidence",
        "discussion_quality": (
            "discussion_quality_pass true/false from explicit ARGUE relation evidence, "
            "separate from lifecycle_pass"
        ),
        "visible_turns_posted": "discord visible turns posted N/expected",
        "real_profile_gateway_replies": "true/false from explicit profile/gateway evidence",
        "cli_actor_speech_only": "true/false from explicit visible-surface evidence",
        "selected_runner_labels": "selected-runner evidence labels separate from lifecycle",
        "participant_closeout_coverage": (
            "covered/missing/unproven from explicit per-participant closeout evidence"
        ),
        "moderator_synthesis_coverage": (
            "covered/missing/unproven from explicit moderator synthesis evidence"
        ),
        "closeout_outcome": (
            "repair_forward/unresolved/unproven from explicit fail-closed closeout evidence"
        ),
        "shared_default_author_fallback_status": (
            "none/shared_default_detected/unproven from visible_author_guard"
        ),
    }


def test_runfix_015_visible_author_guard_is_ready_without_runtime_enforcement_claim() -> None:
    report = build_discussion_activation_plan(complete_runfix_015_plan())

    assert report["status"] == "ready_for_approval"
    assert report["task_id"] == "plugin/RUNFIX-015"
    assert report["behavior_task_id"] == "plugin/RUNFIX-015"
    assert report["live_readiness"] is False
    guard = report["visible_author_guard_report"]
    assert guard["guard_surface"] == "pre_council_new_activation_plan"
    assert guard["runtime_enforcement"] is False
    assert guard["operator_must_consume_before_session_creation"] is True
    assert guard["status"] == "proven"
    assert guard["ready"] is True
    assert guard["profile_author_probes"][0]["status"] == "proven"
    assert guard["env_precedence_proof"]["status"] == "proven"
    assert guard["per_turn_visible_evidence"][0] == {
        "status": "proven",
        "discord_message_id": "msg-turn-1",
        "selected_member": "macho",
        "profile_author_id": "bot-macho",
        "posting_path": "discord.gateway.profile_send",
        "speech_event_id": "evt_speech_1",
    }
    assert guard["final_result_report"] == {
        "status": "proven",
        "lifecycle": "pre_session_blocker_check_only",
        "visible_turns_posted": 1,
        "real_profile_gateway_replies": True,
        "selected_runner_labels": ["selected_runner_pass"],
        "shared_default_author_fallback_status": "none",
    }


def test_runfix_015_missing_visible_author_guard_fails_closed_before_session() -> None:
    plan = complete_runfix_015_plan()
    plan.pop("visible_author_guard")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["visible_author_guard_report"]["ready"] is False
    assert any(blocker["code"] == "visible_author_guard_missing" for blocker in report["blockers"])


def test_runfix_015_missing_final_lifecycle_fails_closed() -> None:
    plan = complete_runfix_015_plan()
    guard = plan["visible_author_guard"]
    assert isinstance(guard, dict)
    final_result = guard["final_result"]
    assert isinstance(final_result, dict)
    final_result.pop("lifecycle")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    guard_report = report["visible_author_guard_report"]
    assert isinstance(guard_report, dict)
    final_report = guard_report["final_result_report"]
    assert isinstance(final_report, dict)
    assert final_report["status"] == "blocked"
    assert final_report["lifecycle"] == "unproven"
    assert any(
        blocker["code"] == "visible_author_final_lifecycle_missing"
        for blocker in report["blockers"]
    )


def test_runfix_015_missing_same_path_probe_fails_closed() -> None:
    plan = complete_runfix_015_plan()
    guard = plan["visible_author_guard"]
    assert isinstance(guard, dict)
    profiles = guard["profile_author_probes"]
    assert isinstance(profiles, list)
    profile = profiles[0]
    assert isinstance(profile, dict)
    profile["same_path_probe"] = {"message_id": "msg-probe-macho"}

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "visible_author_same_path_probe_missing"
        for blocker in report["blockers"]
    )


def test_runfix_015_shared_default_author_fails_closed() -> None:
    plan = complete_runfix_015_plan()
    guard = plan["visible_author_guard"]
    assert isinstance(guard, dict)
    profiles = guard["profile_author_probes"]
    assert isinstance(profiles, list)
    profile = profiles[0]
    assert isinstance(profile, dict)
    profile["shared_default_author"] = True
    final_result = guard["final_result"]
    assert isinstance(final_result, dict)
    final_result["shared_default_author_fallback_status"] = "shared_default_detected"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "visible_author_shared_default_detected"
        for blocker in report["blockers"]
    )
    assert any(
        blocker["code"] == "visible_author_final_shared_default_status_not_clear"
        for blocker in report["blockers"]
    )


def test_runfix_015_unexpected_observed_bot_id_fails_closed() -> None:
    plan = complete_runfix_015_plan()
    guard = plan["visible_author_guard"]
    assert isinstance(guard, dict)
    profiles = guard["profile_author_probes"]
    assert isinstance(profiles, list)
    profile = profiles[0]
    assert isinstance(profile, dict)
    profile["observed_bot_id"] = "bot-shared"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "visible_author_observed_bot_mismatch" for blocker in report["blockers"]
    )


def test_runfix_015_unexpected_per_turn_profile_author_id_fails_closed() -> None:
    plan = complete_runfix_015_plan()
    guard = plan["visible_author_guard"]
    assert isinstance(guard, dict)
    turns = guard["per_turn_visible_evidence"]
    assert isinstance(turns, list)
    turn = turns[0]
    assert isinstance(turn, dict)
    turn["profile_author_id"] = "bot-shared"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "visible_author_per_turn_author_mismatch"
        for blocker in report["blockers"]
    )


def test_runfix_015_posting_path_mismatch_fails_closed() -> None:
    plan = complete_runfix_015_plan()
    guard = plan["visible_author_guard"]
    assert isinstance(guard, dict)
    profiles = guard["profile_author_probes"]
    assert isinstance(profiles, list)
    profile = profiles[0]
    assert isinstance(profile, dict)
    same_path_probe = profile["same_path_probe"]
    assert isinstance(same_path_probe, dict)
    same_path_probe["posting_path"] = "discord.gateway.generic_send"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "visible_author_posting_path_mismatch" for blocker in report["blockers"]
    )


def test_runfix_015_ambiguous_expected_author_source_fails_closed() -> None:
    plan = complete_runfix_015_plan()
    guard = plan["visible_author_guard"]
    assert isinstance(guard, dict)
    profiles = guard["profile_author_probes"]
    assert isinstance(profiles, list)
    profile = profiles[0]
    assert isinstance(profile, dict)
    profile["expected_author_source"] = "manual_guess"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "visible_author_expected_source_ambiguous"
        for blocker in report["blockers"]
    )


def test_runfix_015_reversed_env_precedence_fails_closed() -> None:
    plan = complete_runfix_015_plan()
    guard = plan["visible_author_guard"]
    assert isinstance(guard, dict)
    env = guard["env_precedence_proof"]
    assert isinstance(env, dict)
    env["order"] = ["profile_local", "shared_default"]

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["visible_author_guard_report"]["env_precedence_proof"]["status"] == "blocked"
    assert any(
        blocker["code"] == "visible_author_env_precedence_reversed"
        for blocker in report["blockers"]
    )


def test_runfix_015_per_turn_evidence_without_speech_event_id_fails_closed() -> None:
    plan = complete_runfix_015_plan()
    guard = plan["visible_author_guard"]
    assert isinstance(guard, dict)
    turns = guard["per_turn_visible_evidence"]
    assert isinstance(turns, list)
    turn = turns[0]
    assert isinstance(turn, dict)
    turn.pop("speech_event_id")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert any(
        blocker["code"] == "visible_author_per_turn_speech_link_missing"
        for blocker in report["blockers"]
    )


def test_runfix_010_artifact_only_from_discord_requires_explicit_confirmation() -> None:
    plan = complete_runfix_008_plan()
    plan["task_id"] = "plugin/RUNFIX-010"
    plan["request_context"] = {
        "source": "discord_thread",
        "requested_output_mode": "artifact_only",
    }

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["requested_output_mode"] == "artifact_only"
    assert {
        "code": "non_visible_output_override_missing",
        "owner": "operator",
        "message": (
            "Live-visible Discord output is the default ATN discussion target; "
            "artifact-only, daemon CLI actor speech, activation-planning-only, or "
            "local-daemon-only discussion requires explicit user-requested override "
            "with override_reason before session creation."
        ),
    } in report["blockers"]


def test_runfix_012_complete_runtime_readiness_is_ready_for_approval_not_live() -> None:
    report = build_discussion_activation_plan(complete_runfix_012_plan())

    assert report["status"] == "ready_for_approval"
    assert report["task_id"] == "plugin/RUNFIX-012"
    assert report["behavior_task_id"] == "plugin/RUNFIX-012"
    assert report["live_readiness"] is False
    readiness = report["participant_runtime_readiness_report"]
    assert readiness["ready"] is True
    assert readiness["control_dependency"] == {
        "status": "proven",
        "task_id": "control/RUNFIX-011",
        "dependency_status": "local implementation proof",
        "evidence_ref": "control/docs/roadmap.md#runfix-011",
    }
    assert readiness["subscriber_presence"]["status"] == "proven"
    assert readiness["cursor_ack_freshness"]["status"] == "proven"
    assert readiness["heartbeat_freshness"]["status"] == "proven"
    assert readiness["attendance_terminal"]["status"] == "proven"
    assert readiness["preparation_terminal"]["status"] == "proven"
    assert readiness["selected_runner_readiness"]["status"] == "proven"
    assert readiness["visible_surface_proof"]["status"] == "proven"
    assert readiness["diagnostics"] == []
    assert readiness["rejected_substitutions"] == []


def test_runfix_012_requires_control_runfix_011_dependency() -> None:
    plan = complete_runfix_012_plan()
    plan["control_dependency"] = {
        "task_id": "control/RUNFIX-005",
        "status": "completed/local-control",
        "evidence_ref": "control/runfix-005",
    }

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert (
        report["participant_runtime_readiness_report"]["control_dependency"]["status"] == "unproven"
    )
    assert {
        "code": "control_dependency_task_mismatch",
        "owner": "control",
        "message": "control_dependency.task_id must be control/RUNFIX-011.",
    } in report["blockers"]


def test_runfix_012_missing_runtime_readiness_fails_closed() -> None:
    plan = complete_runfix_012_plan()
    plan.pop("participant_runtime_readiness")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["participant_runtime_readiness_report"]["ready"] is False
    assert {
        "code": "participant_runtime_readiness_missing",
        "owner": "control/operator",
        "message": (
            "plugin/RUNFIX-012 requires explicit participant_runtime_readiness evidence "
            "from control/RUNFIX-011 diagnostics."
        ),
    } in report["blockers"]


@pytest.mark.parametrize(
    ("evidence_key", "report_key"),
    [
        ("subscriber", "subscriber_presence"),
        ("cursor_ack", "cursor_ack_freshness"),
        ("heartbeat", "heartbeat_freshness"),
        ("attendance", "attendance_terminal"),
        ("preparation", "preparation_terminal"),
        ("selected_runner", "selected_runner_readiness"),
        ("visible_surface", "visible_surface_proof"),
    ],
)
def test_runfix_012_missing_evidence_class_fails_closed(evidence_key: str, report_key: str) -> None:
    plan = complete_runfix_012_plan()
    readiness = plan["participant_runtime_readiness"]
    assert isinstance(readiness, dict)
    readiness.pop(evidence_key)

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["participant_runtime_readiness_report"]["ready"] is False
    assert report["participant_runtime_readiness_report"][report_key]["status"] == "unproven"
    assert any(
        blocker["code"] == f"{evidence_key}_evidence_missing" for blocker in report["blockers"]
    )


@pytest.mark.parametrize(
    ("evidence_key", "report_key"),
    [
        ("cursor_ack", "cursor_ack_freshness"),
        ("heartbeat", "heartbeat_freshness"),
    ],
)
def test_runfix_012_stale_runtime_evidence_fails_closed(evidence_key: str, report_key: str) -> None:
    plan = complete_runfix_012_plan()
    readiness = plan["participant_runtime_readiness"]
    assert isinstance(readiness, dict)
    evidence = readiness[evidence_key]
    assert isinstance(evidence, dict)
    evidence["fresh"] = False

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["participant_runtime_readiness_report"][report_key]["status"] == "stale"
    assert any(
        blocker["code"] == f"{evidence_key}_evidence_stale" for blocker in report["blockers"]
    )


def test_runfix_012_ambiguous_selected_runner_fails_closed() -> None:
    plan = complete_runfix_012_plan()
    readiness = plan["participant_runtime_readiness"]
    assert isinstance(readiness, dict)
    selected_runner = readiness["selected_runner"]
    assert isinstance(selected_runner, dict)
    selected_runner["ambiguous"] = True

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert (
        report["participant_runtime_readiness_report"]["selected_runner_readiness"]["status"]
        == "ambiguous"
    )
    assert any(
        blocker["code"] == "selected_runner_evidence_ambiguous" for blocker in report["blockers"]
    )


@pytest.mark.parametrize(
    ("evidence_key", "flag", "kind"),
    [
        ("heartbeat", "gateway_only", "gateway-only"),
        ("visible_surface", "transcript_export_only", "transcript/export-only"),
        ("visible_surface", "parent_channel_fallback_only", "parent-channel-fallback-only"),
        ("selected_runner", "manual_profile_only", "manual/fallback-profile-only"),
    ],
)
def test_runfix_012_rejects_substituted_runtime_evidence(
    evidence_key: str, flag: str, kind: str
) -> None:
    plan = complete_runfix_012_plan()
    readiness = plan["participant_runtime_readiness"]
    assert isinstance(readiness, dict)
    evidence = readiness[evidence_key]
    assert isinstance(evidence, dict)
    evidence[flag] = True

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["participant_runtime_readiness_report"]["ready"] is False
    assert {"kind": kind, "reason": flag} in report["participant_runtime_readiness_report"][
        "rejected_substitutions"
    ]
    assert any(
        blocker["code"] == f"{evidence_key}_substituted_evidence" for blocker in report["blockers"]
    )


@pytest.mark.parametrize("evidence_key", ["attendance", "preparation"])
def test_runfix_012_terminal_timeout_or_failure_is_diagnostic_not_ready(
    evidence_key: str,
) -> None:
    plan = complete_runfix_012_plan()
    readiness = plan["participant_runtime_readiness"]
    assert isinstance(readiness, dict)
    evidence = readiness[evidence_key]
    assert isinstance(evidence, dict)
    evidence["terminal_success"] = False
    evidence["terminal_status"] = "timeout"

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    report_key = f"{evidence_key}_terminal"
    assert report["participant_runtime_readiness_report"][report_key]["status"] == (
        "terminal_failure"
    )
    assert any(
        blocker["code"] == f"{evidence_key}_terminal_timeout" for blocker in report["blockers"]
    )


def test_missing_control_dependency_fails_closed() -> None:
    plan = complete_plan()
    plan.pop("control_dependency")

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["live_readiness"] is False
    assert {
        "code": "control_dependency_missing",
        "owner": "control",
        "message": "control/RUNFIX-005 completed/local-control evidence is required.",
    } in report["blockers"]


def test_bot_to_bot_enabled_profiles_are_excluded_by_default() -> None:
    plan = complete_plan()
    plan["participant_profiles"] = [
        {
            "profile": "jonghoe",
            "tools_visible": True,
            "bot_to_bot_enabled": True,
            "evidence_ref": "profile/jonghoe/bot-to-bot",
        }
    ]

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "not_ready"
    assert report["eligible_profiles"] == []
    assert report["excluded_profiles"] == [
        {
            "profile": "jonghoe",
            "reason": "bot_to_bot_enabled",
            "evidence_ref": "profile/jonghoe/bot-to-bot",
            "remediation": (
                "Disable bot-to-bot replies for this profile or omit it from the "
                "ATN discussion allow-list."
            ),
        }
    ]
    assert report["allow_list_targets"] == []
    assert {
        "code": "no_eligible_profiles",
        "owner": "operator",
        "message": "At least one non-bot-to-bot profile with visible tools is required.",
    } in report["blockers"]


@pytest.mark.parametrize(
    ("profile_patch", "reason"),
    [
        ({"tools_visible": False}, "tools_visibility_missing_or_false"),
        ({"tools_visible": None}, "tools_visibility_unknown"),
        ({"bot_to_bot_enabled": None}, "bot_to_bot_eligibility_unknown"),
    ],
)
def test_missing_tool_visibility_or_eligibility_blocks_profile(
    profile_patch: dict[str, object], reason: str
) -> None:
    plan = complete_plan()
    profile = {
        "profile": "manchong",
        "tools_visible": True,
        "bot_to_bot_enabled": False,
        "evidence_ref": "profile/manchong",
    }
    profile.update(profile_patch)
    plan["participant_profiles"] = [profile]

    report = build_discussion_activation_plan(plan)

    assert report["status"] in {"blocked", "not_ready"}
    assert report["eligible_profiles"] == []
    assert report["blocked_profiles"] == [
        {
            "profile": "manchong",
            "reason": reason,
            "evidence_ref": "profile/manchong",
            "remediation": (
                "Provide explicit effective Hermes profile tool visibility evidence."
                if reason == "tools_visibility_unknown"
                else "Enable/verify the profile-visible ATN plugin tools before allow-listing."
                if reason == "tools_visibility_missing_or_false"
                else "Provide explicit effective Hermes bot-to-bot policy evidence."
            ),
        }
    ]


def test_effective_discord_unknowns_block_even_when_legacy_fields_look_eligible() -> None:
    plan = complete_plan()
    plan["participant_profiles"] = [
        {
            "profile": "macho",
            "tools_visible": True,
            "bot_to_bot_enabled": False,
            "effective_discord": {
                "tools_visible": True,
                "bot_to_bot_enabled": None,
                "evidence_ref": "profile/macho/effective-discord-unknown",
            },
        }
    ]

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["eligible_profiles"] == []
    assert report["blocked_profiles"] == [
        {
            "profile": "macho",
            "reason": "bot_to_bot_eligibility_unknown",
            "evidence_ref": "profile/macho/effective-discord-unknown",
            "remediation": "Provide explicit effective Hermes bot-to-bot policy evidence.",
        }
    ]


def test_unproven_parent_channel_inheritance_is_gateway_blocker() -> None:
    plan = complete_plan()
    plan["discord_parent_channel"] = {
        "channel_id": "parent-123",
        "allow_list_inheritance_proven": False,
        "proof_source": "gateway_parent_allow_list_inheritance",
        "proof_ref": None,
    }

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert {
        "code": "parent_channel_allow_list_inheritance_unproven",
        "owner": "Hermes/gateway",
        "message": (
            "Parent-channel allow-list inheritance proof is required before "
            "activation planning can proceed."
        ),
    } in report["blockers"]


def test_thread_only_parent_channel_proof_is_rejected() -> None:
    plan = complete_plan()
    plan["discord_parent_channel"] = {
        "channel_id": "thread-456",
        "allow_list_inheritance_proven": True,
        "proof_source": "thread_only_current_channel",
        "proof_ref": "profile/manual-thread-reply",
    }

    report = build_discussion_activation_plan(plan)

    assert report["status"] == "blocked"
    assert report["parent_channel_plan"]["allow_list_inheritance_proven"] is False
    assert report["parent_channel_plan"]["thread_allow_list_behavior_proven"] is False
    assert {
        "code": "parent_channel_allow_list_inheritance_unproven",
        "owner": "Hermes/gateway",
        "message": (
            "Parent-channel allow-list inheritance proof is required before "
            "activation planning can proceed."
        ),
    } in report["blockers"]


def test_handler_wraps_report_and_keeps_live_readiness_false() -> None:
    body = json.loads(handle_discussion_activation_plan({"plan": complete_plan()}))

    assert body["ok"] is True
    assert body["tool"] == "atn_discussion_activation_plan"
    assert body["live_readiness"] is False
    assert body["data"]["status"] == "ready_for_approval"
    assert body["data"]["live_readiness"] is False


def test_handler_fails_closed_for_malformed_args() -> None:
    body = json.loads(handle_discussion_activation_plan({"plan": {"schema_version": 2}}))

    assert body["ok"] is False
    assert body["tool"] == "atn_discussion_activation_plan"
    assert body["live_readiness"] is False
    assert body["error"]["category"] == "validation"
