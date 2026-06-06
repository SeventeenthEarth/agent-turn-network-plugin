from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_bootstrap_smoke.py"


def load_bootstrap_smoke() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_bootstrap_smoke", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hplug_register_lines(*, include_hook: bool = False, include_command: bool = False) -> str:
    hook_line = (
        '    ctx.register_hook("message.created", lambda event: event)\n' if include_hook else ""
    )
    command_line = (
        '    ctx.register_command("kan", lambda args: "{}", "unsupported", None)\n'
        if include_command
        else ""
    )
    return (
        "def register(ctx: object) -> None:\n"
        "    ctx.register_tool(\n"
        '        name="kan_daemon_status",\n'
        '        toolset="kkachi_agent_network",\n'
        '        schema={"name": "kan_daemon_status"},\n'
        '        handler=lambda args: "{}",\n'
        "    )\n"
        "    ctx.register_tool(\n"
        '        name="kan_compatibility_diagnostics",\n'
        '        toolset="kkachi_agent_network",\n'
        '        schema={"name": "kan_compatibility_diagnostics"},\n'
        '        handler=lambda args: "{}",\n'
        "    )\n"
        "    ctx.register_tool(\n"
        '        name="kan_stream_tail",\n'
        '        toolset="kkachi_agent_network",\n'
        '        schema={"name": "kan_stream_tail"},\n'
        '        handler=lambda args: "{}",\n'
        "    )\n"
        "    ctx.register_tool(\n"
        '        name="kan_delegate_new",\n'
        '        toolset="kkachi_agent_network",\n'
        '        schema={"name": "kan_delegate_new"},\n'
        '        handler=lambda args: "{}",\n'
        "    )\n"
        "    ctx.register_tool(\n"
        '        name="kan_delegate_action",\n'
        '        toolset="kkachi_agent_network",\n'
        '        schema={"name": "kan_delegate_action"},\n'
        '        handler=lambda args: "{}",\n'
        "    )\n"
        "    ctx.register_tool(\n"
        '        name="kan_council_command",\n'
        '        toolset="kkachi_agent_network",\n'
        '        schema={"name": "kan_council_command"},\n'
        '        handler=lambda args: "{}",\n'
        "    )\n"
        "    ctx.register_tool(\n"
        '        name="kan_delivery_evidence",\n'
        '        toolset="kkachi_agent_network",\n'
        '        schema={"name": "kan_delivery_evidence"},\n'
        '        handler=lambda args: "{}",\n'
        "    )\n"
        f"{hook_line}"
        f"{command_line}"
    )


def write_bootstrap_fixture(
    root: Path,
    *,
    package_version: str = "0.1.0",
    package_metadata: str | None = None,
    manifest_text: str | None = None,
    manifest_version: str = "0.1.0",
    provides_tools: str = (
        '["kan_daemon_status", "kan_compatibility_diagnostics", "kan_stream_tail", '
        '"kan_delegate_new", "kan_delegate_action", "kan_council_command", '
        '"kan_delivery_evidence"]'
    ),
    provides_hooks: str = "[]",
    provides_commands: str = "[]",
    root_entrypoint: str | None = None,
) -> None:
    package = root / "src" / "kkachi_agent_network_plugin"
    package.mkdir(parents=True)
    package.joinpath("__init__.py").write_text(
        package_metadata
        or "from __future__ import annotations\n"
        f'__version__ = "{package_version}"\n\n'
        "def package_metadata() -> dict[str, str]:\n"
        "    return {\n"
        '        "name": "kkachi-agent-network-plugin",\n'
        '        "module": "kkachi_agent_network_plugin",\n'
        '        "version": __version__,\n'
        "    }\n",
        encoding="utf-8",
    )
    root.joinpath("plugin.yaml").write_text(
        manifest_text
        or "name: kkachi-agent-network-plugin\n"
        f"version: {manifest_version}\n"
        'description: "Hermes plugin scaffold for kkachi-agent-network."\n'
        'author: "17번째 지구 Kkachi"\n'
        "kind: standalone\n"
        f"provides_tools: {provides_tools}\n"
        f"provides_hooks: {provides_hooks}\n"
        f"provides_commands: {provides_commands}\n",
        encoding="utf-8",
    )
    root.joinpath("__init__.py").write_text(
        root_entrypoint or "from __future__ import annotations\n\n" + hplug_register_lines(),
        encoding="utf-8",
    )


