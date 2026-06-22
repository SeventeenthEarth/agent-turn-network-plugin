from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_MODULE = "hermes_unified_network_plugin"
PACKAGE_NAME = "hermes-unified-network-plugin"
EXPECTED_TOOLS = [
    "hun_daemon_status",
    "hun_compatibility_diagnostics",
    "hun_stream_tail",
    "hun_stream_ack",
    "hun_delegate_new",
    "hun_delegate_action",
    "hun_council_command",
    "hun_selected_participant_response",
    "hun_delivery_evidence",
    "hun_surface_render_projection",
    "hun_discussion_activation_plan",
    "hun_discord_send_message",
]


def load_module(path: Path, name: str, *, package_root: bool = False) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        name,
        path,
        submodule_search_locations=[str(path.parent)] if package_root else None,
    )
    if spec is None or spec.loader is None:
        raise SystemExit(f"bootstrap smoke cannot load module spec: {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise SystemExit(f"bootstrap smoke failed to load module {path}: {exc}") from exc
    return module


def import_package_from_src(root: Path) -> ModuleType:
    """Import the package through normal import machinery from the src layout."""

    src_path = str(root / "src")
    previous_path = list(sys.path)
    previous_module = sys.modules.pop(PACKAGE_MODULE, None)
    try:
        sys.path.insert(0, src_path)
        return importlib.import_module(PACKAGE_MODULE)
    except Exception as exc:
        raise SystemExit(
            f"bootstrap smoke failed to import package {PACKAGE_MODULE}: {exc}"
        ) from exc
    finally:
        sys.path[:] = previous_path
        if previous_module is None:
            sys.modules.pop(PACKAGE_MODULE, None)
        else:
            sys.modules[PACKAGE_MODULE] = previous_module


def require_package_metadata(root: Path) -> str:
    package = load_module(
        root / "src" / PACKAGE_MODULE / "__init__.py",
        f"{PACKAGE_MODULE}_bootstrap_smoke",
    )
    package_version = getattr(package, "__version__", None)
    if not isinstance(package_version, str) or not package_version:
        raise SystemExit(
            f"package version metadata must be a non-empty string: {package_version!r}"
        )

    package_metadata = getattr(package, "package_metadata", None)
    if not callable(package_metadata):
        raise SystemExit("package_metadata is not callable")
    expected = {
        "name": PACKAGE_NAME,
        "module": PACKAGE_MODULE,
        "version": package_version,
    }
    actual_metadata = package_metadata()
    if actual_metadata != expected:
        raise SystemExit(f"package metadata mismatch: {actual_metadata} != {expected}")

    imported_package = import_package_from_src(root)
    imported_metadata = getattr(imported_package, "package_metadata", None)
    if not callable(imported_metadata):
        raise SystemExit("imported package_metadata is not callable")
    if imported_metadata() != expected:
        raise SystemExit(f"imported package metadata mismatch: {imported_metadata()} != {expected}")

    return package_version


def require_manifest(root: Path, *, package_version: str) -> None:
    manifest_path = root / "plugin.yaml"
    if not manifest_path.exists():
        raise SystemExit(f"missing plugin manifest: {manifest_path}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise SystemExit(f"plugin manifest must be a YAML mapping: {manifest_path}")

    actual_name = manifest.get("name")
    if actual_name != PACKAGE_NAME:
        raise SystemExit(f"manifest name mismatch: got {actual_name!r}, expected {PACKAGE_NAME!r}")
    actual_version = manifest.get("version")
    if str(actual_version) != package_version:
        raise SystemExit(
            f"manifest version mismatch: got {actual_version!r}, expected {package_version!r}"
        )
    actual_kind = manifest.get("kind")
    if actual_kind != "standalone":
        raise SystemExit(f"manifest kind mismatch: got {actual_kind!r}, expected 'standalone'")

    actual_tools = manifest.get("provides_tools")
    if actual_tools != EXPECTED_TOOLS:
        raise SystemExit(
            f"manifest provides_tools mismatch: got {actual_tools!r}, expected {EXPECTED_TOOLS!r}"
        )
    actual_hooks = manifest.get("provides_hooks")
    if actual_hooks != []:
        raise SystemExit(
            f"manifest provides_hooks must remain explicit empty list for HPLUG/DELRV-1: "
            f"got {actual_hooks!r}"
        )
    actual_commands = manifest.get("provides_commands")
    if actual_commands != []:
        raise SystemExit(
            f"manifest provides_commands must remain explicit empty list for HPLUG/DELRV-1: "
            f"got {actual_commands!r}"
        )


def path_exposes_package(path: str) -> bool:
    base = Path(path or os.getcwd()).resolve()
    return any(
        candidate.is_dir() for candidate in (base / PACKAGE_MODULE, base / "src" / PACKAGE_MODULE)
    )


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


def require_entrypoint(root: Path) -> None:
    entrypoint_path = root / "__init__.py"
    if not entrypoint_path.exists():
        raise SystemExit(f"missing root plugin entrypoint: {entrypoint_path}")
    previous_path = list(sys.path)
    previous_modules = pop_package_modules()
    try:
        sys.path[:] = entrypoint_sys_path()
        entrypoint = load_module(
            entrypoint_path, "hermes_unified_network_plugin_root_bootstrap", package_root=True
        )
    finally:
        sys.path[:] = previous_path
        restore_package_modules(previous_modules)
    register = getattr(entrypoint, "register", None)
    if not callable(register):
        raise SystemExit("entrypoint register is not callable")

    context = FakePluginContext()
    try:
        register(context)
    except Exception as exc:
        raise SystemExit(f"entrypoint register failed during bootstrap smoke: {exc}") from exc
    registered_tool_names = [tool.get("name") for tool in context.registered_tools]
    if registered_tool_names != EXPECTED_TOOLS:
        raise SystemExit(
            f"entrypoint tool registration mismatch: got {registered_tool_names!r}, "
            f"expected {EXPECTED_TOOLS!r}"
        )
    for tool in context.registered_tools:
        if tool.get("toolset") != "kkachi_agent_network":
            raise SystemExit(f"entrypoint toolset mismatch: {tool!r}")
        if not isinstance(tool.get("schema"), dict):
            raise SystemExit(f"entrypoint tool schema must be a mapping: {tool!r}")
        if not callable(tool.get("handler")):
            raise SystemExit(f"entrypoint tool handler is not callable: {tool!r}")
    if context.registered_hooks:
        raise SystemExit("entrypoint registered HPLUG/DELRV-1-forbidden hooks")
    if context.registered_commands:
        raise SystemExit("entrypoint registered HPLUG/DELRV-1-forbidden commands")
    registered_skill_names = [skill.get("name") for skill in context.registered_skills]
    if registered_skill_names and registered_skill_names != [
        "kan-plugin",
        "kan-moderator",
        "kan-participant",
    ]:
        raise SystemExit(
            "entrypoint bundled skill registration mismatch: "
            f"{registered_skill_names!r}"
        )


class FakePluginContext:
    def __init__(self) -> None:
        self.registered_tools: list[dict[str, Any]] = []
        self.registered_hooks: list[tuple[str, Any]] = []
        self.registered_commands: list[dict[str, Any]] = []
        self.registered_skills: list[dict[str, Any]] = []

    def register_tool(self, **kwargs: Any) -> None:
        self.registered_tools.append(kwargs)

    def register_hook(self, hook_name: str, callback: Any) -> None:
        self.registered_hooks.append((hook_name, callback))

    def register_command(self, *args: Any, **kwargs: Any) -> None:
        self.registered_commands.append({"args": args, "kwargs": kwargs})

    def register_skill(self, **kwargs: Any) -> None:
        self.registered_skills.append(kwargs)


def main(*, root: Path = ROOT) -> None:
    root = root.resolve()
    package_version = require_package_metadata(root)
    require_manifest(root, package_version=package_version)
    require_entrypoint(root)
    print("check-bootstrap-smoke: ok")


if __name__ == "__main__":
    main()
