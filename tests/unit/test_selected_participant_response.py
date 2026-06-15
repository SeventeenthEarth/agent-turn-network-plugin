from __future__ import annotations

import copy
import json
from collections.abc import Callable
from typing import Any, cast

import pytest

from kkachi_agent_network_plugin.client import DaemonClient, StaticDaemonTransport
from kkachi_agent_network_plugin.client.daemon import (
    OP_COMMAND_SUBMIT,
    OP_STREAM_ACK,
    OP_VERSION_READ,
)
from kkachi_agent_network_plugin.protocol import JsonObject
from kkachi_agent_network_plugin.tools import handle_selected_participant_response

BASE_VERSION_WITH_PARTC: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": [
        "version.read",
        "command_envelope",
        "structured_error",
        "council.lifecycle",
        "stream_frame",
        "stream.ack",
    ],
    "live_readiness": False,
}
BASE_COMMAND_SUCCESS: JsonObject = {
    "ok": True,
    "command_id": "cmd-speak-1",
    "event_id": "evt-speak-1",
    "session_id": "sess-partc",
    "request_id": "req-speak-1",
}
BASE_ACK_SUCCESS: JsonObject = {
    "ok": True,
    "command_id": "cmd-ack-1",
    "event_id": "evt-ack-1",
    "session_id": "sess-partc",
    "request_id": "plugin-live-stream-ack",
    "deduplicated": False,
}
SPEAKER_SELECTED_FRAME: JsonObject = {
    "cursor": "cur_000000000042_evt_selected",
    "is_replay": False,
    "sequence": 42,
    "schema_version": 1,
    "event": {
        "schema_version": 1,
        "event_id": "evt-selected",
        "command_id": "cmd-grant-1",
        "session_id": "sess-partc",
        "type": "speaker_selected",
        "from": "agent-mod",
        "to": ["kas"],
        "payload": {"turn": 3, "member": "kas"},
    },
}
PARTICIPANT_RESPONSE: JsonObject = {
    "source": "control_membr_evidence",
    "member": "kas",
    "message": "KAS bounded participant response from wrapper evidence.",
    "role_substitution": False,
    "runner": {
        "invocation_id": "run_cmd-grant-1_1",
        "started_event_id": "evt-run-started",
        "terminal_event_id": "evt-run-terminal",
        "terminal_event_type": "participant_response",
        "adapter_kind": "hermes-agent",
        "wrapper_binding_evidence": "redacted_wrapper_binding",
    },
}


def factory_for_transport(transport: StaticDaemonTransport) -> Callable[[], DaemonClient]:
    return lambda: DaemonClient(transport)


def decode(payload: str) -> dict[str, Any]:
    decoded = json.loads(payload)
    assert isinstance(decoded, dict)
    return decoded


def _args() -> JsonObject:
    return {
        "session_id": "sess-partc",
        "selected_member": "kas",
        "speaker_selected_frame": copy.deepcopy(SPEAKER_SELECTED_FRAME),
        "participant_response": copy.deepcopy(PARTICIPANT_RESPONSE),
        "command_id": "cmd-speak-1",
        "request_id": "req-speak-1",
        "idempotency_key": "idem-speak-1",
        "ack_command_id": "cmd-ack-1",
    }


