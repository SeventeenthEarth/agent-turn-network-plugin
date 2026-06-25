from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, cast

import pytest

from atn_plugin.client import DaemonClient, StaticDaemonTransport
from atn_plugin.client.daemon import OP_COMMAND_SUBMIT
from atn_plugin.protocol import JsonObject, JsonValue
from atn_plugin.tools import handle_delegate_action, handle_delegate_new

CONTROL_CONFORMANCE_ROOT = (
    Path(__file__).resolve().parents[2].parent
    / "agent-turn-network-control"
    / "testdata"
    / "conformance"
)

SUCCESS_CASES = (
    (
        "delegate.new",
        "fixtures/command/delegate-new-request.json",
        "fixtures/command/delegate-new-response.json",
    ),
    (
        "delegate.submit",
        "fixtures/command/delegate-submit-request.json",
        "fixtures/command/delegate-submit-response.json",
    ),
    (
        "delegate.review",
        "fixtures/command/delegate-review-request.json",
        "fixtures/command/delegate-review-response.json",
    ),
    (
        "delegate.review_submit",
        "fixtures/command/delegate-review-submit-request.json",
        "fixtures/command/delegate-review-submit-response.json",
    ),
    (
        "delegate.accept",
        "fixtures/command/delegate-accept-request.json",
        "fixtures/command/delegate-accept-response.json",
    ),
)

ERROR_CASES = (
    (
        "delegate.submit",
        "fixtures/error/delegate-unauthorized-actor.json",
        {"actor": "agent-outside", "command_id": "cmd_delegate_unauthorized_actor"},
    ),
    (
        "delegate.review",
        "fixtures/error/delegate-review-wrong-phase.json",
        {"actor": "agent-mod", "command_id": "cmd_delegate_review_wrong_phase"},
    ),
    (
        "delegate.review_submit",
        "fixtures/error/delegate-review-submit-invalid-verdict.json",
        {
            "actor": "agent-1",
            "command_id": "cmd_delegate_review_submit_invalid_verdict",
            "payload": {"verdict": "maybe"},
        },
    ),
)


def _load_fixture(relative_path: str) -> JsonObject:
    path = CONTROL_CONFORMANCE_ROOT / relative_path
    with path.open(encoding="utf-8") as fixture_file:
        loaded = json.load(fixture_file)
    assert isinstance(loaded, dict), relative_path
    return cast(JsonObject, loaded)


def _manifest_fixture_paths() -> set[str]:
    manifest = _load_fixture("manifest.json")
    fixtures = manifest["fixtures"]
    assert isinstance(fixtures, list)
    return {fixture for fixture in fixtures if isinstance(fixture, str)}


def _mapping(value: object, *, label: str) -> Mapping[str, object]:
    assert isinstance(value, Mapping), label
    return value


def _string(value: object, *, label: str) -> str:
    assert isinstance(value, str) and value, label
    return value


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


def _plugin_error_response(error_fixture: Mapping[str, object]) -> JsonObject:
    error = _mapping(error_fixture["error"], label="error")
    return {
        "ok": False,
        "error": {
            "category": _string(error["category"], label="error.category"),
            "message": _string(error["message"], label="error.message"),
            "request_id": _string(error_fixture["request_id"], label="request_id"),
        },
    }


def _delegate_new_args(request_fixture: Mapping[str, object]) -> JsonObject:
    params = _mapping(request_fixture["params"], label="params")
    return {
        "session_id": _string(params["session_id"], label="params.session_id"),
        "moderator": _string(params["moderator"], label="params.moderator"),
        "assignee": _string(params["assignee"], label="params.assignee"),
        "title": _string(params["title"], label="params.title"),
        "task": _string(params["task"], label="params.task"),
        "context": {"control_fixture_context": _string(params["context"], label="params.context")},
        "participants": cast(list[JsonValue], params["participants"]),
        "acceptance": cast(list[JsonValue], params["acceptance"]),
        "expected_outputs": cast(list[JsonValue], params["expected_outputs"]),
        "limits": {"source": "DELEG-002", "fake_only": True},
        "request_id": _string(request_fixture["request_id"], label="request_id"),
        "idempotency_key": _idempotency_key(request_fixture),
    }


