from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_plugin_load_smoke.py"


def load_plugin_load_smoke() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_plugin_load_smoke", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_repo_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    shutil.copy2(ROOT / "plugin.yaml", root / "plugin.yaml")
    shutil.copy2(ROOT / "__init__.py", root / "__init__.py")
    shutil.copy2(ROOT / "pyproject.toml", root / "pyproject.toml")
    shutil.copytree(ROOT / "src", root / "src")
    return root


@pytest.fixture
def plugin_load_smoke() -> ModuleType:
    return load_plugin_load_smoke()


def test_plugin_load_smoke_accepts_repository_local_isolated_load(
    plugin_load_smoke: ModuleType,
) -> None:
    plugin_load_smoke.main()


def test_plugin_load_smoke_rejects_manifest_command_overclaim(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    manifest = root / "plugin.yaml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(
            "provides_commands: []", "provides_commands: [kan]"
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        SystemExit, match="manifest provides_commands must remain explicit empty list"
    ):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_legacy_manifest_name(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    manifest = root / "plugin.yaml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(
            "name: hermes-unified-network-plugin",
            "name: kkachi-agent-network-plugin",
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="manifest contains legacy identifier"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_legacy_manifest_tool_alias(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    manifest = root / "plugin.yaml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(
            "hun_stream_tail",
            "kan_stream_tail",
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="manifest contains legacy identifier"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_manifest_runfix_public_wording(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    manifest = root / "plugin.yaml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(
            "pure HUN discussion activation planner/doctor",
            "pure RUNFIX discussion activation planner/doctor",
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="stale RUNFIX public wording"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_entrypoint_command_registration(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    entrypoint = root / "__init__.py"
    entrypoint.write_text(
        entrypoint.read_text(encoding="utf-8")
        + "\n\n_original_register = register\n\n"
        + "def register(ctx):\n"
        + "    _original_register(ctx)\n"
        + "    ctx.register_command('kan', lambda args: '{}', 'unsupported', None)\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="registered unsupported commands"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_entrypoint_resource_registration(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    entrypoint = root / "__init__.py"
    entrypoint.write_text(
        entrypoint.read_text(encoding="utf-8")
        + "\n\n_original_register = register\n\n"
        + "def register(ctx):\n"
        + "    _original_register(ctx)\n"
        + "    ctx.register_resource(name='hun_live_state', path='/tmp/unsupported')\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="registered unsupported resources"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_entrypoint_legacy_tool_registration(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    entrypoint = root / "__init__.py"
    entrypoint.write_text(
        entrypoint.read_text(encoding="utf-8")
        + "\n\n_original_register = register\n\n"
        + "def register(ctx):\n"
        + "    _original_register(ctx)\n"
        + "    ctx.register_tool(\n"
        + "        name='kan_stream_tail',\n"
        + "        toolset='kkachi_agent_network',\n"
        + "        schema={},\n"
        + "        handler=lambda args: '{}',\n"
        + "    )\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="tool registration mismatch"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_requires_entrypoint_to_self_bootstrap_src(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    (root / "__init__.py").write_text(
        '"""Broken fixture: imports the src package without local path bootstrapping."""\n\n'
        "from __future__ import annotations\n\n"
        "from hermes_unified_network_plugin.tools import register_tools\n\n"
        "def register(ctx):\n"
        "    register_tools(ctx)\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="No module named 'hermes_unified_network_plugin'"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_python312_only_runtime_syntax(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    protocol = root / "src" / "hermes_unified_network_plugin" / "protocol.py"
    protocol.write_text("type JsonValue = str\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="Python 3.11 syntax failure"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_wheel_package_drift(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    pyproject = root / "pyproject.toml"
    pyproject.write_text(
        pyproject.read_text(encoding="utf-8").replace(
            'packages = ["src/hermes_unified_network_plugin"]',
            'packages = ["src/other_package"]',
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="wheel package inclusion mismatch"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_legacy_package_metadata(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    package = root / "src" / "hermes_unified_network_plugin" / "__init__.py"
    package.write_text(
        package.read_text(encoding="utf-8").replace(
            '"hermes-unified-network-plugin"',
            '"kkachi-agent-network-plugin"',
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="package metadata mismatch"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_legacy_bundled_skill_name(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    skill = (
        root
        / "src"
        / "hermes_unified_network_plugin"
        / "bundled_skills"
        / "hun-plugin"
        / "SKILL.md"
    )
    skill.write_text(
        skill.read_text(encoding="utf-8").replace("name: hun-plugin", "name: kan-plugin"),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="bundled skill hun-plugin"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_live_env_is_inert(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    with pytest.MonkeyPatch.context() as monkeypatch:
        for key, value in plugin_load_smoke.LIVE_LOOKING_ENV.items():
            monkeypatch.setenv(key, f"preexisting-{value}")
        plugin_load_smoke.main(root=root)
