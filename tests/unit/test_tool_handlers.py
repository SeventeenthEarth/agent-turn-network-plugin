from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, cast

import pytest

from kkachi_agent_network_plugin.client import DaemonClient, StaticDaemonTransport
from kkachi_agent_network_plugin.client.daemon import (
    OP_COMMAND_SUBMIT,
    OP_DIAGNOSTICS_READ,
    OP_STATUS_READ,
    OP_STREAM_TAIL,
    OP_VERSION_READ,
)
from kkachi_agent_network_plugin.protocol import JsonObject
from kkachi_agent_network_plugin.tools import (
    handle_compatibility_diagnostics,
    handle_council_command,
    handle_daemon_status,
    handle_delegate_action,
    handle_delegate_new,
    handle_delivery_evidence,
    handle_stream_tail,
)

BASE_STATUS: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "status": "fake-ready",
    "feature_groups": ["version.read", "command_envelope", "structured_error"],
    "live_readiness": False,
}
BASE_VERSION_WITH_STREAM: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": ["version.read", "command_envelope", "structured_error", "stream_frame"],
    "live_readiness": False,
}
BASE_VERSION_WITHOUT_STREAM: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": ["version.read", "command_envelope", "structured_error"],
    "live_readiness": False,
}
BASE_VERSION_WITH_CNDIS: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": [
        "version.read",
        "command_envelope",
        "structured_error",
        "delivery_evidence",
        "council.lifecycle",
    ],
    "live_readiness": False,
}
BASE_VERSION_WITHOUT_CNDIS: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": ["version.read", "command_envelope", "structured_error"],
    "live_readiness": False,
}
BASE_FRAME: JsonObject = {
    "cursor": "cur_000000000012_evt_01HV",
    "is_replay": False,
    "sequence": 12,
    "schema_version": 1,
    "event": {
        "schema_version": 1,
        "event_id": "evt_01HV",
        "session_id": "sess-1",
        "type": "hand_raise_requested",
        "from": "agent-mod",
        "to": ["agent-1"],
        "payload": {"gateway_token": "do-not-leak", "turn": 5},
        "details": {"note": "ok"},
    },
}
BASE_STREAM_TAIL: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "frames": [BASE_FRAME],
    "next_cursor": "cur_next",
}
BASE_DIAGNOSTICS: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "live_readiness": False,
    "checks": [
        {
            "name": "structured_error",
            "ok": True,
            "details": {"gateway_token": "do-not-leak"},
        }
    ],
}
BASE_COMMAND_SUCCESS: JsonObject = {
    "ok": True,
    "command_id": "cmd-1",
    "event_id": "evt-1",
    "session_id": "sess-1",
    "request_id": "req-1",
}


def factory_for(responses: dict[str, JsonObject]) -> Callable[[], DaemonClient]:
    typed_responses = cast(
        dict[str, JsonObject | Callable[[JsonObject | None], JsonObject]],
        responses,
    )
    return lambda: DaemonClient(StaticDaemonTransport(typed_responses))


def factory_for_transport(transport: StaticDaemonTransport) -> Callable[[], DaemonClient]:
    return lambda: DaemonClient(transport)


def decode(payload: str) -> dict[str, Any]:
    decoded = json.loads(payload)
    assert isinstance(decoded, dict)
    return decoded


def test_daemon_status_handler_returns_json_success_from_explicit_fake_client() -> None:
    result = decode(
        handle_daemon_status({}, client_factory=factory_for({OP_STATUS_READ: BASE_STATUS}))
    )

    assert result == {
        "ok": True,
        "tool": "kan_daemon_status",
        "protocol_version": "kan-protocol-v1alpha0",
        "live_readiness": False,
        "data": {
            "daemon_version": "0.0.0-fake",
            "status": "fake-ready",
            "feature_groups": ["version.read", "command_envelope", "structured_error"],
        },
    }


