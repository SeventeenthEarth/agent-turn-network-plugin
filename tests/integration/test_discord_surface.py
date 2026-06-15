from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from kkachi_agent_network_plugin.discord_surface import DiscordMessageResult, DiscordMessageTarget
from kkachi_agent_network_plugin.tools import register_tools


def test_fake_hermes_context_invokes_injected_discord_sender_once() -> None:
    calls: list[tuple[DiscordMessageTarget, str]] = []

    def sender(*, target: DiscordMessageTarget, content: str) -> DiscordMessageResult:
        calls.append((target, content))
        return DiscordMessageResult(
            message_id="msg-cndis-2",
            channel_id=target.channel_id,
            thread_id=target.thread_id,
            message_ref="discord://discord-test-channel/discord-test-thread/msg-cndis-2",
            label=target.label,
            cleanup_hint=target.cleanup_hint,
        )

    ctx = FakePluginContext()
    register_tools(ctx, send_message=sender)

    result = json.loads(
        ctx.handlers["kan_discord_send_message"](
            {
                "content": "CNDIS-2 isolated fake send",
                "target": {
                    "channel_id": "discord-test-channel",
                    "thread_id": "discord-test-thread",
                    "dedicated_test_target": True,
                    "label": "[Kkachi CNDIS-2 isolated E2E]",
                    "cleanup_hint": "Delete this fake/injected helper message.",
                },
            }
        )
    )

    assert result["ok"] is True
    assert result["live_readiness"] is False
    assert result["data"] == {
        "message_id": "msg-cndis-2",
        "channel_id": "discord-test-channel",
        "thread_id": "discord-test-thread",
        "message_ref": "discord://discord-test-channel/discord-test-thread/msg-cndis-2",
        "label": "[Kkachi CNDIS-2 isolated E2E]",
        "cleanup_hint": "Delete this fake/injected helper message.",
    }
    assert len(calls) == 1
    assert calls[0][1] == "CNDIS-2 isolated fake send"


def test_fake_hermes_context_discord_tool_fails_closed_without_sender() -> None:
    ctx = FakePluginContext()
    register_tools(ctx)

    result = json.loads(
        ctx.handlers["kan_discord_send_message"](
            {
                "content": "must not post",
                "target": {
                    "channel_id": "discord-test-channel",
                    "dedicated_test_target": True,
                },
            }
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "kan_discord_send_message"
    assert result["error"]["category"] == "validation"
    assert "no live Discord fallback" in result["error"]["message"]


def test_fake_hermes_context_surface_projection_tool_is_local_and_pure() -> None:
    ctx = FakePluginContext()
    register_tools(ctx)

    result = json.loads(
        ctx.handlers["kan_surface_render_projection"](
            {
                "projection": {
                    "schema_version": 1,
                    "session_id": "sess-surface",
                    "events": [
                        {
                            "cursor": "cur_000000000001_evt_session",
                            "event": {
                                "event_id": "evt-session",
                                "session_id": "sess-surface",
                                "type": "session_created",
                                "payload": {},
                            },
                        }
                    ],
                }
            }
        )
    )

    assert result["ok"] is True
    assert result["tool"] == "kan_surface_render_projection"
    assert result["live_readiness"] is False
    assert result["data"]["local_projection"]["rows"][0]["status"] == "created"
    assert ctx.registered_hooks == []
    assert ctx.registered_commands == []


def test_fake_hermes_context_keeps_hooks_and_commands_empty_for_discord_helper() -> None:
    ctx = FakePluginContext()
    register_tools(ctx)

    assert [tool["name"] for tool in ctx.registered_tools][-1] == "kan_discord_send_message"
    assert ctx.registered_hooks == []
    assert ctx.registered_commands == []


class FakePluginContext:
    def __init__(self) -> None:
        self.registered_tools: list[dict[str, Any]] = []
        self.registered_hooks: list[tuple[str, Any]] = []
        self.registered_commands: list[dict[str, Any]] = []
        self.handlers: dict[str, Callable[[dict[str, object]], str]] = {}

    def register_tool(self, **kwargs: Any) -> None:
        self.registered_tools.append(kwargs)
        name = kwargs["name"]
        handler = kwargs["handler"]
        assert isinstance(name, str)
        assert callable(handler)
        self.handlers[name] = handler

    def register_hook(self, hook_name: str, callback: Any) -> None:
        self.registered_hooks.append((hook_name, callback))

    def register_command(self, *args: Any, **kwargs: Any) -> None:
        self.registered_commands.append({"args": args, "kwargs": kwargs})