def test_selected_participant_response_submits_speak_then_acks_selected_cursor() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS,
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )

    result = decode(
        handle_selected_participant_response(
            _args(),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result == {
        "ok": True,
        "tool": "kan_selected_participant_response",
        "live_readiness": False,
        "data": {
            "selected_member": "kas",
            "speaker_selected_event_id": "evt-selected",
            "speaker_selected_cursor": "cur_000000000042_evt_selected",
            "speak": {
                "command_id": "cmd-speak-1",
                "event_id": "evt-speak-1",
                "session_id": "sess-partc",
                "request_id": "req-speak-1",
            },
            "ack": {
                "command_id": "cmd-ack-1",
                "event_id": "evt-ack-1",
                "session_id": "sess-partc",
                "request_id": "plugin-live-stream-ack",
                "deduplicated": False,
            },
            "proof": {
                "source": "control_membr_evidence",
                "runner_invocation_id": "run_cmd-grant-1_1",
                "runner_terminal_event_id": "evt-run-terminal",
                "no_role_substitution": True,
                "real_profile_live_invocation": False,
            },
        },
    }
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
        OP_VERSION_READ,
        OP_STREAM_ACK,
    ]
    submitted = transport.requests[1][1]
    assert submitted is not None
    assert submitted["command"] == "council.speak"
    assert submitted["request_id"] == "req-speak-1"
    assert submitted["idempotency_key"] == "idem-speak-1"
    assert submitted["payload"] == {
        "session_id": "sess-partc",
        "actor": "kas",
        "command_id": "cmd-speak-1",
        "payload": {
            "speech": "KAS bounded participant response from wrapper evidence.",
            "turn": 3,
            "evidence": {
                "source": "control_membr_evidence",
                "speaker_selected_event_id": "evt-selected",
                "speaker_selected_cursor": "cur_000000000042_evt_selected",
                "runner_invocation_id": "run_cmd-grant-1_1",
                "runner_started_event_id": "evt-run-started",
                "runner_terminal_event_id": "evt-run-terminal",
                "runner_terminal_event_type": "participant_response",
                "adapter_kind": "hermes-agent",
                "wrapper_binding_evidence": "redacted_wrapper_binding",
                "no_role_substitution": True,
                "real_profile_live_invocation": False,
            },
        },
    }
    assert transport.requests[3] == (
        OP_STREAM_ACK,
        {
            "protocol_version": "kan-protocol-v1alpha0",
            "session_id": "sess-partc",
            "member": "kas",
            "cursor": "cur_000000000042_evt_selected",
            "command_id": "cmd-ack-1",
        },
    )


def test_selected_participant_response_rejects_role_substitution_before_transport() -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    args = _args()
    response = cast(JsonObject, args["participant_response"])
    args["participant_response"] = {**response, "role_substitution": True}

    result = decode(handle_selected_participant_response(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["tool"] == "kan_selected_participant_response"
    assert result["error"] == {
        "category": "validation",
        "message": "participant_response.role_substitution must be false",
        "retryable": False,
    }
    assert client_factory_called is False


def test_selected_participant_response_rejects_member_mismatch_before_transport() -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    args = _args()
    response = cast(JsonObject, args["participant_response"])
    args["participant_response"] = {**response, "member": "kah"}

    result = decode(handle_selected_participant_response(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "participant_response.member must match selected_member",
        "retryable": False,
    }
    assert client_factory_called is False


@pytest.mark.parametrize(
    ("mutate_args", "message"),
    [
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["speaker_selected_frame"])["event"]
            ).__setitem__("type", "hand_raise_requested"),
            "speaker_selected_frame.event.type must be speaker_selected",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["speaker_selected_frame"])["event"]
            ).__setitem__("session_id", "sess-other"),
            "speaker_selected_frame.event.session_id must match session_id",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["speaker_selected_frame"])["event"]
            ).__setitem__("to", ["kah"]),
            "speaker_selected_frame.event.to must select exactly selected_member",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["speaker_selected_frame"])["event"]
            ).__setitem__("to", ["kas", "kah"]),
            "speaker_selected_frame.event.to must select exactly selected_member",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["speaker_selected_frame"])["event"]
            ).pop("to"),
            "speaker_selected_frame.event.to must select exactly selected_member",
        ),
        (
            lambda args: cast(JsonObject, args["participant_response"]).__setitem__(
                "source", "role_prompt"
            ),
            "participant_response.source must be control_membr_evidence",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["participant_response"])["runner"]
            ).__setitem__("adapter_kind", "role-prompt"),
            "participant_response.runner.adapter_kind must be hermes-agent",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["participant_response"])["runner"]
            ).__setitem__("terminal_event_type", "runner_invocation_failed"),
            "participant_response.runner.terminal_event_type must be participant_response",
        ),
    ],
)
def test_selected_participant_response_rejects_invalid_membr_evidence_before_transport(
    mutate_args: Callable[[JsonObject], object], message: str
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    args = _args()
    mutate_args(args)

    result = decode(handle_selected_participant_response(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["tool"] == "kan_selected_participant_response"
    assert result["error"] == {
        "category": "validation",
        "message": message,
        "retryable": False,
    }
    assert client_factory_called is False


def test_selected_participant_response_does_not_ack_when_speak_submit_fails() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: {
                "ok": False,
                "error": {
                    "category": "conflict",
                    "message": "speaker grant is missing",
                    "retryable": False,
                    "session_id": "sess-partc",
                    "request_id": "req-speak-1",
                },
            },
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )

    result = decode(
        handle_selected_participant_response(
            _args(),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "kan_selected_participant_response"
    assert result["error"]["category"] == "conflict"
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
    ]
