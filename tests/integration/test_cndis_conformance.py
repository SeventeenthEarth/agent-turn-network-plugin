from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, cast

import pytest

from atn_plugin import schemas
from atn_plugin.client import DaemonClient, StaticDaemonTransport
from atn_plugin.client.daemon import OP_COMMAND_SUBMIT, OP_VERSION_READ
from atn_plugin.protocol import JsonObject
from atn_plugin.tools import handle_council_command, handle_delivery_evidence

CONTROL_CONFORMANCE_ROOT = (
    Path(__file__).resolve().parents[2].parent
    / "agent-turn-network-control"
    / "testdata"
    / "conformance"
)

COUNCIL_CASES = tuple(
    (
        command,
        f"fixtures/command/{command.replace('.', '-').replace('_', '-')}-request.json",
        f"fixtures/command/{command.replace('.', '-').replace('_', '-')}-response.json",
    )
    for command in schemas.COUNCIL_COMMANDS
)

TURN_BEARING_COUNCIL_COMMANDS = frozenset(
    {
        "council.poll",
        "council.hand_raise",
        "council.drop",
        "council.grant",
        "council.speak",
    }
)
DELIVERY_CASES = (
    (
        "delegate.escalation_delivered",
        "fixtures/command/delegate-escalation-delivered-request.json",
        "fixtures/command/delegate-escalation-delivered-response.json",
    ),
    (
        "delegate.escalation_delivery_failed",
        "fixtures/command/delegate-escalation-delivery-failed-request.json",
        "fixtures/command/delegate-escalation-delivery-failed-response.json",
    ),
)
ARGUE_COMMAND_CASES = (
    (
        "council.speak",
        "fixtures/command/council-speak-argument-graph-request.json",
    ),
    (
        "council.hand_raise",
        "fixtures/command/council-hand-raise-argument-graph-request.json",
    ),
)
ARGUE_REQUIRED_FIXTURES = (
    "fixtures/event/argument-graph-opening-new-axis-council.json",
    "fixtures/event/argument-graph-support-prior-council.json",
    "fixtures/event/argument-graph-multi-link-council.json",
    "fixtures/event/argument-graph-synthesize-council.json",
    "fixtures/event/argument-graph-dual-field-speech-council.json",
    "fixtures/event/argument-graph-legacy-only-speech-council.json",
    "fixtures/event/argument-graph-hand-raise-target-links-council.json",
    "fixtures/error/argument-graph-invalid-stance.json",
    "fixtures/error/argument-graph-new-axis-missing-reason.json",
    "fixtures/error/argument-graph-synthesize-single-target.json",
    "fixtures/error/argument-graph-quality-required-missing-claims.json",
    "fixtures/error/argument-graph-quality-required-orphan-speech.json",
)


def _load_fixture(relative_path: str) -> JsonObject:
    path = CONTROL_CONFORMANCE_ROOT / relative_path
    with path.open(encoding="utf-8") as fixture_file:
        loaded = json.load(fixture_file)
    assert isinstance(loaded, dict), relative_path
    return cast(JsonObject, loaded)


def _mapping(value: object, *, label: str) -> Mapping[str, object]:
    assert isinstance(value, Mapping), label
    return value


def _string(value: object, *, label: str) -> str:
    assert isinstance(value, str) and value, label
    return value


def _manifest() -> JsonObject:
    return _load_fixture("manifest.json")


def _manifest_fixture_paths() -> set[str]:
    fixtures = _manifest()["fixtures"]
    assert isinstance(fixtures, list)
    return {fixture for fixture in fixtures if isinstance(fixture, str)}


def _version_response() -> JsonObject:
    manifest = _manifest()
    required_feature_groups = manifest["required_feature_groups"]
    assert isinstance(required_feature_groups, list)
    return {
        "protocol_version": "atn-protocol-v1alpha0",
        "daemon_version": "0.0.0-conformance-fake",
        "feature_groups": cast(list[str], required_feature_groups),
        "live_readiness": False,
    }


def _idempotency_key(request_fixture: Mapping[str, object]) -> str:
    params = _mapping(request_fixture["params"], label="params")
    command_id = params.get("command_id")
    if isinstance(command_id, str) and command_id:
        return f"idem-{command_id}"
    return f"idem-{_string(request_fixture['request_id'], label='request_id')}"


def _event_id_from_control_response(response_fixture: Mapping[str, object]) -> str | None:
    result = _mapping(response_fixture["result"], label="result")
    event_id = result.get("event_id")
    if isinstance(event_id, str) and event_id:
        return event_id
    results = result.get("results")
    if isinstance(results, list) and results:
        last = results[-1]
        if isinstance(last, Mapping):
            last_event_id = last.get("event_id")
            if isinstance(last_event_id, str) and last_event_id:
                return last_event_id
    return None


def _plugin_success_response(
    request_fixture: Mapping[str, object],
    response_fixture: Mapping[str, object],
) -> JsonObject:
    params = _mapping(request_fixture["params"], label="params")
    result = _mapping(response_fixture["result"], label="result")
    response: JsonObject = {
        "ok": True,
        "command_id": _string(params["command_id"], label="params.command_id"),
        "request_id": _string(response_fixture["request_id"], label="response.request_id"),
    }
    event_id = _event_id_from_control_response(response_fixture)
    if event_id is not None:
        response["event_id"] = event_id
    session_id = result.get("session_id", params.get("session_id"))
    if isinstance(session_id, str) and session_id:
        response["session_id"] = session_id
    return response


