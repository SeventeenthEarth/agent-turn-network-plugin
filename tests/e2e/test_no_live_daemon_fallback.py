from __future__ import annotations

import json
import os

import pytest

from hermes_unified_network_plugin.client import DaemonClient, StaticDaemonTransport
from hermes_unified_network_plugin.client.daemon import OP_STATUS_READ, OP_STREAM_TAIL
from hermes_unified_network_plugin.errors import (
    DaemonProtocolError,
    DaemonTransportError,
)
from hermes_unified_network_plugin.tools import (
    handle_daemon_status,
    handle_delegate_action,
    handle_delegate_new,
    handle_stream_tail,
)


def test_e2e_no_live_daemon_fallback_even_when_live_env_names_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert os.environ.get("KAN_E2E") == "1"
    monkeypatch.setenv("KAN_DAEMON_URL", "http://127.0.0.1:65535")
    monkeypatch.setenv("KAN_STREAM_URL", "ws://127.0.0.1:65535/stream")
    monkeypatch.setenv("KAN_STREAM_SSE_URL", "http://127.0.0.1:65535/stream")
    monkeypatch.setenv("HERMES_HOME", os.environ.get("HERMES_HOME", "/tmp/fake-hermes-home"))
    monkeypatch.setenv("KAB_GATEWAY_TOKEN", "fake-token")
    monkeypatch.setenv("DISCORD_TOKEN", "fake-token")
    monkeypatch.setenv("DISCORD_TEST_TARGET", "")

    with pytest.raises(DaemonTransportError, match="no live localhost/CLI/Hermes/Discord fallback"):
        DaemonClient()


def test_e2e_requires_explicit_fake_transport_for_status() -> None:
    assert os.environ.get("KAN_E2E") == "1"
    client = DaemonClient(StaticDaemonTransport({OP_STATUS_READ: {"malformed": True}}))

    with pytest.raises(DaemonProtocolError):
        client.read_status()


def test_e2e_stream_tail_requires_version_probe_even_with_live_env_vars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert os.environ.get("KAN_E2E") == "1"
    monkeypatch.setenv("KAN_DAEMON_URL", "http://127.0.0.1:65535")
    monkeypatch.setenv("KAN_STREAM_URL", "ws://127.0.0.1:65535/stream")
    client = DaemonClient(
        StaticDaemonTransport(
            {OP_STREAM_TAIL: {"protocol_version": "hun-protocol-v1alpha0", "frames": []}}
        )
    )

    with pytest.raises(DaemonTransportError, match="version.read"):
        client.read_stream_tail(session_id="sess-e2e", member="agent-1")


def test_e2e_plugin_handler_does_not_use_live_env_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    assert os.environ.get("KAN_E2E") == "1"
    monkeypatch.setenv("KAN_DAEMON_URL", "http://127.0.0.1:65535")
    monkeypatch.setenv("DISCORD_TOKEN", "fake-token")

    result = json.loads(handle_daemon_status({}))

    assert result["ok"] is False
    assert result["error"]["category"] == "unavailable"
    assert "client factory" in result["error"]["message"]


def test_e2e_stream_tail_handler_does_not_use_live_env_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert os.environ.get("KAN_E2E") == "1"
    monkeypatch.setenv("KAN_DAEMON_URL", "http://127.0.0.1:65535")
    monkeypatch.setenv("KAN_STREAM_URL", "ws://127.0.0.1:65535/stream")
    monkeypatch.setenv("KAB_GATEWAY_TOKEN", "fake-token")

    result = json.loads(handle_stream_tail({"session_id": "sess-e2e", "member": "agent-1"}))

    assert result["ok"] is False
    assert result["tool"] == "hun_stream_tail"
    assert result["error"]["category"] == "unavailable"
    assert "client factory" in result["error"]["message"]


def test_e2e_delegate_handlers_do_not_use_live_env_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert os.environ.get("KAN_E2E") == "1"
    monkeypatch.setenv("KAN_DAEMON_URL", "http://127.0.0.1:65535")
    monkeypatch.setenv("KAN_STREAM_URL", "ws://127.0.0.1:65535/stream")
    monkeypatch.setenv("KAB_GATEWAY_TOKEN", "fake-token")
    monkeypatch.setenv("DISCORD_TOKEN", "fake-token")

    delegate_new = json.loads(
        handle_delegate_new(
            {
                "session_id": "sess-e2e",
                "moderator": "agent-mod",
                "assignee": "agent-impl",
                "title": "No live fallback",
                "task": "Prove delegate.new requires an injected client",
                "context": {},
                "participants": [],
                "acceptance": [],
                "expected_outputs": [],
                "limits": {},
                "request_id": "req-e2e-1",
                "idempotency_key": "idem-e2e-1",
            }
        )
    )
    delegate_action = json.loads(
        handle_delegate_action(
            {
                "session_id": "sess-e2e",
                "command": "delegate.review",
                "request_id": "req-e2e-2",
                "idempotency_key": "idem-e2e-2",
                "payload": {},
            }
        )
    )

    assert delegate_new["ok"] is False
    assert delegate_new["tool"] == "hun_delegate_new"
    assert delegate_new["error"]["category"] == "unavailable"
    assert "client factory" in delegate_new["error"]["message"]
    assert delegate_action["ok"] is False
    assert delegate_action["tool"] == "hun_delegate_action"
    assert delegate_action["error"]["category"] == "unavailable"
    assert "client factory" in delegate_action["error"]["message"]
