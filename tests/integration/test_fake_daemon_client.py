from __future__ import annotations

import pytest

from kkachi_agent_network_plugin.client import DaemonClient, StaticDaemonTransport
from kkachi_agent_network_plugin.client.daemon import (
    OP_COMMAND_SUBMIT,
    OP_STATUS_READ,
    OP_VERSION_READ,
)
from kkachi_agent_network_plugin.errors import DaemonCommandError, DaemonProtocolError
from kkachi_agent_network_plugin.protocol import JsonObject

BASE_RESPONSE = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": ["version_features", "command_envelope", "structured_error"],
    "live_readiness": False,
}


def test_fake_daemon_status_version_and_command_success_flow() -> None:
    def submit(body: JsonObject | None) -> JsonObject:
        assert body is not None
        assert body["command"] == "session.note"
        assert body["request_id"] == "req-int-1"
        assert body["idempotency_key"] == "idem-int-1"
        return {
            "ok": True,
            "command_id": "cmd-int-1",
            "event_id": "evt-int-1",
            "session_id": "sess-int-1",
            "request_id": body["request_id"],
        }

    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: dict(BASE_RESPONSE),
            OP_STATUS_READ: {**BASE_RESPONSE, "status": "fake-ready"},
            OP_COMMAND_SUBMIT: submit,
        }
    )
    client = DaemonClient(transport)

    assert client.read_version().live_readiness is False
    assert client.read_status().status == "fake-ready"
    envelope = client.build_command_envelope(
        command="session.note",
        payload={"message": "draft fixture only"},
        request_id="req-int-1",
        idempotency_key="idem-int-1",
    )
    result = client.submit_command(envelope)

    assert result.command_id == "cmd-int-1"
    assert result.event_id == "evt-int-1"
    assert result.session_id == "sess-int-1"


def test_fake_daemon_command_error_preserves_category_ids_and_redacts() -> None:
    client = DaemonClient(
        StaticDaemonTransport(
            {
                OP_COMMAND_SUBMIT: {
                    "ok": False,
                    "error": {
                        "category": "conflict",
                        "message": "duplicate command",
                        "command_id": "cmd-existing",
                        "event_id": "evt-existing",
                        "session_id": "sess-existing",
                        "request_id": "req-dup",
                        "retryable": False,
                        "diagnostics": {"discord_token": "do-not-leak"},
                    },
                }
            }
        )
    )
    envelope = client.build_command_envelope(
        command="session.note",
        payload={},
        request_id="req-dup",
        idempotency_key="idem-dup",
    )

    with pytest.raises(DaemonCommandError) as exc_info:
        client.submit_command(envelope)

    details = exc_info.value.details
    assert details.category == "conflict"
    assert details.command_id == "cmd-existing"
    assert details.event_id == "evt-existing"
    assert details.session_id == "sess-existing"
    assert details.request_id == "req-dup"
    assert details.diagnostics == {"discord_token": "[REDACTED]"}


@pytest.mark.parametrize(
    "response",
    [
        {"ok": "yes"},
        {"ok": False},
        {"ok": False, "error": {"category": "unknown", "message": "bad"}},
        {"ok": True},
    ],
)
def test_fake_daemon_malformed_command_responses_fail_closed(response: JsonObject) -> None:
    client = DaemonClient(StaticDaemonTransport({OP_COMMAND_SUBMIT: response}))
    envelope = client.build_command_envelope(
        command="session.note",
        payload={},
        request_id="req-bad",
        idempotency_key="idem-bad",
    )

    with pytest.raises(DaemonProtocolError):
        client.submit_command(envelope)