def _tool_args(request_fixture: Mapping[str, object]) -> JsonObject:
    params = dict(_mapping(request_fixture["params"], label="params"))
    session_id = _string(params["session_id"], label="params.session_id")
    params["session_id"] = "payload-session-must-be-overwritten"
    return {
        "session_id": session_id,
        "command": _string(request_fixture["command"], label="command"),
        "request_id": _string(request_fixture["request_id"], label="request_id"),
        "idempotency_key": _idempotency_key(request_fixture),
        "payload": cast(JsonObject, params),
    }


def _decode(payload: str) -> dict[str, Any]:
    decoded = json.loads(payload)
    assert isinstance(decoded, dict)
    return decoded


def _client_factory_for(transport: StaticDaemonTransport) -> Callable[[], DaemonClient]:
    return lambda: DaemonClient(transport)


def test_cndis_manifest_exposes_required_feature_groups() -> None:
    feature_groups = _version_response()["feature_groups"]

    assert "delivery_evidence" in feature_groups
    assert "council.lifecycle" in feature_groups


def test_argue_control_fixture_dependency_is_present_in_manifest() -> None:
    manifest_paths = _manifest_fixture_paths()

    for fixture_path in ARGUE_REQUIRED_FIXTURES:
        assert fixture_path in manifest_paths


@pytest.mark.parametrize(("command", "request_path", "response_path"), COUNCIL_CASES)
def test_council_conformance_fixtures_probe_then_submit_exact_fake_envelopes(
    command: str,
    request_path: str,
    response_path: str,
) -> None:
    manifest_paths = _manifest_fixture_paths()
    assert request_path in manifest_paths
    assert response_path in manifest_paths
    request_fixture = _load_fixture(request_path)
    response_fixture = _load_fixture(response_path)
    assert request_fixture["command"] == command
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: _version_response(),
            OP_COMMAND_SUBMIT: _plugin_success_response(request_fixture, response_fixture),
        }
    )

    result = _decode(
        handle_council_command(
            _tool_args(request_fixture), client_factory=_client_factory_for(transport)
        )
    )

    assert result["ok"] is True
    assert result["live_readiness"] is False
    data = result["data"]
    params = _mapping(request_fixture["params"], label="params")
    assert data["command_id"] == params["command_id"]
    assert data["request_id"] == response_fixture["request_id"]
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
    ]
    body = transport.requests[1][1]
    assert body is not None
    assert body["command"] == command
    assert body["request_id"] == request_fixture["request_id"]
    assert body["idempotency_key"] == _idempotency_key(request_fixture)
    payload = _mapping(body["payload"], label="body.payload")
    assert payload == params
    if command in TURN_BEARING_COUNCIL_COMMANDS:
        nested_payload = _mapping(payload["payload"], label="body.payload.payload")
        assert nested_payload["turn"] == _mapping(params["payload"], label="params.payload")["turn"]
        assert "round" not in nested_payload


@pytest.mark.parametrize(("command", "request_path"), ARGUE_COMMAND_CASES)
def test_argue_command_fixtures_probe_then_preserve_exact_payloads(
    command: str,
    request_path: str,
) -> None:
    manifest_paths = _manifest_fixture_paths()
    assert request_path in manifest_paths
    request_fixture = _load_fixture(request_path)
    assert request_fixture["command"] == command
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: _version_response(),
            OP_COMMAND_SUBMIT: _plugin_success_response(
                request_fixture,
                {
                    "request_id": request_fixture["request_id"],
                    "result": {
                        "event_id": "evt-argue-static",
                        "session_id": _mapping(request_fixture["params"], label="params")[
                            "session_id"
                        ],
                    },
                },
            ),
        }
    )

    result = _decode(
        handle_council_command(
            _tool_args(request_fixture), client_factory=_client_factory_for(transport)
        )
    )

    assert result["ok"] is True
    assert result["live_readiness"] is False
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
    ]
    body = transport.requests[1][1]
    assert body is not None
    assert body["command"] == command
    payload = _mapping(body["payload"], label="body.payload")
    assert payload["payload"] == _mapping(request_fixture["params"], label="params")["payload"]


@pytest.mark.parametrize(("command", "request_path", "response_path"), DELIVERY_CASES)
def test_delivery_conformance_fixtures_probe_then_submit_exact_fake_envelopes(
    command: str,
    request_path: str,
    response_path: str,
) -> None:
    manifest_paths = _manifest_fixture_paths()
    assert request_path in manifest_paths
    assert response_path in manifest_paths
    request_fixture = _load_fixture(request_path)
    response_fixture = _load_fixture(response_path)
    assert request_fixture["command"] == command
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: _version_response(),
            OP_COMMAND_SUBMIT: _plugin_success_response(request_fixture, response_fixture),
        }
    )

    result = _decode(
        handle_delivery_evidence(
            _tool_args(request_fixture), client_factory=_client_factory_for(transport)
        )
    )

    assert result["ok"] is True
    assert result["live_readiness"] is False
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
    ]
    body = transport.requests[1][1]
    assert body is not None
    assert body["command"] == command
    assert body["request_id"] == request_fixture["request_id"]
    assert body["idempotency_key"] == _idempotency_key(request_fixture)
    payload = _mapping(body["payload"], label="body.payload")
    assert (
        payload["session_id"] == _mapping(request_fixture["params"], label="params")["session_id"]
    )
