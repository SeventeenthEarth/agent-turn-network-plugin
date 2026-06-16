from __future__ import annotations

from pathlib import Path

import pytest

from kkachi_agent_network_plugin.client.live import (
    configured_live_client_factory,
    live_client_factory_from_config,
    load_plugin_local_live_config,
    parse_plugin_local_live_config,
)
from kkachi_agent_network_plugin.errors import DaemonTransportError


def test_no_config_preserves_fail_closed_no_client_factory() -> None:
    assert configured_live_client_factory(None) is None
    assert configured_live_client_factory({}) is None


def test_load_plugin_local_live_config_accepts_only_approved_shape(tmp_path: Path) -> None:
    socket_path = "/var/run/kkachi-agent-networkd.sock"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f'live_transport:\n  unix_socket_path: "{socket_path}"\n',
        encoding="utf-8",
    )

    assert load_plugin_local_live_config(config_path) == {
        "live_transport": {"unix_socket_path": socket_path}
    }


def test_load_plugin_local_live_config_missing_file_is_no_config(tmp_path: Path) -> None:
    assert load_plugin_local_live_config(tmp_path / "config.yaml") is None


def test_load_plugin_local_live_config_wraps_non_utf8_decode_failure(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(DaemonTransportError, match="could not be loaded"):
        load_plugin_local_live_config(config_path)


def test_load_plugin_local_live_config_wraps_path_check_os_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.yaml"
    original_exists = Path.exists

    def fail_exists(path: Path) -> bool:
        if path == config_path:
            raise OSError("permission denied")
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", fail_exists)

    with pytest.raises(DaemonTransportError, match="could not be loaded"):
        load_plugin_local_live_config(config_path)


@pytest.mark.parametrize(
    "text",
    [
        "live_transport:\n  unix_socket_path: /tmp/kan.sock\n  extra: true\n",
        "other:\n  unix_socket_path: /tmp/kan.sock\n",
        "live_transport: /tmp/kan.sock\n",
        "live_transport:\n  unix_socket_path:\n",
        "live_transport:\n  unix_socket_path: ${KAN_DAEMON_SOCKET}\n",
        "live_transport:\n  unix_socket_path: [/tmp/kan.sock]\n",
    ],
)
def test_plugin_local_live_config_rejects_malformed_or_unknown_shape(text: str) -> None:
    with pytest.raises(DaemonTransportError):
        parse_plugin_local_live_config(text)


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
