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
SUPPORTED_TASK_IDS: Final[frozenset[str]] = frozenset({RUNFIX_006_TASK_ID, RUNFIX_007_TASK_ID})
TASK_ID: Final = RUNFIX_007_TASK_ID
CONTROL_DEPENDENCY_TASK_ID: Final = "control/RUNFIX-005"
CONTROL_DEPENDENCY_STATUS: Final = "completed/local-control"
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
        raise ValueError("plan.task_id must be plugin/RUNFIX-006 or plugin/RUNFIX-007")

    blockers: list[JsonObject] = []
    excluded_profiles: list[JsonObject] = []
    blocked_profiles: list[JsonObject] = []

    _validate_control_dependency(source.get("control_dependency"), blockers=blockers)
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
        "behavior_task_id": RUNFIX_007_TASK_ID,
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
            "production activation or live readiness claim",
        ],
    }


def _validate_control_dependency(value: object, *, blockers: list[JsonObject]) -> None:
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
