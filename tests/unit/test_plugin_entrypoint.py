from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[2]


def test_plugin_manifest_declares_scaffold_only_surface() -> None:
    manifest = yaml.safe_load((ROOT / "plugin.yaml").read_text(encoding="utf-8"))

    assert manifest == {
        "name": "kkachi-agent-network-plugin",
        "version": "0.1.0",
        "description": (
            "Hermes plugin scaffold for kkachi-agent-network; real tools are added in later "
            "HPLUG/DAEMN tasks."
        ),
        "author": "17번째 지구 Kkachi",
        "kind": "standalone",
        "provides_tools": [],
        "provides_hooks": [],
    }


def test_root_entrypoint_matches_hermes_directory_plugin_contract() -> None:
    module = _load_root_entrypoint()

    assert callable(module.register)
    fake_ctx = FakePluginContext()
    module.register(fake_ctx)

    assert fake_ctx.registered_tools == []
    assert fake_ctx.registered_hooks == []
    assert fake_ctx.registered_commands == []


def _load_root_entrypoint() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "hermes_plugins.kkachi_agent_network_plugin_under_test",
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
        self.registered_hooks: list[tuple[str, Any]] = []
        self.registered_commands: list[dict[str, Any]] = []

    def register_tool(self, **kwargs: Any) -> None:
        self.registered_tools.append(kwargs)

    def register_hook(self, hook_name: str, callback: Any) -> None:
        self.registered_hooks.append((hook_name, callback))

    def register_command(self, *args: Any, **kwargs: Any) -> None:
        self.registered_commands.append({"args": args, "kwargs": kwargs})
