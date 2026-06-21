from __future__ import annotations

import importlib.util
import json
import stat
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml  # type: ignore[import-untyped]

from hermes_unified_network_plugin.client import DaemonClient, StaticDaemonTransport
from hermes_unified_network_plugin.client import transport as transport_module
from hermes_unified_network_plugin.client.daemon import OP_STATUS_READ
from hermes_unified_network_plugin.protocol import JsonObject

ROOT = Path(__file__).resolve().parents[2]


EXPECTED_TOOLS = [
    "kan_daemon_status",
    "kan_compatibility_diagnostics",
    "kan_stream_tail",
    "kan_stream_ack",
    "kan_delegate_new",
    "kan_delegate_action",
    "kan_council_command",
    "kan_selected_participant_response",
    "kan_delivery_evidence",
    "kan_surface_render_projection",
    "kan_discussion_activation_plan",
    "kan_discord_send_message",
]

EXPECTED_BUNDLED_SKILLS = [
    "kan-plugin",
    "kan-moderator",
    "kan-participant",
]


def test_plugin_manifest_declares_fake_injected_tool_surface() -> None:
    manifest = yaml.safe_load((ROOT / "plugin.yaml").read_text(encoding="utf-8"))

    assert manifest == {
        "name": "hermes-unified-network-plugin",
        "version": "0.1.0",
        "description": (
            "Hermes plugin adapter for Hermes Unified Network; exposes fake/injected "
            "read-only tools, delegation/review command-envelope tools, CNDIS "
            "council/delivery-evidence tools, selected participant response proof, "
            "pure visible-surface projection rendering, a pure RUNFIX discussion "
            "activation planner/doctor, and an injected-only Discord helper without "
            "slash-command bindings."
        ),
        "author": "17번째 지구 Kkachi",
        "kind": "standalone",
        "provides_tools": EXPECTED_TOOLS,
        "provides_hooks": [],
        "provides_commands": [],
    }


def test_root_entrypoint_matches_hermes_directory_plugin_contract() -> None:
    module = _load_root_entrypoint()

    assert callable(module.register)
    fake_ctx = FakePluginContext()
    module.register(fake_ctx)

    assert [tool["name"] for tool in fake_ctx.registered_tools] == EXPECTED_TOOLS
    assert all(callable(tool["handler"]) for tool in fake_ctx.registered_tools)
    assert [skill["name"] for skill in fake_ctx.registered_skills] == EXPECTED_BUNDLED_SKILLS
    assert all(skill["path"].name == "SKILL.md" for skill in fake_ctx.registered_skills)
    assert all(skill["path"].exists() for skill in fake_ctx.registered_skills)
    assert fake_ctx.registered_hooks == []
    assert fake_ctx.registered_commands == []


