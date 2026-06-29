from __future__ import annotations

import json
import os
import stat
from typing import Any

import pytest

from atn_plugin.client import DaemonClient
from atn_plugin.client import transport as transport_module
from atn_plugin.client.daemon import (
    OP_STATUS_READ,
    OP_STREAM_ACK,
    OP_VERSION_READ,
)
from atn_plugin.client.live import live_client_factory_from_config
from atn_plugin.client.transport import UnixSocketDaemonTransport
from atn_plugin.errors import DaemonCommandError, DaemonTransportError
from atn_plugin.protocol import JsonObject
from atn_plugin.tools import register_tools

BASE_RESPONSE: JsonObject = {
    "protocol_version": "atn-protocol-v1alpha0",
    "daemon_version": "0.0.0-live-smoke",
    "feature_groups": ["version.read", "command_envelope", "structured_error"],
    "live_readiness": False,
}


def test_unix_socket_transport_reads_version_and_status_live_smoke(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/atn-controld.sock"
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
            "params": {"protocol_version": "atn-protocol-v1alpha0"},
            "request_id": "plugin-live-version-read",
            "schema_version": 1,
        },
        {
            "command": OP_STATUS_READ,
            "params": {"protocol_version": "atn-protocol-v1alpha0"},
            "request_id": "plugin-live-status-read",
            "schema_version": 1,
        },
    ]
    assert socket_script.connected_paths == [socket_path, socket_path]


def test_configured_register_time_factory_powers_status_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/atn-controld.sock"
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
    status = json.loads(ctx.handler("atn_daemon_status")({}))

    assert status["ok"] is True
    assert status["data"]["status"] == "registered-live-smoke"
    assert socket_script.requests == [
        {
            "command": OP_STATUS_READ,
            "params": {"protocol_version": "atn-protocol-v1alpha0"},
            "request_id": "plugin-live-status-read",
            "schema_version": 1,
        }
    ]


def test_unix_socket_transport_accepts_control_status_shape_without_readiness_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/atn-controld.sock"
    patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={
            OP_VERSION_READ: {
                "protocol_version": "atn-protocol-v1alpha0",
                "daemon_version": "0.0.0-control",
                "feature_groups": ["version.read", "command_envelope", "structured_error"],
            },
            OP_STATUS_READ: {
                "protocol_version": "atn-protocol-v1alpha0",
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


def test_unix_socket_transport_maps_stream_tail_to_canonical_stream_replay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/atn-controld.sock"
    old_frame: JsonObject = {
        "cursor": "cur_000000000011_evt_old",
        "is_replay": True,
        "event": {
            "schema_version": 1,
            "event_id": "evt_old",
            "session_id": "sess-1",
            "session_type": "delegation",
            "phase": "running",
            "type": "member_ready",
            "from": "agent-1",
            "to": ["agent-mod"],
            "created_at": "2026-06-10T00:00:00Z",
            "payload": {"summary": "old"},
        },
    }
    new_frame: JsonObject = {
        "cursor": "cur_000000000012_evt_01HV",
        "is_replay": True,
        "event": {
            "schema_version": 1,
            "event_id": "evt_01HV",
            "session_id": "sess-1",
            "session_type": "delegation",
            "phase": "running",
            "type": "member_ready",
            "from": "agent-1",
            "to": ["agent-mod"],
            "created_at": "2026-06-10T00:00:00Z",
            "payload": {"summary": "ok"},
        },
    }
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={
            OP_VERSION_READ: {
                **BASE_RESPONSE,
                "feature_groups": [
                    "version.read",
                    "command_envelope",
                    "structured_error",
                    "stream_frame",
                ],
            },
            "stream.replay": {"frames": [old_frame, new_frame], "follow_bounded": False},
        },
    )
    client = DaemonClient(UnixSocketDaemonTransport(socket_path, timeout=1.0))

    tail = client.read_stream_tail(
        session_id="sess-1",
        member="agent-1",
        since_cursor="cur_prev",
        limit=1,
    )

    assert tail.protocol_version == "atn-protocol-v1alpha0"
    assert tail.next_cursor == "cur_000000000012_evt_01HV"
    assert len(tail.frames) == 1
    assert tail.frames[0].event.event_id == "evt_01HV"
    assert socket_script.requests == [
        {
            "command": OP_VERSION_READ,
            "params": {"protocol_version": "atn-protocol-v1alpha0"},
            "request_id": "plugin-live-version-read",
            "schema_version": 1,
        },
        {
            "command": "stream.replay",
            "params": {
                "member": "agent-1",
                "session_id": "sess-1",
                "since": "cur_prev",
            },
            "request_id": "plugin-live-stream-tail",
            "schema_version": 1,
        },
    ]


def test_unix_socket_transport_maps_stream_ack_to_canonical_daemon_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/atn-controld.sock"
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={
            OP_VERSION_READ: {
                **BASE_RESPONSE,
                "feature_groups": [
                    "version.read",
                    "command_envelope",
                    "structured_error",
                    "stream_frame",
                    "stream.ack",
                ],
            },
            OP_STREAM_ACK: {
                "command_id": "cmd-stream-ack-partc001",
                "event_id": "evt_stream_ack_partc001",
                "session_id": "sess-1",
                "request_id": "daemon-req-stream-ack",
                "deduplicated": True,
            },
        },
    )
    client = DaemonClient(UnixSocketDaemonTransport(socket_path, timeout=1.0))

    result = client.ack_stream(
        session_id="sess-1",
        member="agent-1",
        cursor="cur_000000000012_evt_01HV",
        command_id="cmd-stream-ack-partc001",
    )

    assert result.command_id == "cmd-stream-ack-partc001"
    assert result.event_id == "evt_stream_ack_partc001"
    assert result.session_id == "sess-1"
    assert result.request_id == "daemon-req-stream-ack"
    assert result.deduplicated is True
    assert socket_script.requests == [
        {
            "command": "version.read",
            "params": {"protocol_version": "atn-protocol-v1alpha0"},
            "request_id": "plugin-live-version-read",
            "schema_version": 1,
        },
        {
            "command": "stream.ack",
            "params": {
                "command_id": "cmd-stream-ack-partc001",
                "cursor": "cur_000000000012_evt_01HV",
                "member": "agent-1",
                "session_id": "sess-1",
            },
            "request_id": "plugin-live-stream-ack",
            "schema_version": 1,
        },
    ]