def test_compatibility_diagnostics_handler_returns_redacted_json_success() -> None:
    result = decode(
        handle_compatibility_diagnostics(
            {"session_id": "sess-1"},
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )

    assert result == {
        "ok": True,
        "tool": "kan_compatibility_diagnostics",
        "protocol_version": "kan-protocol-v1alpha0",
        "live_readiness": False,
        "data": {
            "daemon_version": "0.0.0-fake",
            "checks": [
                {
                    "name": "structured_error",
                    "ok": True,
                    "message": None,
                    "details": {"gateway_token": "[REDACTED]"},
                    "error": None,
                }
            ],
        },
    }


def test_stream_tail_handler_returns_redacted_json_success_from_explicit_fake_client() -> None:
    result = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1", "since_cursor": "cur_prev", "limit": 1},
            client_factory=factory_for(
                {OP_VERSION_READ: BASE_VERSION_WITH_STREAM, OP_STREAM_TAIL: BASE_STREAM_TAIL}
            ),
        )
    )

    assert result == {
        "ok": True,
        "tool": "kan_stream_tail",
        "protocol_version": "kan-protocol-v1alpha0",
        "live_readiness": False,
        "data": {
            "frames": [
                {
                    "cursor": "cur_000000000012_evt_01HV",
                    "is_replay": False,
                    "sequence": 12,
                    "schema_version": 1,
                    "event": {
                        "schema_version": 1,
                        "event_id": "evt_01HV",
                        "session_id": "sess-1",
                        "type": "hand_raise_requested",
                        "from": "agent-mod",
                        "to": ["agent-1"],
                        "payload": {"gateway_token": "[REDACTED]", "turn": 5},
                        "details": {"note": "ok"},
                    },
                }
            ],
            "next_cursor": "cur_next",
        },
    }


def test_handlers_fail_closed_without_client_factory() -> None:
    status = decode(handle_daemon_status({}))
    diagnostics = decode(handle_compatibility_diagnostics({}))
    stream_tail = decode(handle_stream_tail({"session_id": "sess-1", "member": "agent-1"}))

    assert status["ok"] is False
    assert status["tool"] == "kan_daemon_status"
    assert status["error"]["category"] == "unavailable"
    assert "client factory" in status["error"]["message"]
    assert diagnostics["ok"] is False
    assert diagnostics["error"]["category"] == "unavailable"
    assert stream_tail["ok"] is False
    assert stream_tail["tool"] == "kan_stream_tail"
    assert stream_tail["error"]["category"] == "unavailable"


def test_diagnostics_handler_rejects_invalid_session_id_before_transport() -> None:
    result = decode(
        handle_compatibility_diagnostics(
            {"session_id": ""},
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "session_id must be a non-empty string when present",
        "retryable": False,
    }


def test_stream_tail_handler_rejects_invalid_args_before_transport() -> None:
    factory = factory_for(
        {OP_VERSION_READ: BASE_VERSION_WITH_STREAM, OP_STREAM_TAIL: BASE_STREAM_TAIL}
    )

    missing_member = decode(handle_stream_tail({"session_id": "sess-1"}, client_factory=factory))
    empty_cursor = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1", "since_cursor": ""},
            client_factory=factory,
        )
    )
    bad_limit = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1", "limit": 1001},
            client_factory=factory,
        )
    )

    assert missing_member["ok"] is False
    assert missing_member["error"] == {
        "category": "validation",
        "message": "member must be a non-empty string",
        "retryable": False,
    }
    assert empty_cursor["ok"] is False
    assert empty_cursor["error"]["category"] == "validation"
    assert bad_limit["ok"] is False
    assert bad_limit["error"] == {
        "category": "validation",
        "message": "limit must be between 1 and 1000",
        "retryable": False,
    }


def test_handlers_reject_non_object_args_without_raising() -> None:
    status = decode(
        handle_daemon_status(
            [],
            client_factory=factory_for({OP_STATUS_READ: BASE_STATUS}),
        )
    )
    diagnostics = decode(
        handle_compatibility_diagnostics(
            [],
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )
    stream_tail = decode(
        handle_stream_tail(
            [],
            client_factory=factory_for(
                {OP_VERSION_READ: BASE_VERSION_WITH_STREAM, OP_STREAM_TAIL: BASE_STREAM_TAIL}
            ),
        )
    )

    assert status["ok"] is False
    assert status["error"]["category"] == "validation"
    assert diagnostics["ok"] is False
    assert diagnostics["error"]["category"] == "validation"
    assert stream_tail["ok"] is False
    assert stream_tail["error"]["category"] == "validation"


def test_handlers_reject_unknown_args_before_transport() -> None:
    status = decode(
        handle_daemon_status(
            {"unexpected": "x"},
            client_factory=factory_for({OP_STATUS_READ: BASE_STATUS}),
        )
    )
    diagnostics = decode(
        handle_compatibility_diagnostics(
            {"unexpected": "x"},
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )
    stream_tail = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1", "unexpected": "x"},
            client_factory=factory_for(
                {OP_VERSION_READ: BASE_VERSION_WITH_STREAM, OP_STREAM_TAIL: BASE_STREAM_TAIL}
            ),
        )
    )

    assert status["ok"] is False
    assert status["error"] == {
        "category": "validation",
        "message": "unsupported tool args: unexpected",
        "retryable": False,
    }
    assert diagnostics["ok"] is False
    assert diagnostics["error"] == {
        "category": "validation",
        "message": "unsupported tool args: unexpected",
        "retryable": False,
    }
    assert stream_tail["ok"] is False
    assert stream_tail["error"] == {
        "category": "validation",
        "message": "unsupported tool args: unexpected",
        "retryable": False,
    }