def _delegate_action_args(request_fixture: Mapping[str, object]) -> JsonObject:
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


@pytest.mark.parametrize(("command", "request_path", "response_path"), SUCCESS_CASES)
def test_deleg_002_success_fixtures_submit_exact_fake_command_envelopes(
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
        {OP_COMMAND_SUBMIT: _plugin_success_response(request_fixture, response_fixture)}
    )

    if command == "delegate.new":
        result = _decode(
            handle_delegate_new(
                _delegate_new_args(request_fixture),
                client_factory=_client_factory_for(transport),
            )
        )
    else:
        result = _decode(
            handle_delegate_action(
                _delegate_action_args(request_fixture),
                client_factory=_client_factory_for(transport),
            )
        )

    assert result["ok"] is True
    assert result["live_readiness"] is False
    data = result["data"]
    assert data["command_id"] == _mapping(request_fixture["params"], label="params")["command_id"]
    assert data["request_id"] == response_fixture["request_id"]
    assert data.get("event_id") == _event_id_from_control_response(response_fixture)
    operation, body = transport.requests[0]
    assert operation == OP_COMMAND_SUBMIT
    assert body is not None
    assert body["command"] == command
    assert body["request_id"] == request_fixture["request_id"]
    assert body["idempotency_key"] == _idempotency_key(request_fixture)
    assert body["client_metadata"] == {
        "name": "atn-plugin",
        "version": "0.1.0",
        "transport": "injected",
    }
    payload = _mapping(body["payload"], label="body.payload")
    assert (
        payload["session_id"] == _mapping(request_fixture["params"], label="params")["session_id"]
    )


def test_deleg_002_duplicate_submit_is_sent_twice_without_local_dedupe() -> None:
    request_fixture = _load_fixture("fixtures/command/delegate-submit-request.json")
    response_fixture = _load_fixture("fixtures/command/delegate-submit-response.json")
    duplicate_request = _load_fixture("fixtures/command/delegate-submit-duplicate-request.json")
    duplicate_response = _load_fixture("fixtures/command/delegate-submit-duplicate-response.json")
    scripted_responses = iter(
        (
            _plugin_success_response(request_fixture, response_fixture),
            _plugin_success_response(duplicate_request, duplicate_response),
        )
    )

    def submit(_: JsonObject | None) -> JsonObject:
        return next(scripted_responses)

    transport = StaticDaemonTransport({OP_COMMAND_SUBMIT: submit})

    first = _decode(
        handle_delegate_action(
            _delegate_action_args(request_fixture),
            client_factory=_client_factory_for(transport),
        )
    )
    second = _decode(
        handle_delegate_action(
            _delegate_action_args(duplicate_request),
            client_factory=_client_factory_for(transport),
        )
    )

    assert first["ok"] is True
    assert second["ok"] is True
    assert len(transport.requests) == 2
    first_body = _mapping(transport.requests[0][1], label="first request body")
    second_body = _mapping(transport.requests[1][1], label="second request body")
    assert first_body["command"] == second_body["command"] == "delegate.submit"
    assert first_body["idempotency_key"] == second_body["idempotency_key"]
    assert (
        _mapping(first_body["payload"], label="first payload")["command_id"]
        == _mapping(second_body["payload"], label="second payload")["command_id"]
    )
    assert first["data"]["command_id"] == second["data"]["command_id"]
    assert first["data"]["event_id"] == second["data"]["event_id"]
    assert second["data"]["request_id"] == duplicate_response["request_id"]


