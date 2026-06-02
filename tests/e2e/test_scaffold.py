from __future__ import annotations

import os

import kkachi_agent_network_plugin as plugin


def test_e2e_scaffold_uses_isolated_environment_only() -> None:
    # TODO(HPLUG-1): expand this tier to plugin tool-handler smoke behavior when handlers exist.
    assert os.environ.get("KAN_E2E") == "1"
    assert os.environ.get("HERMES_HOME")
    assert os.environ.get("DISCORD_TEST_TARGET", "") == ""
    assert plugin.__version__ == plugin.package_metadata()["version"]
