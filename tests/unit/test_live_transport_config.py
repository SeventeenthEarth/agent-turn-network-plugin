from __future__ import annotations

from pathlib import Path

import pytest

from kkachi_agent_network_plugin.client.live import (
    configured_live_client_factory,
    live_client_factory_from_config,
)
from kkachi_agent_network_plugin.errors import DaemonTransportError


def test_no_config_preserves_fail_closed_no_client_factory() -> None:
    assert configured_live_client_factory(None) is None
    assert configured_live_client_factory({}) is None


@pytest.mark.parametrize(
    "socket_path",
    [
        "",
        "relative.sock",
        "~/kan.sock",
        "http://127.0.0.1:8080",
        "tcp://127.0.0.1:8080",
        "unix:///tmp/kan.sock",
        "localhost:8080",
        "127.0.0.1:8080",
    ],
)
def test_live_transport_rejects_non_absolute_unix_socket_paths(socket_path: str) -> None:
    with pytest.raises(DaemonTransportError):
        live_client_factory_from_config({"live_transport": {"unix_socket_path": socket_path}})


def test_live_transport_rejects_missing_unix_socket_path(tmp_path: Path) -> None:
    missing = tmp_path / "missing.sock"

    with pytest.raises(DaemonTransportError, match="does not exist"):
        live_client_factory_from_config({"live_transport": {"unix_socket_path": str(missing)}})


def test_live_transport_rejects_regular_file_and_directory(tmp_path: Path) -> None:
    regular_file = tmp_path / "not-a-socket"
    regular_file.write_text("not a socket", encoding="utf-8")

    with pytest.raises(DaemonTransportError, match="not a Unix socket"):
        live_client_factory_from_config({"live_transport": {"unix_socket_path": str(regular_file)}})

    with pytest.raises(DaemonTransportError, match="not a Unix socket"):
        live_client_factory_from_config({"live_transport": {"unix_socket_path": str(tmp_path)}})


def test_live_transport_requires_nested_config_key() -> None:
    with pytest.raises(DaemonTransportError, match="live_transport.unix_socket_path"):
        live_client_factory_from_config({"unix_socket_path": "/tmp/kan.sock"})
