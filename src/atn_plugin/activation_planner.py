"""Pure dry-run ATN discussion activation planner.

The planner consumes explicit caller-provided evidence only. It performs no
environment, Discord, Hermes, daemon, socket, CLI, profile, gateway, provider,
auth, token, or model discovery/mutation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final, cast

from .protocol import JsonObject, JsonValue, ProtocolValidationError, require_json_object

ACTIVATION_PLAN_SCHEMA_VERSION: Final = 1
RUNFIX_006_TASK_ID: Final = "plugin/RUNFIX-006"
RUNFIX_007_TASK_ID: Final = "plugin/RUNFIX-007"
RUNFIX_008_TASK_ID: Final = "plugin/RUNFIX-008"
RUNFIX_010_TASK_ID: Final = "plugin/RUNFIX-010"
RUNFIX_012_TASK_ID: Final = "plugin/RUNFIX-012"
RUNFIX_015_TASK_ID: Final = "plugin/RUNFIX-015"
RUNFIX_017_TASK_ID: Final = "plugin/RUNFIX-017"
RUNFIX_019_TASK_ID: Final = "plugin/RUNFIX-019"
RUNFIX2_005_TASK_ID: Final = "plugin/RUNFIX2-005"
RUNFIX3_003_TASK_ID: Final = "plugin/RUNFIX3-003"
NEWFIX_006_TASK_ID: Final = "plugin/NEWFIX-006"
ATN_005_TASK_ID: Final = "plugin/ATN-005"
SUPPORTED_TASK_IDS: Final[frozenset[str]] = frozenset(
    {
        RUNFIX_006_TASK_ID,
        RUNFIX_007_TASK_ID,
        RUNFIX_008_TASK_ID,
        RUNFIX_010_TASK_ID,
        RUNFIX_012_TASK_ID,
        RUNFIX_015_TASK_ID,
        RUNFIX_017_TASK_ID,
        RUNFIX_019_TASK_ID,
        RUNFIX2_005_TASK_ID,
        RUNFIX3_003_TASK_ID,
        NEWFIX_006_TASK_ID,
        ATN_005_TASK_ID,
    }
)
TASK_ID: Final = RUNFIX_010_TASK_ID
CONTROL_DEPENDENCY_TASK_ID: Final = "control/RUNFIX-005"
CONTROL_DEPENDENCY_STATUS: Final = "completed/local-control"
NEWFIX_004_CONTROL_DEPENDENCY_TASK_ID: Final = "control/NEWFIX-004"
NEWFIX_005_CONTROL_DEPENDENCY_TASK_ID: Final = "control/NEWFIX-005"
NEWFIX_REVIEW_PENDING_STATUS: Final = "implementation_complete/review_pending"
NEWFIX_ACCEPTED_CONTROL_STATUSES: Final[frozenset[str]] = frozenset({"completed"})
NEWFIX_CONSUMABLE_CONTROL_STATUSES: Final[frozenset[str]] = frozenset(
    {NEWFIX_REVIEW_PENDING_STATUS, "completed"}
)
NEWFIX_006_CONTROL_DEPENDENCY_TASK_IDS: Final[frozenset[str]] = frozenset(
    {
        CONTROL_DEPENDENCY_TASK_ID,
        NEWFIX_004_CONTROL_DEPENDENCY_TASK_ID,
        NEWFIX_005_CONTROL_DEPENDENCY_TASK_ID,
    }
)
NEWFIX_006_CONTROL_DEPENDENCY_STATUSES: Final[frozenset[str]] = frozenset(
    {CONTROL_DEPENDENCY_STATUS, NEWFIX_REVIEW_PENDING_STATUS, "completed"}
)
NEWFIX_REQUIRED_TIMEOUT_SEC: Final = 120
RUNFIX_012_CONTROL_DEPENDENCY_TASK_ID: Final = "control/RUNFIX-011"
RUNFIX_012_CONTROL_DEPENDENCY_STATUSES: Final[frozenset[str]] = frozenset(
    {"local implementation proof", "completed/local-control", "local-control"}
)
RUNFIX_019_CONTROL_DEPENDENCY_TASK_ID: Final = "control/RUNFIX-018"
RUNFIX_019_CONTROL_DEPENDENCY_STATUSES: Final[frozenset[str]] = frozenset(
    {"local implementation proof", "completed/local-control", "local-control"}
)
ATN_005_HISTORICAL_DEPENDENCY_LABELS: Final[tuple[str, ...]] = (
    CONTROL_DEPENDENCY_TASK_ID,
    RUNFIX_012_CONTROL_DEPENDENCY_TASK_ID,
    RUNFIX_019_CONTROL_DEPENDENCY_TASK_ID,
)
ATN_005_CONTROL_DEPENDENCY_TASK_IDS: Final[frozenset[str]] = frozenset(
    ATN_005_HISTORICAL_DEPENDENCY_LABELS
)
ATN_005_CONTROL_DEPENDENCY_STATUSES: Final[frozenset[str]] = frozenset(
    {"completed/local-control", "local implementation proof", "local-control"}
)
RUNFIX3_ACCEPTANCE_ONLY_CODES: Final[frozenset[str]] = frozenset(
    {
        "runfix3_live_thread_proof_missing",
        "runfix3_selected_runner_proof_missing",
        "runfix3_selected_runner_proof_unproven",
        "runfix3_participant_closeout_missing",
        "runfix3_participant_closeout_unproven",
        "runfix3_moderator_synthesis_coverage_missing",
        "runfix3_moderator_synthesis_coverage_unproven",
        "runfix3_delivery_target_missing",
        "runfix3_delivery_target_rows_missing",
        "runfix3_delivery_target_row_invalid",
        "runfix3_delivery_target_row_unproven",
        "runfix3_delivery_target_mismatch",
        "runfix3_prompt_envelope_missing",
        "runfix3_prompt_envelope_unproven",
        "runfix3_dialogue_mode_missing",
        "runfix3_dialogue_mode_unproven",
        "runfix3_drift_missing",
        "runfix3_drift_unproven",
        "runfix3_fail_closed_missing",
        "runfix3_fail_closed_unproven",
        "runfix3_visible_turn_count_unproven",
    }
)

TOOL_NAME: Final = "atn_discussion_activation_plan"
EVIDENCE_LABELS: Final[tuple[str, ...]] = (
    "lifecycle_pass",
    "fallback_profile_pass",
    "selected_runner_pass",
    "visible_surface_pass",
    "discussion_quality_pass",
)


def build_discussion_activation_plan(plan: Mapping[str, object]) -> JsonObject:
    """Return a deterministic dry-run activation report from explicit evidence."""

    source = require_json_object(plan, label="plan")
    if source.get("schema_version") != ACTIVATION_PLAN_SCHEMA_VERSION:
        raise ValueError("plan.schema_version must be 1")
    task_id = _required_string(source.get("task_id"), label="plan.task_id")
    if task_id not in SUPPORTED_TASK_IDS:
        raise ValueError(
            "plan.task_id must be plugin/RUNFIX-006, plugin/RUNFIX-007, "
            "plugin/RUNFIX-008, plugin/RUNFIX-010, plugin/RUNFIX-012, "
            "plugin/RUNFIX-015, plugin/RUNFIX-017, plugin/RUNFIX-019, "
            "plugin/RUNFIX2-005, plugin/RUNFIX3-003, plugin/NEWFIX-006, or "
            "plugin/ATN-005"
        )

    blockers: list[JsonObject] = []
    excluded_profiles: list[JsonObject] = []
    blocked_profiles: list[JsonObject] = []

    _validate_control_dependency(
        source.get("control_dependency"), task_id=task_id, blockers=blockers
    )
    _validate_plugin_install(source.get("plugin_install"), blockers=blockers)
    _validate_control_daemon(source.get("control_daemon"), blockers=blockers)
    parent_channel_plan = _parent_channel_plan(
        source.get("discord_parent_channel"), blockers=blockers
    )

    eligible_profiles = _profile_classification(
        source.get("participant_profiles"),
        excluded_profiles=excluded_profiles,
        blocked_profiles=blocked_profiles,
        blockers=blockers,
    )
    dry_run_actions = _required_string_list(
        source.get("planned_changes"),
        label="plan.planned_changes",
        blocker_code="planned_changes_missing",
        blocker_owner="operator",
        blocker_message="Planned dry-run changes are required.",
        blockers=blockers,
    )
    rollback = _rollback_steps(source.get("rollback"), blockers=blockers)
    verification_commands = _required_string_list(
        source.get("verification_commands"),
        label="plan.verification_commands",
        blocker_code="verification_commands_missing",
        blocker_owner="operator",
        blocker_message="Smoke/verification commands are required.",
        blockers=blockers,
    )
    required_approvals = _required_string_list(
        source.get("approval_gates"),
        label="plan.approval_gates",
        blocker_code="approval_gates_missing",
        blocker_owner="operator",
        blocker_message="Approval gates are required before any apply/live-local pilot.",
        blockers=blockers,
    )
    operator_blockers = _optional_operator_blockers(source.get("operator_blockers"))
    blockers.extend(operator_blockers)
    operator_evidence = _operator_evidence_report(
        source.get("operator_evidence"),
        runfix_task_id=RUNFIX_017_TASK_ID if task_id == RUNFIX_017_TASK_ID else RUNFIX_008_TASK_ID,
        require_evidence=task_id in {RUNFIX_008_TASK_ID, RUNFIX_010_TASK_ID, RUNFIX_017_TASK_ID},
        require_quality=task_id == RUNFIX_017_TASK_ID,
        blockers=blockers,
    )
    visible_surface_readiness = _visible_surface_readiness_report(
        source.get("request_context"),
        source.get("visible_surface_readiness"),
        task_id=task_id,
        blockers=blockers,
    )
    requested_output_mode = cast(str, visible_surface_readiness["requested_output_mode"])
    request_source = cast(str, visible_surface_readiness["request_source"])
    selected_runner_prompt_evidence = _newfix_prompt_evidence_report(
        source.get("selected_runner_prompt_evidence"),
        task_id=task_id,
        requested_output_mode=requested_output_mode,
        request_source=request_source,
        blockers=blockers,
    )
    selected_runner_timeout_evidence = _newfix_timeout_evidence_report(
        source.get("selected_runner_timeout_evidence"),
        task_id=task_id,
        requested_output_mode=requested_output_mode,
        request_source=request_source,
        blockers=blockers,
    )
    daemon_registry_membership = _daemon_registry_membership_report(
        source.get("daemon_registry_membership"),
        eligible_profiles=eligible_profiles,
        task_id=task_id,
        requested_output_mode=requested_output_mode,
        blockers=blockers,
    )
    participant_runtime_readiness = _participant_runtime_readiness_report(
        source.get("participant_runtime_readiness"),
        control_dependency_value=source.get("control_dependency"),
        task_id=task_id,
        blockers=blockers,
    )
    visible_author_guard = _visible_author_guard_report(
        source.get("visible_author_guard"),
        eligible_profiles=eligible_profiles,
        requested_output_mode=cast(str, visible_surface_readiness["requested_output_mode"]),
        task_id=task_id,
        blockers=blockers,
    )
    integrated_discussion_proof = _integrated_discussion_proof_report(
        source.get("integrated_discussion_proof"),
        task_id=task_id,
        blockers=blockers,
    )
    runfix3_live_thread_proof = _runfix3_live_thread_proof_report(
        source.get("runfix3_live_thread_proof"),
        task_id=task_id,
        requested_output_mode=cast(str, visible_surface_readiness["requested_output_mode"]),
        expected_profiles=[
            profile_name
            for profile_name in (
                _optional_string_value(item.get("profile")) for item in eligible_profiles
            )
            if profile_name is not None
        ],
        expected_visible_turns=(
            _non_negative_int_or_none(
                visible_surface_readiness.get("visible_turns_formula_expected")
            )
            if task_id == RUNFIX3_003_TASK_ID
            else _non_negative_int_or_none(visible_surface_readiness.get("visible_turns_expected"))
        ),
        approved_delivery_target=_optional_string_value(
            visible_surface_readiness.get("approved_delivery_target")
        ),
        visible_turn_count_proven=(
            visible_surface_readiness.get("visible_turn_count_proven") is True
        ),
        blockers=blockers,
    )

    if not eligible_profiles:
        blockers.append(
            _blocker(
                code="no_eligible_profiles",
                owner="operator",
                message="At least one non-bot-to-bot profile with visible tools is required.",
            )
        )

    start_status = _start_status(
        blockers=blockers,
        blocked_profiles=blocked_profiles,
        excluded_profiles=excluded_profiles,
        eligible_profiles=eligible_profiles,
        requested_output_mode=requested_output_mode,
        request_source=request_source,
        task_id=task_id,
    )
    runfix3_acceptance_status = _runfix3_acceptance_status(
        task_id=task_id,
        requested_output_mode=requested_output_mode,
        runfix3_live_thread_proof=runfix3_live_thread_proof,
    )
    status = _overall_status(
        start_status=start_status,
        runfix3_acceptance_status=runfix3_acceptance_status,
    )
    additional_operator_approval_required = start_status == "ready_for_approval"
    start_authority = (
        "discord_request_authorizes_live_visible_thread"
        if start_status == "ready_to_start"
        else "explicit_operator_approval_required"
        if start_status == "ready_for_approval"
        else "blocked_or_not_ready"
    )
    return {
        "schema_version": ACTIVATION_PLAN_SCHEMA_VERSION,
        "task_id": task_id,
        "behavior_task_id": _behavior_task_id(task_id),
        "status": status,
        "start_status": start_status,
        "runfix3_acceptance_status": runfix3_acceptance_status,
        "additional_operator_approval_required": additional_operator_approval_required,
        "start_authority": start_authority,
        "live_readiness": False,
        "eligible_profiles": cast(list[JsonValue], eligible_profiles),
        "excluded_profiles": cast(list[JsonValue], excluded_profiles),
        "blocked_profiles": cast(list[JsonValue], blocked_profiles),
        "allow_list_targets": [profile["profile"] for profile in eligible_profiles],
        "profile_remediation": _profile_remediation(
            excluded_profiles=excluded_profiles, blocked_profiles=blocked_profiles
        ),
        "parent_channel_plan": parent_channel_plan,
        "participant_argue_response_template": _participant_argue_response_template(),
        "operator_evidence_report": operator_evidence,
        "activation_evidence_model_report": _activation_evidence_model_report(),
        "requested_output_mode": visible_surface_readiness["requested_output_mode"],
        "visible_surface_readiness_report": visible_surface_readiness,
        "daemon_registry_membership_report": daemon_registry_membership,
        "participant_runtime_readiness_report": participant_runtime_readiness,
        "selected_runner_prompt_evidence_report": selected_runner_prompt_evidence,
        "selected_runner_timeout_evidence_report": selected_runner_timeout_evidence,
        "visible_author_guard_report": visible_author_guard,
        "integrated_discussion_proof_report": integrated_discussion_proof,
        "runfix3_live_thread_proof_report": runfix3_live_thread_proof,
        "final_report_contract": _final_report_contract(),
        "fallback_audit": cast(list[JsonValue], _fallback_audit()),
        "required_approvals": cast(list[JsonValue], required_approvals),
        "dry_run_actions": cast(list[JsonValue], dry_run_actions),
        "rollback": cast(list[JsonValue], rollback),
        "verification_commands": cast(list[JsonValue], verification_commands),
        "evidence_labels": _evidence_labels(source.get("evidence_labels")),
        "blockers": cast(list[JsonValue], blockers),
        "non_scope": [
            "live Discord delivery",
            "Discord channel creation",
            "profile/gateway/provider/auth/token/model mutation",
            "daemon startup or lifecycle ownership",
            "hidden CLI fallback",
            "silent artifact-only substitution for a Discord-origin council request",
            "production activation or live readiness claim",
        ],
    }


def _behavior_task_id(task_id: str) -> str:
    if task_id in {
        RUNFIX_008_TASK_ID,
        RUNFIX_010_TASK_ID,
        RUNFIX_012_TASK_ID,
        RUNFIX_015_TASK_ID,
        RUNFIX_017_TASK_ID,
        RUNFIX_019_TASK_ID,
        RUNFIX2_005_TASK_ID,
        RUNFIX3_003_TASK_ID,
        NEWFIX_006_TASK_ID,
        ATN_005_TASK_ID,
    }:
        return task_id
    return RUNFIX_007_TASK_ID


def _validate_control_dependency(
    value: object, *, task_id: str, blockers: list[JsonObject]
) -> None:
    if task_id == NEWFIX_006_TASK_ID:
        _validate_newfix_006_control_dependency(value, blockers=blockers)
        return
    if task_id == RUNFIX_012_TASK_ID:
        _validate_runfix_012_control_dependency(value, blockers=blockers)
        return
    if task_id == RUNFIX_019_TASK_ID:
        _validate_runfix_019_control_dependency(value, blockers=blockers)
        return
    if task_id == ATN_005_TASK_ID:
        _validate_atn_005_control_dependency(value, blockers=blockers)
        return

    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="control_dependency_missing",
                owner="control",
                message="control/RUNFIX-005 completed/local-control evidence is required.",
            )
        )
        return
    dependency = _json_object(value, label="plan.control_dependency")
    if dependency.get("task_id") != CONTROL_DEPENDENCY_TASK_ID:
        blockers.append(
            _blocker(
                code="control_dependency_task_mismatch",
                owner="control",
                message="control_dependency.task_id must be control/RUNFIX-005.",
            )
        )
    if dependency.get("status") != CONTROL_DEPENDENCY_STATUS:
        blockers.append(
            _blocker(
                code="control_dependency_not_completed",
                owner="control",
                message="control/RUNFIX-005 must be completed/local-control.",
            )
        )
    if not _non_empty_string(dependency.get("evidence_ref")):
        blockers.append(
            _blocker(
                code="control_dependency_evidence_missing",
                owner="control",
                message="control/RUNFIX-005 evidence_ref is required.",
            )
        )


def _validate_newfix_006_control_dependency(value: object, *, blockers: list[JsonObject]) -> None:
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="control_dependency_missing",
                owner="control",
                message=(
                    "plugin/NEWFIX-006 requires explicit historical activation-planner or "
                    "NEWFIX control dependency evidence."
                ),
            )
        )
        return
    dependency = _json_object(value, label="plan.control_dependency")
    if dependency.get("task_id") not in NEWFIX_006_CONTROL_DEPENDENCY_TASK_IDS:
        blockers.append(
            _blocker(
                code="control_dependency_task_mismatch",
                owner="control",
                message=(
                    "plugin/NEWFIX-006 control_dependency.task_id must be control/RUNFIX-005, "
                    "control/NEWFIX-004, or control/NEWFIX-005."
                ),
            )
        )
    if dependency.get("status") not in NEWFIX_006_CONTROL_DEPENDENCY_STATUSES:
        blockers.append(
            _blocker(
                code="control_dependency_not_completed",
                owner="control",
                message=(
                    "plugin/NEWFIX-006 control_dependency.status must be completed/local-control, "
                    "implementation_complete/review_pending, or completed."
                ),
            )
        )
    if not _non_empty_string(dependency.get("evidence_ref")):
        blockers.append(
            _blocker(
                code="control_dependency_evidence_missing",
                owner="control",
                message="plugin/NEWFIX-006 control_dependency.evidence_ref is required.",
            )
        )


def _validate_runfix_012_control_dependency(value: object, *, blockers: list[JsonObject]) -> None:
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="control_dependency_missing",
                owner="control",
                message=(
                    "control/RUNFIX-011 local participant-runtime readiness evidence is required."
                ),
            )
        )
        return
    dependency = _json_object(value, label="plan.control_dependency")
    if dependency.get("task_id") != RUNFIX_012_CONTROL_DEPENDENCY_TASK_ID:
        blockers.append(
            _blocker(
                code="control_dependency_task_mismatch",
                owner="control",
                message="control_dependency.task_id must be control/RUNFIX-011.",
            )
        )
    if dependency.get("status") not in RUNFIX_012_CONTROL_DEPENDENCY_STATUSES:
        blockers.append(
            _blocker(
                code="control_dependency_not_completed",
                owner="control",
                message=(
                    "control/RUNFIX-011 must have local implementation proof, "
                    "completed/local-control, or local-control status."
                ),
            )
        )
    if not _non_empty_string(dependency.get("evidence_ref")):
        blockers.append(
            _blocker(
                code="control_dependency_evidence_missing",
                owner="control",
                message="control/RUNFIX-011 evidence_ref is required.",
            )
        )


def _validate_runfix_019_control_dependency(value: object, *, blockers: list[JsonObject]) -> None:
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="control_dependency_missing",
                owner="control",
                message="control/RUNFIX-018 registry reconciliation evidence is required.",
            )
        )
        return
    dependency = _json_object(value, label="plan.control_dependency")
    if dependency.get("task_id") != RUNFIX_019_CONTROL_DEPENDENCY_TASK_ID:
        blockers.append(
            _blocker(
                code="control_dependency_task_mismatch",
                owner="control",
                message="control_dependency.task_id must be control/RUNFIX-018.",
            )
        )
    if dependency.get("status") not in RUNFIX_019_CONTROL_DEPENDENCY_STATUSES:
        blockers.append(
            _blocker(
                code="control_dependency_not_completed",
                owner="control",
                message=(
                    "control/RUNFIX-018 must have local implementation proof, "
                    "completed/local-control, or local-control status."
                ),
            )
        )
    if not _non_empty_string(dependency.get("evidence_ref")):
        blockers.append(
            _blocker(
                code="control_dependency_evidence_missing",
                owner="control",
                message="control/RUNFIX-018 evidence_ref is required.",
            )
        )


def _validate_atn_005_control_dependency(value: object, *, blockers: list[JsonObject]) -> None:
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="control_dependency_missing",
                owner="control",
                message=(
                    "plugin/ATN-005 requires explicit historical control dependency "
                    "evidence for the activation planner model."
                ),
            )
        )
        return
    dependency = _json_object(value, label="plan.control_dependency")
    if dependency.get("task_id") not in ATN_005_CONTROL_DEPENDENCY_TASK_IDS:
        blockers.append(
            _blocker(
                code="control_dependency_task_mismatch",
                owner="control",
                message=(
                    "control_dependency.task_id must be one of the known historical "
                    "activation planner dependency labels."
                ),
            )
        )
    if dependency.get("status") not in ATN_005_CONTROL_DEPENDENCY_STATUSES:
        blockers.append(
            _blocker(
                code="control_dependency_not_completed",
                owner="control",
                message=(
                    "plugin/ATN-005 control dependency status must be completed/local-control, "
                    "local implementation proof, or local-control."
                ),
            )
        )
    if not _non_empty_string(dependency.get("evidence_ref")):
        blockers.append(
            _blocker(
                code="control_dependency_evidence_missing",
                owner="control",
                message="plugin/ATN-005 control_dependency.evidence_ref is required.",
            )
        )


def _validate_plugin_install(value: object, *, blockers: list[JsonObject]) -> None:
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="plugin_install_evidence_missing",
                owner="plugin",
                message="Explicit plugin installed/enabled/tool visibility evidence is required.",
            )
        )
        return
    install = _json_object(value, label="plan.plugin_install")
    if install.get("installed") is not True:
        blockers.append(
            _blocker(
                code="plugin_not_installed",
                owner="plugin",
                message="plugin_install.installed must be true.",
            )
        )
    if install.get("enabled") is not True:
        blockers.append(
            _blocker(
                code="plugin_not_enabled",
                owner="plugin",
                message="plugin_install.enabled must be true.",
            )
        )
    tool_names = install.get("tool_names")
    if not isinstance(tool_names, Sequence) or isinstance(tool_names, (str, bytes)):
        blockers.append(
            _blocker(
                code="plugin_tool_visibility_missing",
                owner="plugin",
                message="plugin_install.tool_names must list visible plugin tools.",
            )
        )
        return
    visible_tools = {item for item in tool_names if isinstance(item, str)}
    if TOOL_NAME not in visible_tools:
        blockers.append(
            _blocker(
                code="activation_tool_visibility_missing",
                owner="plugin",
                message=(
                    "atn_discussion_activation_plan must be visible in plugin_install.tool_names."
                ),
            )
        )


def _validate_control_daemon(value: object, *, blockers: list[JsonObject]) -> None:
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="control_daemon_evidence_missing",
                owner="control",
                message="Explicit daemon socket/config and compatibility evidence is required.",
            )
        )
        return
    daemon = _json_object(value, label="plan.control_daemon")
    if daemon.get("mode") != "explicit":
        blockers.append(
            _blocker(
                code="control_daemon_mode_not_explicit",
                owner="control",
                message=(
                    "control_daemon.mode must be explicit; discovery/autodetection is unsupported."
                ),
            )
        )
    if not _non_empty_string(daemon.get("socket_or_config_ref")):
        blockers.append(
            _blocker(
                code="control_daemon_config_evidence_missing",
                owner="control",
                message="control_daemon.socket_or_config_ref is required.",
            )
        )
    if not _non_empty_string(daemon.get("compatibility_ref")):
        blockers.append(
            _blocker(
                code="control_daemon_compatibility_evidence_missing",
                owner="control",
                message="control_daemon.compatibility_ref is required.",
            )
        )


def _parent_channel_plan(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    output: JsonObject = {
        "channel_id": None,
        "allow_list_inheritance_proven": False,
        "proof_ref": None,
        "proof_source": None,
        "thread_allow_list_behavior_proven": False,
        "remediation": (
            "Provide explicit Hermes/gateway proof that parent-channel allow-list "
            "inheritance covers newly created discussion threads."
        ),
    }
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="discord_parent_channel_plan_missing",
                owner="Hermes/gateway",
                message="Selected Discord parent-channel plan is required.",
            )
        )
        return output
    parent = _json_object(value, label="plan.discord_parent_channel")
    channel_id = parent.get("channel_id")
    if not _non_empty_string(channel_id):
        blockers.append(
            _blocker(
                code="parent_channel_id_missing",
                owner="Hermes/gateway",
                message="discord_parent_channel.channel_id is required.",
            )
        )
    else:
        output["channel_id"] = cast(str, channel_id)
    proof_ref = parent.get("proof_ref")
    proof_source = parent.get("proof_source")
    explicit_gateway_parent_proof = parent.get("proof_covers_parent_inheritance") is True or (
        proof_source == "gateway_parent_allow_list_inheritance"
    )
    proven = (
        parent.get("allow_list_inheritance_proven") is True
        and _non_empty_string(proof_ref)
        and explicit_gateway_parent_proof
    )
    output["allow_list_inheritance_proven"] = proven
    output["thread_allow_list_behavior_proven"] = proven
    if _non_empty_string(proof_ref):
        output["proof_ref"] = cast(str, proof_ref)
    if _non_empty_string(proof_source):
        output["proof_source"] = cast(str, proof_source)
    if not proven:
        blockers.append(
            _blocker(
                code="parent_channel_allow_list_inheritance_unproven",
                owner="Hermes/gateway",
                message=(
                    "Parent-channel allow-list inheritance proof is required before "
                    "activation planning can proceed."
                ),
            )
        )
    return output


def _profile_classification(
    value: object,
    *,
    excluded_profiles: list[JsonObject],
    blocked_profiles: list[JsonObject],
    blockers: list[JsonObject],
) -> list[JsonObject]:
    if not isinstance(value, list):
        blockers.append(
            _blocker(
                code="participant_profiles_missing",
                owner="operator",
                message="participant_profiles must be an explicit list.",
            )
        )
        return []
    eligible: list[JsonObject] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            blocked_profiles.append(
                {"profile": f"index:{index}", "reason": "profile_row_not_object"}
            )
            continue
        profile = _json_object(item, label=f"plan.participant_profiles[{index}]")
        profile_name = _required_string(
            profile.get("profile"), label=f"plan.participant_profiles[{index}].profile"
        )
        effective_hermes = _effective_hermes_visibility(profile, index=index)
        evidence_ref = effective_hermes.get("evidence_ref") or profile.get("evidence_ref")
        row = {"profile": profile_name}
        if _non_empty_string(evidence_ref):
            row["evidence_ref"] = cast(str, evidence_ref)
        principal = profile.get("principal")
        if _non_empty_string(principal) and principal != profile_name:
            row["principal"] = cast(str, principal)
        tools_visible = effective_hermes.get("tools_visible")
        bot_to_bot_enabled = effective_hermes.get("bot_to_bot_enabled")
        if tools_visible is None:
            blocked_profiles.append(
                {
                    **row,
                    "reason": "tools_visibility_unknown",
                    "remediation": (
                        "Provide explicit effective Hermes profile tool visibility evidence."
                    ),
                }
            )
            continue
        if tools_visible is not True:
            blocked_profiles.append(
                {
                    **row,
                    "reason": "tools_visibility_missing_or_false",
                    "remediation": (
                        "Enable/verify the profile-visible ATN plugin tools before allow-listing."
                    ),
                }
            )
            continue
        if bot_to_bot_enabled is None:
            blocked_profiles.append(
                {
                    **row,
                    "reason": "bot_to_bot_eligibility_unknown",
                    "remediation": "Provide explicit effective Hermes bot-to-bot policy evidence.",
                }
            )
            continue
        if bot_to_bot_enabled is True:
            excluded_profiles.append(
                {
                    **row,
                    "reason": "bot_to_bot_enabled",
                    "remediation": (
                        "Disable bot-to-bot replies for this profile or omit it from the "
                        "ATN discussion allow-list."
                    ),
                }
            )
            continue
        if bot_to_bot_enabled is not False:
            blocked_profiles.append(
                {
                    **row,
                    "reason": "bot_to_bot_eligibility_unknown",
                    "remediation": "Provide explicit effective Hermes bot-to-bot policy evidence.",
                }
            )
            continue
        eligible.append(
            {
                **row,
                "reason": "effective_hermes_tools_visible_and_bot_to_bot_disabled",
            }
        )
    return eligible


def _effective_hermes_visibility(profile: JsonObject, *, index: int) -> JsonObject:
    value = profile.get("effective_hermes")
    if value is None:
        value = profile.get("effective_discord")
    if value is None:
        return {
            "tools_visible": profile.get("tools_visible"),
            "bot_to_bot_enabled": profile.get("bot_to_bot_enabled"),
            "evidence_ref": profile.get("evidence_ref"),
        }
    if not isinstance(value, Mapping):
        raise ValueError(
            f"plan.participant_profiles[{index}].effective_hermes must be an object when present"
        )
    return _json_object(value, label=f"plan.participant_profiles[{index}].effective_hermes")


def _profile_remediation(
    *,
    excluded_profiles: list[JsonObject],
    blocked_profiles: list[JsonObject],
) -> JsonObject:
    return {
        "excluded": cast(list[JsonValue], excluded_profiles),
        "blocked": cast(list[JsonValue], blocked_profiles),
    }


def _activation_evidence_model_report() -> JsonObject:
    return {
        "task_id": ATN_005_TASK_ID,
        "public_tool_name": TOOL_NAME,
        "legacy_public_aliases_allowed": False,
        "historical_dependency_labels": list(ATN_005_HISTORICAL_DEPENDENCY_LABELS),
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


def _daemon_registry_membership_report(
    value: object,
    *,
    eligible_profiles: Sequence[JsonObject],
    task_id: str,
    requested_output_mode: str,
    blockers: list[JsonObject],
) -> JsonObject:
    required = task_id == RUNFIX_019_TASK_ID or (
        task_id in {RUNFIX_010_TASK_ID, RUNFIX3_003_TASK_ID, NEWFIX_006_TASK_ID}
        and requested_output_mode == "live_visible_thread"
    )
    required_principals = [
        cast(str, profile.get("principal") or profile.get("profile"))
        for profile in eligible_profiles
        if _non_empty_string(profile.get("principal") or profile.get("profile"))
    ]
    report: JsonObject = {
        "required": required,
        "registry_loaded": False,
        "evidence_ref": None,
        "required_principals": cast(list[JsonValue], required_principals),
        "present": [],
        "planned_reconcile": [],
        "blocked": [],
        "ready": not required,
    }
    if not isinstance(value, Mapping):
        if required:
            blockers.append(
                _blocker(
                    code="daemon_registry_membership_missing",
                    owner="control/operator",
                    message=(
                        "Live-visible council activation requires explicit loaded daemon "
                        "registry membership evidence or an unambiguous planned reconcile."
                    ),
                )
            )
            report["ready"] = False
        return report

    membership = _json_object(value, label="plan.daemon_registry_membership")
    report["registry_loaded"] = membership.get("registry_loaded") is True
    if _non_empty_string(membership.get("evidence_ref")):
        report["evidence_ref"] = cast(str, membership.get("evidence_ref"))
    elif required:
        _append_registry_block(
            report,
            blockers,
            code="daemon_registry_evidence_ref_missing",
            message="daemon_registry_membership.evidence_ref is required.",
            required=required,
        )
    if membership.get("registry_loaded") is not True:
        _append_registry_block(
            report,
            blockers,
            code="daemon_registry_not_loaded",
            message="daemon_registry_membership.registry_loaded must be true with evidence.",
            required=required,
        )

    moderator = _optional_string_value(
        membership.get("selected_moderator_principal") or membership.get("moderator")
    )
    if required and moderator is None:
        _append_registry_block(
            report,
            blockers,
            code="daemon_registry_moderator_missing",
            message=(
                "daemon_registry_membership.selected_moderator_principal or moderator is required "
                "for live-visible activation."
            ),
            required=required,
        )
    elif moderator is not None and moderator not in required_principals:
        required_principals.append(moderator)
        report["required_principals"] = cast(list[JsonValue], required_principals)

    participants_value = membership.get("participants") or membership.get("members")
    if not isinstance(participants_value, list):
        _append_registry_block(
            report,
            blockers,
            code="daemon_registry_participants_missing",
            message="daemon_registry_membership.participants must list each planned principal.",
            required=required,
        )
        return report

    rows: dict[str, JsonObject] = {}
    for index, item in enumerate(participants_value):
        if not isinstance(item, Mapping):
            _append_registry_block(
                report,
                blockers,
                code="daemon_registry_participant_row_invalid",
                message=f"daemon_registry_membership.participants[{index}] must be an object.",
                required=required,
            )
            continue
        row = _json_object(item, label=f"plan.daemon_registry_membership.participants[{index}]")
        principal = _optional_string_value(row.get("principal") or row.get("member"))
        if principal is None:
            _append_registry_block(
                report,
                blockers,
                code="daemon_registry_principal_missing",
                message=f"daemon_registry_membership.participants[{index}].principal is required.",
                required=required,
            )
            continue
        if principal in rows:
            _append_registry_block(
                report,
                blockers,
                code="daemon_registry_principal_duplicate",
                message=f"daemon_registry_membership has duplicate principal {principal}.",
                required=required,
            )
            continue
        rows[principal] = row

    for principal in required_principals:
        evidence_row = rows.get(principal)
        if evidence_row is None:
            _append_registry_block(
                report,
                blockers,
                code="daemon_registry_required_principal_missing",
                message=f"daemon registry evidence is missing required principal {principal}.",
                required=required,
            )
            continue
        if evidence_row.get("mapping_unambiguous") is not True:
            _append_registry_block(
                report,
                blockers,
                code="daemon_registry_principal_ambiguous",
                message=f"principal {principal} mapping is not explicitly unambiguous.",
                principal=principal,
                required=required,
            )
            continue
        if evidence_row.get("in_loaded_registry") is True:
            if evidence_row.get("enabled") is not True:
                _append_registry_block(
                    report,
                    blockers,
                    code="daemon_registry_principal_not_enabled",
                    message=(
                        f"principal {principal} must have enabled=true in the loaded registry."
                    ),
                    principal=principal,
                    required=required,
                )
                continue
            cast(list[JsonValue], report["present"]).append(principal)
            continue
        if (
            evidence_row.get("planned_reconcile") is True
            and evidence_row.get("wrapper_resolves") is True
        ):
            cast(list[JsonValue], report["planned_reconcile"]).append(principal)
            continue
        _append_registry_block(
            report,
            blockers,
            code="daemon_registry_reconcile_not_proven",
            message=(
                f"principal {principal} is absent from the loaded registry and lacks "
                "planned_reconcile=true plus wrapper_resolves=true evidence."
            ),
            principal=principal,
            required=required,
        )

    report["ready"] = bool(report["registry_loaded"]) and not report["blocked"]
    return report


def _append_registry_block(
    report: JsonObject,
    blockers: list[JsonObject],
    *,
    code: str,
    message: str,
    required: bool,
    principal: str | None = None,
) -> None:
    blocked: JsonObject = {"code": code, "message": message}
    if principal is not None:
        blocked["principal"] = principal
    cast(list[JsonValue], report["blocked"]).append(blocked)
    if required:
        blockers.append(_blocker(code=code, owner="control/operator", message=message))


def _visible_surface_readiness_report(
    request_context_value: object,
    readiness_value: object,
    *,
    task_id: str,
    blockers: list[JsonObject],
) -> JsonObject:
    request_context = (
        _json_object(request_context_value, label="plan.request_context")
        if isinstance(request_context_value, Mapping)
        else {}
    )
    request_source = _optional_string_value(request_context.get("source")) or "unspecified"
    requested_output_mode = _optional_string_value(
        request_context.get("requested_output_mode")
        or request_context.get("requested_output")
        or request_context.get("mode")
    )
    explicit_non_visible_override = request_context.get("explicit_non_visible_override") is True
    override_reason = _optional_string_value(request_context.get("override_reason"))
    if requested_output_mode is None:
        requested_output_mode = (
            "live_visible_thread"
            if request_source.startswith("discord")
            or task_id in {RUNFIX_010_TASK_ID, RUNFIX3_003_TASK_ID}
            else "activation_planning_only"
        )
    report: JsonObject = {
        "requested_output_mode": requested_output_mode,
        "request_source": request_source,
        "explicit_non_visible_override": explicit_non_visible_override,
        "override_reason": override_reason,
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
    if task_id not in {RUNFIX_010_TASK_ID, RUNFIX3_003_TASK_ID, NEWFIX_006_TASK_ID}:
        report["ready"] = requested_output_mode != "live_visible_thread"
        return report

    if requested_output_mode in {"transcript/export-only", "transcript_export_only"}:
        requested_output_mode = "artifact_only"
        report["requested_output_mode"] = requested_output_mode
    elif requested_output_mode in {"local-daemon-only", "local_daemon_only"}:
        requested_output_mode = "activation_planning_only"
        report["requested_output_mode"] = requested_output_mode

    if requested_output_mode not in {
        "live_visible_thread",
        "artifact_only",
        "daemon_cli_actor_speech",
        "activation_planning_only",
    }:
        blockers.append(
            _blocker(
                code="requested_output_mode_unsupported",
                owner="operator",
                message=(
                    "requested_output_mode must be live_visible_thread, artifact_only, "
                    "daemon_cli_actor_speech, transcript/export-only/transcript_export_only, "
                    "local-daemon-only/local_daemon_only, or activation_planning_only."
                ),
            )
        )
        return report

    if requested_output_mode in {
        "artifact_only",
        "daemon_cli_actor_speech",
        "activation_planning_only",
    }:
        if not explicit_non_visible_override or override_reason is None:
            blockers.append(
                _blocker(
                    code="non_visible_output_override_missing",
                    owner="operator",
                    message=(
                        "Live-visible Discord output is the default ATN discussion target; "
                        "artifact-only, daemon CLI actor speech, activation-planning-only, or "
                        "local-daemon-only discussion requires explicit user-requested override "
                        "with override_reason before session creation."
                    ),
                )
            )
            report["ready"] = False
            return report
        report["ready"] = True
        return report

    if requested_output_mode != "live_visible_thread":
        report["ready"] = True
        return report

    if not isinstance(readiness_value, Mapping):
        blockers.append(
            _blocker(
                code="visible_surface_readiness_missing",
                owner="operator/Hermes-gateway",
                message=(
                    "Discord-origin ATN council requests default to live visible thread output; "
                    "provide surface binding, turn-posting, profile/gateway reply, and closeout "
                    "evidence or record an explicit non-visible override_reason before creating "
                    "the session."
                ),
            )
        )
        return report

    readiness = _json_object(readiness_value, label="plan.visible_surface_readiness")
    origin_binding = _visible_surface_origin_binding_report(
        request_context=request_context,
        readiness=readiness,
    )
    surface_bound = readiness.get("surface_bound") is True and (
        _non_empty_string(readiness.get("thread_id"))
        or (
            _optional_string_value(readiness.get("mode")) == "parent_channel_fallback"
            and _non_empty_string(readiness.get("parent_channel_id"))
            and _non_empty_string(readiness.get("fallback_reason"))
        )
    )
    turn_delivery_proven = _optional_string_value(readiness.get("turn_posting_strategy")) in {
        "selected_speaker_profile_send",
        "fallback_poster",
    } and _non_empty_string(readiness.get("turn_delivery_probe_ref"))
    visible_closeout_proven = _non_empty_string(readiness.get("visible_closeout_probe_ref"))
    real_profile_gateway_replies = readiness.get("real_profile_gateway_replies") is True
    cli_actor_speech_only = readiness.get("cli_actor_speech_only") is True
    expected = _non_negative_int(readiness.get("visible_turns_expected"))
    posted = _non_negative_int(readiness.get("visible_turns_posted"))
    max_discussion_turns = _non_negative_int_or_none(readiness.get("max_discussion_turns"))
    participant_count = _non_negative_int_or_none(readiness.get("participant_count"))
    formula_expected = (
        max_discussion_turns + participant_count + 2
        if max_discussion_turns is not None and participant_count is not None
        else None
    )
    visible_turn_count_proven = (
        expected > 0
        and posted > 0
        and expected == posted
        and (
            task_id != RUNFIX3_003_TASK_ID
            or (formula_expected is not None and expected == formula_expected)
        )
    )
    report.update(origin_binding)
    report.update(
        {
            "surface_bound": surface_bound,
            "turn_delivery_proven": turn_delivery_proven,
            "visible_closeout_proven": visible_closeout_proven,
            "real_profile_gateway_replies": real_profile_gateway_replies,
            "cli_actor_speech_only": cli_actor_speech_only,
            "visible_turns_expected": expected,
            "visible_turns_posted": posted,
            "visible_turns_formula_expected": formula_expected,
            "visible_turn_count_proven": visible_turn_count_proven,
        }
    )
    missing: list[str] = []
    if task_id == RUNFIX3_003_TASK_ID and not origin_binding["exact_origin_binding_proven"]:
        missing.append("exact origin binding")
    if not surface_bound:
        missing.append("surface binding")
    if not turn_delivery_proven:
        missing.append("turn delivery probe")
    if not visible_closeout_proven:
        missing.append("visible closeout probe")
    if not real_profile_gateway_replies:
        missing.append("real profile/gateway replies")
    if cli_actor_speech_only:
        missing.append("non-CLI-actor speech path")
    if missing:
        blockers.append(
            _blocker(
                code="live_visible_surface_not_ready",
                owner="operator/Hermes-gateway",
                message="Live visible council preflight is missing: " + ", ".join(missing) + ".",
            )
        )
    report["ready"] = not missing
    return report


def _visible_surface_origin_binding_report(
    *,
    request_context: Mapping[str, object],
    readiness: Mapping[str, object],
) -> JsonObject:
    requested_chat_id = _optional_string_value(
        request_context.get("chat_id") or request_context.get("origin_chat_id")
    )
    requested_thread_id = _optional_string_value(
        request_context.get("thread_id") or request_context.get("origin_thread_id")
    )
    observed_chat_id = _optional_string_value(
        readiness.get("observed_chat_id") or readiness.get("chat_id")
    )
    observed_thread_id = _optional_string_value(
        readiness.get("observed_thread_id") or readiness.get("thread_id")
    )
    evidence_ref = _optional_string_value(
        readiness.get("origin_binding_evidence_ref") or readiness.get("exact_origin_binding_ref")
    )
    exact_origin_binding_proven = False
    exact_origin_binding_status = "unproven"
    exact_origin_binding_flag = readiness.get("exact_origin_binding") is True
    origin_values_present = (
        requested_chat_id is not None
        and requested_thread_id is not None
        and observed_chat_id is not None
        and observed_thread_id is not None
    )
    exact_origin_binding_matches = (
        origin_values_present
        and requested_chat_id == observed_chat_id
        and requested_thread_id == observed_thread_id
        and evidence_ref is not None
    )
    parent_channel_id = _optional_string_value(readiness.get("parent_channel_id"))
    fallback_target_approved = (
        _optional_string_value(readiness.get("mode")) == "parent_channel_fallback"
        and requested_chat_id is not None
        and parent_channel_id is not None
        and requested_chat_id == parent_channel_id
        and _non_empty_string(readiness.get("fallback_reason"))
        and evidence_ref is not None
    )
    fallback_observed_mismatch = fallback_target_approved and (
        (observed_chat_id is not None and observed_chat_id != parent_channel_id)
        or observed_thread_id is not None
    )
    approved_delivery_target = (
        parent_channel_id
        if fallback_target_approved
        else f"{requested_chat_id}:{requested_thread_id}"
        if requested_chat_id is not None and requested_thread_id is not None
        else None
    )
    if exact_origin_binding_flag and evidence_ref is not None:
        if exact_origin_binding_matches:
            exact_origin_binding_proven = True
            exact_origin_binding_status = "proven"
        elif fallback_target_approved and not fallback_observed_mismatch:
            exact_origin_binding_proven = True
            exact_origin_binding_status = "parent_channel_fallback"
        elif origin_values_present or fallback_observed_mismatch:
            exact_origin_binding_status = "mismatched"
    elif exact_origin_binding_matches:
        exact_origin_binding_proven = True
        exact_origin_binding_status = "proven"
    elif fallback_target_approved and not fallback_observed_mismatch:
        exact_origin_binding_proven = True
        exact_origin_binding_status = "parent_channel_fallback"
    elif origin_values_present or fallback_observed_mismatch:
        exact_origin_binding_status = "mismatched"
    return {
        "exact_origin_binding_status": exact_origin_binding_status,
        "exact_origin_binding_proven": exact_origin_binding_proven,
        "requested_chat_id": requested_chat_id,
        "requested_thread_id": requested_thread_id,
        "observed_chat_id": observed_chat_id,
        "observed_thread_id": observed_thread_id,
        "origin_binding_evidence_ref": evidence_ref,
        "approved_delivery_target": approved_delivery_target,
    }


def _participant_runtime_readiness_report(
    value: object,
    *,
    control_dependency_value: object,
    task_id: str,
    blockers: list[JsonObject],
) -> JsonObject:
    require_evidence = task_id == RUNFIX_012_TASK_ID
    report: JsonObject = {
        "runfix_task_id": RUNFIX_012_TASK_ID,
        "ready": False,
        "control_dependency": _runtime_control_dependency_report(control_dependency_value),
        "subscriber_presence": _empty_runtime_class_report("subscriber_presence"),
        "cursor_ack_freshness": _empty_runtime_class_report("cursor_ack_freshness"),
        "heartbeat_freshness": _empty_runtime_class_report("heartbeat_freshness"),
        "attendance_terminal": _empty_runtime_class_report("attendance_terminal"),
        "preparation_terminal": _empty_runtime_class_report("preparation_terminal"),
        "selected_runner_readiness": _empty_runtime_class_report("selected_runner_readiness"),
        "visible_surface_proof": _empty_runtime_class_report("visible_surface_proof"),
        "diagnostics": [],
        "rejected_substitutions": [],
    }
    if not isinstance(value, Mapping):
        if require_evidence:
            blockers.append(
                _blocker(
                    code="participant_runtime_readiness_missing",
                    owner="control/operator",
                    message=(
                        "plugin/RUNFIX-012 requires explicit participant_runtime_readiness "
                        "evidence from control/RUNFIX-011 diagnostics."
                    ),
                )
            )
        return report

    readiness = _json_object(value, label="plan.participant_runtime_readiness")
    diagnostics: list[JsonObject] = []
    rejected: list[JsonObject] = []
    source_mode = readiness.get("source_mode")
    if source_mode != "explicit":
        _append_runtime_blocker(
            blockers,
            diagnostics,
            code="participant_runtime_source_not_explicit",
            message=(
                "participant_runtime_readiness.source_mode must be explicit; gateway, "
                "transcript, export, profile, socket, or environment inference is unsupported."
            ),
        )

    class_specs: tuple[tuple[str, str, str], ...] = (
        ("subscriber_presence", "subscriber", "subscriber"),
        ("cursor_ack_freshness", "cursor_ack", "fresh"),
        ("heartbeat_freshness", "heartbeat", "fresh"),
        ("attendance_terminal", "attendance", "terminal_success"),
        ("preparation_terminal", "preparation", "terminal_success"),
        ("selected_runner_readiness", "selected_runner", "ready"),
        ("visible_surface_proof", "visible_surface", "proven"),
    )
    all_ready = source_mode == "explicit"
    for output_key, input_key, success_key in class_specs:
        class_report = _runtime_class_report(
            readiness.get(input_key),
            input_key=input_key,
            success_key=success_key,
            blockers=blockers,
            diagnostics=diagnostics,
            rejected_substitutions=rejected,
            require_evidence=require_evidence,
        )
        report[output_key] = class_report
        if class_report["status"] != "proven":
            all_ready = False

    control_dependency = cast(JsonObject, report["control_dependency"])
    if control_dependency["status"] != "proven":
        all_ready = False
    report["ready"] = bool(all_ready)
    report["diagnostics"] = cast(list[JsonValue], diagnostics)
    report["rejected_substitutions"] = cast(list[JsonValue], rejected)
    return report


def _runtime_control_dependency_report(value: object) -> JsonObject:
    output: JsonObject = {
        "status": "unproven",
        "task_id": None,
        "dependency_status": None,
        "evidence_ref": None,
    }
    if not isinstance(value, Mapping):
        return output
    dependency = _json_object(value, label="plan.control_dependency")
    task_id = dependency.get("task_id")
    status = dependency.get("status")
    evidence_ref = dependency.get("evidence_ref")
    if _non_empty_string(task_id):
        output["task_id"] = cast(str, task_id)
    if _non_empty_string(status):
        output["dependency_status"] = cast(str, status)
    if _non_empty_string(evidence_ref):
        output["evidence_ref"] = cast(str, evidence_ref)
    if (
        task_id == RUNFIX_012_CONTROL_DEPENDENCY_TASK_ID
        and status in RUNFIX_012_CONTROL_DEPENDENCY_STATUSES
        and _non_empty_string(evidence_ref)
    ):
        output["status"] = "proven"
    return output


def _newfix_start_gate_required(
    *, task_id: str, requested_output_mode: str, request_source: str
) -> bool:
    return (
        task_id == NEWFIX_006_TASK_ID
        and requested_output_mode == "live_visible_thread"
        and request_source.startswith("discord")
    )


def _newfix_control_dependency_report(value: object, *, expected_task_id: str) -> JsonObject:
    output: JsonObject = {
        "status": "unproven",
        "task_id": None,
        "dependency_status": None,
        "evidence_ref": None,
        "accepted_for_start": False,
    }
    if not isinstance(value, Mapping):
        return output
    dependency = _json_object(value, label="newfix.control_dependency")
    task_id = dependency.get("task_id")
    status = dependency.get("status")
    evidence_ref = dependency.get("evidence_ref")
    if _non_empty_string(task_id):
        output["task_id"] = cast(str, task_id)
    if _non_empty_string(status):
        output["dependency_status"] = cast(str, status)
    if _non_empty_string(evidence_ref):
        output["evidence_ref"] = cast(str, evidence_ref)
    if (
        task_id == expected_task_id
        and status in NEWFIX_CONSUMABLE_CONTROL_STATUSES
        and _non_empty_string(evidence_ref)
    ):
        output["status"] = "proven"
        output["accepted_for_start"] = status in NEWFIX_ACCEPTED_CONTROL_STATUSES
    return output


def _empty_newfix_prompt_evidence_report() -> JsonObject:
    return {
        "runfix_task_id": NEWFIX_006_TASK_ID,
        "status": "not_required",
        "control_dependency": _newfix_control_dependency_report(
            {}, expected_task_id=NEWFIX_004_CONTROL_DEPENDENCY_TASK_ID
        ),
        "result": "unproven",
        "prompt_context_sha256": None,
        "own_history_source_event_ids": [],
        "own_history_sources_present": False,
        "evidence_ref": None,
    }


def _newfix_prompt_evidence_report(
    value: object,
    *,
    task_id: str,
    requested_output_mode: str,
    request_source: str,
    blockers: list[JsonObject],
) -> JsonObject:
    report = _empty_newfix_prompt_evidence_report()
    if not _newfix_start_gate_required(
        task_id=task_id,
        requested_output_mode=requested_output_mode,
        request_source=request_source,
    ):
        return report
    report["status"] = "blocked"
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="newfix_prompt_evidence_missing",
                owner="control/operator",
                message=(
                    "plugin/NEWFIX-006 requires explicit selected_runner_prompt_evidence from "
                    "control/NEWFIX-004 before Discord-origin live-visible start can be reported."
                ),
            )
        )
        return report
    prompt = _json_object(value, label="plan.selected_runner_prompt_evidence")
    dependency = _newfix_control_dependency_report(
        prompt, expected_task_id=NEWFIX_004_CONTROL_DEPENDENCY_TASK_ID
    )
    result = _optional_string_value(prompt.get("result")) or "unproven"
    prompt_context_sha256 = _optional_string_value(prompt.get("prompt_context_sha256"))
    own_history_source_event_ids = _optional_string_list(
        prompt.get("own_history_source_event_ids") or prompt.get("own_history_source_ids")
    )
    report.update(
        {
            "control_dependency": dependency,
            "result": result,
            "prompt_context_sha256": prompt_context_sha256,
            "own_history_source_event_ids": cast(list[JsonValue], own_history_source_event_ids),
            "own_history_sources_present": bool(own_history_source_event_ids),
            "evidence_ref": dependency["evidence_ref"],
        }
    )
    if dependency["status"] != "proven":
        blockers.append(
            _blocker(
                code="newfix_prompt_control_dependency_unproven",
                owner="control",
                message=(
                    "selected_runner_prompt_evidence must cite control/NEWFIX-004 with a review-"
                    "pending or completed status and evidence_ref."
                ),
            )
        )
        return report
    if result == "blocked":
        blockers.append(
            _blocker(
                code="newfix_prompt_evidence_blocked",
                owner="control/operator",
                message=(
                    "selected_runner_prompt_evidence.result=blocked keeps Discord-origin live-"
                    "visible NEWFIX start blocked."
                ),
            )
        )
        return report
    if result != "pass":
        blockers.append(
            _blocker(
                code="newfix_prompt_result_unproven",
                owner="control/operator",
                message=(
                    "selected_runner_prompt_evidence.result must be pass for "
                    "NEWFIX start authority."
                ),
            )
        )
        return report
    if not own_history_source_event_ids:
        blockers.append(
            _blocker(
                code="newfix_prompt_own_history_missing",
                owner="control/operator",
                message=(
                    "selected_runner_prompt_evidence must include distinguishable selected-member "
                    "own-history source ids before NEWFIX live-visible start can be reported."
                ),
            )
        )
        return report
    if prompt_context_sha256 is None:
        blockers.append(
            _blocker(
                code="newfix_prompt_hash_missing",
                owner="control/operator",
                message="selected_runner_prompt_evidence.prompt_context_sha256 is required.",
            )
        )
        return report
    report["status"] = "proven"
    if dependency["accepted_for_start"] is not True:
        blockers.append(
            _blocker(
                code="newfix_prompt_review_closeout_pending",
                owner="control",
                message=(
                    "control/NEWFIX-004 remains review-pending, so prompt own-history proof may be "
                    "reported provisionally but cannot unlock ready_to_start."
                ),
            )
        )
    return report


def _empty_newfix_timeout_evidence_report() -> JsonObject:
    return {
        "runfix_task_id": NEWFIX_006_TASK_ID,
        "status": "not_required",
        "control_dependency": _newfix_control_dependency_report(
            {}, expected_task_id=NEWFIX_005_CONTROL_DEPENDENCY_TASK_ID
        ),
        "policy_required": False,
        "configured_timeout_sec": None,
        "effective_timeout_sec": None,
        "approved_alternative": False,
        "approval_basis": None,
        "compliant": False,
        "drift_blocked": False,
        "evidence_ref": None,
    }


def _newfix_timeout_evidence_report(
    value: object,
    *,
    task_id: str,
    requested_output_mode: str,
    request_source: str,
    blockers: list[JsonObject],
) -> JsonObject:
    report = _empty_newfix_timeout_evidence_report()
    if not _newfix_start_gate_required(
        task_id=task_id,
        requested_output_mode=requested_output_mode,
        request_source=request_source,
    ):
        return report
    report["status"] = "blocked"
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="newfix_timeout_evidence_missing",
                owner="control/operator",
                message=(
                    "plugin/NEWFIX-006 requires explicit selected_runner_timeout_evidence from "
                    "control/NEWFIX-005 before Discord-origin live-visible start can be reported."
                ),
            )
        )
        return report
    timeout_evidence = _json_object(value, label="plan.selected_runner_timeout_evidence")
    dependency = _newfix_control_dependency_report(
        timeout_evidence, expected_task_id=NEWFIX_005_CONTROL_DEPENDENCY_TASK_ID
    )
    policy_required = timeout_evidence.get("policy_required") is True
    configured_timeout_sec = _non_negative_int_or_none(
        timeout_evidence.get("configured_timeout_sec")
    )
    effective_timeout_sec = _non_negative_int_or_none(timeout_evidence.get("effective_timeout_sec"))
    approved_alternative = timeout_evidence.get("approved_alternative") is True
    approval_basis = _optional_string_value(timeout_evidence.get("approval_basis"))
    compliant = timeout_evidence.get("compliant") is True
    drift_blocked = (
        timeout_evidence.get("drift_blocked") is True
        or timeout_evidence.get("selected_runner_timeout_policy_blocked") is True
    )
    report.update(
        {
            "control_dependency": dependency,
            "policy_required": policy_required,
            "configured_timeout_sec": configured_timeout_sec,
            "effective_timeout_sec": effective_timeout_sec,
            "approved_alternative": approved_alternative,
            "approval_basis": approval_basis,
            "compliant": compliant,
            "drift_blocked": drift_blocked,
            "evidence_ref": dependency["evidence_ref"],
        }
    )
    if dependency["status"] != "proven":
        blockers.append(
            _blocker(
                code="newfix_timeout_control_dependency_unproven",
                owner="control",
                message=(
                    "selected_runner_timeout_evidence must cite control/NEWFIX-005 with a review-"
                    "pending or completed status and evidence_ref."
                ),
            )
        )
        return report
    if drift_blocked:
        blockers.append(
            _blocker(
                code="newfix_timeout_drift_blocked",
                owner="control/operator",
                message=(
                    "selected_runner_timeout_evidence reports timeout-policy drift, so NEWFIX live-"
                    "visible start remains blocked."
                ),
            )
        )
        return report
    if not policy_required or not compliant:
        blockers.append(
            _blocker(
                code="newfix_timeout_policy_invalid",
                owner="control/operator",
                message=(
                    "selected_runner_timeout_evidence must be policy_required=true "
                    "and compliant=true for NEWFIX live-visible start authority."
                ),
            )
        )
        return report
    valid_default = (
        configured_timeout_sec == NEWFIX_REQUIRED_TIMEOUT_SEC
        and effective_timeout_sec == NEWFIX_REQUIRED_TIMEOUT_SEC
        and not approved_alternative
    )
    valid_alternative = (
        approved_alternative
        and approval_basis is not None
        and configured_timeout_sec is not None
        and configured_timeout_sec > 0
        and effective_timeout_sec == configured_timeout_sec
    )
    if not (valid_default or valid_alternative):
        blockers.append(
            _blocker(
                code="newfix_timeout_policy_invalid",
                owner="control/operator",
                message=(
                    "selected_runner_timeout_evidence must prove dispatch_timeout_sec=120 or an "
                    "explicit approved alternative with approval_basis."
                ),
            )
        )
        return report
    report["status"] = "proven"
    if dependency["accepted_for_start"] is not True:
        blockers.append(
            _blocker(
                code="newfix_timeout_review_closeout_pending",
                owner="control",
                message=(
                    "control/NEWFIX-005 remains review-pending, so timeout proof may be reported "
                    "provisionally but cannot unlock ready_to_start."
                ),
            )
        )
    return report


def _empty_runtime_class_report(evidence_class: str) -> JsonObject:
    return {
        "status": "unproven",
        "evidence_class": evidence_class,
        "evidence_ref": None,
        "diagnostic": "not_supplied",
    }


def _runtime_class_report(
    value: object,
    *,
    input_key: str,
    success_key: str,
    blockers: list[JsonObject],
    diagnostics: list[JsonObject],
    rejected_substitutions: list[JsonObject],
    require_evidence: bool,
) -> JsonObject:
    report = _empty_runtime_class_report(input_key)
    if not isinstance(value, Mapping):
        if require_evidence:
            _append_runtime_blocker(
                blockers,
                diagnostics,
                code=f"{input_key}_evidence_missing",
                message=f"participant_runtime_readiness.{input_key} evidence is required.",
            )
        return report

    evidence = _json_object(value, label=f"plan.participant_runtime_readiness.{input_key}")
    evidence_ref = evidence.get("evidence_ref")
    if _non_empty_string(evidence_ref):
        report["evidence_ref"] = cast(str, evidence_ref)

    substitution = _runtime_substitution(evidence)
    if substitution is not None:
        report["status"] = "rejected"
        report["diagnostic"] = substitution["reason"]
        rejected_substitutions.append(substitution)
        if require_evidence:
            _append_runtime_blocker(
                blockers,
                diagnostics,
                code=f"{input_key}_substituted_evidence",
                message=(
                    f"participant_runtime_readiness.{input_key} uses substituted "
                    f"{substitution['kind']} evidence, not participant runtime readiness proof."
                ),
            )
        return report

    if evidence.get("ambiguous") is True:
        report["status"] = "ambiguous"
        report["diagnostic"] = "ambiguous"
        if require_evidence:
            _append_runtime_blocker(
                blockers,
                diagnostics,
                code=f"{input_key}_evidence_ambiguous",
                message=f"participant_runtime_readiness.{input_key} evidence is ambiguous.",
            )
        return report

    if evidence.get("stale") is True or evidence.get("fresh") is False:
        report["status"] = "stale"
        report["diagnostic"] = "stale"
        if require_evidence:
            _append_runtime_blocker(
                blockers,
                diagnostics,
                code=f"{input_key}_evidence_stale",
                message=f"participant_runtime_readiness.{input_key} evidence is stale.",
            )
        return report

    if input_key in {"attendance", "preparation"}:
        terminal_status = _optional_string_value(evidence.get("terminal_status"))
        report["terminal_status"] = terminal_status
        if terminal_status in {"timeout", "failure"} and _non_empty_string(evidence_ref):
            report["status"] = "terminal_failure"
            report["diagnostic"] = terminal_status
            if require_evidence:
                _append_runtime_blocker(
                    blockers,
                    diagnostics,
                    code=f"{input_key}_terminal_{terminal_status}",
                    message=(
                        f"participant_runtime_readiness.{input_key} reached terminal "
                        f"{terminal_status}; evidence is diagnostic, not readiness proof."
                    ),
                )
            return report

    if evidence.get(success_key) is True and _non_empty_string(evidence_ref):
        if input_key == "selected_runner" and evidence.get("prerequisites_met") is not True:
            report["status"] = "unproven"
            report["diagnostic"] = "selected_runner_prerequisites_missing"
            if require_evidence:
                _append_runtime_blocker(
                    blockers,
                    diagnostics,
                    code="selected_runner_prerequisites_missing",
                    message=(
                        "participant_runtime_readiness.selected_runner requires "
                        "prerequisites_met=true."
                    ),
                )
            return report
        report["status"] = "proven"
        report["diagnostic"] = "explicit"
        return report

    if require_evidence:
        _append_runtime_blocker(
            blockers,
            diagnostics,
            code=f"{input_key}_evidence_unproven",
            message=(
                f"participant_runtime_readiness.{input_key} must provide {success_key}=true "
                "and a non-empty evidence_ref."
            ),
        )
    return report


def _runtime_substitution(evidence: JsonObject) -> JsonObject | None:
    substitution_flags: tuple[tuple[str, str], ...] = (
        ("gateway_only", "gateway-only"),
        ("transcript_export_only", "transcript/export-only"),
        ("parent_channel_fallback_only", "parent-channel-fallback-only"),
        ("manual_profile_only", "manual/fallback-profile-only"),
    )
    for key, kind in substitution_flags:
        if evidence.get(key) is True:
            return {"kind": kind, "reason": key}
    evidence_kind = _optional_string_value(evidence.get("evidence_kind")) or _optional_string_value(
        evidence.get("source_kind")
    )
    if evidence_kind in {
        "gateway_only",
        "transcript_export_only",
        "parent_channel_fallback_only",
        "manual_profile_only",
    }:
        return {"kind": evidence_kind.replace("_", "-"), "reason": evidence_kind}
    return None


def _append_runtime_blocker(
    blockers: list[JsonObject],
    diagnostics: list[JsonObject],
    *,
    code: str,
    message: str,
) -> None:
    blocker = _blocker(code=code, owner="control/operator", message=message)
    blockers.append(blocker)
    diagnostics.append(blocker)


def _visible_author_guard_report(
    value: object,
    *,
    eligible_profiles: list[JsonObject],
    requested_output_mode: str,
    task_id: str,
    blockers: list[JsonObject],
) -> JsonObject:
    require_evidence = task_id == RUNFIX_015_TASK_ID
    evaluate_optional_guard = (
        task_id in {RUNFIX_010_TASK_ID, RUNFIX3_003_TASK_ID}
        and requested_output_mode == "live_visible_thread"
        and isinstance(value, Mapping)
    )
    report: JsonObject = {
        "runfix_task_id": RUNFIX_015_TASK_ID,
        "guard_surface": "pre_council_new_activation_plan",
        "runtime_enforcement": False,
        "operator_must_consume_before_session_creation": True,
        "status": "not_required",
        "ready": not require_evidence,
        "profile_author_probes": [],
        "env_precedence_proof": _empty_env_precedence_report(),
        "per_turn_visible_evidence": [],
        "final_result_report": {
            "status": "unproven",
            "lifecycle": "not_evaluated",
            "visible_turns_posted": 0,
            "real_profile_gateway_replies": False,
            "selected_runner_labels": [],
            "shared_default_author_fallback_status": "unproven",
        },
        "rejected_substitutions": [],
    }
    if not require_evidence and not evaluate_optional_guard:
        return report

    report["status"] = "blocked"
    report["ready"] = False
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="visible_author_guard_missing",
                owner="operator/Hermes-gateway",
                message=(
                    "Live-visible Discord-origin start requires explicit visible_author_guard "
                    "evidence before council.new/session creation."
                ),
            )
        )
        return report

    guard = _json_object(value, label="plan.visible_author_guard")
    if guard.get("guard_surface") != "pre_council_new_activation_plan":
        blockers.append(
            _blocker(
                code="visible_author_guard_surface_invalid",
                owner="operator",
                message=(
                    "visible_author_guard.guard_surface must be pre_council_new_activation_plan."
                ),
            )
        )
    if guard.get("runtime_enforcement") is True:
        blockers.append(
            _blocker(
                code="visible_author_guard_runtime_claim_unsupported",
                owner="operator",
                message=(
                    "atn_discussion_activation_plan is planner-only and must not claim "
                    "runtime visible-author enforcement."
                ),
            )
        )

    profile_reports, profile_by_name = _visible_author_profile_reports(
        guard.get("profile_author_probes"),
        eligible_profiles=eligible_profiles,
        blockers=blockers,
    )
    env_report = _env_precedence_report(
        guard.get("env_precedence_proof"),
        profiles=profile_reports,
        blockers=blockers,
    )
    turn_reports = _per_turn_visible_evidence_reports(
        guard.get("per_turn_visible_evidence"),
        profile_by_name=profile_by_name,
        blockers=blockers,
    )
    final_result = _visible_author_final_result_report(
        guard.get("final_result"),
        turn_reports=turn_reports,
        profile_reports=profile_reports,
        blockers=blockers,
    )
    rejected_substitutions = [
        item for item in profile_reports if item.get("same_path_probe_status") == "rejected"
    ]

    report["profile_author_probes"] = cast(list[JsonValue], profile_reports)
    report["env_precedence_proof"] = env_report
    report["per_turn_visible_evidence"] = cast(list[JsonValue], turn_reports)
    report["final_result_report"] = final_result
    report["rejected_substitutions"] = cast(list[JsonValue], rejected_substitutions)
    ready = (
        all(item["status"] == "proven" for item in profile_reports)
        and env_report["status"] == "proven"
        and bool(turn_reports)
        and all(item["status"] == "proven" for item in turn_reports)
        and final_result["status"] == "proven"
        and final_result["shared_default_author_fallback_status"] == "none"
    )
    report["ready"] = ready
    report["status"] = "proven" if ready else "blocked"
    return report


def _visible_author_profile_reports(
    value: object,
    *,
    eligible_profiles: list[JsonObject],
    blockers: list[JsonObject],
) -> tuple[list[JsonObject], dict[str, JsonObject]]:
    if not isinstance(value, list):
        blockers.append(
            _blocker(
                code="visible_author_profile_probes_missing",
                owner="operator/Hermes-gateway",
                message="visible_author_guard.profile_author_probes must be an explicit list.",
            )
        )
        return [], {}

    reports: list[JsonObject] = []
    by_name: dict[str, JsonObject] = {}
    eligible_names = {
        cast(str, item["profile"])
        for item in eligible_profiles
        if _non_empty_string(item.get("profile"))
    }
    supplied_names: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            blockers.append(
                _blocker(
                    code="visible_author_profile_probe_invalid",
                    owner="operator/Hermes-gateway",
                    message=(
                        f"visible_author_guard.profile_author_probes[{index}] must be an object."
                    ),
                )
            )
            continue
        probe = _json_object(
            item, label=f"plan.visible_author_guard.profile_author_probes[{index}]"
        )
        profile = _optional_string_value(probe.get("profile"))
        report = _visible_author_profile_report(probe, index=index, blockers=blockers)
        reports.append(report)
        if profile is not None:
            supplied_names.add(profile)
            by_name[profile] = report

    missing_profiles = sorted(eligible_names - supplied_names)
    for profile in missing_profiles:
        blockers.append(
            _blocker(
                code="visible_author_profile_probe_missing",
                owner="operator/Hermes-gateway",
                message=(
                    "visible_author_guard.profile_author_probes is missing same-path "
                    f"author evidence for eligible profile {profile}."
                ),
            )
        )
    return reports, by_name


def _visible_author_profile_report(
    probe: JsonObject,
    *,
    index: int,
    blockers: list[JsonObject],
) -> JsonObject:
    profile = _optional_string_value(probe.get("profile"))
    expected_source = _optional_string_value(probe.get("expected_author_source"))
    expected_author_id = _optional_string_value(probe.get("expected_author_id"))
    absence_reason = _optional_string_value(probe.get("expected_author_absence_approved_reason"))
    observed_bot_id = _optional_string_value(probe.get("observed_bot_id"))
    observed_username = _optional_string_value(probe.get("observed_username"))
    source_env = _optional_string_value(probe.get("source_env"))
    posting_path = _optional_string_value(probe.get("posting_path"))
    shared_default_author = probe.get("shared_default_author") is True
    negative_proof_ref = _optional_string_value(probe.get("shared_default_negative_proof_ref"))
    profile_local_override_present = probe.get("profile_local_override_present") is True
    same_path_probe = (
        _json_object(probe.get("same_path_probe"), label="same_path_probe")
        if isinstance(probe.get("same_path_probe"), Mapping)
        else {}
    )
    same_path_probe_status = _same_path_probe_status(
        same_path_probe,
        profile=profile,
        posting_path=posting_path,
        blockers=blockers,
    )
    output: JsonObject = {
        "status": "proven",
        "profile": profile,
        "expected_author_source": expected_source,
        "expected_author_id": expected_author_id,
        "expected_author_absence_approved_reason": absence_reason,
        "observed_bot_id": observed_bot_id,
        "observed_username": observed_username,
        "source_env": source_env,
        "posting_path": posting_path,
        "same_path_probe": {
            "status": same_path_probe_status,
            "evidence_ref": _optional_string_value(same_path_probe.get("evidence_ref")),
            "message_id": _optional_string_value(same_path_probe.get("message_id")),
            "surface": _optional_string_value(same_path_probe.get("surface")),
            "posting_path": _optional_string_value(same_path_probe.get("posting_path")),
        },
        "same_path_probe_status": same_path_probe_status,
        "shared_default_author": shared_default_author,
        "shared_default_negative_proof_ref": negative_proof_ref,
        "profile_local_override_present": profile_local_override_present,
    }
    missing_fields = [
        name
        for name, item in (
            ("profile", profile),
            ("observed_bot_id", observed_bot_id),
            ("observed_username", observed_username),
            ("source_env", source_env),
            ("posting_path", posting_path),
        )
        if item is None
    ]
    if missing_fields:
        _append_visible_author_blocker(
            blockers,
            output,
            code="visible_author_profile_probe_fields_missing",
            message=(
                f"visible_author_guard.profile_author_probes[{index}] is missing: "
                + ", ".join(missing_fields)
                + "."
            ),
        )
    if expected_source not in {"registry_snapshot", "approved_profile_author_map"}:
        _append_visible_author_blocker(
            blockers,
            output,
            code="visible_author_expected_source_ambiguous",
            message=(
                "expected_author_source must be registry_snapshot or approved_profile_author_map."
            ),
        )
    if expected_author_id is None and absence_reason is None:
        _append_visible_author_blocker(
            blockers,
            output,
            code="visible_author_expected_author_missing",
            message=("expected_author_id or expected_author_absence_approved_reason is required."),
        )
    if expected_author_id is not None and observed_bot_id != expected_author_id:
        _append_visible_author_blocker(
            blockers,
            output,
            code="visible_author_observed_bot_mismatch",
            message=(
                f"Observed bot id for {profile or 'unknown profile'} does not match "
                "expected_author_id."
            ),
        )
    if expected_author_id is not None and not profile_local_override_present:
        _append_visible_author_blocker(
            blockers,
            output,
            code="visible_author_profile_local_override_missing",
            message=(
                f"Profile-local author override is required for {profile or 'unknown profile'}."
            ),
        )
    if shared_default_author:
        _append_visible_author_blocker(
            blockers,
            output,
            code="visible_author_shared_default_detected",
            message=(
                f"Shared/default author fallback is detected for {profile or 'unknown profile'}."
            ),
        )
    if not negative_proof_ref:
        _append_visible_author_blocker(
            blockers,
            output,
            code="visible_author_shared_default_negative_proof_missing",
            message=(
                "shared_default_negative_proof_ref is required to prove no shared/default "
                "author fallback."
            ),
        )
    if same_path_probe_status != "proven":
        output["status"] = "blocked"
    return output


def _same_path_probe_status(
    probe: JsonObject,
    *,
    profile: str | None,
    posting_path: str | None,
    blockers: list[JsonObject],
) -> str:
    evidence_ref = _optional_string_value(probe.get("evidence_ref"))
    message_id = _optional_string_value(probe.get("message_id"))
    surface = _optional_string_value(probe.get("surface"))
    probe_posting_path = _optional_string_value(probe.get("posting_path"))
    forbidden_surfaces = {
        "generic_discord_send",
        "transcript_export",
        "daemon_cli_actor_speech",
        "manual_profile_reply",
        "parent_channel_fallback",
        "raw_message_id",
    }
    if surface in forbidden_surfaces:
        blockers.append(
            _blocker(
                code="visible_author_same_path_probe_substituted",
                owner="operator/Hermes-gateway",
                message=(
                    "Same-path author probe cannot be satisfied by generic Discord send, "
                    "transcript/export, daemon CLI actor speech, manual profile reply, "
                    "parent-channel fallback, or raw message id alone."
                ),
            )
        )
        return "rejected"
    if not evidence_ref or not message_id or not surface or not probe_posting_path:
        blockers.append(
            _blocker(
                code="visible_author_same_path_probe_missing",
                owner="operator/Hermes-gateway",
                message=(
                    f"Same-path probe for {profile or 'unknown profile'} requires "
                    "evidence_ref, message_id, surface, and posting_path."
                ),
            )
        )
        return "unproven"
    if posting_path is not None and probe_posting_path != posting_path:
        blockers.append(
            _blocker(
                code="visible_author_posting_path_mismatch",
                owner="operator/Hermes-gateway",
                message=(
                    f"Same-path probe posting_path for {profile or 'unknown profile'} "
                    "must match the profile posting_path."
                ),
            )
        )
        return "mismatch"
    return "proven"


def _empty_env_precedence_report() -> JsonObject:
    return {
        "status": "unproven",
        "order": [],
        "per_key_source": [],
        "final_author_source": None,
    }


def _env_precedence_report(
    value: object,
    *,
    profiles: list[JsonObject],
    blockers: list[JsonObject],
) -> JsonObject:
    report = _empty_env_precedence_report()
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="visible_author_env_precedence_missing",
                owner="operator/Hermes-gateway",
                message="visible_author_guard.env_precedence_proof is required.",
            )
        )
        return report

    proof = _json_object(value, label="plan.visible_author_guard.env_precedence_proof")
    order = _optional_string_list(proof.get("order"))
    per_key_source = _env_per_key_source(proof.get("per_key_source"))
    final_author_source = _optional_string_value(proof.get("final_author_source"))
    report["order"] = cast(list[JsonValue], order)
    report["per_key_source"] = cast(list[JsonValue], per_key_source)
    report["final_author_source"] = final_author_source
    report["status"] = "proven"

    if not order:
        _append_env_blocker(
            blockers,
            report,
            code="visible_author_env_precedence_order_missing",
            message="env_precedence_proof.order is required.",
        )
    if proof.get("ambiguous_order") is True or len(order) != len(set(order)):
        _append_env_blocker(
            blockers,
            report,
            code="visible_author_env_precedence_ambiguous",
            message="env_precedence_proof.order must be unambiguous.",
        )
    if _env_order_reversed(order):
        _append_env_blocker(
            blockers,
            report,
            code="visible_author_env_precedence_reversed",
            message="shared/default sources must precede profile_local in env precedence order.",
        )
    if final_author_source in {"shared_default", "default"}:
        _append_env_blocker(
            blockers,
            report,
            code="visible_author_env_final_author_shared_default",
            message="Final visible author must not be sourced from shared/default env.",
        )
    if final_author_source != "profile_local":
        _append_env_blocker(
            blockers,
            report,
            code="visible_author_env_final_author_not_profile_local",
            message="env_precedence_proof.final_author_source must be profile_local.",
        )

    expected_author_profiles = {
        cast(str, item["profile"])
        for item in profiles
        if _non_empty_string(item.get("profile"))
        and _non_empty_string(item.get("expected_author_id"))
    }
    profile_local_sources = {
        cast(str, item["profile"])
        for item in per_key_source
        if item.get("source") == "profile_local" and _non_empty_string(item.get("profile"))
    }
    for profile in sorted(expected_author_profiles - profile_local_sources):
        _append_env_blocker(
            blockers,
            report,
            code="visible_author_env_profile_local_override_absent",
            message=(
                f"env_precedence_proof.per_key_source lacks profile_local source for {profile}."
            ),
        )
    return report


def _env_per_key_source(value: object) -> list[JsonObject]:
    if not isinstance(value, list):
        return []
    output: list[JsonObject] = []
    for index, item in enumerate(value):
        source = _json_object(item, label=f"env_precedence_proof.per_key_source[{index}]")
        output.append(
            {
                "profile": _optional_string_value(source.get("profile")),
                "key": _optional_string_value(source.get("key")),
                "source": _optional_string_value(source.get("source")),
                "value_ref": _optional_string_value(source.get("value_ref")),
            }
        )
    return output


def _env_order_reversed(order: list[str]) -> bool:
    if "profile_local" not in order:
        return True
    profile_index = order.index("profile_local")
    default_indexes = [
        index for index, source in enumerate(order) if source in {"shared_default", "default"}
    ]
    if not default_indexes:
        return True
    return any(index > profile_index for index in default_indexes)


def _per_turn_visible_evidence_reports(
    value: object,
    *,
    profile_by_name: dict[str, JsonObject],
    blockers: list[JsonObject],
) -> list[JsonObject]:
    if not isinstance(value, list):
        blockers.append(
            _blocker(
                code="visible_author_per_turn_evidence_missing",
                owner="operator/Hermes-gateway",
                message="visible_author_guard.per_turn_visible_evidence must be an explicit list.",
            )
        )
        return []
    reports: list[JsonObject] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            blockers.append(
                _blocker(
                    code="visible_author_per_turn_evidence_invalid",
                    owner="operator/Hermes-gateway",
                    message=(
                        "visible_author_guard.per_turn_visible_evidence"
                        f"[{index}] must be an object."
                    ),
                )
            )
            continue
        turn = _json_object(
            item, label=f"plan.visible_author_guard.per_turn_visible_evidence[{index}]"
        )
        reports.append(
            _per_turn_visible_evidence_report(
                turn,
                index=index,
                profile_by_name=profile_by_name,
                blockers=blockers,
            )
        )
    return reports


def _per_turn_visible_evidence_report(
    turn: JsonObject,
    *,
    index: int,
    profile_by_name: dict[str, JsonObject],
    blockers: list[JsonObject],
) -> JsonObject:
    discord_message_id = _optional_string_value(turn.get("discord_message_id"))
    selected_member = _optional_string_value(turn.get("selected_member"))
    profile_author_id = _optional_string_value(turn.get("profile_author_id"))
    posting_path = _optional_string_value(turn.get("posting_path"))
    speech_event_id = _optional_string_value(turn.get("speech_event_id"))
    output: JsonObject = {
        "status": "proven",
        "discord_message_id": discord_message_id,
        "selected_member": selected_member,
        "profile_author_id": profile_author_id,
        "posting_path": posting_path,
        "speech_event_id": speech_event_id,
    }
    missing = [
        name
        for name, item in (
            ("discord_message_id", discord_message_id),
            ("selected_member", selected_member),
            ("profile_author_id", profile_author_id),
            ("posting_path", posting_path),
            ("speech_event_id", speech_event_id),
        )
        if item is None
    ]
    if missing:
        _append_turn_blocker(
            blockers,
            output,
            code="visible_author_per_turn_fields_missing",
            message=(
                f"visible_author_guard.per_turn_visible_evidence[{index}] is missing: "
                + ", ".join(missing)
                + "."
            ),
        )
    if speech_event_id is None:
        _append_turn_blocker(
            blockers,
            output,
            code="visible_author_per_turn_speech_link_missing",
            message="Per-turn visible evidence must link to a speech_event_id.",
        )
    profile_report = profile_by_name.get(selected_member or "")
    if profile_report is None:
        _append_turn_blocker(
            blockers,
            output,
            code="visible_author_per_turn_selected_member_unproven",
            message="selected_member must have proven profile author evidence.",
        )
        return output
    if profile_author_id != profile_report.get("expected_author_id"):
        _append_turn_blocker(
            blockers,
            output,
            code="visible_author_per_turn_author_mismatch",
            message="Per-turn profile_author_id must match the selected member profile author id.",
        )
    if posting_path != profile_report.get("posting_path"):
        _append_turn_blocker(
            blockers,
            output,
            code="visible_author_per_turn_posting_path_mismatch",
            message="Per-turn posting_path must match the selected member posting path.",
        )
    return output


def _visible_author_final_result_report(
    value: object,
    *,
    turn_reports: list[JsonObject],
    profile_reports: list[JsonObject],
    blockers: list[JsonObject],
) -> JsonObject:
    result = (
        _json_object(value, label="plan.visible_author_guard.final_result")
        if isinstance(value, Mapping)
        else {}
    )
    selected_runner_labels = _optional_string_list(result.get("selected_runner_labels"))
    shared_default_status = (
        _optional_string_value(result.get("shared_default_author_fallback_status")) or "unproven"
    )
    output: JsonObject = {
        "status": "proven",
        "lifecycle": _optional_string_value(result.get("lifecycle")) or "unproven",
        "visible_turns_posted": _non_negative_int(result.get("visible_turns_posted")),
        "real_profile_gateway_replies": result.get("real_profile_gateway_replies") is True,
        "selected_runner_labels": cast(list[JsonValue], selected_runner_labels),
        "shared_default_author_fallback_status": shared_default_status,
    }
    if output["lifecycle"] == "unproven":
        output["status"] = "blocked"
        blockers.append(
            _blocker(
                code="visible_author_final_lifecycle_missing",
                owner="operator/atn-control",
                message="final_result.lifecycle must be explicit.",
            )
        )
    if output["visible_turns_posted"] != len(turn_reports):
        output["status"] = "blocked"
        blockers.append(
            _blocker(
                code="visible_author_final_visible_turn_count_mismatch",
                owner="operator/Hermes-gateway",
                message="final_result.visible_turns_posted must equal per-turn evidence count.",
            )
        )
    if output["real_profile_gateway_replies"] is not True:
        output["status"] = "blocked"
        blockers.append(
            _blocker(
                code="visible_author_final_real_profile_gateway_replies_missing",
                owner="operator/Hermes-gateway",
                message="final_result.real_profile_gateway_replies must be true.",
            )
        )
    if not selected_runner_labels:
        output["status"] = "blocked"
        blockers.append(
            _blocker(
                code="visible_author_final_selected_runner_labels_missing",
                owner="operator",
                message="final_result.selected_runner_labels must separate selected-runner proof.",
            )
        )
    if shared_default_status != "none" or any(
        item.get("shared_default_author") is True for item in profile_reports
    ):
        output["status"] = "blocked"
        blockers.append(
            _blocker(
                code="visible_author_final_shared_default_status_not_clear",
                owner="operator/Hermes-gateway",
                message="final_result.shared_default_author_fallback_status must be none.",
            )
        )
    return output


def _append_visible_author_blocker(
    blockers: list[JsonObject],
    report: JsonObject,
    *,
    code: str,
    message: str,
) -> None:
    blockers.append(_blocker(code=code, owner="operator/Hermes-gateway", message=message))
    report["status"] = "blocked"


def _append_env_blocker(
    blockers: list[JsonObject],
    report: JsonObject,
    *,
    code: str,
    message: str,
) -> None:
    blockers.append(_blocker(code=code, owner="operator/Hermes-gateway", message=message))
    report["status"] = "blocked"


def _append_turn_blocker(
    blockers: list[JsonObject],
    report: JsonObject,
    *,
    code: str,
    message: str,
) -> None:
    blockers.append(_blocker(code=code, owner="operator/Hermes-gateway", message=message))
    report["status"] = "blocked"


def _final_report_contract() -> JsonObject:
    return {
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


def _runfix3_live_thread_proof_report(
    value: object,
    *,
    task_id: str,
    requested_output_mode: str,
    expected_profiles: Sequence[str],
    expected_visible_turns: int | None,
    approved_delivery_target: str | None,
    visible_turn_count_proven: bool,
    blockers: list[JsonObject],
) -> JsonObject:
    report: JsonObject = {
        "runfix_task_id": RUNFIX3_003_TASK_ID,
        "status": "not_required",
        "selected_runner_proof": _empty_runfix3_selected_runner_report(),
        "participant_closeout_coverage": _empty_runfix3_closeout_report(),
        "moderator_synthesis_coverage": _empty_runfix3_moderator_synthesis_report(),
        "delivery_target_rows": [],
        "delivery_target_proof": _empty_runfix3_delivery_target_proof(),
        "prompt_envelope_proof": _empty_runfix3_prompt_envelope_report(),
        "dialogue_mode_proof": _empty_runfix3_dialogue_mode_report(),
        "drift_status": _empty_runfix3_drift_status_report(),
        "fail_closed_final_status": _empty_runfix3_fail_closed_report(),
    }
    if task_id != RUNFIX3_003_TASK_ID or requested_output_mode != "live_visible_thread":
        return report

    report["status"] = "blocked"
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="runfix3_live_thread_proof_missing",
                owner="operator",
                message="plugin/RUNFIX3-003 requires explicit runfix3_live_thread_proof evidence.",
            )
        )
        return report

    proof = _json_object(value, label="plan.runfix3_live_thread_proof")
    selected_runner = _runfix3_selected_runner_report(
        proof.get("selected_runner") or proof.get("selected_runner_proof"),
        blockers=blockers,
    )
    participant_closeout = _runfix3_participant_closeout_report(
        proof.get("participant_closeout") or proof.get("participant_closeout_coverage"),
        expected_profiles=expected_profiles,
        blockers=blockers,
    )
    moderator_synthesis = _runfix3_moderator_synthesis_report(
        proof.get("moderator_synthesis") or proof.get("moderator_synthesis_coverage"),
        blockers=blockers,
    )
    delivery_target = _runfix3_delivery_target_report(
        proof.get("delivery_targets") or proof.get("delivery_target_proof"),
        expected_row_count=expected_visible_turns,
        approved_delivery_target=approved_delivery_target,
        blockers=blockers,
    )
    prompt_envelope = _runfix3_prompt_envelope_report(
        proof.get("prompt_envelope") or proof.get("prompt_envelope_proof"),
        blockers=blockers,
    )
    dialogue_mode = _runfix3_dialogue_mode_report(
        proof.get("dialogue_mode") or proof.get("dialogue_mode_proof"),
        blockers=blockers,
    )
    drift_status = _runfix3_drift_status_report(
        proof.get("drift") or proof.get("drift_status"),
        blockers=blockers,
    )
    fail_closed = _runfix3_fail_closed_report(
        proof.get("final_fail_closed") or proof.get("fail_closed_proof_status"),
        blockers=blockers,
    )
    report.update(
        {
            "selected_runner_proof": selected_runner,
            "participant_closeout_coverage": participant_closeout,
            "moderator_synthesis_coverage": moderator_synthesis,
            "delivery_target_rows": delivery_target["rows"],
            "delivery_target_proof": delivery_target["delivery_target_proof"],
            "prompt_envelope_proof": prompt_envelope,
            "dialogue_mode_proof": dialogue_mode,
            "drift_status": drift_status,
            "fail_closed_final_status": fail_closed,
        }
    )
    if not visible_turn_count_proven:
        blockers.append(
            _blocker(
                code="runfix3_visible_turn_count_unproven",
                owner="operator/control",
                message=(
                    "visible turns must prove max_discussion_turns + participant_count + 2 "
                    "before RUNFIX3 live-thread proof can be reported as proven."
                ),
            )
        )
    required_reports = (
        selected_runner,
        participant_closeout,
        moderator_synthesis,
        cast(JsonObject, delivery_target["delivery_target_proof"]),
        prompt_envelope,
        dialogue_mode,
        drift_status,
        fail_closed,
    )
    if visible_turn_count_proven and all(item["status"] == "proven" for item in required_reports):
        report["status"] = "proven"
    return report


def _empty_runfix3_closeout_report() -> JsonObject:
    return {
        "status": "unproven",
        "expected_participants": [],
        "closed_out_participants": [],
        "missing_participants": [],
        "evidence_ref": None,
    }


def _empty_runfix3_moderator_synthesis_report() -> JsonObject:
    return {
        "status": "unproven",
        "synthesis_posted": False,
        "evidence_ref": None,
    }


def _empty_runfix3_delivery_target_proof() -> JsonObject:
    return {
        "status": "unproven",
        "aggregate_match": False,
        "evidence_ref": None,
    }


def _empty_runfix3_prompt_envelope_report() -> JsonObject:
    return {
        "status": "unproven",
        "content_audit_separated": False,
        "control_metadata_leaked": False,
        "evidence_ref": None,
    }


def _empty_runfix3_dialogue_mode_report() -> JsonObject:
    return {
        "status": "unproven",
        "participant_to_participant": False,
        "moderator_substitute_turns": False,
        "evidence_ref": None,
    }


def _empty_runfix3_drift_status_report() -> JsonObject:
    return {
        "status": "unproven",
        "drift_detected": False,
        "repaired_forward": False,
        "unresolved_closeout": False,
        "evidence_ref": None,
    }


def _empty_runfix3_fail_closed_report() -> JsonObject:
    return {
        "status": "unproven",
        "final_status": "unproven",
        "fail_closed": False,
        "evidence_ref": None,
    }


def _empty_runfix3_selected_runner_report() -> JsonObject:
    return {
        "status": "unproven",
        "selected_member": None,
        "speaker_selected_event_id": None,
        "runner_invocation_started_ref": None,
        "runner_invocation_succeeded_ref": None,
        "speech_event_id": None,
        "delivery_target_match": False,
        "evidence_ref": None,
    }


def _runfix3_selected_runner_report(
    value: object,
    *,
    blockers: list[JsonObject],
) -> JsonObject:
    report = _empty_runfix3_selected_runner_report()
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="runfix3_selected_runner_proof_missing",
                owner="operator/control",
                message=(
                    "runfix3_live_thread_proof.selected_runner evidence is required to "
                    "expose the selected-runner proof chain as a separate RUNFIX3 "
                    "acceptance axis."
                ),
            )
        )
        report["status"] = "blocked"
        return report

    selected_runner = _json_object(value, label="plan.runfix3_live_thread_proof.selected_runner")
    report.update(
        {
            "selected_member": _optional_string_value(selected_runner.get("selected_member")),
            "speaker_selected_event_id": _optional_string_value(
                selected_runner.get("speaker_selected_event_id")
            ),
            "runner_invocation_started_ref": _optional_string_value(
                selected_runner.get("runner_invocation_started_ref")
            ),
            "runner_invocation_succeeded_ref": _optional_string_value(
                selected_runner.get("runner_invocation_succeeded_ref")
            ),
            "speech_event_id": _optional_string_value(selected_runner.get("speech_event_id")),
            "delivery_target_match": selected_runner.get("delivery_target_match") is True,
            "evidence_ref": _optional_string_value(selected_runner.get("evidence_ref")),
        }
    )
    if all(
        (
            _non_empty_string(report["selected_member"]),
            _non_empty_string(report["speaker_selected_event_id"]),
            _non_empty_string(report["runner_invocation_started_ref"]),
            _non_empty_string(report["runner_invocation_succeeded_ref"]),
            _non_empty_string(report["speech_event_id"]),
            report["delivery_target_match"] is True,
            _non_empty_string(report["evidence_ref"]),
        )
    ):
        report["status"] = "proven"
        return report

    blockers.append(
        _blocker(
            code="runfix3_selected_runner_proof_unproven",
            owner="operator/control",
            message=(
                "selected-runner proof must link selected_member, speaker_selected, "
                "runner started, runner succeeded, canonical speech, and bound delivery "
                "evidence before RUNFIX3 acceptance can be reported as proven."
            ),
        )
    )
    report["status"] = "blocked"
    return report


def _runfix3_participant_closeout_report(
    value: object,
    *,
    expected_profiles: Sequence[str],
    blockers: list[JsonObject],
) -> JsonObject:
    report = _empty_runfix3_closeout_report()
    report["expected_participants"] = list(expected_profiles)
    if not expected_profiles:
        report["status"] = "blocked"
        return report
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="runfix3_participant_closeout_missing",
                owner="operator/control",
                message="runfix3_live_thread_proof.participant_closeout evidence is required.",
            )
        )
        report["status"] = "blocked"
        return report

    closeout = _json_object(value, label="plan.runfix3_live_thread_proof.participant_closeout")
    rows_value = closeout.get("rows")
    evidence_ref = _optional_string_value(closeout.get("evidence_ref"))
    closed_out: list[str] = []
    if isinstance(rows_value, list):
        for index, item in enumerate(rows_value):
            if not isinstance(item, Mapping):
                continue
            row = _json_object(
                item, label=f"plan.runfix3_live_thread_proof.participant_closeout.rows[{index}]"
            )
            participant = _optional_string_value(row.get("participant"))
            if participant is None:
                continue
            closeout_turn = _json_value_or_none(row.get("closeout_turn"))
            row_evidence_ref = _optional_string_value(row.get("evidence_ref"))
            speech_event_id = _optional_string_value(row.get("speech_event_id"))
            delivery_target_match = row.get("delivery_target_match") is True
            if (
                closeout_turn is not None
                and row_evidence_ref is not None
                and speech_event_id is not None
                and delivery_target_match
            ):
                closed_out.append(participant)
    closed_out = sorted(dict.fromkeys(closed_out))
    missing_participants = [profile for profile in expected_profiles if profile not in closed_out]
    report.update(
        {
            "closed_out_participants": cast(list[JsonValue], closed_out),
            "missing_participants": cast(list[JsonValue], missing_participants),
            "evidence_ref": evidence_ref,
        }
    )
    closeout_pass = closeout.get("participant_closeout_pass") is True
    if closeout_pass and evidence_ref is not None and not missing_participants:
        report["status"] = "proven"
        return report
    blockers.append(
        _blocker(
            code="runfix3_participant_closeout_unproven",
            owner="operator/control",
            message=(
                "participant_closeout must prove completed closeouts for every expected "
                "participant with evidence_ref."
            ),
        )
    )
    report["status"] = "blocked"
    return report


def _runfix3_moderator_synthesis_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    report = _empty_runfix3_moderator_synthesis_report()
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="runfix3_moderator_synthesis_coverage_missing",
                owner="operator/control",
                message="runfix3_live_thread_proof.moderator_synthesis evidence is required.",
            )
        )
        report["status"] = "blocked"
        return report

    synthesis = _json_object(value, label="plan.runfix3_live_thread_proof.moderator_synthesis")
    evidence_ref = _optional_string_value(synthesis.get("evidence_ref"))
    synthesis_posted = (
        synthesis.get("moderator_synthesis_pass") is True
        and _non_empty_string(synthesis.get("speech_event_id"))
        and synthesis.get("delivery_target_match") is True
        and evidence_ref is not None
    )
    report.update({"synthesis_posted": synthesis_posted, "evidence_ref": evidence_ref})
    if synthesis_posted:
        report["status"] = "proven"
        return report
    blockers.append(
        _blocker(
            code="runfix3_moderator_synthesis_coverage_unproven",
            owner="operator/control",
            message=(
                "moderator_synthesis must prove posted synthesis, delivery-target match, and "
                "evidence_ref."
            ),
        )
    )
    report["status"] = "blocked"
    return report


def _runfix3_delivery_target_report(
    value: object,
    *,
    expected_row_count: int | None,
    approved_delivery_target: str | None,
    blockers: list[JsonObject],
) -> JsonObject:
    proof = _empty_runfix3_delivery_target_proof()
    report: JsonObject = {"rows": [], "delivery_target_proof": proof}
    if not isinstance(value, Mapping):
        _append_runfix3_blocker(
            blockers,
            proof,
            code="runfix3_delivery_target_missing",
            message="runfix3_live_thread_proof.delivery_targets evidence is required.",
        )
        return report

    delivery = _json_object(value, label="plan.runfix3_live_thread_proof.delivery_targets")
    rows_value = delivery.get("rows")
    rows: list[JsonObject] = []
    if not isinstance(rows_value, list) or not rows_value:
        _append_runfix3_blocker(
            blockers,
            proof,
            code="runfix3_delivery_target_rows_missing",
            message="delivery_targets.rows must list per-turn delivery-target evidence.",
        )
        report["rows"] = cast(list[JsonValue], rows)
        return report

    for index, item in enumerate(rows_value):
        rows.append(
            _runfix3_delivery_target_row(
                item,
                index=index,
                approved_delivery_target=approved_delivery_target,
                blockers=blockers,
            )
        )
    evidence_ref = _optional_string_value(delivery.get("evidence_ref"))
    aggregate_match = (
        delivery.get("delivery_target_pass") is True
        and bool(rows)
        and all(row["status"] == "proven" for row in rows)
        and evidence_ref is not None
        and (expected_row_count is None or len(rows) == expected_row_count)
    )
    report.update(
        {
            "rows": cast(list[JsonValue], rows),
            "delivery_target_proof": {
                "status": "proven" if aggregate_match else "blocked",
                "aggregate_match": aggregate_match,
                "evidence_ref": evidence_ref,
            },
        }
    )
    if aggregate_match:
        return report
    blockers.append(
        _blocker(
            code="runfix3_delivery_target_mismatch",
            owner="operator/control",
            message=(
                "delivery_targets must prove matching per-turn targets bound to the requested "
                "origin or approved fallback target, aggregate delivery_target_pass=true, and full "
                "visible-turn coverage with evidence_ref."
            ),
        )
    )
    return report


def _runfix3_delivery_target_row(
    value: object,
    *,
    index: int,
    approved_delivery_target: str | None,
    blockers: list[JsonObject],
) -> JsonObject:
    row: JsonObject = {
        "status": "blocked",
        "turn": None,
        "speaker_selected_event_id": None,
        "speech_event_id": None,
        "expected_delivery_target": None,
        "posted_delivery_target": None,
        "match": False,
        "evidence_ref": None,
    }
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="runfix3_delivery_target_row_invalid",
                owner="operator/control",
                message=f"delivery_targets.rows[{index}] must be an object.",
            )
        )
        return row

    item = _json_object(
        value, label=f"plan.runfix3_live_thread_proof.delivery_targets.rows[{index}]"
    )
    expected_target = _optional_string_value(item.get("expected_delivery_target"))
    posted_target = _optional_string_value(item.get("posted_delivery_target"))
    evidence_ref = _optional_string_value(item.get("evidence_ref"))
    explicit_match = item.get("delivery_target_match")
    match = (
        approved_delivery_target is not None
        and expected_target is not None
        and posted_target is not None
        and expected_target == approved_delivery_target
        and posted_target == approved_delivery_target
        and explicit_match is not False
    )
    row.update(
        {
            "turn": _json_value_or_none(item.get("turn")),
            "speaker_selected_event_id": _optional_string_value(
                item.get("speaker_selected_event_id")
            ),
            "speech_event_id": _optional_string_value(item.get("speech_event_id")),
            "expected_delivery_target": expected_target,
            "posted_delivery_target": posted_target,
            "match": match,
            "evidence_ref": evidence_ref,
        }
    )
    if (
        row["turn"] is not None
        and row["speaker_selected_event_id"] is not None
        and row["speech_event_id"] is not None
        and expected_target is not None
        and posted_target is not None
        and evidence_ref is not None
        and match
    ):
        row["status"] = "proven"
        return row
    blockers.append(
        _blocker(
            code="runfix3_delivery_target_row_unproven",
            owner="operator/control",
            message=(
                f"delivery_targets.rows[{index}] must include turn, speaker_selected_event_id, "
                "speech_event_id, and expected/posted delivery targets bound to the requested "
                "origin or approved fallback target with evidence_ref."
            ),
        )
    )
    return row


def _runfix3_prompt_envelope_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    report = _empty_runfix3_prompt_envelope_report()
    if not isinstance(value, Mapping):
        _append_runfix3_blocker(
            blockers,
            report,
            code="runfix3_prompt_envelope_missing",
            message="runfix3_live_thread_proof.prompt_envelope evidence is required.",
        )
        return report

    prompt_envelope = _json_object(value, label="plan.runfix3_live_thread_proof.prompt_envelope")
    evidence_ref = _optional_string_value(prompt_envelope.get("evidence_ref"))
    content_audit_separated = prompt_envelope.get("content_audit_separated") is True
    control_metadata_leaked = prompt_envelope.get("control_metadata_leaked") is True
    report.update(
        {
            "content_audit_separated": content_audit_separated,
            "control_metadata_leaked": control_metadata_leaked,
            "evidence_ref": evidence_ref,
        }
    )
    if (
        prompt_envelope.get("prompt_envelope_pass") is True
        and content_audit_separated
        and not control_metadata_leaked
        and evidence_ref is not None
    ):
        report["status"] = "proven"
        return report
    _append_runfix3_blocker(
        blockers,
        report,
        code="runfix3_prompt_envelope_unproven",
        message=(
            "prompt_envelope must prove content_audit_separated=true, "
            "control_metadata_leaked=false, and evidence_ref."
        ),
    )
    return report


def _runfix3_dialogue_mode_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    report = _empty_runfix3_dialogue_mode_report()
    if not isinstance(value, Mapping):
        _append_runfix3_blocker(
            blockers,
            report,
            code="runfix3_dialogue_mode_missing",
            message="runfix3_live_thread_proof.dialogue_mode evidence is required.",
        )
        return report

    dialogue_mode = _json_object(value, label="plan.runfix3_live_thread_proof.dialogue_mode")
    evidence_ref = _optional_string_value(dialogue_mode.get("evidence_ref"))
    participant_to_participant = dialogue_mode.get("participant_to_participant") is True
    moderator_substitute_turns = dialogue_mode.get("moderator_substitute_turns") is True
    report.update(
        {
            "participant_to_participant": participant_to_participant,
            "moderator_substitute_turns": moderator_substitute_turns,
            "evidence_ref": evidence_ref,
        }
    )
    if (
        dialogue_mode.get("dialogue_mode_pass") is True
        and participant_to_participant
        and not moderator_substitute_turns
        and evidence_ref is not None
    ):
        report["status"] = "proven"
        return report
    _append_runfix3_blocker(
        blockers,
        report,
        code="runfix3_dialogue_mode_unproven",
        message=(
            "dialogue_mode must prove participant_to_participant=true, "
            "moderator_substitute_turns=false, and evidence_ref."
        ),
    )
    return report


def _runfix3_drift_status_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    report = _empty_runfix3_drift_status_report()
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="runfix3_drift_missing",
                owner="operator/control",
                message="runfix3_live_thread_proof.drift evidence is required.",
            )
        )
        report["status"] = "blocked"
        return report

    drift = _json_object(value, label="plan.runfix3_live_thread_proof.drift")
    status_value = (
        _optional_string_value(drift.get("status") or drift.get("drift_status")) or "unknown"
    )
    evidence_ref = _optional_string_value(drift.get("evidence_ref"))
    drift_detected = drift.get("drift_detected") is True or status_value != "clean"
    repaired_forward = drift.get("repaired_forward") is True or status_value == "repair_forward"
    unresolved_closeout = drift.get("unresolved_closeout") is True or status_value == "unresolved"
    report.update(
        {
            "drift_detected": drift_detected,
            "repaired_forward": repaired_forward,
            "unresolved_closeout": unresolved_closeout,
            "evidence_ref": evidence_ref,
        }
    )
    if evidence_ref is not None and (
        status_value == "clean"
        and not unresolved_closeout
        or status_value == "repair_forward"
        and repaired_forward
        and not unresolved_closeout
    ):
        report["status"] = "proven"
        return report
    blockers.append(
        _blocker(
            code="runfix3_drift_unproven",
            owner="operator/control",
            message="drift must resolve cleanly or repair_forward with evidence_ref.",
        )
    )
    report["status"] = "blocked"
    return report


def _runfix3_fail_closed_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    report = _empty_runfix3_fail_closed_report()
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="runfix3_fail_closed_missing",
                owner="operator/control",
                message="runfix3_live_thread_proof.final_fail_closed evidence is required.",
            )
        )
        report["status"] = "blocked"
        return report

    final_fail_closed = _json_object(
        value, label="plan.runfix3_live_thread_proof.final_fail_closed"
    )
    final_status = _optional_string_value(final_fail_closed.get("final_status")) or "unproven"
    fail_closed = final_fail_closed.get("fail_closed") is True
    evidence_ref = _optional_string_value(final_fail_closed.get("evidence_ref"))
    report.update(
        {
            "final_status": final_status,
            "fail_closed": fail_closed,
            "evidence_ref": evidence_ref,
        }
    )
    if (
        final_fail_closed.get("final_fail_closed_pass") is True
        and fail_closed
        and final_status in {"clean", "repair_forward"}
        and evidence_ref is not None
    ):
        report["status"] = "proven"
        return report
    blockers.append(
        _blocker(
            code="runfix3_fail_closed_unproven",
            owner="operator/control",
            message=(
                "final_fail_closed must prove fail_closed=true with final_status clean or "
                "repair_forward and evidence_ref."
            ),
        )
    )
    report["status"] = "blocked"
    return report


def _append_runfix3_blocker(
    blockers: list[JsonObject],
    report: JsonObject,
    *,
    code: str,
    message: str,
) -> None:
    blockers.append(_blocker(code=code, owner="operator/control", message=message))
    report["status"] = "blocked"
    if "pass" in report:
        report["pass"] = False


def _integrated_discussion_proof_report(
    value: object,
    *,
    task_id: str,
    blockers: list[JsonObject],
) -> JsonObject:
    report: JsonObject = {
        "runfix_task_id": RUNFIX2_005_TASK_ID,
        "status": "not_required",
        "lifecycle_pass": _empty_integrated_check("lifecycle_pass"),
        "selected_runner_pass": _empty_integrated_check("selected_runner_pass"),
        "participant_runtime_ready_at_turns": _empty_integrated_check(
            "participant_runtime_ready_at_turns"
        )
        | {"turns": []},
        "visible_turn_count": {
            "status": "unproven",
            "max_discussion_turns": None,
            "participant_count": None,
            "expected_visible_turns": None,
            "visible_turns_posted": None,
            "evidence_ref": None,
        },
        "visible_surface_pass": _empty_integrated_check("visible_surface_pass"),
        "clean_transcript_pass": _empty_integrated_check("clean_transcript_pass"),
        "visible_closeout_pass": _empty_integrated_check("visible_closeout_pass"),
        "fallback_profile_pass": {
            "status": "not_supplied",
            "label": "fallback_profile_pass",
            "diagnostic_only": True,
            "full_atn_success": False,
            "evidence_ref": None,
            "missing_evidence": [],
        },
        "discussion_quality_pass": _empty_integrated_check("discussion_quality_pass"),
        "final_labels": {},
    }
    if task_id != RUNFIX2_005_TASK_ID:
        return report

    report["status"] = "blocked"
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="integrated_discussion_proof_missing",
                owner="operator",
                message=(
                    "plugin/RUNFIX2-005 requires explicit integrated_discussion_proof evidence."
                ),
            )
        )
        return report

    proof = _json_object(value, label="plan.integrated_discussion_proof")
    lifecycle = _integrated_lifecycle_report(proof.get("lifecycle"), blockers=blockers)
    selected_runner = _integrated_selected_runner_report(
        proof.get("selected_runner"), blockers=blockers
    )
    canonical = _integrated_canonical_speech_report(
        proof.get("canonical_speech"),
        selected_runner=selected_runner,
        blockers=blockers,
    )
    runtime = _integrated_turn_runtime_report(
        proof.get("grant_turn_runtime_readiness"), blockers=blockers
    )
    visible_turn_count = _integrated_visible_turn_count_report(
        proof.get("visible_turns"), blockers=blockers
    )
    visible_surface = _integrated_visible_surface_report(
        proof.get("visible_surface"), blockers=blockers
    )
    clean_transcript = _integrated_clean_transcript_report(
        proof.get("clean_transcript"), blockers=blockers
    )
    visible_closeout = _integrated_visible_closeout_report(
        proof.get("visible_closeout"), blockers=blockers
    )
    fallback = _integrated_fallback_report(proof.get("fallback_profile"))
    discussion_quality = _integrated_discussion_quality_report(
        proof.get("discussion_quality"), blockers=blockers
    )
    final_labels = _integrated_final_labels_report(
        proof.get("final_labels"),
        lifecycle=lifecycle,
        selected_runner=selected_runner,
        canonical=canonical,
        runtime=runtime,
        visible_surface=visible_surface,
        clean_transcript=clean_transcript,
        visible_closeout=visible_closeout,
        fallback=fallback,
        discussion_quality=discussion_quality,
        blockers=blockers,
    )

    selected_runner_pass = dict(selected_runner)
    selected_runner_pass["canonical_speech"] = canonical
    if canonical["status"] != "proven":
        selected_runner_pass["status"] = "blocked"
        selected_runner_pass["pass"] = False

    report.update(
        {
            "lifecycle_pass": lifecycle,
            "selected_runner_pass": selected_runner_pass,
            "participant_runtime_ready_at_turns": runtime,
            "visible_turn_count": visible_turn_count,
            "visible_surface_pass": visible_surface,
            "clean_transcript_pass": clean_transcript,
            "visible_closeout_pass": visible_closeout,
            "fallback_profile_pass": fallback,
            "discussion_quality_pass": discussion_quality,
            "final_labels": final_labels,
        }
    )
    required_reports = (
        lifecycle,
        selected_runner_pass,
        runtime,
        visible_turn_count,
        visible_surface,
        clean_transcript,
        visible_closeout,
        final_labels,
    )
    if all(item["status"] == "proven" for item in required_reports):
        report["status"] = "proven"
    return report


def _empty_integrated_check(label: str) -> JsonObject:
    return {"status": "unproven", "label": label, "pass": False, "evidence_ref": None}


def _integrated_lifecycle_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    report = _empty_integrated_check("lifecycle_pass")
    if not isinstance(value, Mapping):
        _append_integrated_blocker(
            blockers,
            report,
            code="integrated_lifecycle_missing",
            message="integrated_discussion_proof.lifecycle evidence is required.",
        )
        return report
    lifecycle = _json_object(value, label="plan.integrated_discussion_proof.lifecycle")
    evidence_ref = _optional_string_value(lifecycle.get("evidence_ref"))
    if evidence_ref is not None:
        report["evidence_ref"] = evidence_ref
    if lifecycle.get("lifecycle_pass") is True and evidence_ref is not None:
        report["status"] = "proven"
        report["pass"] = True
        return report
    _append_integrated_blocker(
        blockers,
        report,
        code="integrated_lifecycle_unproven",
        message="lifecycle.lifecycle_pass=true and lifecycle.evidence_ref are required.",
    )
    return report


def _integrated_selected_runner_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    report = _empty_integrated_check("selected_runner_pass") | {
        "selected_member": None,
        "speaker_selected_event_id": None,
        "runner_invocation_started_ref": None,
        "runner_invocation_succeeded_ref": None,
        "durable_runner_failure_ref": None,
    }
    if not isinstance(value, Mapping):
        _append_integrated_blocker(
            blockers,
            report,
            code="integrated_selected_runner_missing",
            message="integrated_discussion_proof.selected_runner evidence is required.",
        )
        return report
    runner = _json_object(value, label="plan.integrated_discussion_proof.selected_runner")
    for key in (
        "selected_member",
        "speaker_selected_event_id",
        "runner_invocation_started_ref",
        "runner_invocation_succeeded_ref",
        "durable_runner_failure_ref",
        "evidence_ref",
    ):
        item = _optional_string_value(runner.get(key))
        if item is not None:
            report[key] = item
    substitution = _integrated_substitution(runner)
    if substitution is not None:
        _append_integrated_blocker(
            blockers,
            report,
            code="integrated_selected_runner_substituted",
            message=(
                "selected_runner_pass cannot be satisfied by fallback/manual, transcript, "
                "export, gateway-only, or delivery-only evidence."
            ),
        )
    if _optional_string_value(runner.get("durable_runner_failure_ref")) is not None:
        _append_integrated_blocker(
            blockers,
            report,
            code="integrated_selected_runner_durable_failure",
            message="Durable selected-runner failure blocks selected_runner_pass.",
        )
        return report
    if substitution is not None:
        return report
    if (
        _optional_string_value(runner.get("selected_member")) is not None
        and _optional_string_value(runner.get("speaker_selected_event_id")) is not None
        and _optional_string_value(runner.get("runner_invocation_succeeded_ref")) is not None
        and runner.get("runner_invocation_succeeded") is True
    ):
        report["status"] = "proven"
        report["pass"] = True
        return report
    if _optional_string_value(runner.get("runner_invocation_started_ref")) is not None:
        _append_integrated_blocker(
            blockers,
            report,
            code="integrated_selected_runner_started_only",
            message="Selected-runner started evidence is not selected-runner success.",
        )
        return report
    _append_integrated_blocker(
        blockers,
        report,
        code="integrated_selected_runner_unproven",
        message=(
            "selected_member, speaker_selected_event_id, and "
            "runner_invocation_succeeded_ref are required."
        ),
    )
    return report


def _integrated_canonical_speech_report(
    value: object,
    *,
    selected_runner: JsonObject,
    blockers: list[JsonObject],
) -> JsonObject:
    report = _empty_integrated_check("canonical_speech_linkage") | {
        "speaker_selected_event_id": None,
        "speech_event_id": None,
        "speaker": None,
    }
    if not isinstance(value, Mapping):
        _append_integrated_blocker(
            blockers,
            report,
            code="integrated_canonical_speech_missing",
            message="integrated_discussion_proof.canonical_speech evidence is required.",
        )
        return report
    link = _json_object(value, label="plan.integrated_discussion_proof.canonical_speech")
    for key in ("speaker_selected_event_id", "speech_event_id", "speaker", "evidence_ref"):
        item = _optional_string_value(link.get(key))
        if item is not None:
            report[key] = item
    if _integrated_substitution(link) is not None:
        _append_integrated_blocker(
            blockers,
            report,
            code="integrated_canonical_speech_substituted",
            message="Canonical speech linkage cannot be satisfied by fallback/manual evidence.",
        )
        return report
    selected_event = selected_runner.get("speaker_selected_event_id")
    selected_member = selected_runner.get("selected_member")
    linked = (
        _optional_string_value(link.get("speaker_selected_event_id")) is not None
        and _optional_string_value(link.get("speech_event_id")) is not None
        and _optional_string_value(link.get("speaker")) is not None
        and link.get("speaker_selected_event_id") == selected_event
        and link.get("speaker") == selected_member
    )
    if linked:
        report["status"] = "proven"
        report["pass"] = True
        return report
    _append_integrated_blocker(
        blockers,
        report,
        code="integrated_canonical_speech_unlinked",
        message=(
            "canonical_speech must link the selected speaker_selected_event_id to "
            "a speech_event_id for the selected member."
        ),
    )
    return report


def _integrated_turn_runtime_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    report = _empty_integrated_check("participant_runtime_ready_at_turns") | {"turns": []}
    if not isinstance(value, list) or not value:
        _append_integrated_blocker(
            blockers,
            report,
            code="integrated_runtime_turns_missing",
            message="grant_turn_runtime_readiness must list grant/turn-time readiness rows.",
        )
        return report
    rows: list[JsonObject] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            row: JsonObject = {"status": "blocked", "turn": None, "diagnostic": "row_invalid"}
            rows.append(row)
            blockers.append(
                _blocker(
                    code="integrated_runtime_turn_invalid",
                    owner="control/operator",
                    message=f"grant_turn_runtime_readiness[{index}] must be an object.",
                )
            )
            continue
        readiness = _json_object(
            item, label=f"plan.integrated_discussion_proof.grant_turn_runtime_readiness[{index}]"
        )
        row = _integrated_runtime_turn_row(readiness, index=index, blockers=blockers)
        rows.append(row)
    report["turns"] = cast(list[JsonValue], rows)
    if all(row["status"] == "proven" for row in rows):
        report["status"] = "proven"
        report["pass"] = True
    return report


def _integrated_runtime_turn_row(
    readiness: JsonObject,
    *,
    index: int,
    blockers: list[JsonObject],
) -> JsonObject:
    turn = readiness.get("turn")
    event_ref = _optional_string_value(
        readiness.get("speaker_selected_event_id") or readiness.get("grant_event_id")
    )
    evidence_ref = _optional_string_value(readiness.get("evidence_ref"))
    row: JsonObject = {
        "status": "proven",
        "turn": _json_value_or_none(turn),
        "speaker_selected_event_id": event_ref,
        "evidence_ref": evidence_ref,
        "diagnostics": [],
    }
    missing: list[str] = []
    if evidence_ref is None:
        missing.append("evidence_ref")
    if event_ref is None:
        missing.append("speaker_selected_event_id")
    for key in (
        "subscriber_present",
        "cursor_ack_fresh",
        "heartbeat_fresh",
        "attendance_terminal_success",
        "preparation_terminal_success",
        "selected_runner_prerequisites_met",
    ):
        if readiness.get(key) is not True:
            missing.append(key)
    if readiness.get("current_only") is True:
        row["status"] = "blocked"
        cast(list[JsonValue], row["diagnostics"]).append("current_only_status")
        blockers.append(
            _blocker(
                code="integrated_runtime_current_only",
                owner="control/operator",
                message="Current-only runtime status is not grant/turn-time readiness proof.",
            )
        )
    if readiness.get("stale") is True or readiness.get("fresh") is False:
        row["status"] = "blocked"
        cast(list[JsonValue], row["diagnostics"]).append("stale")
        blockers.append(
            _blocker(
                code="integrated_runtime_turn_stale",
                owner="control/operator",
                message=f"grant_turn_runtime_readiness[{index}] evidence is stale.",
            )
        )
    if readiness.get("ambiguous") is True:
        row["status"] = "blocked"
        cast(list[JsonValue], row["diagnostics"]).append("ambiguous")
        blockers.append(
            _blocker(
                code="integrated_runtime_turn_ambiguous",
                owner="control/operator",
                message=f"grant_turn_runtime_readiness[{index}] evidence is ambiguous.",
            )
        )
    substitution = _integrated_substitution(readiness)
    if substitution is not None:
        row["status"] = "blocked"
        cast(list[JsonValue], row["diagnostics"]).append(substitution["reason"])
        blockers.append(
            _blocker(
                code="integrated_runtime_turn_substituted",
                owner="control/operator",
                message="Runtime readiness at turns cannot use substituted evidence.",
            )
        )
    if missing:
        row["status"] = "blocked"
        row["missing"] = cast(list[JsonValue], missing)
        blockers.append(
            _blocker(
                code="integrated_runtime_turn_unproven",
                owner="control/operator",
                message=(
                    f"grant_turn_runtime_readiness[{index}] is missing: " + ", ".join(missing) + "."
                ),
            )
        )
    return row


def _integrated_visible_turn_count_report(
    value: object, *, blockers: list[JsonObject]
) -> JsonObject:
    report: JsonObject = {
        "status": "unproven",
        "max_discussion_turns": None,
        "participant_count": None,
        "expected_visible_turns": None,
        "visible_turns_posted": None,
        "evidence_ref": None,
    }
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="integrated_visible_turn_count_missing",
                owner="operator",
                message="integrated_discussion_proof.visible_turns evidence is required.",
            )
        )
        return report
    turns = _json_object(value, label="plan.integrated_discussion_proof.visible_turns")
    max_discussion_turns = _non_negative_int_or_none(turns.get("max_discussion_turns"))
    participant_count = _non_negative_int_or_none(turns.get("participant_count"))
    posted = _non_negative_int_or_none(turns.get("visible_turns_posted") or turns.get("posted"))
    evidence_ref = _optional_string_value(turns.get("evidence_ref"))
    expected = (
        max_discussion_turns + participant_count + 2
        if max_discussion_turns is not None and participant_count is not None
        else None
    )
    supplied_expected = _non_negative_int_or_none(turns.get("expected_visible_turns"))
    if expected is not None and supplied_expected is not None and supplied_expected != expected:
        blockers.append(
            _blocker(
                code="integrated_visible_turn_expected_formula_mismatch",
                owner="operator/control",
                message=(
                    "expected_visible_turns must equal max_discussion_turns + "
                    "participant_count + 2."
                ),
            )
        )
    report.update(
        {
            "max_discussion_turns": max_discussion_turns,
            "participant_count": participant_count,
            "expected_visible_turns": expected,
            "visible_turns_posted": posted,
            "evidence_ref": evidence_ref,
        }
    )
    if expected is not None and posted == expected and evidence_ref is not None:
        report["status"] = "proven"
        return report
    blockers.append(
        _blocker(
            code="integrated_visible_turn_count_mismatch",
            owner="operator/control",
            message=(
                "Visible turns posted must equal max_discussion_turns + "
                "participant_count + 2 with evidence_ref."
            ),
        )
    )
    return report


def _integrated_visible_surface_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    return _integrated_boolean_evidence_report(
        value,
        label="visible_surface_pass",
        field="visible_surface_pass",
        source_label="visible_surface",
        missing_code="integrated_visible_surface_missing",
        unproven_code="integrated_visible_surface_unproven",
        message="visible_surface.visible_surface_pass=true and evidence_ref are required.",
        blockers=blockers,
    )


def _integrated_clean_transcript_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    report = _integrated_boolean_evidence_report(
        value,
        label="clean_transcript_pass",
        field="clean_transcript_pass",
        source_label="clean_transcript",
        missing_code="integrated_clean_transcript_missing",
        unproven_code="integrated_clean_transcript_unproven",
        message="clean_transcript.clean_transcript_pass=true and evidence_ref are required.",
        blockers=blockers,
    )
    if isinstance(value, Mapping):
        clean = _json_object(value, label="plan.integrated_discussion_proof.clean_transcript")
        forbidden = (
            clean.get("audit_ids_in_visible_text") is True
            or clean.get("raw_ids_in_visible_text") is True
        )
        if forbidden:
            _append_integrated_blocker(
                blockers,
                report,
                code="integrated_clean_transcript_audit_ids_visible",
                message="Clean transcript proof must keep audit IDs out of visible rows.",
            )
    return report


def _integrated_visible_closeout_report(value: object, *, blockers: list[JsonObject]) -> JsonObject:
    return _integrated_boolean_evidence_report(
        value,
        label="visible_closeout_pass",
        field="visible_closeout_pass",
        source_label="visible_closeout",
        missing_code="integrated_visible_closeout_missing",
        unproven_code="integrated_visible_closeout_unproven",
        message="visible_closeout.visible_closeout_pass=true and evidence_ref are required.",
        blockers=blockers,
    )


def _integrated_discussion_quality_report(
    value: object, *, blockers: list[JsonObject]
) -> JsonObject:
    if value is None:
        return {
            "status": "not_supplied",
            "label": "discussion_quality_pass",
            "pass": False,
            "evidence_ref": None,
        }
    return _integrated_boolean_evidence_report(
        value,
        label="discussion_quality_pass",
        field="discussion_quality_pass",
        source_label="discussion_quality",
        missing_code="integrated_discussion_quality_invalid",
        unproven_code="integrated_discussion_quality_unproven",
        message=(
            "discussion_quality.discussion_quality_pass=true and evidence_ref are required "
            "when supplied."
        ),
        blockers=blockers,
    )


def _integrated_boolean_evidence_report(
    value: object,
    *,
    label: str,
    field: str,
    source_label: str,
    missing_code: str,
    unproven_code: str,
    message: str,
    blockers: list[JsonObject],
) -> JsonObject:
    report = _empty_integrated_check(label)
    if not isinstance(value, Mapping):
        _append_integrated_blocker(
            blockers,
            report,
            code=missing_code,
            message=f"integrated_discussion_proof.{source_label} evidence is required.",
        )
        return report
    evidence = _json_object(value, label=f"plan.integrated_discussion_proof.{source_label}")
    evidence_ref = _optional_string_value(evidence.get("evidence_ref"))
    if evidence_ref is not None:
        report["evidence_ref"] = evidence_ref
    if _integrated_substitution(evidence) is not None:
        _append_integrated_blocker(
            blockers,
            report,
            code=f"{unproven_code}_substituted",
            message=f"integrated_discussion_proof.{source_label} uses substituted evidence.",
        )
        return report
    if evidence.get(field) is True and evidence_ref is not None:
        report["status"] = "proven"
        report["pass"] = True
        return report
    _append_integrated_blocker(blockers, report, code=unproven_code, message=message)
    return report


def _integrated_fallback_report(value: object) -> JsonObject:
    report: JsonObject = {
        "status": "not_supplied",
        "label": "fallback_profile_pass",
        "diagnostic_only": True,
        "full_atn_success": False,
        "evidence_ref": None,
        "missing_evidence": [],
    }
    if not isinstance(value, Mapping):
        return report
    fallback = _json_object(value, label="plan.integrated_discussion_proof.fallback_profile")
    evidence_ref = _optional_string_value(fallback.get("evidence_ref"))
    missing = _optional_string_list(fallback.get("missing_evidence"))
    if evidence_ref is not None:
        report["evidence_ref"] = evidence_ref
    report["missing_evidence"] = cast(list[JsonValue], missing)
    report["status"] = "diagnostic_only"
    return report


def _integrated_final_labels_report(
    value: object,
    *,
    lifecycle: JsonObject,
    selected_runner: JsonObject,
    canonical: JsonObject,
    runtime: JsonObject,
    visible_surface: JsonObject,
    clean_transcript: JsonObject,
    visible_closeout: JsonObject,
    fallback: JsonObject,
    discussion_quality: JsonObject,
    blockers: list[JsonObject],
) -> JsonObject:
    required = {
        "lifecycle_pass": lifecycle["status"] == "proven",
        "selected_runner_pass": (
            selected_runner["status"] == "proven" and canonical["status"] == "proven"
        ),
        "participant_runtime_ready_at_turns": runtime["status"] == "proven",
        "visible_surface_pass": visible_surface["status"] == "proven",
        "clean_transcript_pass": clean_transcript["status"] == "proven",
        "visible_closeout_pass": visible_closeout["status"] == "proven",
        "fallback_profile_pass": fallback["status"] == "diagnostic_only",
    }
    if discussion_quality["status"] != "not_supplied":
        required["discussion_quality_pass"] = discussion_quality["status"] == "proven"
    report: JsonObject = {"status": "proven", "labels": {}, "collapsed": False}
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="integrated_final_labels_missing",
                owner="operator",
                message="integrated_discussion_proof.final_labels must keep labels separate.",
            )
        )
        report["status"] = "blocked"
        return report
    labels = _json_object(value, label="plan.integrated_discussion_proof.final_labels")
    if labels.get("collapsed") is True or labels.get("all_pass") is True:
        blockers.append(
            _blocker(
                code="integrated_final_labels_collapsed",
                owner="operator",
                message="Final labels must not collapse evidence axes into one pass label.",
            )
        )
        report["status"] = "blocked"
        report["collapsed"] = True
    output_labels: JsonObject = {}
    for label, expected in required.items():
        item = labels.get(label)
        if not isinstance(item, Mapping):
            blockers.append(
                _blocker(
                    code=f"integrated_final_label_{label}_missing",
                    owner="operator",
                    message=f"final_labels.{label} is required and must be separate.",
                )
            )
            report["status"] = "blocked"
            continue
        label_value = _json_object(
            item, label=f"plan.integrated_discussion_proof.final_labels.{label}"
        )
        passed = label_value.get("pass") is True
        evidence_ref = _optional_string_value(label_value.get("evidence_ref"))
        output_labels[label] = {
            "pass": passed,
            "evidence_ref": evidence_ref,
        }
        if passed != expected:
            blockers.append(
                _blocker(
                    code=f"integrated_final_label_{label}_mismatch",
                    owner="operator",
                    message=f"final_labels.{label} must match its evidence-derived result.",
                )
            )
            report["status"] = "blocked"
        if passed and evidence_ref is None and label != "fallback_profile_pass":
            blockers.append(
                _blocker(
                    code=f"integrated_final_label_{label}_evidence_missing",
                    owner="operator",
                    message=f"final_labels.{label}.evidence_ref is required when pass=true.",
                )
            )
            report["status"] = "blocked"
    report["labels"] = output_labels
    return report


def _append_integrated_blocker(
    blockers: list[JsonObject],
    report: JsonObject,
    *,
    code: str,
    message: str,
) -> None:
    blockers.append(_blocker(code=code, owner="operator/control", message=message))
    report["status"] = "blocked"
    report["pass"] = False


def _integrated_substitution(evidence: JsonObject) -> JsonObject | None:
    flags: tuple[tuple[str, str], ...] = (
        ("fallback_manual", "fallback/manual"),
        ("manual_profile_only", "manual/fallback-profile-only"),
        ("fallback_profile_only", "manual/fallback-profile-only"),
        ("transcript_export_only", "transcript/export-only"),
        ("gateway_only", "gateway-only"),
        ("delivery_only", "delivery-only"),
        ("current_only", "current-only"),
    )
    for key, kind in flags:
        if evidence.get(key) is True:
            return {"kind": kind, "reason": key}
    evidence_kind = _optional_string_value(evidence.get("evidence_kind"))
    normalized_kind = _normalized_integrated_evidence_kind(evidence_kind)
    if normalized_kind is not None:
        return {"kind": normalized_kind, "reason": cast(str, evidence_kind)}
    return None


def _normalized_integrated_evidence_kind(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower().replace("_", "-")
    substitutions = {
        "fallback-manual": "fallback/manual",
        "fallback/manual": "fallback/manual",
        "manual-profile-only": "manual/fallback-profile-only",
        "manual/fallback-profile-only": "manual/fallback-profile-only",
        "fallback-profile-only": "manual/fallback-profile-only",
        "fallback/profile-only": "manual/fallback-profile-only",
        "transcript-export-only": "transcript/export-only",
        "transcript/export-only": "transcript/export-only",
        "gateway-only": "gateway-only",
        "delivery-only": "delivery-only",
        "current-only": "current-only",
    }
    return substitutions.get(normalized)


def _json_value_or_none(value: object) -> JsonValue | None:
    if value is None:
        return None
    try:
        return cast(JsonValue, value)
    except TypeError:
        return None


def _non_negative_int_or_none(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _non_negative_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return 0
    return value


def _optional_string_value(value: object) -> str | None:
    return cast(str, value) if _non_empty_string(value) else None


def _fallback_audit() -> list[JsonObject]:
    forbidden = (
        ("hidden_plugin_to_cli_subprocess_fallback", "Plugin must not shell out to CLI."),
        ("current_hermes_or_discord_inference", "Planner uses explicit caller evidence only."),
        (
            "manual_profile_replies_as_full_atn_success",
            "Manual replies are fallback evidence only.",
        ),
        ("daemon_startup_or_discovery", "Daemon lifecycle/discovery remains outside the plugin."),
        (
            "profile_gateway_provider_auth_token_model_mutation",
            (
                "Activation planning cannot mutate profile, gateway, provider, auth, "
                "token, or model state."
            ),
        ),
        ("codex_exec", "Stage 1 direct Codex SDK/app-server work must not use codex exec."),
        ("generic_openai_sdk", "Generic OpenAI SDK is not a plugin participant-tool fallback."),
        ("raw_app_server_transport", "Raw app-server transport is not exposed by this planner."),
        ("kab_native_codex", "KAB native_codex is outside the plugin participant-agent surface."),
    )
    return [
        {
            "fallback": name,
            "allowed": False,
            "reason": reason,
        }
        for name, reason in forbidden
    ]


def _participant_argue_response_template() -> JsonObject:
    return {
        "required_fields": [
            "speech",
            "claims[]",
            "stance_links[]",
            "contribution_type",
            "new_axis_reason",
        ],
        "optional_fields": ["evidence[]"],
        "speech_rule": (
            "Visible speech only; runtime warnings, wrapper logs, transport metadata, "
            "and role-substitution text are not participant speech."
        ),
        "role_substitution_prohibited": True,
        "relation_rule": (
            "Use stance_links[] for prior-claim engagement, or contribution_type=new_axis "
            "with a non-empty new_axis_reason when opening a necessary new axis."
        ),
        "prior_claim_graph_targets": {
            "required_authority_fields": ["event_id"],
            "optional_authority_fields": ["claim_id"],
            "prompt_guidance_fields": ["speaker", "summary", "available_stances"],
            "validation_rule": (
                "Only caller-provided event_id and claim_id values are local validation "
                "authority. Speaker, summary, available_stances, prose, Discord order, "
                "Hermes messages, and responds_to_event_id are prompt guidance only."
            ),
            "example": {
                "event_id": "evt_speech_0",
                "claim_id": "T01.C1",
                "speaker": "macho",
                "summary": "Canonical speech linkage gates pilot acceptance.",
                "available_stances": ["support", "challenge", "refine", "synthesize"],
            },
        },
    }


def _operator_evidence_report(
    value: object,
    *,
    runfix_task_id: str,
    require_evidence: bool,
    require_quality: bool,
    blockers: list[JsonObject],
) -> JsonObject:
    if not isinstance(value, Mapping):
        if require_evidence:
            message = (
                "plugin/RUNFIX-017 requires explicit runner, ARGUE, canonical "
                "speech-link, and discussion_quality evidence."
                if require_quality
                else (
                    "plugin/RUNFIX-008 requires explicit runner, ARGUE, and "
                    "canonical speech-link evidence."
                )
            )
            blockers.append(
                _blocker(
                    code="operator_evidence_missing",
                    owner="operator",
                    message=message,
                )
            )
        return _empty_operator_evidence_report(runfix_task_id=runfix_task_id)

    evidence = _json_object(value, label="plan.operator_evidence")
    runner = _runner_evidence_report(
        evidence.get("runner"), require_evidence=require_evidence, blockers=blockers
    )
    participant = _participant_response_report(
        evidence.get("participant_response"),
        require_evidence=require_evidence,
        blockers=blockers,
    )
    discussion_quality = _discussion_quality_report(
        evidence.get("discussion_quality"),
        require_quality=require_quality,
        blockers=blockers,
    )
    canonical_link = _canonical_speech_linkage_report(
        evidence.get("canonical_speech"),
        runner=runner,
        participant=cast(JsonObject, participant["participant_response"]),
        require_evidence=require_evidence,
        blockers=blockers,
    )
    fallback_disclosure = _fallback_disclosure_report(
        evidence.get("fallback_disclosure"),
        require_evidence=require_evidence,
        blockers=blockers,
    )
    return {
        "runfix_task_id": runfix_task_id,
        "runner_evidence": runner,
        "canonical_speaker_selected_to_speech": canonical_link,
        "participant_response": participant["participant_response"],
        "argue_counts": participant["argue_counts"],
        "discussion_quality": discussion_quality,
        "fallback_disclosure": fallback_disclosure,
    }


def _empty_operator_evidence_report(*, runfix_task_id: str = RUNFIX_008_TASK_ID) -> JsonObject:
    return {
        "runfix_task_id": runfix_task_id,
        "runner_evidence": {
            "status": "unproven",
            "speaker_selected_event_id": None,
            "selected_member": None,
            "runner_invocation_started_ref": None,
            "durable_runner_failure_ref": None,
        },
        "canonical_speaker_selected_to_speech": {
            "status": "unproven",
            "linked": False,
            "speaker_selected_event_id": None,
            "speech_event_id": None,
            "speaker": None,
        },
        "participant_response": {
            "status": "unproven",
            "speech": None,
            "claims": [],
            "stance_links": [],
            "contribution_type": None,
            "new_axis_reason": None,
            "evidence": [],
        },
        "argue_counts": {
            "status": "unproven",
            "speech_present": False,
            "claims": 0,
            "stance_links": 0,
            "new_axis": 0,
            "evidence": 0,
            "contribution_types": {},
        },
        "discussion_quality": _empty_discussion_quality_report(),
        "fallback_disclosure": {
            "status": "not_supplied",
            "label": "fallback_profile_pass",
            "full_atn_success": False,
            "evidence_ref": None,
            "missing_evidence": [],
        },
    }


def _runner_evidence_report(
    value: object,
    *,
    require_evidence: bool,
    blockers: list[JsonObject],
) -> JsonObject:
    output: JsonObject = {
        "status": "unproven",
        "speaker_selected_event_id": None,
        "selected_member": None,
        "runner_invocation_started_ref": None,
        "durable_runner_failure_ref": None,
    }
    if not isinstance(value, Mapping):
        if require_evidence:
            blockers.append(
                _blocker(
                    code="runner_evidence_missing",
                    owner="member-runtime",
                    message=(
                        "Selected runner evidence from speaker_selected is required "
                        "or must fail closed as durable failure evidence."
                    ),
                )
            )
        return output

    runner = _json_object(value, label="plan.operator_evidence.runner")
    speaker_selected_event_id = runner.get("speaker_selected_event_id")
    selected_member = runner.get("selected_member")
    invocation_ref = runner.get("runner_invocation_started_ref")
    failure_ref = runner.get("durable_runner_failure_ref")
    for key, item in (
        ("speaker_selected_event_id", speaker_selected_event_id),
        ("selected_member", selected_member),
        ("runner_invocation_started_ref", invocation_ref),
        ("durable_runner_failure_ref", failure_ref),
    ):
        if _non_empty_string(item):
            output[key] = cast(str, item)

    has_identity = _non_empty_string(speaker_selected_event_id) and _non_empty_string(
        selected_member
    )
    has_invocation = _non_empty_string(invocation_ref)
    has_failure = _non_empty_string(failure_ref)
    if has_identity and has_invocation:
        output["status"] = "proven"
        return output
    if has_identity and has_failure:
        output["status"] = "blocked"
        if require_evidence:
            blockers.append(
                _blocker(
                    code="runner_durable_failure_reported",
                    owner="member-runtime",
                    message=(
                        "Selected runner reported durable failure instead of successful speech."
                    ),
                )
            )
        return output

    if require_evidence:
        blockers.append(
            _blocker(
                code="runner_evidence_unproven",
                owner="member-runtime",
                message=(
                    "runner.speaker_selected_event_id, runner.selected_member, and "
                    "runner_invocation_started_ref are required for selected_runner_pass."
                ),
            )
        )
    return output


def _participant_response_report(
    value: object,
    *,
    require_evidence: bool,
    blockers: list[JsonObject],
) -> JsonObject:
    response_output: JsonObject = {
        "status": "unproven",
        "speech": None,
        "claims": [],
        "stance_links": [],
        "contribution_type": None,
        "new_axis_reason": None,
        "evidence": [],
    }
    counts: JsonObject = {
        "status": "unproven",
        "speech_present": False,
        "claims": 0,
        "stance_links": 0,
        "new_axis": 0,
        "evidence": 0,
        "contribution_types": {},
    }
    if not isinstance(value, Mapping):
        if require_evidence:
            blockers.append(
                _blocker(
                    code="argue_evidence_missing",
                    owner="participant",
                    message=(
                        "Participant ARGUE evidence requires speech, claims[], "
                        "stance_links[], contribution_type, and optional evidence[]."
                    ),
                )
            )
        return {"participant_response": response_output, "argue_counts": counts}

    response = _json_object(value, label="plan.operator_evidence.participant_response")
    speech = response.get("speech")
    claims = _optional_json_object_list(response.get("claims"), label="claims")
    stance_links = _optional_json_object_list(response.get("stance_links"), label="stance_links")
    evidence_items = _optional_json_object_list(response.get("evidence"), label="evidence")
    contribution_type = response.get("contribution_type")
    new_axis_reason = response.get("new_axis_reason")

    if _non_empty_string(speech):
        response_output["speech"] = cast(str, speech)
        counts["speech_present"] = True
    response_output["claims"] = cast(list[JsonValue], claims)
    response_output["stance_links"] = cast(list[JsonValue], stance_links)
    response_output["evidence"] = cast(list[JsonValue], evidence_items)
    if _non_empty_string(contribution_type):
        contribution = cast(str, contribution_type)
        response_output["contribution_type"] = contribution
        counts["contribution_types"] = {contribution: 1}
    if _non_empty_string(new_axis_reason):
        response_output["new_axis_reason"] = cast(str, new_axis_reason)

    counts["claims"] = len(claims)
    counts["stance_links"] = len(stance_links)
    counts["evidence"] = len(evidence_items)
    is_new_axis = contribution_type == "new_axis"
    counts["new_axis"] = 1 if is_new_axis else 0

    has_argue_linkage = bool(stance_links) or (is_new_axis and _non_empty_string(new_axis_reason))
    if (
        _non_empty_string(speech)
        and claims
        and _non_empty_string(contribution_type)
        and has_argue_linkage
    ):
        response_output["status"] = "proven"
        counts["status"] = "proven"
        return {"participant_response": response_output, "argue_counts": counts}

    if require_evidence:
        blockers.append(
            _blocker(
                code="argue_evidence_unproven",
                owner="participant",
                message=(
                    "Participant response must include visible speech, claims[], "
                    "a contribution_type, and either stance_links[] or a justified new_axis_reason."
                ),
            )
        )
    return {"participant_response": response_output, "argue_counts": counts}


def _empty_discussion_quality_report() -> JsonObject:
    return {
        "status": "unproven",
        "label": "discussion_quality_pass",
        "quality_mode": "not_supplied",
        "discussion_quality_pass": False,
        "first_orphan_speech_event_id": None,
        "orphan_speech_count": 0,
        "repeated_orphan_count": 0,
        "linked_speech_count": 0,
        "stance_link_count": 0,
        "valid_stance_link_count": 0,
        "new_axis_count": 0,
        "diagnostics": [],
        "synthetic_links_created": False,
    }


def _discussion_quality_report(
    value: object,
    *,
    require_quality: bool,
    blockers: list[JsonObject],
) -> JsonObject:
    report = _empty_discussion_quality_report()
    quality_mode = "quality_required" if require_quality else "default"
    local_context_sufficient = True
    prior_claims: dict[str, set[str]] = {}
    turn_sources: list[JsonObject] = []

    if isinstance(value, Mapping):
        quality = _json_object(value, label="plan.operator_evidence.discussion_quality")
        if "quality_mode" in quality:
            quality_mode = _required_string(
                quality.get("quality_mode"),
                label="plan.operator_evidence.discussion_quality.quality_mode",
            )
            if quality_mode not in {"default", "quality_warn", "quality_required"}:
                raise ValueError(
                    "plan.operator_evidence.discussion_quality.quality_mode must be supported"
                )
        local_context_sufficient = quality.get("local_context_sufficient") is not False
        prior_claims = _discussion_prior_claims(quality.get("prior_claims", []))
        turns = quality.get("turns")
        if isinstance(turns, list):
            for index, item in enumerate(turns):
                turn_sources.append(
                    _json_object(
                        item,
                        label=f"plan.operator_evidence.discussion_quality.turns[{index}]",
                    )
                )

    report["quality_mode"] = quality_mode
    if not turn_sources:
        if require_quality:
            blockers.append(
                _blocker(
                    code="discussion_quality_evidence_missing",
                    owner="participant",
                    message=("plugin/RUNFIX-017 requires explicit discussion_quality evidence."),
                )
            )
            report["status"] = "blocked"
        return report

    orphan_count = 0
    linked_count = 0
    stance_link_count = 0
    valid_stance_link_count = 0
    new_axis_count = 0
    diagnostics: list[JsonObject] = []
    first_orphan_event_id: str | None = None

    for index, turn in enumerate(turn_sources):
        response = _discussion_turn_response(turn, index=index)
        is_opening = response.get("is_opening_speech") is True
        turn_local_context_sufficient = (
            local_context_sufficient and response.get("local_context_sufficient") is not False
        )
        speech_event_id = _optional_string_value(response.get("speech_event_id"))
        stance_links = response.get("stance_links")
        turn_stance_count = len(stance_links) if isinstance(stance_links, list) else 0
        turn_valid_links = _valid_discussion_stance_link_count(stance_links, prior_claims)
        has_new_axis = _has_justified_new_axis(response)
        stance_link_count += turn_stance_count
        valid_stance_link_count += turn_valid_links
        if turn_valid_links > 0:
            linked_count += 1
        if has_new_axis:
            new_axis_count += 1

        orphan = (
            not is_opening
            and turn_local_context_sufficient
            and turn_valid_links == 0
            and not has_new_axis
        )
        if orphan:
            orphan_count += 1
            if first_orphan_event_id is None:
                first_orphan_event_id = speech_event_id or f"turn[{index}]"
            diagnostics.append(
                {
                    "code": "orphan_non_opening_speech",
                    "speech_event_id": speech_event_id,
                    "turn_index": index,
                    "synthetic_link_created": False,
                }
            )
        if turn_stance_count and turn_valid_links == 0:
            diagnostics.append(
                {
                    "code": "stance_links_not_validated_against_prior_claims",
                    "speech_event_id": speech_event_id,
                    "turn_index": index,
                    "synthetic_link_created": False,
                }
            )

    report.update(
        {
            "first_orphan_speech_event_id": first_orphan_event_id,
            "orphan_speech_count": orphan_count,
            "repeated_orphan_count": max(0, orphan_count - 1),
            "linked_speech_count": linked_count,
            "stance_link_count": stance_link_count,
            "valid_stance_link_count": valid_stance_link_count,
            "new_axis_count": new_axis_count,
            "diagnostics": cast(list[JsonValue], diagnostics),
        }
    )

    if quality_mode == "quality_required" and orphan_count:
        report["status"] = "blocked"
        report["discussion_quality_pass"] = False
        if require_quality:
            blockers.append(
                _blocker(
                    code="discussion_quality_orphan_speech",
                    owner="participant",
                    message=(
                        "quality_required evidence has a non-opening speech without a "
                        "valid prior-target stance_links[] entry or justified new_axis."
                    ),
                )
            )
        return report

    report["discussion_quality_pass"] = True
    report["status"] = "warning" if orphan_count else "proven"
    return report


def _discussion_turn_response(turn: Mapping[str, object], *, index: int) -> JsonObject:
    response_value = turn.get("participant_response")
    if isinstance(response_value, Mapping):
        response = _json_object(
            response_value,
            label=f"plan.operator_evidence.discussion_quality.turns[{index}].participant_response",
        )
        for key in (
            "speech_event_id",
            "is_opening_speech",
            "local_context_sufficient",
        ):
            if key in turn and key not in response:
                response[key] = cast(JsonValue, turn[key])
        return response
    return cast(JsonObject, turn)


def _has_justified_new_axis(response: Mapping[str, object]) -> bool:
    return response.get("contribution_type") == "new_axis" and _non_empty_string(
        response.get("new_axis_reason")
    )


def _discussion_prior_claims(value: object) -> dict[str, set[str]]:
    if value is None:
        return {}
    if not isinstance(value, list):
        raise ValueError("plan.operator_evidence.discussion_quality.prior_claims must be an array")
    prior_claims: dict[str, set[str]] = {}
    for index, item in enumerate(value):
        claim = _json_object(
            item,
            label=f"plan.operator_evidence.discussion_quality.prior_claims[{index}]",
        )
        event_id = _required_string(
            claim.get("event_id"),
            label=f"plan.operator_evidence.discussion_quality.prior_claims[{index}].event_id",
        )
        claim_ids = prior_claims.setdefault(event_id, set())
        claim_id = claim.get("claim_id")
        if claim_id is not None:
            claim_ids.add(
                _required_string(
                    claim_id,
                    label=(
                        f"plan.operator_evidence.discussion_quality.prior_claims[{index}].claim_id"
                    ),
                )
            )
    return prior_claims


def _valid_discussion_stance_link_count(value: object, prior_claims: Mapping[str, set[str]]) -> int:
    if not isinstance(value, list) or not prior_claims:
        return 0
    valid = 0
    for item in value:
        if not isinstance(item, Mapping):
            continue
        target_event_id = item.get("target_event_id")
        if not _non_empty_string(target_event_id) or target_event_id not in prior_claims:
            continue
        target_claim_ids = prior_claims[cast(str, target_event_id)]
        if not target_claim_ids:
            valid += 1
            continue
        target_claim_id = item.get("target_claim_id")
        if _non_empty_string(target_claim_id) and cast(str, target_claim_id) in target_claim_ids:
            valid += 1
    return valid


def _canonical_speech_linkage_report(
    value: object,
    *,
    runner: JsonObject,
    participant: JsonObject,
    require_evidence: bool,
    blockers: list[JsonObject],
) -> JsonObject:
    output: JsonObject = {
        "status": "unproven",
        "linked": False,
        "speaker_selected_event_id": None,
        "speech_event_id": None,
        "speaker": None,
    }
    if not isinstance(value, Mapping):
        if require_evidence:
            blockers.append(
                _blocker(
                    code="canonical_speech_link_missing",
                    owner="control/plugin",
                    message="Canonical speaker_selected -> speech linkage evidence is required.",
                )
            )
        return output

    link = _json_object(value, label="plan.operator_evidence.canonical_speech")
    speaker_selected_event_id = link.get("speaker_selected_event_id")
    speech_event_id = link.get("speech_event_id")
    speaker = link.get("speaker")
    for key, item in (
        ("speaker_selected_event_id", speaker_selected_event_id),
        ("speech_event_id", speech_event_id),
        ("speaker", speaker),
    ):
        if _non_empty_string(item):
            output[key] = cast(str, item)

    runner_selected = runner.get("speaker_selected_event_id")
    selected_member = runner.get("selected_member")
    linked = (
        _non_empty_string(speaker_selected_event_id)
        and _non_empty_string(speech_event_id)
        and participant.get("status") == "proven"
        and (not _non_empty_string(runner_selected) or speaker_selected_event_id == runner_selected)
        and (not _non_empty_string(selected_member) or speaker == selected_member)
    )
    if linked:
        output["status"] = "proven"
        output["linked"] = True
        return output

    if require_evidence:
        blockers.append(
            _blocker(
                code="canonical_speech_link_unproven",
                owner="control/plugin",
                message=(
                    "speaker_selected_event_id must link to a speech_event_id for the "
                    "selected member and participant speech evidence."
                ),
            )
        )
    return output


def _fallback_disclosure_report(
    value: object,
    *,
    require_evidence: bool,
    blockers: list[JsonObject],
) -> JsonObject:
    output: JsonObject = {
        "status": "not_supplied",
        "label": "fallback_profile_pass",
        "full_atn_success": False,
        "evidence_ref": None,
        "missing_evidence": [],
    }
    if not isinstance(value, Mapping):
        return output

    disclosure = _json_object(value, label="plan.operator_evidence.fallback_disclosure")
    evidence_ref = disclosure.get("evidence_ref")
    missing_evidence = _optional_string_list(disclosure.get("missing_evidence"))
    fallback_obtained = disclosure.get("fallback_profile_pass") is True
    if _non_empty_string(evidence_ref):
        output["evidence_ref"] = cast(str, evidence_ref)
    output["missing_evidence"] = cast(list[JsonValue], missing_evidence)
    if fallback_obtained or _non_empty_string(evidence_ref) or missing_evidence:
        output["status"] = "diagnostic_only"
    if require_evidence and fallback_obtained and not missing_evidence:
        blockers.append(
            _blocker(
                code="fallback_disclosure_missing_missing_evidence",
                owner="operator",
                message=(
                    "Fallback profile evidence must name the missing runner, ARGUE, "
                    "canonical-link, delivery, or gateway evidence."
                ),
            )
        )
    return output


def _rollback_steps(value: object, *, blockers: list[JsonObject]) -> list[str]:
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="rollback_missing",
                owner="operator",
                message="rollback.steps are required.",
            )
        )
        return []
    rollback = _json_object(value, label="plan.rollback")
    return _required_string_list(
        rollback.get("steps"),
        label="plan.rollback.steps",
        blocker_code="rollback_steps_missing",
        blocker_owner="operator",
        blocker_message="rollback.steps must include at least one step.",
        blockers=blockers,
    )


def _optional_operator_blockers(value: object) -> list[JsonObject]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("plan.operator_blockers must be a JSON array when present")
    blockers: list[JsonObject] = []
    for index, item in enumerate(value):
        blocker = _json_object(item, label=f"plan.operator_blockers[{index}]")
        blockers.append(
            _blocker(
                code=_required_string(blocker.get("code"), label="operator_blocker.code"),
                owner=_required_string(blocker.get("owner"), label="operator_blocker.owner"),
                message=_required_string(blocker.get("message"), label="operator_blocker.message"),
            )
        )
    return blockers


def _evidence_labels(value: object) -> JsonObject:
    if value is None:
        labels: Mapping[str, object] = {}
    else:
        labels = _json_object(value, label="plan.evidence_labels")
    output: JsonObject = {}
    for label in EVIDENCE_LABELS:
        item = labels.get(label)
        output[label] = cast(JsonValue, item) if _non_empty_evidence(item) else "unproven"
    return output


def _required_string_list(
    value: object,
    *,
    label: str,
    blocker_code: str,
    blocker_owner: str,
    blocker_message: str,
    blockers: list[JsonObject],
) -> list[str]:
    if not isinstance(value, list):
        blockers.append(_blocker(code=blocker_code, owner=blocker_owner, message=blocker_message))
        return []
    items = [item for item in value if isinstance(item, str) and item]
    if len(items) != len(value) or not items:
        blockers.append(_blocker(code=blocker_code, owner=blocker_owner, message=blocker_message))
        return []
    return items


def _optional_string_list(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _optional_json_object_list(value: object, *, label: str) -> list[JsonObject]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"plan.operator_evidence.participant_response.{label} must be an array")
    output: list[JsonObject] = []
    for index, item in enumerate(value):
        output.append(
            _json_object(
                item,
                label=f"plan.operator_evidence.participant_response.{label}[{index}]",
            )
        )
    return output


def _start_status(
    *,
    blockers: list[JsonObject],
    blocked_profiles: list[JsonObject],
    excluded_profiles: list[JsonObject],
    eligible_profiles: list[JsonObject],
    requested_output_mode: str,
    request_source: str,
    task_id: str,
) -> str:
    acceptance_only_codes = (
        RUNFIX3_ACCEPTANCE_ONLY_CODES
        if task_id == RUNFIX3_003_TASK_ID and requested_output_mode == "live_visible_thread"
        else frozenset()
    )
    blocking_codes = [
        cast(str, blocker["code"])
        for blocker in blockers
        if blocker["code"] != "no_eligible_profiles"
        and blocker["code"] not in acceptance_only_codes
    ]
    if blocking_codes or blocked_profiles:
        return "blocked"
    if (
        task_id == RUNFIX3_003_TASK_ID
        and requested_output_mode == "live_visible_thread"
        and request_source.startswith("discord")
        and excluded_profiles
    ):
        return "blocked"
    if (
        any(blocker["code"] not in acceptance_only_codes for blocker in blockers)
        or not eligible_profiles
    ):
        return "not_ready"
    if (
        task_id in {RUNFIX_010_TASK_ID, RUNFIX3_003_TASK_ID, NEWFIX_006_TASK_ID}
        and requested_output_mode == "live_visible_thread"
        and request_source.startswith("discord")
    ):
        return "ready_to_start"
    return "ready_for_approval"


def _runfix3_acceptance_status(
    *,
    task_id: str,
    requested_output_mode: str,
    runfix3_live_thread_proof: JsonObject,
) -> str:
    if task_id != RUNFIX3_003_TASK_ID or requested_output_mode != "live_visible_thread":
        return "not_required"
    return cast(str, runfix3_live_thread_proof["status"])


def _overall_status(*, start_status: str, runfix3_acceptance_status: str) -> str:
    if runfix3_acceptance_status == "not_required":
        return start_status
    if start_status in {"blocked", "not_ready"}:
        return start_status
    if runfix3_acceptance_status == "proven":
        return start_status
    return "blocked"


def _blocker(*, code: str, owner: str, message: str) -> JsonObject:
    return {"code": code, "owner": owner, "message": message}


def _json_object(value: object, *, label: str) -> JsonObject:
    try:
        return require_json_object(cast(Mapping[str, object], value), label=label)
    except ProtocolValidationError as exc:
        raise ValueError(str(exc)) from exc


def _required_string(value: object, *, label: str) -> str:
    if not _non_empty_string(value):
        raise ValueError(f"{label} must be a non-empty string")
    return cast(str, value)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_evidence(value: object) -> bool:
    if _non_empty_string(value):
        return True
    if isinstance(value, Mapping):
        return bool(value)
    return False


__all__ = ["ACTIVATION_PLAN_SCHEMA_VERSION", "TOOL_NAME", "build_discussion_activation_plan"]
