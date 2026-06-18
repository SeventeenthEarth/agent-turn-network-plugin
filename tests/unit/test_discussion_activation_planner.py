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


def complete_runfix_008_plan() -> dict[str, object]:
    plan = complete_plan()
    plan["task_id"] = "plugin/RUNFIX-008"
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
