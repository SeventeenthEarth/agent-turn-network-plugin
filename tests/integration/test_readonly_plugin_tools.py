from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from hermes_unified_network_plugin.client import DaemonClient, StaticDaemonTransport
from hermes_unified_network_plugin.client.daemon import (
    OP_DIAGNOSTICS_READ,
    OP_STATUS_READ,
    OP_STREAM_TAIL,
    OP_VERSION_READ,
)
from hermes_unified_network_plugin.tools import register_tools


def test_fake_hermes_context_invokes_registered_readonly_handlers() -> None:
    transport = StaticDaemonTransport(
        {
            OP_STATUS_READ: {
                "protocol_version": "hun-protocol-v1alpha0",
                "daemon_version": "0.0.0-fake",
                "status": "fake-ready",
                "feature_groups": ["version.read", "command_envelope", "structured_error"],
                "live_readiness": False,
            },
            OP_DIAGNOSTICS_READ: {
                "protocol_version": "hun-protocol-v1alpha0",
                "daemon_version": "0.0.0-fake",
                "live_readiness": False,
                "checks": [{"name": "structured_error", "ok": True}],
            },
            OP_VERSION_READ: {
                "protocol_version": "hun-protocol-v1alpha0",
                "daemon_version": "0.0.0-fake",
                "feature_groups": [
                    "version.read",
                    "command_envelope",
                    "structured_error",
                    "stream_frame",
                ],
                "live_readiness": False,
            },
            OP_STREAM_TAIL: {
                "protocol_version": "hun-protocol-v1alpha0",
                "frames": [
                    {
                        "cursor": "cur_1",
                        "is_replay": False,
                        "event": {
                            "schema_version": 1,
                            "event_id": "evt_1",
                            "session_id": "sess-int",
                            "type": "status",
                            "from": "agent-1",
                            "to": ["agent-2"],
                            "payload": {},
                        },
                    }
                ],
            },
        }
    )
    ctx = FakePluginContext()
    register_tools(ctx, client_factory=lambda: DaemonClient(transport))

    assert [tool["name"] for tool in ctx.registered_tools] == [
        "kan_daemon_status",
        "kan_compatibility_diagnostics",
        "kan_stream_tail",
        "kan_stream_ack",
        "kan_delegate_new",
        "kan_delegate_action",
        "kan_council_command",
        "kan_selected_participant_response",
        "kan_delivery_evidence",
        "kan_surface_render_projection",
        "kan_discussion_activation_plan",
        "kan_discord_send_message",
    ]
    status = json.loads(ctx.handlers["kan_daemon_status"]({}))
    diagnostics = json.loads(
        ctx.handlers["kan_compatibility_diagnostics"]({"session_id": "sess-int"})
    )
    stream_tail = json.loads(
        ctx.handlers["kan_stream_tail"](
            {"session_id": "sess-int", "member": "agent-1", "since_cursor": "cur_prev"}
        )
    )

    assert status["ok"] is True
    assert diagnostics["ok"] is True
    assert stream_tail["ok"] is True
    assert transport.requests == [
        (OP_STATUS_READ, {"protocol_version": "hun-protocol-v1alpha0"}),
        (
            OP_DIAGNOSTICS_READ,
            {"protocol_version": "hun-protocol-v1alpha0", "session_id": "sess-int"},
        ),
        (OP_VERSION_READ, {"protocol_version": "hun-protocol-v1alpha0"}),
        (
            OP_STREAM_TAIL,
            {
                "protocol_version": "hun-protocol-v1alpha0",
                "session_id": "sess-int",
                "member": "agent-1",
                "since_cursor": "cur_prev",
                "limit": 100,
            },
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
