from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from kkachi_agent_network_plugin.client import DaemonClient, StaticDaemonTransport
from kkachi_agent_network_plugin.client.daemon import OP_DIAGNOSTICS_READ, OP_STATUS_READ
from kkachi_agent_network_plugin.tools import register_tools


def test_fake_hermes_context_invokes_registered_readonly_handlers() -> None:
    transport = StaticDaemonTransport(
        {
            OP_STATUS_READ: {
                "protocol_version": "kan-protocol-v1alpha0",
                "daemon_version": "0.0.0-fake",
                "status": "fake-ready",
                "feature_groups": ["version_features", "command_envelope", "structured_error"],
                "live_readiness": False,
            },
            OP_DIAGNOSTICS_READ: {
                "protocol_version": "kan-protocol-v1alpha0",
                "daemon_version": "0.0.0-fake",
                "live_readiness": False,
                "checks": [{"name": "structured_error", "ok": True}],
            },
        }
    )
    ctx = FakePluginContext()
    register_tools(ctx, client_factory=lambda: DaemonClient(transport))

    assert [tool["name"] for tool in ctx.registered_tools] == [
        "kan_daemon_status",
        "kan_compatibility_diagnostics",
    ]
    status = json.loads(ctx.handlers["kan_daemon_status"]({}))
    diagnostics = json.loads(
        ctx.handlers["kan_compatibility_diagnostics"]({"session_id": "sess-int"})
    )

    assert status["ok"] is True
    assert diagnostics["ok"] is True
    assert transport.requests == [
        (OP_STATUS_READ, {"protocol_version": "kan-protocol-v1alpha0"}),
        (
            OP_DIAGNOSTICS_READ,
            {"protocol_version": "kan-protocol-v1alpha0", "session_id": "sess-int"},
        ),
    ]


class FakePluginContext:
    def __init__(self) -> None:
        self.registered_tools: list[dict[str, Any]] = []
        self.handlers: dict[str, Callable[[dict[str, object]], str]] = {}

    def register_tool(self, **kwargs: Any) -> None:
        self.registered_tools.append(kwargs)
        name = kwargs["name"]
        handler = kwargs["handler"]
        assert isinstance(name, str)
        assert callable(handler)
        self.handlers[name] = handler
