"""Hermes directory plugin entrypoint for atn-plugin.

Registers read-only status/diagnostics/stream-tail tools, DELRV-1
delegation/review command-envelope tools, CNDIS-1 council/delivery-evidence
command tools, a pure visible-surface projection renderer, and the CNDIS-2
injected-only Discord helper. Daemon handlers fail closed unless a fake,
explicitly injected daemon client factory, or explicit
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

from atn_plugin.bundled_skills import (  # noqa: E402
    bundled_skill_names,
    bundled_skill_resource,
)
from atn_plugin.client.daemon import DaemonClient  # noqa: E402
from atn_plugin.client.live import load_plugin_local_live_config  # noqa: E402
from atn_plugin.errors import DaemonTransportError  # noqa: E402
from atn_plugin.tools import (  # noqa: E402
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

    effective_client_factory = client_factory
    effective_config = config
    if client_factory is None and config is None:
        try:
            effective_config = load_plugin_local_live_config(_PLUGIN_ROOT / "config.yaml")
        except DaemonTransportError as exc:
            effective_client_factory = _failing_client_factory(exc)
    register_tools(ctx, client_factory=effective_client_factory, config=effective_config)
    _register_bundled_skills(ctx)


def _register_bundled_skills(ctx: object) -> None:
    """Register required ATN operator/role skills bundled with this plugin.

    Hermes exposes plugin skills as read-only, plugin-qualified skills.  This
    does not mutate profile skill directories and keeps the plugin package as
    the canonical source for ATN operator guidance.
    """

    register_skill = getattr(ctx, "register_skill", None)
    if not callable(register_skill):
        return
    descriptions = {
        "atn-plugin": "ATN plugin operator surface and boundaries.",
        "atn-moderator": "ATN council moderator preflight, lifecycle, and closeout guidance.",
        "atn-participant": "ATN selected-speaker participant response guidance.",
    }
    for name in bundled_skill_names():
        register_skill(
            name=name,
            path=Path(str(bundled_skill_resource(name))),
            description=descriptions.get(name, "ATN bundled operator guidance."),
        )


def _failing_client_factory(exc: DaemonTransportError) -> ClientFactory:
    def factory() -> DaemonClient:
        raise exc

    return factory


__all__ = ["register"]
