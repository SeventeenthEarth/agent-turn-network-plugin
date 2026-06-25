"""Fail-closed stream frame parsing for fake/injected DAEMN-2 clients."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import cast

from ..errors import (
    DaemonProtocolError,
    DaemonStreamError,
    decode_daemon_error,
)
from ..protocol import (
    STREAM_EVENT_SCHEMA_VERSION,
    STREAM_FRAME_SCHEMA_VERSION,
    STREAM_TAIL_FRAME_LIMIT,
    SUPPORTED_PROTOCOL_VERSION,
    JsonObject,
    ProtocolValidationError,
    StreamEvent,
    StreamFrame,
    StreamTail,
    require_json_object,
)


def parse_stream_frame(value: Mapping[str, object] | str) -> StreamFrame:
    """Parse one mapping or NDJSON line as a stream event frame.

    Explicit error frames are structured daemon failures and raise
    :class:`DaemonStreamError`; malformed data raises :class:`DaemonProtocolError`.
    """

    frame = _coerce_object(value, label="stream frame")
    kind = _frame_kind(frame)
    if kind == "error":
        raw_error = frame.get("error")
        if not isinstance(raw_error, Mapping):
            raise DaemonProtocolError("stream error frame missing structured error object")
        raise DaemonStreamError(decode_daemon_error(raw_error))

    schema_version = _optional_supported_schema_version(frame.get("schema_version"))
    return StreamFrame(
        cursor=_require_string(frame.get("cursor"), label="stream frame cursor"),
        is_replay=_require_bool(frame.get("is_replay"), label="stream frame is_replay"),
        event=_parse_event(frame.get("event")),
        sequence=_optional_sequence(frame.get("sequence")),
        schema_version=schema_version,
    )


def parse_stream_frames_ndjson(value: str) -> tuple[StreamFrame, ...]:
    """Parse newline-delimited JSON stream frames."""

    frames: list[StreamFrame] = []
    for line_number, line in enumerate(value.splitlines(), start=1):
        if not line.strip():
            raise DaemonProtocolError(f"stream NDJSON line {line_number} is empty")
        try:
            frames.append(parse_stream_frame(line))
        except DaemonStreamError:
            raise
        except DaemonProtocolError as exc:
            raise DaemonProtocolError(f"stream NDJSON line {line_number}: {exc}") from exc
    return tuple(frames)


def parse_stream_tail_response(value: Mapping[str, object] | str) -> StreamTail:
    """Parse a fake/injected transport stream tail response."""

    response = _coerce_object(value, label="stream tail response")
    protocol_version = _require_string(
        response.get("protocol_version"), label="stream tail protocol_version"
    )
    if protocol_version != SUPPORTED_PROTOCOL_VERSION:
        raise DaemonProtocolError(
            f"unsupported stream tail protocol: {protocol_version} != {SUPPORTED_PROTOCOL_VERSION}"
        )

    raw_frames = response.get("frames")
    if not isinstance(raw_frames, list):
        raise DaemonProtocolError("stream tail frames must be a list")
    if len(raw_frames) > STREAM_TAIL_FRAME_LIMIT:
        raise DaemonProtocolError(
            f"stream tail frames exceeds limit: {len(raw_frames)} > {STREAM_TAIL_FRAME_LIMIT}"
        )

    frames: list[StreamFrame] = []
    for index, raw_frame in enumerate(raw_frames):
        if not isinstance(raw_frame, (Mapping, str)):
            raise DaemonProtocolError(f"stream tail frame {index} must be an object or NDJSON line")
        try:
            frames.append(parse_stream_frame(raw_frame))
        except DaemonStreamError:
            raise
        except DaemonProtocolError as exc:
            raise DaemonProtocolError(f"stream tail frame {index}: {exc}") from exc

    return StreamTail(
        protocol_version=protocol_version,
        frames=tuple(frames),
        next_cursor=_optional_string(response.get("next_cursor"), label="stream tail next_cursor"),
    )


def _coerce_object(value: Mapping[str, object] | str, *, label: str) -> JsonObject:
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as exc:
            raise DaemonProtocolError(f"{label} must be valid JSON") from exc
        if not isinstance(decoded, dict):
            raise DaemonProtocolError(f"{label} JSON root must be an object")
        value = cast(Mapping[str, object], decoded)
    if not isinstance(value, Mapping):
        raise DaemonProtocolError(f"{label} must be an object")
    try:
        return require_json_object(value, label=label)
    except ProtocolValidationError as exc:
        raise DaemonProtocolError(str(exc)) from exc


def _frame_kind(frame: Mapping[str, object]) -> str:
    raw_kind = frame.get("kind")
    if raw_kind is None:
        if "event" in frame:
            return "event"
        raise DaemonProtocolError("stream frame missing event")
    if not isinstance(raw_kind, str) or not raw_kind:
        raise DaemonProtocolError("stream frame kind must be a non-empty string when present")
    if raw_kind not in {"event", "error"}:
        raise DaemonProtocolError(f"unsupported stream frame kind: {raw_kind}")
    return raw_kind


def _parse_event(raw_event: object) -> StreamEvent:
    if not isinstance(raw_event, Mapping):
        raise DaemonProtocolError("stream frame event must be an object")
    try:
        event = require_json_object(raw_event, label="stream event")
    except ProtocolValidationError as exc:
        raise DaemonProtocolError(str(exc)) from exc

    schema_version = _required_supported_schema_version(event.get("schema_version"))
    raw_payload = event.get("payload")
    if not isinstance(raw_payload, Mapping):
        raise DaemonProtocolError("stream event payload must be an object")
    try:
        payload = require_json_object(raw_payload, label="stream event payload")
    except ProtocolValidationError as exc:
        raise DaemonProtocolError(str(exc)) from exc

    details: JsonObject | None = None
    raw_details = event.get("details")
    if raw_details is not None:
        if not isinstance(raw_details, Mapping):
            raise DaemonProtocolError("stream event details must be an object when present")
        try:
            details = require_json_object(raw_details, label="stream event details")
        except ProtocolValidationError as exc:
            raise DaemonProtocolError(str(exc)) from exc

    return StreamEvent(
        schema_version=schema_version,
        event_id=_require_string(event.get("event_id"), label="stream event event_id"),
        session_id=_require_string(event.get("session_id"), label="stream event session_id"),
        type=_require_string(event.get("type"), label="stream event type"),
        sender=_require_string(event.get("from"), label="stream event from"),
        recipients=_recipients(event.get("to")),
        payload=payload,
        details=details,
    )


def _recipients(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise DaemonProtocolError("stream event to must be a list")
    recipients: list[str] = []
    for item in value:
        recipients.append(_require_string(item, label="stream event to entry"))
    return tuple(recipients)


def _required_supported_schema_version(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DaemonProtocolError("stream event schema_version must be an integer")
    if value != STREAM_EVENT_SCHEMA_VERSION:
        raise DaemonProtocolError(
            f"unsupported stream event schema_version: {value} != {STREAM_EVENT_SCHEMA_VERSION}"
        )
    return value


def _optional_supported_schema_version(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise DaemonProtocolError("stream frame schema_version must be an integer when present")
    if value != STREAM_FRAME_SCHEMA_VERSION:
        raise DaemonProtocolError(
            f"unsupported stream frame schema_version: {value} != {STREAM_FRAME_SCHEMA_VERSION}"
        )
    return value


def _optional_sequence(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise DaemonProtocolError(
            "stream frame sequence must be a non-negative integer when present"
        )
    return value


def _require_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise DaemonProtocolError(f"{label} must be a non-empty string")
    return value


def _optional_string(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, label=label)


def _require_bool(value: object, *, label: str) -> bool:
    if not isinstance(value, bool):
        raise DaemonProtocolError(f"{label} must be a boolean")
    return value


__all__ = ["parse_stream_frame", "parse_stream_frames_ndjson", "parse_stream_tail_response"]
