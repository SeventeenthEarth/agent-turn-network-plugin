"""Pure dry-run KAN discussion activation planner.

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
SUPPORTED_TASK_IDS: Final[frozenset[str]] = frozenset(
    {
        RUNFIX_006_TASK_ID,
        RUNFIX_007_TASK_ID,
        RUNFIX_008_TASK_ID,
        RUNFIX_010_TASK_ID,
        RUNFIX_012_TASK_ID,
        RUNFIX_015_TASK_ID,
    }
)
TASK_ID: Final = RUNFIX_010_TASK_ID
CONTROL_DEPENDENCY_TASK_ID: Final = "control/RUNFIX-005"
CONTROL_DEPENDENCY_STATUS: Final = "completed/local-control"
RUNFIX_012_CONTROL_DEPENDENCY_TASK_ID: Final = "control/RUNFIX-011"
RUNFIX_012_CONTROL_DEPENDENCY_STATUSES: Final[frozenset[str]] = frozenset(
    {"local implementation proof", "completed/local-control", "local-control"}
)
TOOL_NAME: Final = "kan_discussion_activation_plan"
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
            "or plugin/RUNFIX-015"
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
        require_evidence=task_id in {RUNFIX_008_TASK_ID, RUNFIX_010_TASK_ID},
        blockers=blockers,
    )
    visible_surface_readiness = _visible_surface_readiness_report(
        source.get("request_context"),
        source.get("visible_surface_readiness"),
        task_id=task_id,
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
        task_id=task_id,
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

    status = _status(
        blockers=blockers, blocked_profiles=blocked_profiles, eligible_profiles=eligible_profiles
    )
    return {
        "schema_version": ACTIVATION_PLAN_SCHEMA_VERSION,
        "task_id": task_id,
        "behavior_task_id": _behavior_task_id(task_id),
        "status": status,
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
        "requested_output_mode": visible_surface_readiness["requested_output_mode"],
        "visible_surface_readiness_report": visible_surface_readiness,
        "participant_runtime_readiness_report": participant_runtime_readiness,
        "visible_author_guard_report": visible_author_guard,
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
    }:
        return task_id
    return RUNFIX_007_TASK_ID


def _validate_control_dependency(
    value: object, *, task_id: str, blockers: list[JsonObject]
) -> None:
    if task_id == RUNFIX_012_TASK_ID:
        _validate_runfix_012_control_dependency(value, blockers=blockers)
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
                    "kan_discussion_activation_plan must be visible in plugin_install.tool_names."
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
        effective_discord = _effective_discord(profile, index=index)
        evidence_ref = effective_discord.get("evidence_ref") or profile.get("evidence_ref")
        row = {"profile": profile_name}
        if _non_empty_string(evidence_ref):
            row["evidence_ref"] = cast(str, evidence_ref)
        tools_visible = effective_discord.get("tools_visible")
        bot_to_bot_enabled = effective_discord.get("bot_to_bot_enabled")
        if tools_visible is None:
            blocked_profiles.append(
                {
                    **row,
                    "reason": "tools_visibility_unknown",
                    "remediation": "Provide explicit effective Discord tool visibility evidence.",
                }
            )
            continue
        if tools_visible is not True:
            blocked_profiles.append(
                {
                    **row,
                    "reason": "tools_visibility_missing_or_false",
                    "remediation": (
                        "Enable/verify the profile-visible KAN plugin tools before allow-listing."
                    ),
                }
            )
            continue
        if bot_to_bot_enabled is None:
            blocked_profiles.append(
                {
                    **row,
                    "reason": "bot_to_bot_eligibility_unknown",
                    "remediation": "Provide explicit effective Discord bot-to-bot policy evidence.",
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
                        "KAN discussion allow-list."
                    ),
                }
            )
            continue
        if bot_to_bot_enabled is not False:
            blocked_profiles.append(
                {
                    **row,
                    "reason": "bot_to_bot_eligibility_unknown",
                    "remediation": "Provide explicit effective Discord bot-to-bot policy evidence.",
                }
            )
            continue
        eligible.append(
            {
                **row,
                "reason": "effective_discord_tools_visible_and_bot_to_bot_disabled",
            }
        )
    return eligible


def _effective_discord(profile: JsonObject, *, index: int) -> JsonObject:
    value = profile.get("effective_discord")
    if value is None:
        return {
            "tools_visible": profile.get("tools_visible"),
            "bot_to_bot_enabled": profile.get("bot_to_bot_enabled"),
            "evidence_ref": profile.get("evidence_ref"),
        }
    if not isinstance(value, Mapping):
        raise ValueError(
            f"plan.participant_profiles[{index}].effective_discord must be an object when present"
        )
    return _json_object(value, label=f"plan.participant_profiles[{index}].effective_discord")


def _profile_remediation(
    *,
    excluded_profiles: list[JsonObject],
    blocked_profiles: list[JsonObject],
) -> JsonObject:
    return {
        "excluded": cast(list[JsonValue], excluded_profiles),
        "blocked": cast(list[JsonValue], blocked_profiles),
    }


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
    if requested_output_mode is None:
        requested_output_mode = (
            "live_visible_thread"
            if request_source.startswith("discord")
            else "activation_planning_only"
        )
    report: JsonObject = {
        "requested_output_mode": requested_output_mode,
        "request_source": request_source,
        "surface_bound": False,
        "turn_delivery_proven": False,
        "visible_closeout_proven": False,
        "real_profile_gateway_replies": False,
        "cli_actor_speech_only": False,
        "visible_turns_expected": 0,
        "visible_turns_posted": 0,
        "ready": False,
    }
    if task_id != RUNFIX_010_TASK_ID:
        report["ready"] = requested_output_mode != "live_visible_thread"
        return report

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
                    "daemon_cli_actor_speech, or activation_planning_only."
                ),
            )
        )
        return report

    if requested_output_mode in {"artifact_only", "daemon_cli_actor_speech"}:
        if (
            request_source.startswith("discord")
            and request_context.get("artifact_only_confirmed") is not True
        ):
            blockers.append(
                _blocker(
                    code="artifact_only_confirmation_missing",
                    owner="operator",
                    message=(
                        "Artifact-only or daemon CLI actor speech mode for a "
                        "Discord-origin request "
                        "requires explicit operator confirmation before session creation."
                    ),
                )
            )
        report["ready"] = request_context.get("artifact_only_confirmed") is True
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
                    "Discord-origin KAN council requests default to live visible thread output; "
                    "provide surface binding, turn-posting, profile/gateway reply, "
                    "and closeout evidence "
                    "or explicitly confirm artifact-only mode before creating the session."
                ),
            )
        )
        return report

    readiness = _json_object(readiness_value, label="plan.visible_surface_readiness")
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
    report.update(
        {
            "surface_bound": surface_bound,
            "turn_delivery_proven": turn_delivery_proven,
            "visible_closeout_proven": visible_closeout_proven,
            "real_profile_gateway_replies": real_profile_gateway_replies,
            "cli_actor_speech_only": cli_actor_speech_only,
            "visible_turns_expected": expected,
            "visible_turns_posted": posted,
        }
    )
    missing: list[str] = []
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
    task_id: str,
    blockers: list[JsonObject],
) -> JsonObject:
    report: JsonObject = {
        "runfix_task_id": RUNFIX_015_TASK_ID,
        "guard_surface": "pre_council_new_activation_plan",
        "runtime_enforcement": False,
        "operator_must_consume_before_session_creation": True,
        "status": "not_required",
        "ready": task_id != RUNFIX_015_TASK_ID,
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
    if task_id != RUNFIX_015_TASK_ID:
        return report

    report["status"] = "blocked"
    report["ready"] = False
    if not isinstance(value, Mapping):
        blockers.append(
            _blocker(
                code="visible_author_guard_missing",
                owner="operator/Hermes-gateway",
                message=(
                    "plugin/RUNFIX-015 requires explicit visible_author_guard evidence "
                    "before council.new/session creation."
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
                    "kan_discussion_activation_plan is planner-only and must not claim "
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
                owner="operator/KAN-control",
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
        "lifecycle": "kan_lifecycle_finalized true/false from daemon/control evidence",
        "visible_turns_posted": "discord visible turns posted N/expected",
        "real_profile_gateway_replies": "true/false from explicit profile/gateway evidence",
        "selected_runner_labels": "selected-runner evidence labels separate from lifecycle",
        "shared_default_author_fallback_status": (
            "none/shared_default_detected/unproven from visible_author_guard"
        ),
    }


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
            "manual_profile_replies_as_full_kan_success",
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
    }


def _operator_evidence_report(
    value: object,
    *,
    require_evidence: bool,
    blockers: list[JsonObject],
) -> JsonObject:
    if not isinstance(value, Mapping):
        if require_evidence:
            blockers.append(
                _blocker(
                    code="operator_evidence_missing",
                    owner="operator",
                    message=(
                        "plugin/RUNFIX-008 requires explicit runner, ARGUE, and "
                        "canonical speech-link evidence."
                    ),
                )
            )
        return _empty_operator_evidence_report()

    evidence = _json_object(value, label="plan.operator_evidence")
    runner = _runner_evidence_report(
        evidence.get("runner"), require_evidence=require_evidence, blockers=blockers
    )
    participant = _participant_response_report(
        evidence.get("participant_response"),
        require_evidence=require_evidence,
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
        "runfix_task_id": RUNFIX_008_TASK_ID,
        "runner_evidence": runner,
        "canonical_speaker_selected_to_speech": canonical_link,
        "participant_response": participant["participant_response"],
        "argue_counts": participant["argue_counts"],
        "fallback_disclosure": fallback_disclosure,
    }


def _empty_operator_evidence_report() -> JsonObject:
    return {
        "runfix_task_id": RUNFIX_008_TASK_ID,
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
        "fallback_disclosure": {
            "status": "not_supplied",
            "label": "fallback_profile_pass",
            "full_kan_success": False,
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
        "full_kan_success": False,
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


def _status(
    *,
    blockers: list[JsonObject],
    blocked_profiles: list[JsonObject],
    eligible_profiles: list[JsonObject],
) -> str:
    if any(blocker["code"] != "no_eligible_profiles" for blocker in blockers) or blocked_profiles:
        return "blocked"
    if blockers or not eligible_profiles:
        return "not_ready"
    return "ready_for_approval"


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
    return isinstance(value, str) and bool(value)


def _non_empty_evidence(value: object) -> bool:
    if _non_empty_string(value):
        return True
    if isinstance(value, Mapping):
        return bool(value)
    return False


__all__ = ["ACTIVATION_PLAN_SCHEMA_VERSION", "TOOL_NAME", "build_discussion_activation_plan"]
