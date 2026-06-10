"""Hermes directory plugin entrypoint for kkachi-agent-network-plugin.

Registers read-only status/diagnostics/stream-tail tools, DELRV-1
delegation/review command-envelope tools, CNDIS-1 council/delivery-evidence
command tools, and the CNDIS-2 injected-only Discord helper. Handlers fail
closed unless a fake, explicitly injected daemon client factory, or explicit
`live_transport.unix_socket_path` plugin config is supplied at registration;
there is no live daemon discovery, Hermes, Discord, auth, token, gateway,
localhost/TCP, or CLI fallback.
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

from kkachi_agent_network_plugin.tools import (  # noqa: E402
    ClientFactory,
    ToolRegistrationContext,
    register_tools,
)


def register(
    ctx: ToolRegistrationContext,
    *,
    client_factory: ClientFactory | None = None,
    config: dict[str, object] | None = None,
) -> None:
    """Register the plugin tool surface with explicit optional live config."""

    register_tools(ctx, client_factory=client_factory, config=config)


__all__ = ["register"]
