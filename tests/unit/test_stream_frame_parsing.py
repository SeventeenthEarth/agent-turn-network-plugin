from __future__ import annotations

import json
from collections.abc import Callable
from copy import deepcopy
from typing import cast

import pytest

from kkachi_agent_network_plugin.client.stream import (
    parse_stream_frame,
    parse_stream_frames_ndjson,
    parse_stream_tail_response,
)
from kkachi_agent_network_plugin.errors import (
    DaemonProtocolError,
    DaemonStreamError,
)
from kkachi_agent_network_plugin.protocol import STREAM_TAIL_FRAME_LIMIT, JsonObject


def valid_frame() -> JsonObject:
    return {
        "cursor": "cur_000000000012_evt_01HV",
        "is_replay": False,
        "event": {
            "schema_version": 1,
            "event_id": "evt_01HV",
            "session_id": "sess_1",
            "type": "hand_raise_requested",
            "from": "agent-mod",
            "to": ["agent-1", "agent-2"],
            "payload": {"turn": 5},
        },
    }


def test_stream_frame_mapping_without_kind_parses_core_compatible_shape() -> None:
    frame = parse_stream_frame(valid_frame())

    assert frame.cursor == "cur_000000000012_evt_01HV"
    assert frame.is_replay is False
    assert frame.sequence is None
    assert frame.event.event_id == "evt_01HV"
    assert frame.event.sender == "agent-mod"
    assert frame.event.recipients == ("agent-1", "agent-2")
    assert frame.event.payload == {"turn": 5}


def test_stream_frame_ndjson_line_with_explicit_event_kind_parses() -> None:
    raw = valid_frame()
    raw["kind"] = "event"
    raw["sequence"] = 7

    frame = parse_stream_frame(json.dumps(raw))

    assert frame.sequence == 7
    assert frame.event.session_id == "sess_1"


def test_stream_frames_ndjson_parses_multiple_lines() -> None:
    first = valid_frame()
    second = valid_frame()
    second["cursor"] = "cur_000000000013_evt_01HW"
    second["is_replay"] = True

    frames = parse_stream_frames_ndjson(f"{json.dumps(first)}\n{json.dumps(second)}")

    assert [frame.cursor for frame in frames] == [
        "cur_000000000012_evt_01HV",
        "cur_000000000013_evt_01HW",
    ]
    assert frames[1].is_replay is True


def test_stream_frames_ndjson_empty_string_returns_no_frames() -> None:
    assert parse_stream_frames_ndjson("") == ()


def test_stream_error_frame_raises_structured_redacted_error() -> None:
    with pytest.raises(DaemonStreamError) as exc_info:
        parse_stream_frame(
            {
                "kind": "error",
                "error": {
                    "category": "unavailable",
                    "message": "stream cursor gap",
                    "event_id": "evt-gap",
                    "session_id": "sess_1",
                    "retryable": True,
                    "diagnostics": {"gateway_token": "do-not-leak"},
                },
            }
        )

    details = exc_info.value.details
    assert details.category == "unavailable"
    assert details.event_id == "evt-gap"
    assert details.session_id == "sess_1"
    assert details.retryable is True
    assert details.diagnostics == {"gateway_token": "[REDACTED]"}


@pytest.mark.parametrize(
    "raw",
    [
        "{not-json",
        "[]",
        {**valid_frame(), "kind": "mystery"},
        {**valid_frame(), "kind": ""},
        {key: value for key, value in valid_frame().items() if key != "cursor"},
        {**valid_frame(), "cursor": ""},
        {key: value for key, value in valid_frame().items() if key != "is_replay"},
        {**valid_frame(), "is_replay": "false"},
        {key: value for key, value in valid_frame().items() if key != "event"},
        {**valid_frame(), "event": "not-object"},
        {**valid_frame(), "schema_version": 2},
        {**valid_frame(), "schema_version": True},
        {**valid_frame(), "sequence": True},
        {**valid_frame(), "sequence": -1},
    ],
)
def test_malformed_stream_frame_roots_fail_closed(raw: JsonObject | str) -> None:
    with pytest.raises(DaemonProtocolError):
        parse_stream_frame(raw)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda event: event.pop("schema_version"),
        lambda event: event.update({"schema_version": 2}),
        lambda event: event.update({"schema_version": True}),
        lambda event: event.update({"event_id": ""}),
        lambda event: event.update({"session_id": ""}),
        lambda event: event.update({"type": ""}),
        lambda event: event.update({"from": ""}),
        lambda event: event.pop("to"),
        lambda event: event.update({"to": "agent-1"}),
        lambda event: event.update({"to": ["agent-1", ""]}),
        lambda event: event.pop("payload"),
        lambda event: event.update({"payload": ["not-object"]}),
        lambda event: event.update({"details": ["not-object"]}),
    ],
)
def test_malformed_stream_event_fields_fail_closed(
    mutator: Callable[[dict[str, object]], object],
) -> None:
    raw = valid_frame()
    event = cast(dict[str, object], raw["event"])
    mutator(event)

    with pytest.raises(DaemonProtocolError):
        parse_stream_frame(raw)


def test_stream_tail_response_parses_frames_and_next_cursor() -> None:
    response = {
        "protocol_version": "kan-protocol-v1alpha0",
        "frames": [valid_frame(), json.dumps(valid_frame())],
        "next_cursor": "cur_next",
    }

    tail = parse_stream_tail_response(response)

    assert tail.protocol_version == "kan-protocol-v1alpha0"
    assert len(tail.frames) == 2
    assert tail.next_cursor == "cur_next"


def test_stream_tail_response_allows_empty_frames() -> None:
    tail = parse_stream_tail_response({"protocol_version": "kan-protocol-v1alpha0", "frames": []})

    assert tail.frames == ()


@pytest.mark.parametrize(
    "response",
    [
        "{not-json",
        [],
        {"protocol_version": "wrong", "frames": []},
        {"protocol_version": "kan-protocol-v1alpha0"},
        {"protocol_version": "kan-protocol-v1alpha0", "frames": "not-list"},
        {"protocol_version": "kan-protocol-v1alpha0", "frames": ["[]"]},
        {"protocol_version": "kan-protocol-v1alpha0", "frames": [], "next_cursor": ""},
    ],
)
def test_malformed_stream_tail_response_fails_closed(response: object) -> None:
    with pytest.raises(DaemonProtocolError):
        parse_stream_tail_response(response)  # type: ignore[arg-type]


def test_oversized_stream_tail_frames_array_fails_closed() -> None:
    frame = valid_frame()
    response = {
        "protocol_version": "kan-protocol-v1alpha0",
        "frames": [deepcopy(frame) for _ in range(STREAM_TAIL_FRAME_LIMIT + 1)],
    }

    with pytest.raises(DaemonProtocolError, match="exceeds limit"):
        parse_stream_tail_response(response)