def test_unix_socket_transport_unwraps_command_submit_to_canonical_daemon_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/atn-controld.sock"
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={
            "council.ready": {
                "cursor": "cur_000000000005_evt_member_ready_cmd_council_ready_ltran003",
                "event_id": "evt_member_ready_cmd_council_ready_ltran003",
                "offset": 5,
                "deduplicated": False,
            },
        },
    )
    client = DaemonClient(UnixSocketDaemonTransport(socket_path, timeout=1.0))
    envelope = client.build_command_envelope(
        command="council.ready",
        payload={
            "session_id": "sess-1",
            "actor": "agent-1",
            "command_id": "cmd_council_ready_ltran003",
            "payload": {"summary": "ready"},
        },
        request_id="req-council-ready-ltran003",
        idempotency_key="idem-cmd_council_ready_ltran003",
    )

    result = client.submit_command(envelope)

    assert result.command_id == "cmd_council_ready_ltran003"
    assert result.event_id == "evt_member_ready_cmd_council_ready_ltran003"
    assert result.session_id == "sess-1"
    assert result.request_id == "req-council-ready-ltran003"
    assert socket_script.requests == [
        {
            "command": "council.ready",
            "params": {
                "actor": "agent-1",
                "command_id": "cmd_council_ready_ltran003",
                "payload": {"summary": "ready"},
                "session_id": "sess-1",
            },
            "request_id": "req-council-ready-ltran003",
            "schema_version": 1,
        }
    ]


def test_unix_socket_transport_preserves_structured_lock_agenda_payload_to_canonical_daemon_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/atn-controld.sock"
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={
            "council.lock_agenda": {
                "cursor": "cur_000000000006_evt_agenda_locked_cmd_lock_agenda_ltran004",
                "event_id": "evt_agenda_locked_cmd_lock_agenda_ltran004",
                "offset": 6,
                "deduplicated": False,
            },
        },
    )
    client = DaemonClient(UnixSocketDaemonTransport(socket_path, timeout=1.0))
    agenda_payload = {
        "decision_question": "Which visible ATN agenda context must reach selected runners?",
        "success_criteria": [
            "selected-runner prompts include the locked decision question",
            "selected-runner prompts include success criteria and out-of-scope policy",
        ],
        "out_of_scope_policy": "Defer provider, gateway, and Discord runtime mutation.",
        "context": {"source": "control/NEWFIX-007"},
    }
    envelope = client.build_command_envelope(
        command="council.lock_agenda",
        payload={
            "session_id": "sess-1",
            "actor": "moderator-1",
            "command_id": "cmd_lock_agenda_ltran004",
            "payload": agenda_payload,
        },
        request_id="req-lock-agenda-ltran004",
        idempotency_key="idem-cmd_lock_agenda_ltran004",
    )

    result = client.submit_command(envelope)

    assert result.command_id == "cmd_lock_agenda_ltran004"
    assert result.event_id == "evt_agenda_locked_cmd_lock_agenda_ltran004"
    assert result.session_id == "sess-1"
    assert result.request_id == "req-lock-agenda-ltran004"
    assert socket_script.requests == [
        {
            "command": "council.lock_agenda",
            "params": {
                "actor": "moderator-1",
                "command_id": "cmd_lock_agenda_ltran004",
                "payload": agenda_payload,
                "session_id": "sess-1",
            },
            "request_id": "req-lock-agenda-ltran004",
            "schema_version": 1,
        }
    ]


