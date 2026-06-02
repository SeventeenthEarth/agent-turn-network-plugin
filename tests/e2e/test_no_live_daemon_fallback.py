from __future__ import annotations

import os

import pytest

from kkachi_agent_network_plugin.client import DaemonClient, StaticDaemonTransport
from kkachi_agent_network_plugin.client.daemon import OP_STATUS_READ
from kkachi_agent_network_plugin.errors import DaemonProtocolError, DaemonTransportError


def test_e2e_no_live_daemon_fallback_even_when_live_env_names_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert os.environ.get("KAN_E2E") == "1"
    monkeypatch.setenv("KAN_DAEMON_URL", "http://127.0.0.1:65535")
    monkeypatch.setenv("HERMES_HOME", os.environ.get("HERMES_HOME", "/tmp/fake-hermes-home"))
    monkeypatch.setenv("DISCORD_TEST_TARGET", "")

    with pytest.raises(DaemonTransportError, match="no live localhost/CLI/Hermes/Discord fallback"):
        DaemonClient()


def test_e2e_requires_explicit_fake_transport_for_status() -> None:
    assert os.environ.get("KAN_E2E") == "1"
    client = DaemonClient(StaticDaemonTransport({OP_STATUS_READ: {"malformed": True}}))

    with pytest.raises(DaemonProtocolError):
        client.read_status()
