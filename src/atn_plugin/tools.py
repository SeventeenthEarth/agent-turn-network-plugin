"""JSON-string Hermes handlers for fake/injected ATN plugin tools."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Final, Protocol, cast

from . import schemas
from .activation_planner import build_discussion_activation_plan
from .client import DaemonClient
from .client.live import configured_live_client_factory
from .discord_surface import (
    DiscordMessageResult,
    DiscordMessageTarget,
    SendMessageFn,
    send_discord_message,
)
from .errors import (
    DaemonCommandError,
    DaemonCompatibilityError,
    DaemonErrorDetails,
    DaemonProtocolError,
    DaemonStreamError,
    DaemonTransportError,
    redact_sensitive,
)
from .protocol import (
    COUNCIL_LIFECYCLE_REQUIRED_FEATURE_GROUPS,
    DELIVERY_EVIDENCE_REQUIRED_FEATURE_GROUPS,
    STREAM_TAIL_FRAME_LIMIT,
    CommandResult,
    DaemonDiagnostics,
    DaemonStatus,
    DiagnosticCheck,
    JsonObject,
    JsonValue,
    ProtocolValidationError,
    StreamEvent,
    StreamFrame,
    StreamTail,
    require_json_object,
)
from .surface_rendering import render_surface_projection

ClientFactory = Callable[[], DaemonClient]
TOOLSET: Final = "atn_plugin"
ARGUE_SPEECH_PASSTHROUGH_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "claims",
        "stance_links",
        "contribution_type",
        "new_axis_reason",
        "evidence",
        "responds_to_event_id",
    }
)
CALLER_VALIDATION_CONTEXT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "quality_mode",
        "local_context_sufficient",
        "is_opening_speech",
        "selected_member",
        "selected_event_id",
        "selected_cursor",
        "prior_claims",
    }
)
CALLER_VALIDATION_QUALITY_MODES: Final[frozenset[str]] = frozenset(
    {"default", "quality_warn", "quality_required"}
)
RUNTIME_NOISE_PREFIXES: Final[tuple[str, ...]] = (
    "WARNING:",
    "RuntimeWarning:",
    "Traceback (most recent call last):",
)
RUNTIME_NOISE_PREFIXES_LOWER: Final[tuple[str, ...]] = (
    "[warning]",
    "[runtime warning]",
    "system warning:",
    "runtime warning:",
    "max iterations reached",
    "maximum iterations reached",
    "tool run diagnostics:",
    "tool-run diagnostics:",
    "tool diagnostics:",
    "wrapper metadata:",
    "runner diagnostics:",
)
TURN_BEARING_COUNCIL_COMMANDS: Final[frozenset[str]] = frozenset(
    {
        "council.poll",
        schemas.COUNCIL_HAND_RAISE_COMMAND,
        schemas.COUNCIL_DROP_COMMAND,
        "council.grant",
        schemas.COUNCIL_SPEAK_COMMAND,
    }
)


class ToolRegistrationContext(Protocol):
    def register_tool(self, **kwargs: object) -> None: ...


def handle_daemon_status(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Return daemon status as a JSON string or a fail-closed JSON error."""

    try:
        _ = _coerce_args(args, allowed_keys=frozenset())
        client = _require_client(client_factory)
        status = client.read_status()
        return _json_success("atn_daemon_status", status, _status_data(status))
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error("atn_daemon_status", exc)


