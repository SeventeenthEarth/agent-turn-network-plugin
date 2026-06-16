"""Explicit live transport configuration helpers.

This module only turns caller-supplied plugin config into a register-time
client factory.  It does not inspect environment variables, profiles, Hermes
state, localhost endpoints, CLI discovery, or daemon storage files.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Final

from ..errors import DaemonTransportError
from .daemon import DaemonClient
from .transport import UnixSocketDaemonTransport

LIVE_TRANSPORT_SECTION: Final = "live_transport"
UNIX_SOCKET_PATH_KEY: Final = "unix_socket_path"

ClientFactory = Callable[[], DaemonClient]


def load_plugin_local_live_config(config_path: Path) -> dict[str, object] | None:
    """Load the approved adjacent plugin-local live config shape if present."""

    try:
        if not config_path.exists():
            return None
        if not config_path.is_file():
            raise DaemonTransportError("plugin-local config.yaml must be a file")
        text = config_path.read_text(encoding="utf-8")
        return parse_plugin_local_live_config(text)
    except DaemonTransportError:
        raise
    except (OSError, ValueError) as exc:
        raise DaemonTransportError(f"plugin-local config.yaml could not be loaded: {exc}") from exc


def parse_plugin_local_live_config(text: str) -> dict[str, object]:
    """Parse only ``live_transport.unix_socket_path`` from a tiny YAML subset."""

    lines = [
        line.rstrip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines:
        raise DaemonTransportError("plugin-local config.yaml must contain live_transport")
    if len(lines) != 2:
        raise DaemonTransportError(
            "plugin-local config.yaml supports only live_transport.unix_socket_path"
        )
    section_line, socket_line = lines
    if section_line != f"{LIVE_TRANSPORT_SECTION}:":
        raise DaemonTransportError("plugin-local config.yaml has unsupported top-level key")
    prefix = f"  {UNIX_SOCKET_PATH_KEY}:"
    if not socket_line.startswith(prefix):
        raise DaemonTransportError(
            "plugin-local config.yaml supports only live_transport.unix_socket_path"
        )
    raw_value = socket_line[len(prefix) :].strip()
    socket_path = _parse_socket_path_scalar(raw_value)
    return {LIVE_TRANSPORT_SECTION: {UNIX_SOCKET_PATH_KEY: socket_path}}


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


def _parse_socket_path_scalar(raw_value: str) -> str:
    if not raw_value:
        raise DaemonTransportError("live_transport.unix_socket_path is required")
    if "\t" in raw_value or raw_value.startswith(("[", "{", "-", "|", ">", "&", "*")):
        raise DaemonTransportError("live_transport.unix_socket_path must be a scalar string")
    if "$" in raw_value:
        raise DaemonTransportError("live_transport.unix_socket_path must not use interpolation")
    if raw_value[0] in {"'", '"'}:
        quote = raw_value[0]
        if len(raw_value) < 2 or raw_value[-1] != quote:
            raise DaemonTransportError("live_transport.unix_socket_path quote is not closed")
        value = raw_value[1:-1]
        if quote in value:
            raise DaemonTransportError("live_transport.unix_socket_path has unsupported quoting")
        return value
    if any(char.isspace() for char in raw_value) or "#" in raw_value:
        raise DaemonTransportError("live_transport.unix_socket_path must be a scalar string")
    return raw_value


__all__ = [
    "ClientFactory",
    "LIVE_TRANSPORT_SECTION",
    "UNIX_SOCKET_PATH_KEY",
    "configured_live_client_factory",
    "live_client_factory_from_config",
    "load_plugin_local_live_config",
    "parse_plugin_local_live_config",
]