def test_bootstrap_smoke_accepts_repository_scaffold() -> None:
    bootstrap_smoke = load_bootstrap_smoke()

    bootstrap_smoke.main()


def test_bootstrap_smoke_accepts_minimal_scaffold_fixture(tmp_path: Path) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(tmp_path)

    bootstrap_smoke.main(root=tmp_path)


def test_bootstrap_smoke_rejects_manifest_tool_mismatch(tmp_path: Path) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(tmp_path, provides_tools='["kan_status"]')

    with pytest.raises(SystemExit, match="manifest provides_tools mismatch"):
        bootstrap_smoke.main(root=tmp_path)


def test_bootstrap_smoke_rejects_manifest_hook_overclaim(tmp_path: Path) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(tmp_path, provides_hooks='["message.created"]')

    with pytest.raises(SystemExit, match="manifest provides_hooks must remain explicit empty list"):
        bootstrap_smoke.main(root=tmp_path)


def test_bootstrap_smoke_rejects_manifest_command_overclaim(tmp_path: Path) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(tmp_path, provides_commands='["/kan"]')

    with pytest.raises(
        SystemExit, match="manifest provides_commands must remain explicit empty list"
    ):
        bootstrap_smoke.main(root=tmp_path)


def test_bootstrap_smoke_rejects_manifest_version_mismatch(tmp_path: Path) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(tmp_path, package_version="0.2.0", manifest_version="0.1.0")

    with pytest.raises(
        SystemExit, match="manifest version mismatch: got '0.1.0', expected '0.2.0'"
    ):
        bootstrap_smoke.main(root=tmp_path)


def test_bootstrap_smoke_rejects_malformed_manifest(tmp_path: Path) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(tmp_path, manifest_text="---\n")

    with pytest.raises(SystemExit, match="plugin manifest must be a YAML mapping"):
        bootstrap_smoke.main(root=tmp_path)


def test_bootstrap_smoke_rejects_missing_package_metadata(tmp_path: Path) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(
        tmp_path,
        package_metadata=(
            'from __future__ import annotations\n__version__ = "0.1.0"\npackage_metadata = None\n'
        ),
    )

    with pytest.raises(SystemExit, match="package_metadata is not callable"):
        bootstrap_smoke.main(root=tmp_path)


def test_bootstrap_smoke_rejects_entrypoint_that_registers_unexpected_tools(
    tmp_path: Path,
) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(
        tmp_path,
        root_entrypoint=(
            "from __future__ import annotations\n\n"
            "def register(ctx: object) -> None:\n"
            '    ctx.register_tool(name="kan_status")\n'
        ),
    )

    with pytest.raises(SystemExit, match="entrypoint tool registration mismatch"):
        bootstrap_smoke.main(root=tmp_path)


def test_bootstrap_smoke_rejects_entrypoint_that_registers_hooks(tmp_path: Path) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(
        tmp_path,
        root_entrypoint="from __future__ import annotations\n\n"
        + hplug_register_lines(include_hook=True),
    )

    with pytest.raises(SystemExit, match="entrypoint registered HPLUG/DELRV-1-forbidden hooks"):
        bootstrap_smoke.main(root=tmp_path)


def test_bootstrap_smoke_rejects_entrypoint_that_registers_commands(tmp_path: Path) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(
        tmp_path,
        root_entrypoint="from __future__ import annotations\n\n"
        + hplug_register_lines(include_command=True),
    )

    with pytest.raises(SystemExit, match="entrypoint registered HPLUG/DELRV-1-forbidden commands"):
        bootstrap_smoke.main(root=tmp_path)


def test_bootstrap_smoke_rejects_unclear_entrypoint_import_failure(tmp_path: Path) -> None:
    bootstrap_smoke = load_bootstrap_smoke()
    write_bootstrap_fixture(
        tmp_path,
        root_entrypoint=(
            "from __future__ import annotations\n\n"
            "raise RuntimeError('boom')\n\n"
            "def register(ctx: object) -> None:\n"
            "    _ = ctx\n"
        ),
    )

    with pytest.raises(SystemExit, match="bootstrap smoke failed to load module .*boom"):
        bootstrap_smoke.main(root=tmp_path)
