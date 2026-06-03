from __future__ import annotations

import json
import os

import kkachi_agent_network_plugin as plugin
from kkachi_agent_network_plugin.client import DaemonClient, StaticDaemonTransport
from kkachi_agent_network_plugin.client.daemon import OP_STATUS_READ
from kkachi_agent_network_plugin.tools import handle_daemon_status


def test_e2e_scaffold_uses_isolated_environment_only() -> None:
    assert os.environ.get("KAN_E2E") == "1"
    assert os.environ.get("HERMES_HOME")
    assert os.environ.get("DISCORD_TEST_TARGET", "") == ""
    assert plugin.__version__ == plugin.package_metadata()["version"]


def test_e2e_readonly_handler_smoke_uses_explicit_fake_transport_only() -> None:
    assert os.environ.get("KAN_E2E") == "1"
    result = json.loads(
        handle_daemon_status(
            {},
            client_factory=lambda: DaemonClient(
                StaticDaemonTransport(
                    {
                        OP_STATUS_READ: {
                            "protocol_version": "kan-protocol-v1alpha0",
                            "daemon_version": "0.0.0-fake",
                            "status": "fake-ready",
                            "feature_groups": [
                                "version_features",
                                "command_envelope",
                                "structured_error",
                            ],
                            "live_readiness": False,
                        }
                    }
                )
            ),
        )
    )

    assert result["ok"] is True
    assert result["live_readiness"] is False
