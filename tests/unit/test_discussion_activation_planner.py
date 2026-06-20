from __future__ import annotations

import json

import pytest

from kkachi_agent_network_plugin.activation_planner import build_discussion_activation_plan
from kkachi_agent_network_plugin.tools import handle_discussion_activation_plan


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
                "kan_daemon_status",
                "kan_discussion_activation_plan",
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
                "effective_discord": {
                    "tools_visible": True,
                    "bot_to_bot_enabled": False,
                    "evidence_ref": "profile/macho/effective-discord",
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
        "participants": [row],
    }
    if evidence_ref is not None:
        membership["evidence_ref"] = evidence_ref
    return membership


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
            "reason": "effective_discord_tools_visible_and_bot_to_bot_disabled",
            "evidence_ref": "profile/macho/effective-discord",
        }
    ]
    assert report["excluded_profiles"] == [
        {
            "profile": "seohwang",
            "reason": "bot_to_bot_enabled",
            "evidence_ref": "profile/seohwang/bot-to-bot-enabled",
            "remediation": (
                "Disable bot-to-bot replies for this profile or omit it from the "
                "KAN discussion allow-list."
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
        "manual_profile_replies_as_full_kan_success",
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


def test_runfix_006_task_id_remains_accepted_with_runfix_007_behavior_label() -> None:
    plan = complete_plan()
    plan["task_id"] = "plugin/RUNFIX-006"

    report = build_discussion_activation_plan(plan)

    assert report["task_id"] == "plugin/RUNFIX-006"
    assert report["behavior_task_id"] == "plugin/RUNFIX-007"
    assert report["status"] == "ready_for_approval"


@pytest.mark.parametrize(
    "task_id",
    [
        "plugin/RUNFIX-006",
        "plugin/RUNFIX-007",
        "plugin/RUNFIX-008",
        "plugin/RUNFIX-010",
        "plugin/RUNFIX-017",
    ],
)
def test_prior_runfix_task_ids_remain_accepted(task_id: str) -> None:
    plan = (
        complete_runfix_017_plan()
        if task_id == "plugin/RUNFIX-017"
        else complete_runfix_008_plan()
        if task_id in {"plugin/RUNFIX-008", "plugin/RUNFIX-010"}
        else complete_plan()
    )
    plan["task_id"] = task_id
    if task_id == "plugin/RUNFIX-010":
        plan["request_context"] = {
            "source": "operator",
            "requested_output_mode": "activation_planning_only",
        }

    report = build_discussion_activation_plan(plan)

    assert report["task_id"] == task_id
    assert report["status"] == "ready_for_approval"
    assert report["live_readiness"] is False


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
        "full_kan_success": False,
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
        "surface_bound": False,
        "turn_delivery_proven": False,
        "visible_closeout_proven": False,
        "real_profile_gateway_replies": False,
        "cli_actor_speech_only": False,
        "visible_turns_expected": 0,
        "visible_turns_posted": 0,
        "ready": False,
    }
    assert {
        "code": "visible_surface_readiness_missing",
        "owner": "operator/Hermes-gateway",
        "message": (
            "Discord-origin KAN council requests default to live visible thread output; "
            "provide surface binding, turn-posting, profile/gateway reply, and closeout evidence "
            "or explicitly confirm artifact-only mode before creating the session."
        ),
    } in report["blockers"]


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

    assert report["status"] == "ready_for_approval"
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

    assert report["status"] == "ready_for_approval"
    assert report["requested_output_mode"] == "live_visible_thread"
    assert report["visible_surface_readiness_report"]["ready"] is True
    assert report["visible_surface_readiness_report"]["surface_bound"] is True
    assert report["visible_surface_readiness_report"]["turn_delivery_proven"] is True
    registry_report = report["daemon_registry_membership_report"]
    assert isinstance(registry_report, dict)
    assert registry_report["ready"] is True
    assert registry_report["present"] == ["macho"]
    assert report["final_report_contract"] == {
        "lifecycle": "kan_lifecycle_finalized true/false from daemon/control evidence",
        "discussion_quality": (
            "discussion_quality_pass true/false from explicit ARGUE relation evidence, "
            "separate from lifecycle_pass"
        ),
        "visible_turns_posted": "discord visible turns posted N/expected",
        "real_profile_gateway_replies": "true/false from explicit profile/gateway evidence",
        "selected_runner_labels": "selected-runner evidence labels separate from lifecycle",
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
        "code": "artifact_only_confirmation_missing",
        "owner": "operator",
        "message": (
            "Artifact-only or daemon CLI actor speech mode for a Discord-origin request "
            "requires explicit operator confirmation before session creation."
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
                "KAN discussion allow-list."
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
                "Provide explicit effective Discord tool visibility evidence."
                if reason == "tools_visibility_unknown"
                else "Enable/verify the profile-visible KAN plugin tools before allow-listing."
                if reason == "tools_visibility_missing_or_false"
                else "Provide explicit effective Discord bot-to-bot policy evidence."
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
            "remediation": "Provide explicit effective Discord bot-to-bot policy evidence.",
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
    assert body["tool"] == "kan_discussion_activation_plan"
    assert body["live_readiness"] is False
    assert body["data"]["status"] == "ready_for_approval"
    assert body["data"]["live_readiness"] is False


def test_handler_fails_closed_for_malformed_args() -> None:
    body = json.loads(handle_discussion_activation_plan({"plan": {"schema_version": 2}}))

    assert body["ok"] is False
    assert body["tool"] == "kan_discussion_activation_plan"
    assert body["live_readiness"] is False
    assert body["error"]["category"] == "validation"
