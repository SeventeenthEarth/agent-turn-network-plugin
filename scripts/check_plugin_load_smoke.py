from __future__ import annotations

import ast
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import tomllib
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_MODULE = "kkachi_agent_network_plugin"
PACKAGE_NAME = "kkachi-agent-network-plugin"
TOOLSET = "kkachi_agent_network"
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
LIVE_LOOKING_ENV = {
    "HERMES_HOME": "/live/hermes/home",
    "KAN_DAEMON_SOCKET": "/live/kan.sock",
    "KAN_GATEWAY_TOKEN": "live-looking-token",
    "KAB_GATEWAY_TOKEN": "live-looking-kab-token",
    "DISCORD_TOKEN": "live-looking-discord-token",
    "DISCORD_TEST_TARGET": "active-discord-thread",
    "KAN_PROVIDER": "live-provider",
}


def load_module(path: Path, name: str, *, package_root: bool = False) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        name,
        path,
        submodule_search_locations=[str(path.parent)] if package_root else None,
    )
    if spec is None or spec.loader is None:
        raise SystemExit(f"plugin-load smoke cannot load module spec: {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise SystemExit(f"plugin-load smoke failed to load module {path}: {exc}") from exc
    return module


def make_isolated_plugin_home(root: Path, destination: Path) -> Path:
    plugin_home = destination / "plugin-home" / PACKAGE_NAME
    plugin_home.mkdir(parents=True)
    shutil.copy2(root / "plugin.yaml", plugin_home / "plugin.yaml")
    shutil.copy2(root / "__init__.py", plugin_home / "__init__.py")
    shutil.copytree(root / "src", plugin_home / "src")
    shutil.copy2(root / "pyproject.toml", plugin_home / "pyproject.toml")
    return plugin_home


def require_manifest(plugin_home: Path) -> None:
    manifest = yaml.safe_load((plugin_home / "plugin.yaml").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise SystemExit("plugin-load smoke manifest must be a YAML mapping")
    if manifest.get("name") != PACKAGE_NAME:
        raise SystemExit(f"plugin-load smoke manifest name mismatch: {manifest.get('name')!r}")
    if manifest.get("provides_tools") != EXPECTED_TOOLS:
        raise SystemExit(
            "plugin-load smoke manifest provides_tools mismatch: "
            f"{manifest.get('provides_tools')!r}"
        )
    if manifest.get("provides_hooks") != []:
        raise SystemExit(
            "plugin-load smoke manifest provides_hooks must remain explicit empty list"
        )
    if manifest.get("provides_commands") != []:
        raise SystemExit(
            "plugin-load smoke manifest provides_commands must remain explicit empty list"
        )


def require_package_and_bundled_skill(plugin_home: Path) -> None:
    pyproject = tomllib.loads((plugin_home / "pyproject.toml").read_text(encoding="utf-8"))
    wheel = (
        pyproject.get("tool", {})
        .get("hatch", {})
        .get("build", {})
        .get("targets", {})
        .get("wheel", {})
    )
    if wheel.get("packages") != ["src/kkachi_agent_network_plugin"]:
        raise SystemExit("plugin-load smoke wheel package inclusion mismatch")

    skill = plugin_home / "src" / PACKAGE_MODULE / "bundled_skills" / "kan-plugin" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    for phrase in ("name: kan-plugin", "provides_commands: []", "kan_session_status"):
        if phrase not in text:
            raise SystemExit(f"plugin-load smoke bundled skill missing phrase: {phrase}")

    package = load_module(
        plugin_home / "src" / PACKAGE_MODULE / "__init__.py",
        f"{PACKAGE_MODULE}_plugin_load_smoke",
    )
    metadata = getattr(package, "package_metadata", None)
    if not callable(metadata):
        raise SystemExit("plugin-load smoke package_metadata is not callable")
    if metadata().get("name") != PACKAGE_NAME:
        raise SystemExit(f"plugin-load smoke package metadata mismatch: {metadata()!r}")


def require_python311_syntax(plugin_home: Path) -> None:
    for path in sorted([plugin_home / "__init__.py", *(plugin_home / "src").rglob("*.py")]):
        try:
            ast.parse(
                path.read_text(encoding="utf-8"),
                filename=str(path.relative_to(plugin_home)),
                feature_version=(3, 11),
            )
        except SyntaxError as exc:
            raise SystemExit(f"plugin-load smoke Python 3.11 syntax failure: {exc}") from exc


def path_exposes_package(path: str) -> bool:
    """Return whether a sys.path entry could satisfy the runtime package import.

    This keeps the smoke from masking root-entrypoint src bootstrapping bugs.
    """

    base = Path(path or os.getcwd()).resolve()
    candidates = (base / PACKAGE_MODULE, base / "src" / PACKAGE_MODULE)
    return any(candidate.is_dir() for candidate in candidates)


def entrypoint_sys_path() -> list[str]:
    return [path for path in sys.path if not path_exposes_package(path)]


def pop_package_modules() -> dict[str, ModuleType]:
    popped: dict[str, ModuleType] = {}
    for name in list(sys.modules):
        if name == PACKAGE_MODULE or name.startswith(f"{PACKAGE_MODULE}."):
            popped[name] = sys.modules.pop(name)
    return popped


def restore_package_modules(previous: dict[str, ModuleType]) -> None:
    for name in list(sys.modules):
        if name == PACKAGE_MODULE or name.startswith(f"{PACKAGE_MODULE}."):
            sys.modules.pop(name)
    sys.modules.update(previous)


def load_entrypoint(plugin_home: Path) -> ModuleType:
    previous_path = list(sys.path)
    previous_modules = pop_package_modules()
    try:
        sys.path[:] = entrypoint_sys_path()
        return load_module(
            plugin_home / "__init__.py",
            "kkachi_agent_network_plugin_root_plugin_load_smoke",
            package_root=True,
        )
    finally:
        sys.path[:] = previous_path
        restore_package_modules(previous_modules)


def require_entrypoint_load(plugin_home: Path) -> FakeHermesContext:
    entrypoint = load_entrypoint(plugin_home)
    register = getattr(entrypoint, "register", None)
    if not callable(register):
        raise SystemExit("plugin-load smoke entrypoint register is not callable")

    context = FakeHermesContext()
    try:
        register(context)
    except Exception as exc:
        raise SystemExit(f"plugin-load smoke entrypoint register failed: {exc}") from exc

    registered_tool_names = [tool.get("name") for tool in context.registered_tools]
    if registered_tool_names != EXPECTED_TOOLS:
        raise SystemExit(
            "plugin-load smoke tool registration mismatch: "
            f"{registered_tool_names!r} != {EXPECTED_TOOLS!r}"
        )
    if context.registered_hooks:
        raise SystemExit("plugin-load smoke registered unsupported hooks")
    if context.registered_commands:
        raise SystemExit("plugin-load smoke registered unsupported commands")
    for tool in context.registered_tools:
        if tool.get("toolset") != TOOLSET:
            raise SystemExit(f"plugin-load smoke toolset mismatch: {tool!r}")
        if not isinstance(tool.get("schema"), dict):
            raise SystemExit(f"plugin-load smoke tool schema must be a mapping: {tool!r}")
        if not callable(tool.get("handler")):
            raise SystemExit(f"plugin-load smoke handler is not callable: {tool!r}")
    return context


def require_handler_fail_closed(context: FakeHermesContext) -> dict[str, str]:
    outputs: dict[str, str] = {}
    for tool in context.registered_tools:
        name = tool["name"]
        handler = tool["handler"]
        result = handler(representative_args(str(name)))
        if not isinstance(result, str):
            raise SystemExit(f"plugin-load smoke handler did not return JSON string: {name}")
        body = json.loads(result)
        if name in {"kan_surface_render_projection", "kan_discussion_activation_plan"}:
            if body.get("ok") is not True or body.get("live_readiness") is not False:
                raise SystemExit(
                    "plugin-load smoke pure local handler must succeed locally: "
                    f"{body}"
                )
            outputs[str(name)] = result
            continue
        if body.get("ok") is not False:
            raise SystemExit(
                f"plugin-load smoke handler must fail closed without injection: {body}"
            )
        if body.get("tool") != name:
            raise SystemExit(f"plugin-load smoke handler tool mismatch: {body}")
        if "error" not in body or not isinstance(body["error"], dict):
            raise SystemExit(f"plugin-load smoke handler missing structured error: {body}")
        if body["error"].get("category") not in {"unavailable", "validation"}:
            raise SystemExit(f"plugin-load smoke unexpected fail-closed category: {body}")
        outputs[str(name)] = result
    return outputs


def require_entrypoint_fail_closed(plugin_home: Path) -> dict[str, str]:
    return require_handler_fail_closed(require_entrypoint_load(plugin_home))


def representative_args(tool_name: str) -> dict[str, object]:
    if tool_name == "kan_daemon_status":
        return {}
    if tool_name == "kan_compatibility_diagnostics":
        return {"session_id": "sess-smoke"}
    if tool_name == "kan_stream_tail":
        return {"session_id": "sess-smoke", "member": "agent-smoke", "limit": 1}
    if tool_name == "kan_stream_ack":
        return {
            "session_id": "sess-smoke",
            "member": "agent-smoke",
            "cursor": "cur-smoke",
            "command_id": "cmd-smoke-stream-ack",
        }
    if tool_name == "kan_delegate_new":
        return {
            "session_id": "sess-smoke",
            "moderator": "moderator-smoke",
            "assignee": "assignee-smoke",
            "title": "Smoke delegation",
            "task": "Prove local handler fail-closed behavior.",
            "context": {},
            "participants": [],
            "acceptance": [],
            "expected_outputs": [],
            "limits": {},
            "request_id": "req-smoke-delegate-new",
            "idempotency_key": "idem-smoke-delegate-new",
        }
    if tool_name == "kan_delegate_action":
        return {
            "session_id": "sess-smoke",
            "command": "delegate.submit",
            "request_id": "req-smoke-delegate-action",
            "idempotency_key": "idem-smoke-delegate-action",
            "payload": {"command_id": "cmd-smoke"},
        }
    if tool_name == "kan_council_command":
        return {
            "session_id": "sess-smoke",
            "command": "council.ready",
            "request_id": "req-smoke-council",
            "idempotency_key": "idem-smoke-council",
            "payload": {"command_id": "cmd-smoke", "actor": "agent-smoke"},
        }
    if tool_name == "kan_selected_participant_response":
        return {
            "session_id": "sess-smoke",
            "selected_member": "agent-smoke",
            "speaker_selected_frame": {
                "cursor": "cur-smoke-selected",
                "event": {
                    "event_id": "evt-smoke-selected",
                    "session_id": "sess-smoke",
                    "type": "speaker_selected",
                    "to": ["agent-smoke"],
                    "payload": {"turn": 1, "member": "agent-smoke"},
                },
            },
            "participant_response": {
                "source": "control_membr_evidence",
                "member": "agent-smoke",
                "message": "local isolated plugin-load smoke",
                "role_substitution": False,
                "runner": {
                    "invocation_id": "run-smoke",
                    "started_event_id": "evt-smoke-started",
                    "terminal_event_id": "evt-smoke-terminal",
                    "terminal_event_type": "participant_response",
                    "adapter_kind": "hermes-agent",
                    "wrapper_binding_evidence": "local-smoke",
                },
            },
            "command_id": "cmd-smoke-speak",
            "request_id": "req-smoke-speak",
            "idempotency_key": "idem-smoke-speak",
            "ack_command_id": "cmd-smoke-ack",
        }
    if tool_name == "kan_delivery_evidence":
        return {
            "session_id": "sess-smoke",
            "command": "delegate.escalation_delivered",
            "request_id": "req-smoke-delivery",
            "idempotency_key": "idem-smoke-delivery",
            "payload": {"command_id": "cmd-smoke", "escalation": "evt-smoke"},
        }
    if tool_name == "kan_surface_render_projection":
        return {
            "projection": {
                "schema_version": 1,
                "session_id": "sess-smoke",
                "events": [
                    {
                        "cursor": "cur_000000000001_evt_smoke_session",
                        "event": {
                            "event_id": "evt-smoke-session",
                            "session_id": "sess-smoke",
                            "type": "session_created",
                            "payload": {"surface": {"kind": "local_fixture"}},
                        },
                    }
                ],
            }
        }
    if tool_name == "kan_discussion_activation_plan":
        return {
            "plan": {
                "schema_version": 1,
                "task_id": "plugin/RUNFIX-006",
                "control_dependency": {
                    "task_id": "control/RUNFIX-005",
                    "status": "completed/local-control",
                    "evidence_ref": "local-smoke-control-runfix-005",
                },
                "plugin_install": {
                    "installed": True,
                    "enabled": True,
                    "tool_names": [
                        "kan_daemon_status",
                        "kan_discussion_activation_plan",
                    ],
                },
                "control_daemon": {
                    "mode": "explicit",
                    "socket_or_config_ref": "local-smoke-config",
                    "compatibility_ref": "local-smoke-version-read",
                },
                "participant_profiles": [
                    {
                        "profile": "macho",
                        "tools_visible": True,
                        "bot_to_bot_enabled": False,
                        "evidence_ref": "local-smoke-profile-tools",
                    }
                ],
                "discord_parent_channel": {
                    "channel_id": "chan-smoke-parent",
                    "allow_list_inheritance_proven": True,
                    "proof_ref": "local-smoke-parent-proof",
                },
                "planned_changes": ["dry-run allow-list only"],
                "rollback": {"steps": ["remove dry-run allow-list"]},
                "verification_commands": ["make test-prepare"],
                "approval_gates": ["explicit live-local apply approval"],
            }
        }
    if tool_name == "kan_discord_send_message":
        return {
            "content": "local isolated plugin-load smoke",
            "target": {
                "platform": "discord",
                "channel_id": "chan-smoke",
                "dedicated_test_target": True,
                "visible_label": "LOCAL-SMOKE",
                "cleanup_hint": "delete local smoke fixture if copied",
            },
        }
    raise AssertionError(f"unexpected tool: {tool_name}")


def require_live_env_inert(plugin_home: Path, baseline: Mapping[str, str]) -> None:
    with patched_environ(LIVE_LOOKING_ENV):
        env_outputs = require_entrypoint_fail_closed(plugin_home)
    if env_outputs != baseline:
        raise SystemExit("plugin-load smoke changed behavior under live-looking environment")


def require_negative_fixtures(plugin_home: Path) -> None:
    command_manifest = plugin_home / "plugin.yaml"
    original_manifest = command_manifest.read_text(encoding="utf-8")
    try:
        command_manifest.write_text(
            original_manifest.replace("provides_commands: []", "provides_commands: [kan]"),
            encoding="utf-8",
        )
        try:
            require_manifest(plugin_home)
        except SystemExit as exc:
            if "provides_commands" not in str(exc):
                raise
        else:
            raise SystemExit("plugin-load smoke accepted provides_commands overclaim")
    finally:
        command_manifest.write_text(original_manifest, encoding="utf-8")

    entrypoint_path = plugin_home / "__init__.py"
    original_entrypoint = entrypoint_path.read_text(encoding="utf-8")
    try:
        entrypoint_path.write_text(
            original_entrypoint
            + "\n\n_original_register = register\n\n"
            + "def register(ctx):\n"
            + "    _original_register(ctx)\n"
            + "    ctx.register_command('kan', lambda args: '{}', 'unsupported', None)\n",
            encoding="utf-8",
        )
        try:
            require_entrypoint_load(plugin_home)
        except SystemExit as exc:
            if "commands" not in str(exc):
                raise
        else:
            raise SystemExit("plugin-load smoke accepted command-registering entrypoint")
    finally:
        entrypoint_path.write_text(original_entrypoint, encoding="utf-8")


@contextmanager
def patched_environ(values: Mapping[str, str]) -> Iterator[None]:
    original = {key: os.environ.get(key) for key in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class FakeHermesContext:
    def __init__(self) -> None:
        self.registered_tools: list[dict[str, Any]] = []
        self.registered_hooks: list[tuple[str, Any]] = []
        self.registered_commands: list[dict[str, Any]] = []

    def register_tool(self, **kwargs: Any) -> None:
        self.registered_tools.append(kwargs)

    def register_hook(self, hook_name: str, callback: Any) -> None:
        self.registered_hooks.append((hook_name, callback))

    def register_command(self, *args: Any, **kwargs: Any) -> None:
        self.registered_commands.append({"args": args, "kwargs": kwargs})


def main(*, root: Path = ROOT) -> None:
    root = root.resolve()
    with tempfile.TemporaryDirectory(prefix="kan-plugin-load-smoke-") as temp:
        plugin_home = make_isolated_plugin_home(root, Path(temp))
        require_manifest(plugin_home)
        require_python311_syntax(plugin_home)
        require_package_and_bundled_skill(plugin_home)
        baseline = require_entrypoint_fail_closed(plugin_home)
        require_live_env_inert(plugin_home, baseline)
        require_negative_fixtures(plugin_home)
    print("check-plugin-load-smoke: ok")


if __name__ == "__main__":
    main()
