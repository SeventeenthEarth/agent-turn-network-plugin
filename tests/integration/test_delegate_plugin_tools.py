from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from kkachi_agent_network_plugin.client import DaemonClient, StaticDaemonTransport
from kkachi_agent_network_plugin.client.daemon import OP_COMMAND_SUBMIT
from kkachi_agent_network_plugin.tools import register_tools


def test_fake_hermes_context_invokes_registered_delegate_handlers() -> None:
    transport = StaticDaemonTransport(
        {
            OP_COMMAND_SUBMIT: {
                "ok": True,
                "command_id": "cmd-1",
                "event_id": "evt-1",
                "session_id": "sess-1",
                "request_id": "req-1",
            }
        }
    )
    ctx = FakePluginContext()
    register_tools(ctx, client_factory=lambda: DaemonClient(transport))

    assert [tool["name"] for tool in ctx.registered_tools] == [
        "kan_daemon_status",
        "kan_compatibility_diagnostics",
        "kan_stream_tail",
        "kan_delegate_new",
        "kan_delegate_action",
    ]

    delegate_new = json.loads(
        ctx.handlers["kan_delegate_new"](
            {
                "session_id": "sess-1",
                "moderator": "agent-mod",
                "assignee": "agent-impl",
                "title": "Implement DELRV-1",
                "task": "Add fake command envelope tools",
                "context": {"run_id": "run-1"},
                "participants": [],
                "acceptance": [],
                "expected_outputs": [],
                "limits": {"no_live": True},
                "request_id": "req-1",
                "idempotency_key": "idem-1",
            }
        )
    )
    delegate_action = json.loads(
        ctx.handlers["kan_delegate_action"](
            {
                "session_id": "sess-1",
                "command": "delegate.escalation_delivered",
                "request_id": "req-2",
                "idempotency_key": "idem-2",
                "payload": {"delivered_batch_id": None},
            }
        )
    )

    assert delegate_new["ok"] is True
    assert delegate_action["ok"] is True
    assert transport.requests[0][0] == OP_COMMAND_SUBMIT
    assert transport.requests[0][1] is not None
    assert transport.requests[0][1]["command"] == "delegate.new"
    assert transport.requests[0][1]["request_id"] == "req-1"
    assert transport.requests[0][1]["idempotency_key"] == "idem-1"
    assert transport.requests[1][0] == OP_COMMAND_SUBMIT
    assert transport.requests[1][1] is not None
    assert transport.requests[1][1]["command"] == "delegate.escalation_delivered"
    assert transport.requests[1][1]["request_id"] == "req-2"
    assert transport.requests[1][1]["idempotency_key"] == "idem-2"
    assert transport.requests[1][1]["payload"] == {
        "session_id": "sess-1",
        "delivered_batch_id": None,
    }


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