def handle_compatibility_diagnostics(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Return compatibility diagnostics as a JSON string or fail closed."""

    try:
        payload = _coerce_args(args, allowed_keys=frozenset({"session_id"}))
        session_id = _optional_string(payload.get("session_id"), label="session_id")
        client = _require_client(client_factory)
        diagnostics = client.read_diagnostics(session_id=session_id)
        return _json_success(
            "atn_compatibility_diagnostics",
            diagnostics,
            _diagnostics_data(diagnostics),
        )
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error("atn_compatibility_diagnostics", exc)


def handle_stream_tail(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Return retained stream tail frames as a JSON string or fail closed."""

    try:
        payload = _coerce_args(
            args,
            allowed_keys=frozenset({"session_id", "member", "since_cursor", "limit"}),
        )
        session_id = _required_string(payload.get("session_id"), label="session_id")
        member = _required_string(payload.get("member"), label="member")
        since_cursor = _optional_string(payload.get("since_cursor"), label="since_cursor")
        limit = _optional_limit(payload.get("limit"))
        client = _require_client(client_factory)
        stream_tail = client.read_stream_tail(
            session_id=session_id,
            member=member,
            since_cursor=since_cursor,
            limit=limit,
        )
        return _json_stream_success("atn_stream_tail", stream_tail, _stream_tail_data(stream_tail))
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error("atn_stream_tail", exc)


def handle_stream_ack(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Submit a stream cursor acknowledgement as JSON or fail closed."""

    tool = "atn_stream_ack"
    try:
        payload = _coerce_args(
            args,
            allowed_keys=frozenset({"session_id", "member", "cursor", "command_id"}),
        )
        session_id = _required_string(payload.get("session_id"), label="session_id")
        member = _required_string(payload.get("member"), label="member")
        cursor = _required_string(payload.get("cursor"), label="cursor")
        command_id = _required_string(payload.get("command_id"), label="command_id")
        client = _require_client(client_factory)
        result = client.ack_stream(
            session_id=session_id,
            member=member,
            cursor=cursor,
            command_id=command_id,
        )
        return _json_command_success(tool, result)
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def handle_delegate_new(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Submit a delegate.new envelope as a JSON string or fail closed."""

    tool = "atn_delegate_new"
    try:
        payload = _coerce_args(
            args,
            allowed_keys=frozenset(
                {
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
                }
            ),
        )
        command_payload: JsonObject = {
            "session_id": _required_string(payload.get("session_id"), label="session_id"),
            "moderator": _required_string(payload.get("moderator"), label="moderator"),
            "assignee": _required_string(payload.get("assignee"), label="assignee"),
            "title": _required_string(payload.get("title"), label="title"),
            "task": _required_string(payload.get("task"), label="task"),
            "context": _required_json_object(payload.get("context"), label="context"),
            "participants": _required_json_array(payload.get("participants"), label="participants"),
            "acceptance": _required_json_array(payload.get("acceptance"), label="acceptance"),
            "expected_outputs": _required_json_array(
                payload.get("expected_outputs"), label="expected_outputs"
            ),
            "limits": _required_json_object(payload.get("limits"), label="limits"),
        }
        request_id = _required_string(payload.get("request_id"), label="request_id")
        idempotency_key = _required_string(payload.get("idempotency_key"), label="idempotency_key")
        return _submit_command(
            tool=tool,
            client_factory=client_factory,
            command=schemas.DELEGATE_NEW_COMMAND,
            payload=command_payload,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def handle_delegate_action(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Submit an exact delegate.* action envelope as JSON or fail closed."""

    tool = "atn_delegate_action"
    try:
        payload = _coerce_args(
            args,
            allowed_keys=frozenset(
                {"session_id", "command", "request_id", "idempotency_key", "payload"}
            ),
        )
        session_id = _required_string(payload.get("session_id"), label="session_id")
        command = _required_string(payload.get("command"), label="command")
        if command not in schemas.DELEGATE_ACTION_COMMANDS:
            raise ValueError(f"unsupported delegate action command: {command}")
        request_id = _required_string(payload.get("request_id"), label="request_id")
        idempotency_key = _required_string(payload.get("idempotency_key"), label="idempotency_key")
        command_payload = _required_json_object(payload.get("payload"), label="payload")
        # Deterministic normalization rule: the top-level session_id is authoritative
        # and always overwrites/sets payload.session_id before the envelope is submitted.
        command_payload = {**command_payload, "session_id": session_id}

        return _submit_command(
            tool=tool,
            client_factory=client_factory,
            command=command,
            payload=command_payload,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def handle_council_command(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Submit an exact council.* lifecycle envelope as JSON or fail closed."""

    tool = "atn_council_command"
    try:
        payload = _coerce_args(
            args,
            allowed_keys=frozenset(
                {"command", "session_id", "request_id", "idempotency_key", "payload"}
            ),
        )
        session_id = _required_string(payload.get("session_id"), label="session_id")
        command = _required_string(payload.get("command"), label="command")
        if command not in schemas.COUNCIL_COMMANDS:
            raise ValueError(f"unsupported council command: {command}")
        request_id = _required_string(payload.get("request_id"), label="request_id")
        idempotency_key = _required_string(payload.get("idempotency_key"), label="idempotency_key")
        command_payload = _required_json_object(payload.get("payload"), label="payload")
        _validate_council_payload(command, command_payload)
        if command == "council.new":
            _canonicalize_council_new_output_intent(command_payload)
        command_payload = {**command_payload, "session_id": session_id}

        return _submit_feature_gated_command(
            tool=tool,
            client_factory=client_factory,
            required_feature_groups=COUNCIL_LIFECYCLE_REQUIRED_FEATURE_GROUPS,
            command=command,
            payload=command_payload,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def handle_selected_participant_response(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Submit a selected participant council.speak response, then ack its cursor."""

    tool = "atn_selected_participant_response"
    try:
        payload = _coerce_args(
            args,
            allowed_keys=frozenset(
                {
                    "session_id",
                    "selected_member",
                    "speaker_selected_frame",
                    "participant_response",
                    "command_id",
                    "request_id",
                    "idempotency_key",
                    "ack_command_id",
                    "caller_validation_context",
                }
            ),
        )
        session_id = _required_string(payload.get("session_id"), label="session_id")
        selected_member = _required_string(payload.get("selected_member"), label="selected_member")
        frame = _required_json_object(
            payload.get("speaker_selected_frame"), label="speaker_selected_frame"
        )
        participant_response = _required_json_object(
            payload.get("participant_response"), label="participant_response"
        )
        command_id = _required_string(payload.get("command_id"), label="command_id")
        request_id = _required_string(payload.get("request_id"), label="request_id")
        idempotency_key = _required_string(payload.get("idempotency_key"), label="idempotency_key")
        ack_command_id = _required_string(payload.get("ack_command_id"), label="ack_command_id")

        selected_context = _selected_context(
            session_id=session_id,
            frame=frame,
            selected_member=selected_member,
            participant_response=participant_response,
        )
        caller_validation_context = _caller_validation_context(
            payload.get("caller_validation_context"),
            selected_context=selected_context,
            selected_member=selected_member,
        )
        participant_evidence = _participant_response_evidence(
            participant_response=participant_response,
            speaker_selected_event_id=cast(str, selected_context["event_id"]),
            speaker_selected_cursor=cast(str, selected_context["cursor"]),
        )
        speech = _selected_participant_speech(participant_response)
        speech_payload: JsonObject = {
            "speech": speech,
            "turn": selected_context["turn"],
        }
        participant_argue_fields = _selected_participant_argue_fields(participant_response)
        _validate_selected_participant_caller_context(
            caller_validation_context,
            participant_argue_fields=participant_argue_fields,
        )
        if participant_argue_fields:
            speech_payload.update(participant_argue_fields)
            speech_payload["plugin_evidence"] = participant_evidence
        else:
            speech_payload["evidence"] = participant_evidence

        speak_payload: JsonObject = {
            "actor": selected_member,
            "command_id": command_id,
            "payload": speech_payload,
        }
        _validate_council_payload(schemas.COUNCIL_SPEAK_COMMAND, speak_payload)
        speak_payload = {**speak_payload, "session_id": session_id}

        client = _require_client(client_factory)
        client.require_feature_groups(COUNCIL_LIFECYCLE_REQUIRED_FEATURE_GROUPS)
        envelope = client.build_command_envelope(
            command=schemas.COUNCIL_SPEAK_COMMAND,
            payload=speak_payload,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
        speak_result = client.submit_command(envelope)
        ack_result = client.ack_stream(
            session_id=session_id,
            member=selected_member,
            cursor=cast(str, selected_context["cursor"]),
            command_id=ack_command_id,
        )
        return _json_selected_participant_response_success(
            tool=tool,
            selected_member=selected_member,
            speaker_selected_event_id=cast(str, selected_context["event_id"]),
            speaker_selected_cursor=cast(str, selected_context["cursor"]),
            speak_result=speak_result,
            ack_result=ack_result,
            participant_response=participant_response,
        )
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def handle_delivery_evidence(
    args: object | None = None,
    *,
    client_factory: ClientFactory | None = None,
    **_kwargs: object,
) -> str:
    """Submit an exact delivery-evidence envelope as JSON or fail closed."""

    tool = "atn_delivery_evidence"
    try:
        payload = _coerce_args(
            args,
            allowed_keys=frozenset(
                {"command", "session_id", "request_id", "idempotency_key", "payload"}
            ),
        )
        session_id = _required_string(payload.get("session_id"), label="session_id")
        command = _required_string(payload.get("command"), label="command")
        if command not in schemas.DELIVERY_EVIDENCE_COMMANDS:
            raise ValueError(f"unsupported delivery evidence command: {command}")
        request_id = _required_string(payload.get("request_id"), label="request_id")
        idempotency_key = _required_string(payload.get("idempotency_key"), label="idempotency_key")
        command_payload = _required_json_object(payload.get("payload"), label="payload")
        _validate_delivery_evidence_payload(command, command_payload)
        command_payload = {**command_payload, "session_id": session_id}

        return _submit_feature_gated_command(
            tool=tool,
            client_factory=client_factory,
            required_feature_groups=DELIVERY_EVIDENCE_REQUIRED_FEATURE_GROUPS,
            command=command,
            payload=command_payload,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def handle_discord_send_message(
    args: object | None = None,
    *,
    send_message: SendMessageFn | None = None,
    **_kwargs: object,
) -> str:
    """Send Discord message through an explicit injected sender or fail closed."""

    tool = "atn_discord_send_message"
    try:
        payload = _coerce_args(args, allowed_keys=frozenset({"content", "target"}))
        target_value = payload.get("target")
        if not isinstance(target_value, Mapping):
            raise ValueError("target must be a JSON object")
        target = DiscordMessageTarget.from_mapping(target_value)
        result = send_discord_message(
            target=target,
            content=_required_string(payload.get("content"), label="content"),
            sender=send_message,
        )
        return _json_discord_success(tool, result)
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def handle_surface_render_projection(
    args: object | None = None,
    **_kwargs: object,
) -> str:
    """Render explicit daemon/control projection JSON without side effects."""

    tool = "atn_surface_render_projection"
    try:
        payload = _coerce_args(args, allowed_keys=frozenset({"projection"}))
        projection = _required_json_object(payload.get("projection"), label="projection")
        data = render_surface_projection(projection)
        return _json_surface_projection_success(tool, data)
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def handle_discussion_activation_plan(
    args: object | None = None,
    **_kwargs: object,
) -> str:
    """Build a pure dry-run discussion activation planner/doctor report."""

    tool = "atn_discussion_activation_plan"
    try:
        payload = _coerce_args(args, allowed_keys=frozenset({"plan"}))
        plan = _required_json_object(payload.get("plan"), label="plan")
        data = build_discussion_activation_plan(plan)
        ok = data["start_status"] in {"ready_for_approval", "ready_to_start"}
        return _json_activation_plan(tool=tool, ok=bool(ok), data=data)
    except Exception as exc:  # noqa: BLE001 - Hermes handlers must never raise.
        return _json_error(tool, exc)


def register_tools(
    ctx: ToolRegistrationContext,
    *,
    client_factory: ClientFactory | None = None,
    config: Mapping[str, object] | None = None,
    send_message: SendMessageFn | None = None,
) -> None:
    """Register ATN tools with an explicit injected or configured client factory."""

    if client_factory is None:
        try:
            client_factory = configured_live_client_factory(config)
        except DaemonTransportError as exc:
            client_factory = _failing_client_factory(exc)

    def daemon_status_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_daemon_status(args, client_factory=client_factory)

    def compatibility_diagnostics_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_compatibility_diagnostics(args, client_factory=client_factory)

    def stream_tail_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_stream_tail(args, client_factory=client_factory)

    def stream_ack_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_stream_ack(args, client_factory=client_factory)

    def delegate_new_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_delegate_new(args, client_factory=client_factory)

    def delegate_action_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_delegate_action(args, client_factory=client_factory)

    def council_command_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_council_command(args, client_factory=client_factory)

    def selected_participant_response_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_selected_participant_response(args, client_factory=client_factory)

    def delivery_evidence_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_delivery_evidence(args, client_factory=client_factory)

    def surface_render_projection_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_surface_render_projection(args)

    def discussion_activation_plan_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_discussion_activation_plan(args)

    def discord_send_message_handler(args: object | None = None, **_kwargs: object) -> str:
        return handle_discord_send_message(args, send_message=send_message)

    registrations: tuple[tuple[str, dict[str, object], Callable[[object | None], str]], ...]
    registrations = (
        ("atn_daemon_status", schemas.ATN_DAEMON_STATUS, daemon_status_handler),
        (
            "atn_compatibility_diagnostics",
            schemas.ATN_COMPATIBILITY_DIAGNOSTICS,
            compatibility_diagnostics_handler,
        ),
        ("atn_stream_tail", schemas.ATN_STREAM_TAIL, stream_tail_handler),
        ("atn_stream_ack", schemas.ATN_STREAM_ACK, stream_ack_handler),
        ("atn_delegate_new", schemas.ATN_DELEGATE_NEW, delegate_new_handler),
        ("atn_delegate_action", schemas.ATN_DELEGATE_ACTION, delegate_action_handler),
        ("atn_council_command", schemas.ATN_COUNCIL_COMMAND, council_command_handler),
        (
            "atn_selected_participant_response",
            schemas.ATN_SELECTED_PARTICIPANT_RESPONSE,
            selected_participant_response_handler,
        ),
        ("atn_delivery_evidence", schemas.ATN_DELIVERY_EVIDENCE, delivery_evidence_handler),
        (
            "atn_surface_render_projection",
            schemas.ATN_SURFACE_RENDER_PROJECTION,
            surface_render_projection_handler,
        ),
        (
            "atn_discussion_activation_plan",
            schemas.ATN_DISCUSSION_ACTIVATION_PLAN,
            discussion_activation_plan_handler,
        ),
        (
            "atn_discord_send_message",
            schemas.ATN_DISCORD_SEND_MESSAGE,
            discord_send_message_handler,
        ),
    )
    for name, schema, handler in registrations:
        ctx.register_tool(
            name=name,
            toolset=TOOLSET,
            schema=schema,
            handler=handler,
        )


def _coerce_args(args: object | None, *, allowed_keys: frozenset[str]) -> Mapping[str, object]:
    if args is None:
        return {}
    if not isinstance(args, Mapping):
        raise ValueError("tool args must be an object")
    unknown_keys = sorted(str(key) for key in args if key not in allowed_keys)
    if unknown_keys:
        raise ValueError(f"unsupported tool args: {', '.join(unknown_keys)}")
    return args


def _required_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _optional_string(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string when present")
    return value


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _required_json_object(value: object, *, label: str) -> JsonObject:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object")
    try:
        return require_json_object(value, label=label)
    except ProtocolValidationError as exc:
        raise ValueError(str(exc)) from exc


def _required_json_array(value: object, *, label: str) -> list[JsonValue]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array")
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
        decoded = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must contain only JSON-compatible values") from exc
    if not isinstance(decoded, list):
        raise ValueError(f"{label} must be a JSON array")
    return cast(list[JsonValue], decoded)


def _require_payload_string(payload: Mapping[str, object], key: str) -> str:
    return _required_string(payload.get(key), label=f"payload.{key}")


def _require_payload_object(payload: Mapping[str, object], key: str) -> JsonObject:
    return _required_json_object(payload.get(key), label=f"payload.{key}")


def _require_payload_array(payload: Mapping[str, object], key: str) -> list[JsonValue]:
    return _required_json_array(payload.get(key), label=f"payload.{key}")


def _validate_council_payload(command: str, payload: Mapping[str, object]) -> None:
    _require_payload_string(payload, "command_id")
    if command == "council.new":
        _require_payload_string(payload, "moderator")
        _require_payload_array(payload, "members")
        _require_payload_string(payload, "title")
        surface_value = payload.get("surface")
        if surface_value is None:
            surface: Mapping[str, object] = {}
        elif isinstance(surface_value, Mapping):
            surface = require_json_object(surface_value, label="payload.surface")
        else:
            raise ValueError("payload.surface must be a JSON object")
        _require_payload_string(payload, "event_id")
        _validate_council_new_output_intent(payload, surface=surface)
        return
    _require_payload_string(payload, "actor")
    command_payload = _require_payload_object(payload, "payload")
    _validate_turn_bearing_payload(command, command_payload)
    if command == schemas.COUNCIL_SPEAK_COMMAND:
        _validate_argue_speech_payload(command_payload, label="payload")
    elif command == schemas.COUNCIL_HAND_RAISE_COMMAND:
        _validate_argue_hand_raise_payload(command_payload, label="payload")
    elif command == schemas.COUNCIL_DROP_COMMAND:
        _validate_council_drop_payload(command_payload)


def _validate_turn_bearing_payload(command: str, payload: Mapping[str, object]) -> None:
    if command not in TURN_BEARING_COUNCIL_COMMANDS:
        return
    if "round" in payload:
        raise ValueError(
            "payload.payload.round is unsupported for turn-bearing council commands; "
            "use payload.payload.turn"
        )
    turn = payload.get("turn")
    if turn is None:
        raise ValueError("payload.payload.turn is required for turn-bearing council commands")
    if isinstance(turn, bool) or not isinstance(turn, int | str) or turn == "":
        raise ValueError(
            "payload.payload.turn must be a non-empty string or integer for "
            "turn-bearing council commands"
        )


def _validate_council_drop_payload(payload: Mapping[str, object]) -> None:
    _required_string(payload.get("request_event_id"), label="payload.payload.request_event_id")
    _required_string(payload.get("reason"), label="payload.payload.reason")
    if _optional_bool(payload.get("auto")):
        raise ValueError(
            "payload.payload.auto=true is daemon-owned for timeout auto-drops; "
            "plugin/caller-submitted council.drop must be a manual drop with reason"
        )


def _validate_council_new_output_intent(
    payload: Mapping[str, object], *, surface: Mapping[str, object]
) -> None:
    context_value = payload.get("request_context")
    if context_value is None:
        context: Mapping[str, object] = {}
    elif isinstance(context_value, Mapping):
        context = context_value
    else:
        raise ValueError("payload.request_context must be a JSON object")

    requested_raw = _first_non_empty_string(
        payload.get("requested_output_mode"),
        payload.get("output_mode"),
        payload.get("requested_output"),
        context.get("requested_output_mode"),
        context.get("output_mode"),
        context.get("requested_output"),
    )
    _validate_council_new_intent_field_consistency(payload, context)
    requested_mode = _normalize_council_output_mode(requested_raw)
    if requested_raw.strip() and requested_mode is None:
        raise ValueError(
            "payload.request_context.requested_output_mode must be a supported council output mode"
        )
    visible_required = _optional_bool(payload.get("visible_output_required")) or _optional_bool(
        context.get("visible_output_required")
    )
    explicit_override = _optional_bool(
        payload.get("explicit_non_visible_override")
    ) or _optional_bool(context.get("explicit_non_visible_override"))
    override_reason = _first_non_empty_string(
        payload.get("override_reason"), context.get("override_reason")
    )
    non_visible_requested = requested_mode in {
        "artifact_only",
        "daemon_cli_actor_speech",
        "activation_planning_only",
    }
    override_complete = explicit_override and bool(override_reason.strip())
    if non_visible_requested and not override_complete:
        raise ValueError(
            "payload.request_context.explicit_non_visible_override requires "
            "override_reason for non-visible/local-daemon-only council.new"
        )
    if not requested_raw.strip():
        raise ValueError(
            "payload.request_context.requested_output_mode is required: use "
            "live_visible_thread with Discord surface, or supported non-visible/"
            "local-daemon-only mode with explicit override_reason"
        )
    if (
        requested_mode == "live_visible_thread"
        or visible_required
        or (not non_visible_requested and bool(surface))
    ):
        if surface.get("platform") != "discord":
            raise ValueError(
                "payload.surface.platform must be discord for live-visible council.new"
            )
        kind = surface.get("kind")
        if kind == "discord_thread" and not _first_non_empty_string(surface.get("thread_id")):
            raise ValueError("payload.surface.thread_id is required for discord_thread council.new")
        if kind in {"discord_channel", "discord_parent_channel"} and not _first_non_empty_string(
            surface.get("channel_id")
        ):
            raise ValueError(
                "payload.surface.channel_id is required for Discord channel fallback council.new"
            )
        if kind not in {"discord_thread", "discord_channel", "discord_parent_channel"}:
            raise ValueError(
                "payload.surface.kind must be discord_thread or approved Discord channel fallback"
            )


def _canonicalize_council_new_output_intent(payload: JsonObject) -> None:
    context_value = payload.get("request_context")
    if context_value is None:
        context: JsonObject = {}
    elif isinstance(context_value, Mapping):
        context = cast(JsonObject, dict(context_value))
    else:
        raise ValueError("payload.request_context must be a JSON object")

    requested_raw = _first_non_empty_string(
        payload.get("requested_output_mode"),
        payload.get("output_mode"),
        payload.get("requested_output"),
        context.get("requested_output_mode"),
        context.get("output_mode"),
        context.get("requested_output"),
    )
    if requested_raw:
        normalized = _normalize_council_output_mode(requested_raw)
        context["requested_output_mode"] = normalized if normalized is not None else requested_raw
    context.pop("output_mode", None)
    context.pop("requested_output", None)
    payload.pop("requested_output_mode", None)
    payload.pop("output_mode", None)
    payload.pop("requested_output", None)
    payload["request_context"] = context


def _first_non_empty_string(*values: object) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _validate_council_new_intent_field_consistency(
    payload: Mapping[str, object], context: Mapping[str, object]
) -> None:
    _validate_council_new_output_mode_alias_consistency(payload, context)
    for key in ("override_reason",):
        top = _first_non_empty_string(payload.get(key))
        nested = _first_non_empty_string(context.get(key))
        if top and nested and top != nested:
            raise ValueError(
                "payload.request_context output-intent fields must not conflict "
                "with top-level council.new fields"
            )
    for key in ("visible_output_required", "explicit_non_visible_override"):
        if key in payload and not isinstance(payload.get(key), bool):
            raise ValueError(
                "payload.request_context boolean output-intent fields must be true or false"
            )
        if key in context and not isinstance(context.get(key), bool):
            raise ValueError(
                "payload.request_context boolean output-intent fields must be true or false"
            )
        top_bool_present, top_bool = _optional_bool_present(payload.get(key))
        nested_bool_present, nested_bool = _optional_bool_present(context.get(key))
        if top_bool_present and nested_bool_present and top_bool != nested_bool:
            raise ValueError(
                "payload.request_context output-intent fields must not conflict "
                "with top-level council.new fields"
            )


def _validate_council_new_output_mode_alias_consistency(
    payload: Mapping[str, object], context: Mapping[str, object]
) -> None:
    seen: dict[str, str] = {}
    for value in (
        payload.get("requested_output_mode"),
        payload.get("output_mode"),
        payload.get("requested_output"),
        context.get("requested_output_mode"),
        context.get("output_mode"),
        context.get("requested_output"),
    ):
        raw = _first_non_empty_string(value)
        if not raw:
            continue
        normalized = _normalize_council_output_mode(raw) or raw
        seen[normalized] = raw
    if len(seen) > 1:
        raise ValueError(
            "payload.request_context output-mode aliases must not declare "
            "conflicting requested output modes"
        )


def _optional_bool(value: object) -> bool:
    return bool(value) if isinstance(value, bool) else False


def _optional_bool_present(value: object) -> tuple[bool, bool]:
    if isinstance(value, bool):
        return True, value
    return False, False


def _normalize_council_output_mode(mode: str) -> str | None:
    stripped = mode.strip()
    if not stripped:
        return ""
    if stripped in {
        "live_visible_thread",
        "artifact_only",
        "daemon_cli_actor_speech",
        "activation_planning_only",
    }:
        return stripped
    if stripped in {"transcript/export-only", "transcript_export_only"}:
        return "artifact_only"
    if stripped in {"local-daemon-only", "local_daemon_only"}:
        return "activation_planning_only"
    return None


def _selected_participant_argue_fields(participant_response: Mapping[str, object]) -> JsonObject:
    fields: dict[str, object] = {}
    non_evidence_argue_present = any(
        key in participant_response for key in ARGUE_SPEECH_PASSTHROUGH_FIELDS if key != "evidence"
    )
    for key in ARGUE_SPEECH_PASSTHROUGH_FIELDS:
        if key not in participant_response:
            continue
        if (
            key == "evidence"
            and not non_evidence_argue_present
            and not isinstance(participant_response[key], list)
        ):
            continue
        fields[key] = participant_response[key]
    if not fields:
        return {}
    try:
        validated = require_json_object(fields, label="participant_response ARGUE fields")
    except ProtocolValidationError as exc:
        raise ValueError(str(exc)) from exc
    _validate_argue_speech_payload(validated, label="participant_response")
    return validated


def _selected_participant_speech(participant_response: Mapping[str, object]) -> str:
    speech = _required_string(
        participant_response.get("message"), label="participant_response.message"
    )
    if not speech.strip():
        raise ValueError("participant_response.message must be a non-empty string")
    if _contains_runtime_noise(speech):
        raise ValueError("participant_response.message contains runtime/system noise")
    return speech


def _contains_runtime_noise(speech: str) -> bool:
    for line in speech.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if stripped.startswith(RUNTIME_NOISE_PREFIXES):
            return True
        if lowered.startswith(RUNTIME_NOISE_PREFIXES_LOWER):
            return True
    return False


def _caller_validation_context(
    value: object,
    *,
    selected_context: Mapping[str, object],
    selected_member: str,
) -> JsonObject:
    if value is None:
        return {}
    context = _required_json_object(value, label="caller_validation_context")
    unknown_keys = sorted(str(key) for key in context if key not in CALLER_VALIDATION_CONTEXT_KEYS)
    if unknown_keys:
        raise ValueError(f"unsupported caller_validation_context fields: {', '.join(unknown_keys)}")

    quality_mode = context.get("quality_mode")
    if quality_mode is not None:
        quality_mode_value = _required_string(
            quality_mode, label="caller_validation_context.quality_mode"
        )
        if quality_mode_value not in CALLER_VALIDATION_QUALITY_MODES:
            raise ValueError("caller_validation_context.quality_mode must be a supported mode")

    _optional_context_bool(context, "local_context_sufficient")
    _optional_context_bool(context, "is_opening_speech")
    _optional_context_match(
        context,
        "selected_member",
        selected_member,
        "selected_member",
    )
    _optional_context_match(
        context,
        "selected_event_id",
        cast(str, selected_context["event_id"]),
        "speaker_selected_frame.event.event_id",
    )
    _optional_context_match(
        context,
        "selected_cursor",
        cast(str, selected_context["cursor"]),
        "speaker_selected_frame.cursor",
    )
    if "prior_claims" in context:
        _caller_prior_claims(context["prior_claims"])
    return context


def _optional_context_bool(context: Mapping[str, object], key: str) -> None:
    if key in context and not isinstance(context[key], bool):
        raise ValueError(f"caller_validation_context.{key} must be a boolean when present")


def _optional_context_match(
    context: Mapping[str, object],
    key: str,
    expected: str,
    expected_label: str,
) -> None:
    if key not in context:
        return
    actual = _required_string(context[key], label=f"caller_validation_context.{key}")
    if actual != expected:
        raise ValueError(f"caller_validation_context.{key} must match {expected_label}")


def _validate_selected_participant_caller_context(
    context: Mapping[str, object],
    *,
    participant_argue_fields: Mapping[str, object],
) -> None:
    if not context:
        return

    prior_claims = _caller_prior_claims(context.get("prior_claims", []))
    local_context_sufficient = context.get("local_context_sufficient") is True
    quality_mode = context.get("quality_mode")
    valid_stance_links = 0
    if local_context_sufficient and quality_mode == "quality_required":
        valid_stance_links = _validate_stance_links_against_caller_context(
            participant_argue_fields,
            prior_claims=prior_claims,
        )

    if quality_mode != "quality_required":
        return
    if not local_context_sufficient or context.get("is_opening_speech") is True:
        return
    if valid_stance_links > 0 or _has_justified_new_axis(participant_argue_fields):
        return
    raise ValueError(
        "participant_response is orphan speech in quality_required caller_validation_context"
    )


def _has_justified_new_axis(participant_argue_fields: Mapping[str, object]) -> bool:
    return participant_argue_fields.get("contribution_type") == "new_axis" and _non_empty_string(
        participant_argue_fields.get("new_axis_reason")
    )


def _caller_prior_claims(value: object) -> dict[str, set[str]]:
    prior_claim_items = _required_json_array(value, label="caller_validation_context.prior_claims")
    prior_claims: dict[str, set[str]] = {}
    for index, item in enumerate(prior_claim_items):
        label = f"caller_validation_context.prior_claims[{index}]"
        if not isinstance(item, Mapping):
            raise ValueError(f"{label} must be a JSON object")
        prior_claim = _required_json_object(item, label=label)
        event_id = _required_string(prior_claim.get("event_id"), label=f"{label}.event_id")
        claim_ids = prior_claims.setdefault(event_id, set())
        claim_id = prior_claim.get("claim_id")
        if claim_id is not None:
            claim_ids.add(_required_string(claim_id, label=f"{label}.claim_id"))
    return prior_claims


def _validate_stance_links_against_caller_context(
    participant_argue_fields: Mapping[str, object],
    *,
    prior_claims: Mapping[str, set[str]],
) -> int:
    stance_links = participant_argue_fields.get("stance_links")
    if not isinstance(stance_links, list):
        return 0
    valid_links = 0
    for index, item in enumerate(stance_links):
        label = f"participant_response.stance_links[{index}]"
        if not isinstance(item, Mapping):
            raise ValueError(f"{label} must be a JSON object")
        link = _required_json_object(item, label=label)
        target_event_id = _required_string(
            link.get("target_event_id"), label=f"{label}.target_event_id"
        )
        if target_event_id not in prior_claims:
            raise ValueError(
                f"{label}.target_event_id is not in caller_validation_context.prior_claims"
            )
        target_claim_ids = prior_claims[target_event_id]
        if not target_claim_ids:
            valid_links += 1
            continue
        target_claim_id = link.get("target_claim_id")
        if target_claim_id is None:
            raise ValueError(
                f"{label}.target_claim_id is required by caller_validation_context.prior_claims"
            )
        target_claim_id_value = _required_string(target_claim_id, label=f"{label}.target_claim_id")
        if target_claim_id_value not in target_claim_ids:
            raise ValueError(
                f"{label}.target_claim_id is not in caller_validation_context.prior_claims"
            )
        valid_links += 1
    return valid_links


def _validate_argue_speech_payload(payload: Mapping[str, object], *, label: str) -> None:
    has_argue_fields = any(
        key in payload for key in ARGUE_SPEECH_PASSTHROUGH_FIELDS if key != "evidence"
    )
    if "claims" in payload:
        _validate_argue_claims(payload["claims"], label=f"{label}.claims")
    if "stance_links" in payload:
        _validate_argue_stance_links(payload["stance_links"], label=f"{label}.stance_links")
    if "contribution_type" in payload:
        contribution_type = _required_string(
            payload["contribution_type"], label=f"{label}.contribution_type"
        )
        if contribution_type not in schemas.ARGUE_CONTRIBUTION_TYPES:
            raise ValueError(f"{label}.contribution_type must be an ARGUE contribution type")
        if contribution_type == "new_axis":
            _required_string(payload.get("new_axis_reason"), label=f"{label}.new_axis_reason")
        if contribution_type == "synthesize":
            stance_links = payload.get("stance_links")
            if not isinstance(stance_links, list) or len(stance_links) < 2:
                raise ValueError(
                    f"{label}.stance_links must include at least two links for synthesize"
                )
    if "new_axis_reason" in payload and payload["new_axis_reason"] is not None:
        _required_string(payload["new_axis_reason"], label=f"{label}.new_axis_reason")
    if "evidence" in payload and (has_argue_fields or isinstance(payload["evidence"], list)):
        _required_json_array(payload["evidence"], label=f"{label}.evidence")
    if "responds_to_event_id" in payload:
        # Compatibility display hint only. It is validated as a string but never
        # used to infer, rewrite, or override stance_links.
        _required_string(payload["responds_to_event_id"], label=f"{label}.responds_to_event_id")


def _validate_argue_hand_raise_payload(payload: Mapping[str, object], *, label: str) -> None:
    if not _non_empty_string(payload.get("intent")) and not _non_empty_string(
        payload.get("reason")
    ):
        raise ValueError(f"{label}.intent or reason is required for council.hand_raise")
    if "target_links" in payload:
        _validate_argue_stance_links(payload["target_links"], label=f"{label}.target_links")
    if "target_event_ids" in payload:
        _validate_string_array(payload["target_event_ids"], label=f"{label}.target_event_ids")
    if "target_claim_ids" in payload:
        _validate_string_array(payload["target_claim_ids"], label=f"{label}.target_claim_ids")


def _validate_argue_claims(value: object, *, label: str) -> None:
    claims = _required_json_array(value, label=label)
    claim_ids: set[str] = set()
    for index, item in enumerate(claims):
        claim_label = f"{label}[{index}]"
        if not isinstance(item, Mapping):
            raise ValueError(f"{claim_label} must be a JSON object")
        claim = _required_json_object(item, label=claim_label)
        claim_id = _required_string(claim.get("claim_id"), label=f"{claim_label}.claim_id")
        if claim_id in claim_ids:
            raise ValueError(f"{label} claim_id entries must be unique within a speech")
        claim_ids.add(claim_id)
        _required_string(claim.get("summary"), label=f"{claim_label}.summary")
        kind = claim.get("kind")
        if kind is not None:
            kind_value = _required_string(kind, label=f"{claim_label}.kind")
            if kind_value not in schemas.ARGUE_CLAIM_KINDS:
                raise ValueError(f"{claim_label}.kind must be an ARGUE claim kind")


def _validate_argue_stance_links(value: object, *, label: str) -> None:
    links = _required_json_array(value, label=label)
    for index, item in enumerate(links):
        link_label = f"{label}[{index}]"
        if not isinstance(item, Mapping):
            raise ValueError(f"{link_label} must be a JSON object")
        link = _required_json_object(item, label=link_label)
        _required_string(link.get("target_event_id"), label=f"{link_label}.target_event_id")
        target_claim_id = link.get("target_claim_id")
        if target_claim_id is not None:
            _required_string(target_claim_id, label=f"{link_label}.target_claim_id")
        stance = _required_string(link.get("stance"), label=f"{link_label}.stance")
        if stance not in schemas.ARGUE_STANCES:
            raise ValueError(f"{link_label}.stance must be an ARGUE stance")
        rationale = link.get("rationale")
        if rationale is not None:
            _required_string(rationale, label=f"{link_label}.rationale")


def _validate_string_array(value: object, *, label: str) -> None:
    items = _required_json_array(value, label=label)
    for index, item in enumerate(items):
        _required_string(item, label=f"{label}[{index}]")


def _validate_delivery_evidence_payload(command: str, payload: Mapping[str, object]) -> None:
    _require_payload_string(payload, "escalation")
    _require_payload_string(payload, "command_id")
    if command == "delegate.escalation_delivered":
        _require_payload_string(payload, "delivery_target")
        _require_payload_string(payload, "platform")
        _optional_string(payload.get("message_ref"), label="payload.message_ref")
        _optional_string(payload.get("reporter"), label="payload.reporter")
        return
    _require_payload_string(payload, "target")
    _require_payload_string(payload, "reason")
    _require_payload_array(payload, "will_retry_targets")
    _optional_string(payload.get("reporter"), label="payload.reporter")


def _selected_context(
    *,
    session_id: str,
    frame: Mapping[str, object],
    selected_member: str,
    participant_response: Mapping[str, object],
) -> JsonObject:
    if participant_response.get("role_substitution") is not False:
        raise ValueError("participant_response.role_substitution must be false")
    response_member = _required_string(
        participant_response.get("member"), label="participant_response.member"
    )
    if response_member != selected_member:
        raise ValueError("participant_response.member must match selected_member")

    event = _required_json_object(frame.get("event"), label="speaker_selected_frame.event")
    if event.get("type") != "speaker_selected":
        raise ValueError("speaker_selected_frame.event.type must be speaker_selected")
    if event.get("session_id") != session_id:
        raise ValueError("speaker_selected_frame.event.session_id must match session_id")
    event_payload = _required_json_object(
        event.get("payload"), label="speaker_selected_frame.event.payload"
    )
    recipients = event.get("to")
    if not isinstance(recipients, list) or len(recipients) != 1 or recipients[0] != selected_member:
        raise ValueError("speaker_selected_frame.event.to must select exactly selected_member")
    payload_member = event_payload.get("member")
    if payload_member is not None and payload_member != selected_member:
        raise ValueError("speaker_selected_frame.event.payload.member must match selected_member")
    return {
        "cursor": _required_string(frame.get("cursor"), label="speaker_selected_frame.cursor"),
        "event_id": _required_string(
            event.get("event_id"), label="speaker_selected_frame.event.event_id"
        ),
        "turn": event_payload.get("turn"),
    }


def _participant_response_evidence(
    *,
    participant_response: Mapping[str, object],
    speaker_selected_event_id: str,
    speaker_selected_cursor: str,
) -> JsonObject:
    source = _required_string(
        participant_response.get("source"), label="participant_response.source"
    )
    if source != "control_membr_evidence":
        raise ValueError("participant_response.source must be control_membr_evidence")
    runner = _required_json_object(
        participant_response.get("runner"), label="participant_response.runner"
    )
    adapter_kind = _required_string(
        runner.get("adapter_kind"), label="participant_response.runner.adapter_kind"
    )
    if adapter_kind != "hermes-agent":
        raise ValueError("participant_response.runner.adapter_kind must be hermes-agent")
    terminal_event_type = _required_string(
        runner.get("terminal_event_type"),
        label="participant_response.runner.terminal_event_type",
    )
    if terminal_event_type != "participant_response":
        raise ValueError(
            "participant_response.runner.terminal_event_type must be participant_response"
        )
    return {
        "source": source,
        "speaker_selected_event_id": speaker_selected_event_id,
        "speaker_selected_cursor": speaker_selected_cursor,
        "runner_invocation_id": _required_string(
            runner.get("invocation_id"), label="participant_response.runner.invocation_id"
        ),
        "runner_started_event_id": _required_string(
            runner.get("started_event_id"), label="participant_response.runner.started_event_id"
        ),
        "runner_terminal_event_id": _required_string(
            runner.get("terminal_event_id"), label="participant_response.runner.terminal_event_id"
        ),
        "runner_terminal_event_type": terminal_event_type,
        "adapter_kind": adapter_kind,
        "wrapper_binding_evidence": _required_string(
            runner.get("wrapper_binding_evidence"),
            label="participant_response.runner.wrapper_binding_evidence",
        ),
        "no_role_substitution": True,
        "real_profile_live_invocation": False,
    }


def _optional_limit(value: object) -> int:
    if value is None:
        return 100
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("limit must be an integer when present")
    if value < 1 or value > STREAM_TAIL_FRAME_LIMIT:
        raise ValueError(f"limit must be between 1 and {STREAM_TAIL_FRAME_LIMIT}")
    return value


def _require_client(client_factory: ClientFactory | None) -> DaemonClient:
    if client_factory is None:
        raise DaemonTransportError(
            "explicit daemon client factory is required; no live daemon/Hermes/Discord fallback"
        )
    return client_factory()


def _failing_client_factory(exc: DaemonTransportError) -> ClientFactory:
    def factory() -> DaemonClient:
        raise exc

    return factory


def _submit_command(
    *,
    tool: str,
    client_factory: ClientFactory | None,
    command: str,
    payload: JsonObject,
    request_id: str,
    idempotency_key: str,
) -> str:
    client = _require_client(client_factory)
    envelope = client.build_command_envelope(
        command=command,
        payload=payload,
        request_id=request_id,
        idempotency_key=idempotency_key,
    )
    return _json_command_success(tool, client.submit_command(envelope))


def _submit_feature_gated_command(
    *,
    tool: str,
    client_factory: ClientFactory | None,
    required_feature_groups: tuple[str, ...],
    command: str,
    payload: JsonObject,
    request_id: str,
    idempotency_key: str,
) -> str:
    client = _require_client(client_factory)
    client.require_feature_groups(required_feature_groups)
    envelope = client.build_command_envelope(
        command=command,
        payload=payload,
        request_id=request_id,
        idempotency_key=idempotency_key,
    )
    return _json_command_success(tool, client.submit_command(envelope))


def _status_data(status: DaemonStatus) -> JsonObject:
    return {
        "daemon_version": status.daemon_version,
        "status": status.status,
        "feature_groups": list(status.feature_groups),
    }


def _diagnostics_data(diagnostics: DaemonDiagnostics) -> JsonObject:
    return {
        "daemon_version": diagnostics.daemon_version,
        "checks": [_diagnostic_check_data(check) for check in diagnostics.checks],
    }


def _diagnostic_check_data(check: DiagnosticCheck) -> JsonObject:
    return {
        "name": check.name,
        "ok": check.ok,
        "message": check.message,
        "details": check.details,
        "error": check.error.to_mapping() if isinstance(check.error, DaemonErrorDetails) else None,
    }


def _stream_tail_data(stream_tail: StreamTail) -> JsonObject:
    return {
        "frames": [_stream_frame_data(frame) for frame in stream_tail.frames],
        "next_cursor": stream_tail.next_cursor,
    }


def _stream_frame_data(frame: StreamFrame) -> JsonObject:
    return {
        "cursor": frame.cursor,
        "is_replay": frame.is_replay,
        "sequence": frame.sequence,
        "schema_version": frame.schema_version,
        "event": _stream_event_data(frame.event),
    }


def _stream_event_data(event: StreamEvent) -> JsonObject:
    payload = redact_sensitive(event.payload)
    details = redact_sensitive(event.details) if event.details is not None else None
    return {
        "schema_version": event.schema_version,
        "event_id": event.event_id,
        "session_id": event.session_id,
        "type": event.type,
        "from": event.sender,
        "to": list(event.recipients),
        "payload": cast(JsonObject, payload),
        "details": cast(JsonObject | None, details),
    }


def _json_success(tool: str, source: DaemonStatus | DaemonDiagnostics, data: JsonObject) -> str:
    return _dumps(
        {
            "ok": True,
            "tool": tool,
            "protocol_version": source.protocol_version,
            "live_readiness": source.live_readiness,
            "data": data,
        }
    )


def _json_stream_success(tool: str, source: StreamTail, data: JsonObject) -> str:
    return _dumps(
        {
            "ok": True,
            "tool": tool,
            "protocol_version": source.protocol_version,
            # StreamTail carries no live-readiness field in the current fake/injected-only
            # contract. Future live daemon support must source this from version.read.
            "live_readiness": False,
            "data": data,
        }
    )


def _json_command_success(tool: str, result: CommandResult) -> str:
    data = _command_result_data(result)
    return _dumps(
        {
            "ok": True,
            "tool": tool,
            "live_readiness": False,
            "data": data,
        }
    )


def _command_result_data(result: CommandResult) -> JsonObject:
    data: JsonObject = {"command_id": result.command_id}
    if result.event_id is not None:
        data["event_id"] = result.event_id
    if result.session_id is not None:
        data["session_id"] = result.session_id
    if result.request_id is not None:
        data["request_id"] = result.request_id
    if result.deduplicated is not None:
        data["deduplicated"] = result.deduplicated
    return data


def _json_selected_participant_response_success(
    *,
    tool: str,
    selected_member: str,
    speaker_selected_event_id: str,
    speaker_selected_cursor: str,
    speak_result: CommandResult,
    ack_result: CommandResult,
    participant_response: Mapping[str, object],
) -> str:
    runner = _required_json_object(
        participant_response.get("runner"), label="participant_response.runner"
    )
    return _dumps(
        {
            "ok": True,
            "tool": tool,
            "live_readiness": False,
            "data": {
                "selected_member": selected_member,
                "speaker_selected_event_id": speaker_selected_event_id,
                "speaker_selected_cursor": speaker_selected_cursor,
                "speak": _command_result_data(speak_result),
                "ack": _command_result_data(ack_result),
                "proof": {
                    "source": _required_string(
                        participant_response.get("source"), label="participant_response.source"
                    ),
                    "runner_invocation_id": _required_string(
                        runner.get("invocation_id"),
                        label="participant_response.runner.invocation_id",
                    ),
                    "runner_terminal_event_id": _required_string(
                        runner.get("terminal_event_id"),
                        label="participant_response.runner.terminal_event_id",
                    ),
                    "no_role_substitution": True,
                    "real_profile_live_invocation": False,
                },
            },
        }
    )


def _json_discord_success(tool: str, result: DiscordMessageResult) -> str:
    return _dumps(
        {
            "ok": True,
            "tool": tool,
            "live_readiness": False,
            "data": result.to_mapping(),
        }
    )


def _json_surface_projection_success(tool: str, data: JsonObject) -> str:
    return _dumps(
        {
            "ok": True,
            "tool": tool,
            "live_readiness": False,
            "data": {"local_projection": data},
        }
    )


def _json_activation_plan(tool: str, *, ok: bool, data: JsonObject) -> str:
    return _dumps(
        {
            "ok": ok,
            "tool": tool,
            "live_readiness": False,
            "data": data,
        }
    )


def _json_error(tool: str, exc: Exception) -> str:
    live_readiness = False
    return _dumps(
        {
            "ok": False,
            "tool": tool,
            "live_readiness": live_readiness,
            "error": _error_data(exc),
        }
    )


def _error_data(exc: Exception) -> JsonObject:
    if isinstance(exc, DaemonCommandError | DaemonStreamError):
        return exc.details.to_mapping()
    if isinstance(exc, DaemonCompatibilityError):
        return _simple_error("compatibility", str(exc))
    if isinstance(exc, DaemonProtocolError):
        return _simple_error("protocol", str(exc))
    if isinstance(exc, DaemonTransportError):
        return _simple_error("unavailable", str(exc))
    if isinstance(exc, ValueError):
        return _simple_error("validation", str(exc))
    return _simple_error("internal", "internal plugin handler error")


def _simple_error(category: str, message: str) -> JsonObject:
    redacted = redact_sensitive(message)
    if not isinstance(redacted, str):
        redacted = "handler error"
    return {"category": category, "message": redacted, "retryable": False}


def _dumps(value: Mapping[str, JsonValue]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


__all__ = [
    "TOOLSET",
    "handle_council_command",
    "handle_compatibility_diagnostics",
    "handle_daemon_status",
    "handle_delegate_action",
    "handle_delegate_new",
    "handle_delivery_evidence",
    "handle_discussion_activation_plan",
    "handle_discord_send_message",
    "handle_selected_participant_response",
    "handle_surface_render_projection",
    "handle_stream_ack",
    "handle_stream_tail",
    "register_tools",
]
