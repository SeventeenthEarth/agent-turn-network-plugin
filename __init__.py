"""Hermes directory plugin entrypoint for kkachi-agent-network-plugin.

Registers read-only status/diagnostics/stream-tail tools, DELRV-1
delegation/review command-envelope tools, CNDIS-1 council/delivery-evidence
command tools, and the CNDIS-2 injected-only Discord helper. Handlers fail
closed unless a fake or explicitly injected daemon client factory is supplied by
tests or non-live wiring; there is no live daemon, Hermes, Discord, auth, token,
gateway, socket, or CLI fallback.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parent
_SRC_PATH = _PLUGIN_ROOT / "src"
if _SRC_PATH.is_dir():
    _src = str(_SRC_PATH)
    if _src not in sys.path:
        sys.path.insert(0, _src)

from kkachi_agent_network_plugin.tools import ToolRegistrationContext, register_tools  # noqa: E402


def register(ctx: ToolRegistrationContext) -> None:
    """Register the fake/injected plugin tool surface with Hermes."""

    register_tools(ctx)


__all__ = ["register"]
