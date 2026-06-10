from __future__ import annotations

import json
import os
import stat
from typing import Any

import pytest

from kkachi_agent_network_plugin.client import DaemonClient
from kkachi_agent_network_plugin.client import transport as transport_module
from kkachi_agent_network_plugin.client.daemon import (
    OP_STATUS_READ,
    OP_STREAM_TAIL,
    OP_VERSION_READ,
)
from kkachi_agent_network_plugin.client.live import live_client_factory_from_config
from kkachi_agent_network_plugin.client.transport import UnixSocketDaemonTransport
from kkachi_agent_network_plugin.errors import DaemonTransportError
from kkachi_agent_network_plugin.protocol import JsonObject
from kkachi_agent_network_plugin.tools import register_tools

BASE_RESPONSE: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-live-smoke",
    "feature_groups": ["version.read", "command_envelope", "structured_error"],
    "live_readiness": False,
}


def test_unix_socket_transport_reads_version_and_status_live_smoke(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/kkachi-agent-networkd.sock"
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={
            OP_VERSION_READ: dict(BASE_RESPONSE),
            OP_STATUS_READ: {**BASE_RESPONSE, "status": "local-smoke-ready"},
        },
    )
    client = DaemonClient(UnixSocketDaemonTransport(socket_path, timeout=1.0))

    version = client.read_version()
    status = client.read_status()

    assert version.daemon_version == "0.0.0-live-smoke"
    assert status.status == "local-smoke-ready"
    assert socket_script.requests == [
        {
            "command": OP_VERSION_READ,
            "params": {"protocol_version": "kan-protocol-v1alpha0"},
            "request_id": "plugin-live-version-read",
            "schema_version": 1,
        },
        {
            "command": OP_STATUS_READ,
            "params": {"protocol_version": "kan-protocol-v1alpha0"},
            "request_id": "plugin-live-status-read",
            "schema_version": 1,
        },
    ]
    assert socket_script.connected_paths == [socket_path, socket_path]


def test_configured_register_time_factory_powers_status_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/kkachi-agent-networkd.sock"
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={OP_STATUS_READ: {**BASE_RESPONSE, "status": "registered-live-smoke"}},
    )
    ctx = FakePluginContext()
    register_tools(
        ctx,
        config={"live_transport": {"unix_socket_path": socket_path}},
    )
    status = json.loads(ctx.handler("kan_daemon_status")({}))

    assert status["ok"] is True
    assert status["data"]["status"] == "registered-live-smoke"
    assert socket_script.requests == [
        {
            "command": OP_STATUS_READ,
            "params": {"protocol_version": "kan-protocol-v1alpha0"},
            "request_id": "plugin-live-status-read",
            "schema_version": 1,
        }
    ]


def test_unix_socket_transport_accepts_control_status_shape_without_readiness_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/kkachi-agent-networkd.sock"
    patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={
            OP_VERSION_READ: {
                "protocol_version": "kan-protocol-v1alpha0",
                "daemon_version": "0.0.0-control",
                "feature_groups": ["version.read", "command_envelope", "structured_error"],
            },
            OP_STATUS_READ: {
                "protocol_version": "kan-protocol-v1alpha0",
                "daemon_version": "0.0.0-control",
                "daemon": "running",
                "feature_groups": ["version.read", "command_envelope", "structured_error"],
            },
        },
    )
    client = DaemonClient(UnixSocketDaemonTransport(socket_path, timeout=1.0))

    version = client.read_version()
    status = client.read_status()

    assert version.live_readiness is False
    assert status.live_readiness is False
    assert status.status == "running"


def test_unix_socket_transport_rejects_stream_and_write_operations_before_socket_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/kkachi-agent-networkd.sock"
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={OP_STATUS_READ: {**BASE_RESPONSE, "status": "unused"}},
    )
    transport = UnixSocketDaemonTransport(socket_path, timeout=1.0)

    with pytest.raises(DaemonTransportError, match="status.read and version.read only"):
        transport.request(OP_STREAM_TAIL, {"protocol_version": "kan-protocol-v1alpha0"})

    assert socket_script.requests == []
    assert socket_script.connected_paths == []


def test_live_client_factory_uses_explicit_config_only(monkeypatch: pytest.MonkeyPatch) -> None:
    socket_path = "/var/run/kkachi-agent-networkd.sock"
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={OP_VERSION_READ: dict(BASE_RESPONSE)},
    )
    monkeypatch.setenv("KAN_DAEMON_SOCKET", "/tmp/forbidden.sock")
    factory = live_client_factory_from_config({"live_transport": {"unix_socket_path": socket_path}})
    client = factory()
    version = client.read_version()

    assert version.daemon_version == "0.0.0-live-smoke"
    assert socket_script.requests == [
        {
            "command": OP_VERSION_READ,
            "params": {"protocol_version": "kan-protocol-v1alpha0"},
            "request_id": "plugin-live-version-read",
            "schema_version": 1,
        }
    ]
    assert socket_script.connected_paths == [socket_path]


class FakePluginContext:
    def __init__(self) -> None:
        self.registered_tools: list[dict[str, Any]] = []

    def register_tool(self, **kwargs: Any) -> None:
        self.registered_tools.append(kwargs)

    def handler(self, name: str) -> Any:
        for tool in self.registered_tools:
            if tool["name"] == name:
                return tool["handler"]
        raise AssertionError(f"missing registered tool: {name}")


class SocketScript:
    def __init__(self, *, socket_path: str, responses: dict[str, JsonObject]) -> None:
        self.socket_path = socket_path
        self.responses = responses
        self.requests: list[JsonObject] = []
        self.connected_paths: list[str] = []

    def socket_factory(self, family: int, socket_type: int) -> FakeSocket:
        assert family == transport_module.socket.AF_UNIX
        assert socket_type == transport_module.socket.SOCK_STREAM
        return FakeSocket(self)


class FakeSocket:
    def __init__(self, script: SocketScript) -> None:
        self.script = script
        self._response = b""

    def __enter__(self) -> FakeSocket:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def settimeout(self, timeout: float) -> None:
        assert timeout > 0

    def connect(self, socket_path: str) -> None:
        assert socket_path == self.script.socket_path
        self.script.connected_paths.append(socket_path)

    def sendall(self, payload: bytes) -> None:
        request = json.loads(payload.decode("utf-8"))
        self.script.requests.append(request)
        operation = request["command"]
        self._response = (
            json.dumps(
                {
                    "schema_version": 1,
                    "request_id": request["request_id"],
                    "ok": True,
                    "result": self.script.responses[operation],
                },
                sort_keys=True,
            ).encode("utf-8")
            + b"\n"
        )

    def recv(self, _size: int) -> bytes:
        response = self._response
        self._response = b""
        return response

    def close(self) -> None:
        pass


def patch_unix_socket(
    monkeypatch: pytest.MonkeyPatch,
    *,
    socket_path: str,
    responses: dict[str, JsonObject],
) -> SocketScript:
    script = SocketScript(socket_path=socket_path, responses=responses)

    def fake_lstat(value: str) -> os.stat_result:
        assert value == socket_path
        return os.stat_result((stat.S_IFSOCK | 0o600, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    monkeypatch.setattr(transport_module.os, "lstat", fake_lstat)
    monkeypatch.setattr(transport_module.socket, "socket", script.socket_factory)
    return script