def test_root_entrypoint_uses_adjacent_config_when_no_explicit_config_or_factory(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    module = _load_root_entrypoint()
    socket_path = "/var/run/hund.sock"
    (tmp_path / "config.yaml").write_text(
        f'live_transport:\n  unix_socket_path: "{socket_path}"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "_PLUGIN_ROOT", tmp_path)
    socket_script = patch_unix_socket(
        monkeypatch,
        socket_path=socket_path,
        responses={
            OP_STATUS_READ: {
                "protocol_version": "kan-protocol-v1alpha0",
                "daemon_version": "0.0.0-adjacent-config",
                "status": "adjacent-config-ready",
                "feature_groups": ["version.read", "command_envelope", "structured_error"],
                "live_readiness": False,
            }
        },
    )
    fake_ctx = FakePluginContext()

    module.register(fake_ctx)
    status = json.loads(fake_ctx.handler("kan_daemon_status")({}))

    assert status["ok"] is True
    assert status["data"]["status"] == "adjacent-config-ready"
    assert socket_script.connected_paths == [socket_path]


def test_root_entrypoint_malformed_adjacent_config_registers_fail_closed_handler(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    module = _load_root_entrypoint()
    (tmp_path / "config.yaml").write_text(
        "live_transport:\n  unix_socket_path: /tmp/kan.sock\n  extra: true\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "_PLUGIN_ROOT", tmp_path)
    fake_ctx = FakePluginContext()

    module.register(fake_ctx)
    status = json.loads(fake_ctx.handler("kan_daemon_status")({}))

    assert [tool["name"] for tool in fake_ctx.registered_tools] == EXPECTED_TOOLS
    assert status["ok"] is False
    assert status["error"]["category"] == "unavailable"
    assert "config.yaml" in status["error"]["message"]


def test_root_entrypoint_non_utf8_adjacent_config_registers_fail_closed_handler(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    module = _load_root_entrypoint()
    (tmp_path / "config.yaml").write_bytes(b"\xff\xfe\x00")
    monkeypatch.setattr(module, "_PLUGIN_ROOT", tmp_path)
    fake_ctx = FakePluginContext()

    module.register(fake_ctx)
    status = json.loads(fake_ctx.handler("kan_daemon_status")({}))

    assert [tool["name"] for tool in fake_ctx.registered_tools] == EXPECTED_TOOLS
    assert status["ok"] is False
    assert status["error"]["category"] == "unavailable"
    assert "config.yaml" in status["error"]["message"]


def test_root_entrypoint_preserves_explicit_config_precedence(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    module = _load_root_entrypoint()
    explicit_config = {"live_transport": {"unix_socket_path": "/explicit/socket.sock"}}
    captured: dict[str, object] = {}
    (tmp_path / "config.yaml").write_text(
        'live_transport:\n  unix_socket_path: "/adjacent/socket.sock"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "_PLUGIN_ROOT", tmp_path)
    monkeypatch.setattr(
        module,
        "register_tools",
        lambda ctx, *, client_factory=None, config=None: captured.update(
            {"client_factory": client_factory, "config": config}
        ),
    )

    module.register(FakePluginContext(), config=explicit_config)

    assert captured == {"client_factory": None, "config": explicit_config}


def test_root_entrypoint_preserves_explicit_client_factory_precedence(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    module = _load_root_entrypoint()

    def client_factory() -> DaemonClient:
        return DaemonClient(StaticDaemonTransport({}))

    captured: dict[str, object] = {}
    (tmp_path / "config.yaml").write_text(
        'live_transport:\n  unix_socket_path: "/adjacent/socket.sock"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "_PLUGIN_ROOT", tmp_path)
    monkeypatch.setattr(
        module,
        "register_tools",
        lambda ctx, *, client_factory=None, config=None: captured.update(
            {"client_factory": client_factory, "config": config}
        ),
    )

    module.register(FakePluginContext(), client_factory=client_factory)

    assert captured == {"client_factory": client_factory, "config": None}


def _load_root_entrypoint() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "hermes_plugins.hermes_unified_network_plugin_under_test",
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakePluginContext:
    def __init__(self) -> None:
        self.registered_tools: list[dict[str, Any]] = []
        self.registered_skills: list[dict[str, Any]] = []
        self.registered_hooks: list[tuple[str, Any]] = []
        self.registered_commands: list[dict[str, Any]] = []

    def register_tool(self, **kwargs: Any) -> None:
        self.registered_tools.append(kwargs)

    def register_skill(self, **kwargs: Any) -> None:
        self.registered_skills.append(kwargs)

    def handler(self, name: str) -> Any:
        for tool in self.registered_tools:
            if tool["name"] == name:
                return tool["handler"]
        raise AssertionError(f"missing registered tool: {name}")

    def register_hook(self, hook_name: str, callback: Any) -> None:
        self.registered_hooks.append((hook_name, callback))

    def register_command(self, *args: Any, **kwargs: Any) -> None:
        self.registered_commands.append({"args": args, "kwargs": kwargs})


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
        response = self.script.responses[request["command"]]
        self._response = (
            json.dumps(
                {
                    "schema_version": 1,
                    "request_id": request["request_id"],
                    "ok": True,
                    "result": response,
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
    monkeypatch: Any,
    *,
    socket_path: str,
    responses: dict[str, JsonObject],
) -> SocketScript:
    script = SocketScript(socket_path=socket_path, responses=responses)

    def fake_lstat(value: str) -> object:
        assert value == socket_path
        return type(
            "FakeStat",
            (),
            {"st_mode": stat.S_IFSOCK | 0o600},
        )()

    monkeypatch.setattr(transport_module.os, "lstat", fake_lstat)
    monkeypatch.setattr(transport_module.socket, "socket", script.socket_factory)
    return script
