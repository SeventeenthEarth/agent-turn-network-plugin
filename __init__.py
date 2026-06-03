"""Hermes directory plugin entrypoint for kkachi-agent-network-plugin.

HPLUG-2 registers read-only status, compatibility diagnostics, and stream tail tools.
Handlers fail closed unless a fake or explicitly injected daemon client factory is
supplied by tests/future plugin wiring; there is no live daemon, Hermes,
Discord, auth, token, gateway, socket, or CLI fallback.
"""

from __future__ import annotations

from kkachi_agent_network_plugin.tools import ToolRegistrationContext, register_tools


def register(ctx: ToolRegistrationContext) -> None:
    """Register the HPLUG-2 read-only plugin surface with Hermes."""

    register_tools(ctx)


__all__ = ["register"]
