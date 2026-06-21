from __future__ import annotations

import copy
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, cast

from hermes_unified_network_plugin.client import DaemonClient, StaticDaemonTransport
from hermes_unified_network_plugin.client.daemon import OP_COMMAND_SUBMIT, OP_VERSION_READ
from hermes_unified_network_plugin.protocol import JsonObject
from hermes_unified_network_plugin.tools import handle_council_command

CONTROL_CONFORMANCE_ROOT = (
    Path(__file__).resolve().parents[2].parent
    / "kkachi-agent-network-control"
    / "testdata"
    / "conformance"
)
BASE_VERSION_WITH_COUNCIL: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": ["version.read", "command_envelope", "structured_error", "council.lifecycle"],
    "live_readiness": False,
}
BASE_COMMAND_SUCCESS: JsonObject = {
    "ok": True,
    "command_id": "cmd-argue",
    "event_id": "evt-argue",
    "session_id": "sess_conformance_council",
    "request_id": "req-argue",
}


def _decode(payload: str) -> dict[str, Any]:
    decoded = json.loads(payload)
    assert isinstance(decoded, dict)
    return decoded


def _load_fixture(relative_path: str) -> JsonObject:
    path = CONTROL_CONFORMANCE_ROOT / relative_path
    with path.open(encoding="utf-8") as fixture_file:
        loaded = json.load(fixture_file)
    assert isinstance(loaded, dict)
    return cast(JsonObject, loaded)


def _mapping(value: object, *, label: str) -> Mapping[str, object]:
    assert isinstance(value, Mapping), label
    return value


def _tool_args(request_fixture: Mapping[str, object]) -> JsonObject:
    params = dict(_mapping(request_fixture["params"], label="params"))
    session_id = cast(str, params["session_id"])
    return {
        "session_id": session_id,
        "command": cast(str, request_fixture["command"]),
        "request_id": cast(str, request_fixture["request_id"]),
        "idempotency_key": f"idem-{params['command_id']}",
        "payload": cast(JsonObject, params),
    }


def _client_factory_for(transport: StaticDaemonTransport) -> Callable[[], DaemonClient]:
    return lambda: DaemonClient(transport)


def _assert_no_transport_on_invalid(args: JsonObject, expected_message: str) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    result = _decode(handle_council_command(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["tool"] == "kan_council_command"
    assert result["error"] == {
        "category": "validation",
        "message": expected_message,
        "retryable": False,
    }
    assert client_factory_called is False


def test_council_speak_argue_control_fixture_is_preserved_before_submit() -> None:
    fixture = _load_fixture("fixtures/command/council-speak-argument-graph-request.json")
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_COUNCIL, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )

    result = _decode(
        handle_council_command(_tool_args(fixture), client_factory=_client_factory_for(transport))
    )

    assert result["ok"] is True
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
    ]
    submitted = transport.requests[1][1]
    assert submitted is not None
    assert submitted["command"] == "council.speak"
    submitted_payload = _mapping(submitted["payload"], label="submitted.payload")
    fixture_params = _mapping(fixture["params"], label="fixture.params")
    assert submitted_payload["payload"] == fixture_params["payload"]


def test_council_hand_raise_argue_control_fixture_target_links_are_preserved() -> None:
    fixture = _load_fixture("fixtures/command/council-hand-raise-argument-graph-request.json")
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_COUNCIL, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )

    result = _decode(
        handle_council_command(_tool_args(fixture), client_factory=_client_factory_for(transport))
    )

    assert result["ok"] is True
    submitted = transport.requests[1][1]
    assert submitted is not None
    submitted_payload = _mapping(submitted["payload"], label="submitted.payload")
    fixture_params = _mapping(fixture["params"], label="fixture.params")
    assert submitted_payload["payload"] == fixture_params["payload"]


def test_responds_to_event_id_remains_display_hint_and_does_not_override_stance_links() -> None:
    fixture = _load_fixture("fixtures/command/council-speak-argument-graph-request.json")
    args = _tool_args(fixture)
    payload = cast(JsonObject, args["payload"])
    speech_payload = cast(JsonObject, payload["payload"])
    speech_payload["responds_to_event_id"] = "evt_legacy_hint_not_the_stance_target"
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_COUNCIL, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )

    result = _decode(handle_council_command(args, client_factory=_client_factory_for(transport)))

    assert result["ok"] is True
    submitted = transport.requests[1][1]
    assert submitted is not None
    submitted_speech = cast(JsonObject, cast(JsonObject, submitted["payload"])["payload"])
    assert submitted_speech["responds_to_event_id"] == "evt_legacy_hint_not_the_stance_target"
    assert submitted_speech["stance_links"] == speech_payload["stance_links"]


def test_synthesize_with_fewer_than_two_stance_links_fails_before_transport() -> None:
    fixture = _load_fixture("fixtures/command/council-speak-argument-graph-request.json")
    args = _tool_args(fixture)
    payload = cast(JsonObject, args["payload"])
    speech_payload = cast(JsonObject, payload["payload"])
    speech_payload["contribution_type"] = "synthesize"
    speech_payload["stance_links"] = cast(list[JsonObject], speech_payload["stance_links"])[:1]

    _assert_no_transport_on_invalid(
        args,
        "payload.stance_links must include at least two links for synthesize",
    )


def test_new_axis_without_reason_fails_before_transport() -> None:
    fixture = _load_fixture("fixtures/command/council-speak-argument-graph-request.json")
    args = _tool_args(fixture)
    payload = cast(JsonObject, args["payload"])
    speech_payload = cast(JsonObject, payload["payload"])
    speech_payload["contribution_type"] = "new_axis"
    speech_payload["new_axis_reason"] = ""

    _assert_no_transport_on_invalid(
        args,
        "payload.new_axis_reason must be a non-empty string",
    )


def test_invalid_argue_stance_fails_before_transport() -> None:
    fixture = _load_fixture("fixtures/command/council-speak-argument-graph-request.json")
    args = _tool_args(fixture)
    payload = cast(JsonObject, args["payload"])
    speech_payload = cast(JsonObject, payload["payload"])
    stance_links = copy.deepcopy(cast(list[JsonObject], speech_payload["stance_links"]))
    stance_links[0]["stance"] = "agree"
    speech_payload["stance_links"] = stance_links

    _assert_no_transport_on_invalid(args, "payload.stance_links[0].stance must be an ARGUE stance")


def test_duplicate_claim_ids_fail_before_transport() -> None:
    fixture = _load_fixture("fixtures/command/council-speak-argument-graph-request.json")
    args = _tool_args(fixture)
    payload = cast(JsonObject, args["payload"])
    speech_payload = cast(JsonObject, payload["payload"])
    claims = copy.deepcopy(cast(list[JsonObject], speech_payload["claims"]))
    claims.append(copy.deepcopy(claims[0]))
    speech_payload["claims"] = claims

    _assert_no_transport_on_invalid(
        args,
        "payload.claims claim_id entries must be unique within a speech",
    )


def test_argue_evidence_must_be_array_when_argue_fields_are_present() -> None:
    fixture = _load_fixture("fixtures/command/council-speak-argument-graph-request.json")
    args = _tool_args(fixture)
    payload = cast(JsonObject, args["payload"])
    speech_payload = cast(JsonObject, payload["payload"])
    speech_payload["evidence"] = {"source": "not-an-array"}

    _assert_no_transport_on_invalid(args, "payload.evidence must be a JSON array")
