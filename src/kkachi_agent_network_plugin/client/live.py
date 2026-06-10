"""Explicit live transport configuration helpers.

This module only turns caller-supplied plugin config into a register-time
client factory.  It does not inspect environment variables, profiles, Hermes
state, localhost endpoints, CLI discovery, or daemon storage files.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Final

from ..errors import DaemonTransportError
from .daemon import DaemonClient
from .transport import UnixSocketDaemonTransport

LIVE_TRANSPORT_SECTION: Final = "live_transport"
UNIX_SOCKET_PATH_KEY: Final = "unix_socket_path"

ClientFactory = Callable[[], DaemonClient]


def configured_live_client_factory(config: Mapping[str, object] | None) -> ClientFactory | None:
    """Return a live client factory only when explicit live transport config exists."""

    if config is None or not config:
        return None
    if LIVE_TRANSPORT_SECTION not in config:
        return None
    return live_client_factory_from_config(config)


def live_client_factory_from_config(config: Mapping[str, object]) -> ClientFactory:
    live_transport = config.get(LIVE_TRANSPORT_SECTION)
    if not isinstance(live_transport, Mapping):
        raise DaemonTransportError(
            "live_transport.unix_socket_path must be configured under live_transport"
        )
    if UNIX_SOCKET_PATH_KEY not in live_transport:
        raise DaemonTransportError("live_transport.unix_socket_path is required")
    transport = UnixSocketDaemonTransport(live_transport[UNIX_SOCKET_PATH_KEY])

    def factory() -> DaemonClient:
        return DaemonClient(transport)

    return factory


__all__ = [
    "ClientFactory",
    "LIVE_TRANSPORT_SECTION",
    "UNIX_SOCKET_PATH_KEY",
    "configured_live_client_factory",
    "live_client_factory_from_config",
]