def test_unix_socket_transport_rejects_lock_agenda_unrepresentable_idempotency_before_socket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/atn-controld.sock"
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={"council.lock_agenda": {"event_id": "unused"}},
    )
    client = DaemonClient(UnixSocketDaemonTransport(socket_path, timeout=1.0))
    envelope = client.build_command_envelope(
        command="council.lock_agenda",
        payload={
            "session_id": "sess-1",
            "actor": "moderator-1",
            "command_id": "cmd_lock_agenda_ltran005",
            "payload": {
                "decision_question": "Which agenda context is required?",
                "success_criteria": ["required fields are preserved"],
                "out_of_scope_policy": "No local ID generation or CLI fallback.",
            },
        },
        request_id="req-lock-agenda-ltran005",
        idempotency_key="different-idempotency-key",
    )

    with pytest.raises(DaemonTransportError) as exc_info:
        client.submit_command(envelope)

    assert "command.submit cannot be represented as daemon command_id" in str(exc_info.value)
    assert "payload.command_id or idem-{payload.command_id}" in str(exc_info.value)
    assert socket_script.requests == []
    assert socket_script.connected_paths == []


def test_unix_socket_transport_preserves_command_submit_structured_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/atn-controld.sock"
    patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={
            "council.ready": {
                "__raw_response__": {
                    "schema_version": 1,
                    "request_id": "req-council-ready-ltran003",
                    "ok": False,
                    "error": {
                        "category": "conflict",
                        "message": "command_id already used with different payload",
                        "retryable": False,
                        "command_id": "cmd_council_ready_ltran003",
                        "session_id": "sess-1",
                        "request_id": "req-council-ready-ltran003",
                    },
                }
            },
        },
    )
    client = DaemonClient(UnixSocketDaemonTransport(socket_path, timeout=1.0))
    envelope = client.build_command_envelope(
        command="council.ready",
        payload={
            "session_id": "sess-1",
            "actor": "agent-1",
            "command_id": "cmd_council_ready_ltran003",
            "payload": {"summary": "ready"},
        },
        request_id="req-council-ready-ltran003",
        idempotency_key="idem-cmd_council_ready_ltran003",
    )

    with pytest.raises(DaemonCommandError) as exc_info:
        client.submit_command(envelope)

    assert exc_info.value.details.category == "conflict"
    assert exc_info.value.details.command_id == "cmd_council_ready_ltran003"


def test_unix_socket_transport_rejects_unrepresentable_idempotency_boundary_before_socket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = "/var/run/atn-controld.sock"
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={"council.ready": {"event_id": "unused"}},
    )
    client = DaemonClient(UnixSocketDaemonTransport(socket_path, timeout=1.0))
    envelope = client.build_command_envelope(
        command="council.ready",
        payload={
            "session_id": "sess-1",
            "actor": "agent-1",
            "command_id": "cmd_council_ready_ltran003",
            "payload": {"summary": "ready"},
        },
        request_id="req-council-ready-ltran003",
        idempotency_key="different-idempotency-key",
    )

    with pytest.raises(DaemonTransportError, match="cannot be represented as daemon command_id"):
        client.submit_command(envelope)

    assert socket_script.requests == []
    assert socket_script.connected_paths == []


def test_live_client_factory_uses_explicit_config_only(monkeypatch: pytest.MonkeyPatch) -> None:
    socket_path = "/var/run/atn-controld.sock"
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
            "params": {"protocol_version": "atn-protocol-v1alpha0"},
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
        response = self.script.responses[operation]
        raw_response = response.get("__raw_response__")
        if isinstance(raw_response, dict):
            envelope = raw_response
        else:
            envelope = {
                "schema_version": 1,
                "request_id": request["request_id"],
                "ok": True,
                "result": response,
            }
        self._response = (
            json.dumps(
                envelope,
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
