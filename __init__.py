"""Hermes directory plugin entrypoint for kkachi-agent-network-plugin.

Registers read-only status/diagnostics/stream-tail tools and DELRV-1
delegation/review command-envelope tools. Handlers fail closed unless a fake or
explicitly injected daemon client factory is supplied by tests or non-live
wiring; there is no live daemon, Hermes, Discord, auth, token, gateway, socket,
or CLI fallback.
"""

from __future__ import annotations

from kkachi_agent_network_plugin.tools import ToolRegistrationContext, register_tools


def register(ctx: ToolRegistrationContext) -> None:
    """Register the fake/injected plugin tool surface with Hermes."""

    register_tools(ctx)


__all__ = ["register"]