@pytest.mark.parametrize(("command", "error_path", "payload_patch"), ERROR_CASES)
def test_deleg_002_permission_and_validation_error_fixtures_fail_closed(
    command: str,
    error_path: str,
    payload_patch: Mapping[str, JsonValue],
) -> None:
    assert error_path in _manifest_fixture_paths()
    error_fixture = _load_fixture(error_path)
    transport = StaticDaemonTransport({OP_COMMAND_SUBMIT: _plugin_error_response(error_fixture)})
    action_args: JsonObject = {
        "session_id": "sess_conformance_delegation",
        "command": command,
        "request_id": _string(error_fixture["request_id"], label="request_id"),
        "idempotency_key": f"idem-{error_fixture['request_id']}",
        "payload": {"session_id": "will-be-overwritten", **dict(payload_patch)},
    }

    result = _decode(
        handle_delegate_action(action_args, client_factory=_client_factory_for(transport))
    )

    expected_error = _mapping(error_fixture["error"], label="error")
    assert result["ok"] is False
    assert result["tool"] == "atn_delegate_action"
    assert result["live_readiness"] is False
    assert result["error"] == {
        "category": expected_error["category"],
        "message": expected_error["message"],
        "retryable": False,
        "request_id": error_fixture["request_id"],
    }
    assert len(transport.requests) == 1


def test_plugin_local_retryable_fake_error_preserves_retryability() -> None:
    transport = StaticDaemonTransport(
        {
            OP_COMMAND_SUBMIT: {
                "ok": False,
                "error": {
                    "category": "unavailable",
                    "message": "fake daemon temporarily unavailable",
                    "retryable": True,
                    "session_id": "sess_conformance_delegation",
                    "request_id": "req_plugin_local_retryable",
                },
            }
        }
    )

    result = _decode(
        handle_delegate_action(
            {
                "session_id": "sess_conformance_delegation",
                "command": "delegate.review",
                "request_id": "req_plugin_local_retryable",
                "idempotency_key": "idem-plugin-local-retryable",
                "payload": {"actor": "agent-mod"},
            },
            client_factory=_client_factory_for(transport),
        )
    )

    assert result["ok"] is False
    assert result["error"] == {
        "category": "unavailable",
        "message": "fake daemon temporarily unavailable",
        "retryable": True,
        "session_id": "sess_conformance_delegation",
        "request_id": "req_plugin_local_retryable",
    }


@pytest.mark.parametrize(
    "fake_response",
    [
        {"ok": True},
        {
            "ok": False,
            "error": {"category": "validation", "message": "bad", "retryable": "yes"},
        },
    ],
)
def test_plugin_local_malformed_fake_daemon_responses_fail_closed(
    fake_response: JsonObject,
) -> None:
    transport = StaticDaemonTransport({OP_COMMAND_SUBMIT: fake_response})

    result = _decode(
        handle_delegate_action(
            {
                "session_id": "sess_conformance_delegation",
                "command": "delegate.review",
                "request_id": "req_plugin_local_malformed",
                "idempotency_key": "idem-plugin-local-malformed",
                "payload": {"actor": "agent-mod"},
            },
            client_factory=_client_factory_for(transport),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "atn_delegate_action"
    assert result["live_readiness"] is False
    assert result["error"]["category"] == "protocol"


def test_plugin_local_non_object_fake_daemon_response_fails_closed() -> None:
    def submit(_: JsonObject | None) -> JsonObject:
        return cast(JsonObject, "not a response object")

    transport = StaticDaemonTransport({OP_COMMAND_SUBMIT: submit})

    result = _decode(
        handle_delegate_action(
            {
                "session_id": "sess_conformance_delegation",
                "command": "delegate.review",
                "request_id": "req_plugin_local_non_object",
                "idempotency_key": "idem-plugin-local-non-object",
                "payload": {"actor": "agent-mod"},
            },
            client_factory=_client_factory_for(transport),
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "protocol"
