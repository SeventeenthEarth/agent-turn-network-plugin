from __future__ import annotations

import os

import kkachi_agent_network_plugin as plugin


def test_integration_scaffold_stays_offline() -> None:
    # TODO(DAEMN-1): expand this tier to fake-daemon client behavior when the client exists.
    assert os.environ.get("KAN_EXTERNAL", "0") == "0"
    assert plugin.package_metadata()["name"] == "kkachi-agent-network-plugin"