def test_stream_tail_handler_requires_stream_feature_before_tail_operation() -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITHOUT_STREAM, OP_STREAM_TAIL: BASE_STREAM_TAIL}
    )

    result = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1"},
            client_factory=lambda: DaemonClient(transport),
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "compatibility"
    assert transport.requests == [(OP_VERSION_READ, {"protocol_version": "kan-protocol-v1alpha0"})]


def test_handler_malformed_daemon_payload_fails_closed_as_protocol_error() -> None:
    result = decode(
        handle_daemon_status(
            {},
            client_factory=factory_for({OP_STATUS_READ: {"protocol_version": "wrong"}}),
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "compatibility"
    assert result["live_readiness"] is False


def test_stream_tail_handler_malformed_stream_payload_fails_closed() -> None:
    result = decode(
        handle_stream_tail(
            {"session_id": "sess-1", "member": "agent-1"},
            client_factory=factory_for(
                {
                    OP_VERSION_READ: BASE_VERSION_WITH_STREAM,
                    OP_STREAM_TAIL: {"protocol_version": "kan-protocol-v1alpha0", "frames": ["[]"]},
                }
            ),
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "protocol"
    assert result["live_readiness"] is False


def test_delegate_new_submits_delegate_new_envelope_with_caller_metadata() -> None:
    transport = StaticDaemonTransport({OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS})

    result = decode(
        handle_delegate_new(
            {
                "session_id": "sess-1",
                "moderator": "agent-mod",
                "assignee": "agent-impl",
                "title": "Implement DELRV-1",
                "task": "Add fake command envelope tools",
                "context": {"run_id": "run-1"},
                "participants": [{"id": "agent-mod"}, {"id": "agent-impl"}],
                "acceptance": ["tests pass"],
                "expected_outputs": ["summary"],
                "limits": {"no_live": True},
                "request_id": "req-1",
                "idempotency_key": "idem-1",
            },
            client_factory=factory_for_transport(transport),
        )
    )

    assert result == {
        "ok": True,
        "tool": "kan_delegate_new",
        "live_readiness": False,
        "data": {
            "command_id": "cmd-1",
            "event_id": "evt-1",
            "session_id": "sess-1",
            "request_id": "req-1",
        },
    }
    assert transport.requests == [
        (
            OP_COMMAND_SUBMIT,
            {
                "protocol_version": "kan-protocol-v1alpha0",
                "envelope_version": "kan-command-envelope-v1alpha0",
                "command": "delegate.new",
                "payload": {
                    "session_id": "sess-1",
                    "moderator": "agent-mod",
                    "assignee": "agent-impl",
                    "title": "Implement DELRV-1",
                    "task": "Add fake command envelope tools",
                    "context": {"run_id": "run-1"},
                    "participants": [{"id": "agent-mod"}, {"id": "agent-impl"}],
                    "acceptance": ["tests pass"],
                    "expected_outputs": ["summary"],
                    "limits": {"no_live": True},
                },
                "request_id": "req-1",
                "idempotency_key": "idem-1",
                "client_metadata": {
                    "name": "kkachi-agent-network-plugin",
                    "version": "0.1.0",
                    "transport": "injected",
                },
            },
        )
    ]


@pytest.mark.parametrize(
    ("field", "bad_value", "message"),
    [
        ("context", {"nested": object()}, "context must contain only JSON-compatible values"),
        ("limits", {"nested": object()}, "limits must contain only JSON-compatible values"),
        (
            "participants",
            [{"nested": object()}],
            "participants must contain only JSON-compatible values",
        ),
        ("acceptance", [object()], "acceptance must contain only JSON-compatible values"),
        (
            "expected_outputs",
            [{"nested": object()}],
            "expected_outputs must contain only JSON-compatible values",
        ),
    ],
)
def test_delegate_new_rejects_nested_non_json_values_before_transport(
    field: str,
    bad_value: object,
    message: str,
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    args: dict[str, object] = {
        "session_id": "sess-1",
        "moderator": "agent-mod",
        "assignee": "agent-impl",
        "title": "Implement DELRV-1",
        "task": "Add fake command envelope tools",
        "context": {"run_id": "run-1"},
        "participants": [{"id": "agent-mod"}, {"id": "agent-impl"}],
        "acceptance": ["tests pass"],
        "expected_outputs": ["summary"],
        "limits": {"no_live": True},
        "request_id": "req-1",
        "idempotency_key": "idem-1",
    }
    args[field] = bad_value

    result = decode(handle_delegate_new(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["tool"] == "kan_delegate_new"
    assert result["error"] == {
        "category": "validation",
        "message": message,
        "retryable": False,
    }
    assert client_factory_called is False


@pytest.mark.parametrize(
    "command",
    ["delegate.review", "delegate.review_submit", "delegate.escalation_delivered"],
)
def test_delegate_action_submits_representative_closed_enum_commands(command: str) -> None:
    transport = StaticDaemonTransport({OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS})

    result = decode(
        handle_delegate_action(
            {
                "session_id": "sess-top",
                "command": command,
                "request_id": "req-1",
                "idempotency_key": "idem-1",
                "payload": {
                    "session_id": "payload-session-is-overridden",
                    "body": {"ok": True},
                },
            },
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is True
    operation, body = transport.requests[0]
    assert operation == OP_COMMAND_SUBMIT
    assert body is not None
    assert body["command"] == command
    assert body["request_id"] == "req-1"
    assert body["idempotency_key"] == "idem-1"
    assert body["payload"] == {"session_id": "sess-top", "body": {"ok": True}}


@pytest.mark.parametrize("command", ["delegate.request", "review", "delegate.unknown"])
def test_delegate_action_rejects_commands_outside_closed_enum_before_transport(
    command: str,
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    result = decode(
        handle_delegate_action(
            {
                "session_id": "sess-1",
                "command": command,
                "request_id": "req-1",
                "idempotency_key": "idem-1",
                "payload": {},
            },
            client_factory=client_factory,
        )
    )

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": f"unsupported delegate action command: {command}",
        "retryable": False,
    }
    assert client_factory_called is False


@pytest.mark.parametrize("idempotency_value", ["", None])
def test_delegate_action_rejects_missing_or_empty_idempotency_before_transport(
    idempotency_value: object,
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    base_args: dict[str, object] = {
        "session_id": "sess-1",
        "command": "delegate.review",
        "request_id": "req-1",
        "idempotency_key": "idem-1",
        "payload": {},
    }
    if idempotency_value is None:
        del base_args["idempotency_key"]
    else:
        base_args["idempotency_key"] = idempotency_value

    result = decode(handle_delegate_action(base_args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["error"]["category"] == "validation"
    assert result["error"]["message"] == "idempotency_key must be a non-empty string"
    assert client_factory_called is False


def test_delegate_action_preserves_structured_daemon_conflict_error() -> None:
    transport = StaticDaemonTransport(
        {
            OP_COMMAND_SUBMIT: {
                "ok": False,
                "error": {
                    "category": "conflict",
                    "message": "duplicate idempotency key",
                    "retryable": True,
                    "command_id": "cmd-old",
                    "session_id": "sess-1",
                    "request_id": "req-1",
                    "diagnostics": {"duplicate": True},
                },
            }
        }
    )

    result = decode(
        handle_delegate_action(
            {
                "session_id": "sess-1",
                "command": "delegate.review",
                "request_id": "req-1",
                "idempotency_key": "idem-1",
                "payload": {},
            },
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "kan_delegate_action"
    assert result["error"] == {
        "category": "conflict",
        "message": "duplicate idempotency key",
        "retryable": True,
        "command_id": "cmd-old",
        "session_id": "sess-1",
        "request_id": "req-1",
        "diagnostics": {"duplicate": True},
    }


def test_delegate_new_malformed_daemon_response_fails_closed_as_protocol_error() -> None:
    result = decode(
        handle_delegate_new(
            {
                "session_id": "sess-1",
                "moderator": "agent-mod",
                "assignee": "agent-impl",
                "title": "Implement DELRV-1",
                "task": "Add fake command envelope tools",
                "context": {},
                "participants": [],
                "acceptance": [],
                "expected_outputs": [],
                "limits": {},
                "request_id": "req-1",
                "idempotency_key": "idem-1",
            },
            client_factory=factory_for({OP_COMMAND_SUBMIT: {"ok": True}}),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "kan_delegate_new"
    assert result["error"]["category"] == "protocol"
    assert result["live_readiness"] is False


def test_delegate_handlers_fail_closed_without_client_factory() -> None:
    delegate_new = decode(
        handle_delegate_new(
            {
                "session_id": "sess-1",
                "moderator": "agent-mod",
                "assignee": "agent-impl",
                "title": "Implement DELRV-1",
                "task": "Add fake command envelope tools",
                "context": {},
                "participants": [],
                "acceptance": [],
                "expected_outputs": [],
                "limits": {},
                "request_id": "req-1",
                "idempotency_key": "idem-1",
            }
        )
    )
    delegate_action = decode(
        handle_delegate_action(
            {
                "session_id": "sess-1",
                "command": "delegate.review",
                "request_id": "req-1",
                "idempotency_key": "idem-1",
                "payload": {},
            }
        )
    )

    assert delegate_new["ok"] is False
    assert delegate_new["error"]["category"] == "unavailable"
    assert delegate_action["ok"] is False
    assert delegate_action["tool"] == "kan_delegate_action"
    assert delegate_action["error"]["category"] == "unavailable"


def _council_args(command: str, payload: JsonObject | None = None) -> JsonObject:
    if payload is None:
        payload = {
            "actor": "agent-mod",
            "command_id": f"cmd-{command.replace('.', '-')}",
            "payload": {"note": "ok"},
        }
    return {
        "session_id": "sess-council",
        "command": command,
        "request_id": f"req-{command.replace('.', '-')}",
        "idempotency_key": "idem-shared",
        "payload": payload,
    }


def _delivery_args(command: str, payload: JsonObject | None = None) -> JsonObject:
    if payload is None and command == "delegate.escalation_delivered":
        payload = {
            "escalation": "evt-escalation",
            "delivery_target": "origin",
            "platform": "hermes",
            "message_ref": "msg-1",
            "command_id": "cmd-delivered",
        }
    if payload is None:
        payload = {
            "escalation": "evt-escalation",
            "target": "telegram",
            "reason": "unreachable",
            "will_retry_targets": ["origin"],
            "command_id": "cmd-failed",
        }
    return {
        "session_id": "sess-delegate",
        "command": command,
        "request_id": f"req-{command.replace('.', '-')}",
        "idempotency_key": "idem-delivery",
        "payload": payload,
    }


@pytest.mark.parametrize(
    ("command", "payload"),
    [
        (
            "council.new",
            {
                "session_id": "payload-session-is-overridden",
                "moderator": "agent-mod",
                "members": ["agent-1", "agent-2"],
                "title": "Static council",
                "surface": {"kind": "discord_thread", "thread_id": "thread-1"},
                "event_id": "evt-council",
                "command_id": "cmd-council-new",
            },
        ),
        (
            "council.ready",
            {"actor": "agent-1", "command_id": "cmd-ready", "payload": {"summary": "ready"}},
        ),
        (
            "council.finalize",
            {"actor": "agent-mod", "command_id": "cmd-finalize", "payload": {"done": True}},
        ),
    ],
)
def test_council_command_submits_after_feature_probe(command: str, payload: JsonObject) -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )

    result = decode(
        handle_council_command(
            _council_args(command, payload),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is True
    assert transport.requests[0] == (
        OP_VERSION_READ,
        {"protocol_version": "kan-protocol-v1alpha0"},
    )
    operation, body = transport.requests[1]
    assert operation == OP_COMMAND_SUBMIT
    assert body is not None
    assert body["command"] == command
    assert body["request_id"] == f"req-{command.replace('.', '-')}"
    assert body["idempotency_key"] == "idem-shared"
    submitted_payload = cast(JsonObject, body["payload"])
    assert submitted_payload["session_id"] == "sess-council"


@pytest.mark.parametrize(
    "command",
    ["delegate.escalation_delivered", "delegate.escalation_delivery_failed"],
)
def test_delivery_evidence_submits_after_feature_probe(command: str) -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )

    result = decode(
        handle_delivery_evidence(
            _delivery_args(command),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is True
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
    ]
    submitted = transport.requests[1][1]
    assert submitted is not None
    assert submitted["command"] == command
    assert submitted["request_id"] == f"req-{command.replace('.', '-')}"
    assert submitted["idempotency_key"] == "idem-delivery"
    assert cast(JsonObject, submitted["payload"])["session_id"] == "sess-delegate"


@pytest.mark.parametrize(
    ("handler", "args", "missing_feature"),
    [
        (
            handle_council_command,
            _council_args("council.ready"),
            "council.lifecycle",
        ),
        (
            handle_delivery_evidence,
            _delivery_args("delegate.escalation_delivered"),
            "delivery_evidence",
        ),
    ],
)
def test_cndis_handlers_fail_compatibility_before_submit_when_feature_missing(
    handler: Callable[..., str], args: JsonObject, missing_feature: str
) -> None:
    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITHOUT_CNDIS, OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS}
    )

    result = decode(handler(args, client_factory=factory_for_transport(transport)))

    assert result["ok"] is False
    assert result["error"]["category"] == "compatibility"
    assert missing_feature in result["error"]["message"]
    assert transport.requests == [(OP_VERSION_READ, {"protocol_version": "kan-protocol-v1alpha0"})]


@pytest.mark.parametrize(
    ("handler", "args", "message"),
    [
        (
            handle_council_command,
            _council_args("council.unknown"),
            "unsupported council command: council.unknown",
        ),
        (
            handle_council_command,
            _council_args("council.ready", {"actor": "agent-1", "payload": {}}),
            "payload.command_id must be a non-empty string",
        ),
        (
            handle_council_command,
            _council_args("council.new", {"command_id": "cmd"}),
            "payload.moderator must be a non-empty string",
        ),
        (
            handle_delivery_evidence,
            _delivery_args("delegate.unknown", {}),
            "unsupported delivery evidence command: delegate.unknown",
        ),
        (
            handle_delivery_evidence,
            _delivery_args("delegate.escalation_delivered", {"command_id": "cmd"}),
            "payload.escalation must be a non-empty string",
        ),
        (
            handle_delivery_evidence,
            _delivery_args(
                "delegate.escalation_delivery_failed",
                {"escalation": "evt", "command_id": "cmd"},
            ),
            "payload.target must be a non-empty string",
        ),
    ],
)
def test_cndis_handlers_reject_invalid_args_before_transport(
    handler: Callable[..., str], args: JsonObject, message: str
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    result = decode(handler(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["error"] == {"category": "validation", "message": message, "retryable": False}
    assert client_factory_called is False


def test_cndis_duplicate_idempotency_key_is_sent_twice_without_local_dedupe() -> None:
    responses = iter((BASE_COMMAND_SUCCESS, {**BASE_COMMAND_SUCCESS, "event_id": "evt-2"}))

    def submit(_: JsonObject | None) -> JsonObject:
        return next(responses)

    transport = StaticDaemonTransport(
        {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: submit}
    )

    first = decode(
        handle_council_command(
            _council_args("council.ready"), client_factory=factory_for_transport(transport)
        )
    )
    second = decode(
        handle_council_command(
            _council_args("council.ready"), client_factory=factory_for_transport(transport)
        )
    )

    assert first["ok"] is True
    assert second["ok"] is True
    submit_bodies = [
        body for operation, body in transport.requests if operation == OP_COMMAND_SUBMIT
    ]
    assert len(submit_bodies) == 2
    assert submit_bodies[0] is not None
    assert submit_bodies[1] is not None
    assert submit_bodies[0]["idempotency_key"] == submit_bodies[1]["idempotency_key"]


def test_cndis_handler_preserves_structured_daemon_error_after_feature_probe() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_CNDIS,
            OP_COMMAND_SUBMIT: {
                "ok": False,
                "error": {
                    "category": "validation",
                    "message": "only the council moderator may perform this action",
                    "retryable": False,
                    "request_id": "req-council-ready",
                },
            },
        }
    )

    result = decode(
        handle_council_command(
            _council_args("council.ready"), client_factory=factory_for_transport(transport)
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "kan_council_command"
    assert result["error"] == {
        "category": "validation",
        "message": "only the council moderator may perform this action",
        "retryable": False,
        "request_id": "req-council-ready",
    }


def test_cndis_malformed_daemon_response_fails_closed_after_feature_probe() -> None:
    result = decode(
        handle_delivery_evidence(
            _delivery_args("delegate.escalation_delivered"),
            client_factory=factory_for(
                {OP_VERSION_READ: BASE_VERSION_WITH_CNDIS, OP_COMMAND_SUBMIT: {"ok": True}}
            ),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "kan_delivery_evidence"
    assert result["error"]["category"] == "protocol"


def _discord_tool_args(target: JsonObject | None = None) -> JsonObject:
    return {
        "content": "CNDIS-2 isolated Discord helper smoke",
        "target": target
        or {
            "channel_id": "discord-test-channel-123",
            "thread_id": "discord-test-thread-456",
            "dedicated_test_target": True,
            "label": "[Kkachi CNDIS-2 isolated E2E]",
            "cleanup_hint": "Delete CNDIS-2 helper test messages.",
        },
    }


def test_discord_send_message_handler_fails_closed_without_sender() -> None:
    from kkachi_agent_network_plugin.tools import handle_discord_send_message

    result = decode(handle_discord_send_message(_discord_tool_args()))

    assert result["ok"] is False
    assert result["tool"] == "kan_discord_send_message"
    assert result["live_readiness"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "explicit Discord send_message sender is required; no live Discord fallback",
        "retryable": False,
    }


def test_discord_send_message_handler_rejects_missing_target_before_sender() -> None:
    from kkachi_agent_network_plugin.discord_surface import (
        DiscordMessageResult,
        DiscordMessageTarget,
    )
    from kkachi_agent_network_plugin.tools import handle_discord_send_message

    sender_called = False

    def sender(*, target: DiscordMessageTarget, content: str) -> DiscordMessageResult:
        nonlocal sender_called
        sender_called = True
        _ = (target, content)
        return DiscordMessageResult(message_id="msg-1", channel_id="discord-test-channel-123")

    result = decode(handle_discord_send_message({"content": "hello"}, send_message=sender))

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "target must be a JSON object",
        "retryable": False,
    }
    assert sender_called is False


def test_discord_send_message_handler_rejects_active_target_before_sender() -> None:
    from kkachi_agent_network_plugin.discord_surface import (
        DiscordMessageResult,
        DiscordMessageTarget,
    )
    from kkachi_agent_network_plugin.tools import handle_discord_send_message

    sender_called = False

    def sender(*, target: DiscordMessageTarget, content: str) -> DiscordMessageResult:
        nonlocal sender_called
        sender_called = True
        _ = (target, content)
        return DiscordMessageResult(message_id="msg-1", channel_id=target.channel_id)

    result = decode(
        handle_discord_send_message(
            _discord_tool_args(
                {
                    "channel_id": "current-thread",
                    "dedicated_test_target": True,
                    "label": "[Kkachi CNDIS-2 isolated E2E]",
                    "cleanup_hint": "Delete CNDIS-2 helper test messages.",
                }
            ),
            send_message=sender,
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "validation"
    assert "current or active Discord targets" in result["error"]["message"]
    assert sender_called is False


def test_discord_send_message_handler_calls_fake_sender_once_on_valid_target() -> None:
    from kkachi_agent_network_plugin.discord_surface import (
        DiscordMessageResult,
        DiscordMessageTarget,
    )
    from kkachi_agent_network_plugin.tools import handle_discord_send_message

    calls: list[tuple[DiscordMessageTarget, str]] = []

    def sender(*, target: DiscordMessageTarget, content: str) -> DiscordMessageResult:
        calls.append((target, content))
        return DiscordMessageResult(
            message_id="msg-1",
            channel_id=target.channel_id,
            thread_id=target.thread_id,
            message_ref="discord://discord-test-channel-123/discord-test-thread-456/msg-1",
            label=target.label,
            cleanup_hint=target.cleanup_hint,
        )

    result = decode(handle_discord_send_message(_discord_tool_args(), send_message=sender))

    assert result == {
        "ok": True,
        "tool": "kan_discord_send_message",
        "live_readiness": False,
        "data": {
            "message_id": "msg-1",
            "channel_id": "discord-test-channel-123",
            "thread_id": "discord-test-thread-456",
            "message_ref": "discord://discord-test-channel-123/discord-test-thread-456/msg-1",
            "label": "[Kkachi CNDIS-2 isolated E2E]",
            "cleanup_hint": "Delete CNDIS-2 helper test messages.",
        },
    }
    assert len(calls) == 1
    assert calls[0][1] == "CNDIS-2 isolated Discord helper smoke"
