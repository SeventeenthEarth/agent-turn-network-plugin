from __future__ import annotations

import json
import os

import pytest

from kkachi_agent_network_plugin.client import DaemonClient, StaticDaemonTransport
from kkachi_agent_network_plugin.client.daemon import OP_STATUS_READ, OP_STREAM_TAIL
from kkachi_agent_network_plugin.errors import (
    DaemonProtocolError,
    DaemonTransportError,
)
from kkachi_agent_network_plugin.tools import handle_daemon_status, handle_stream_tail


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
            {OP_STREAM_TAIL: {"protocol_version": "kan-protocol-v1alpha0", "frames": []}}
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
    assert result["tool"] == "kan_stream_tail"
    assert result["error"]["category"] == "unavailable"
    assert "client factory" in result["error"]["message"]
