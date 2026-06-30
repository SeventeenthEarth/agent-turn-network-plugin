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


class FakePluginContext:
    def __init__(self) -> None:
        self.handlers = {}
        self.skills = {}

    def register_tool(self, **kwargs: object) -> None:
        self.handlers[str(kwargs["name"])] = kwargs["handler"]

    def register_skill(self, **kwargs: object) -> None:
        self.skills[str(kwargs["name"])] = kwargs


def load_entrypoint_from_path(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("atn_plugin_symlink_smoke", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def plugin_load_smoke() -> ModuleType:
    return load_plugin_load_smoke()


def test_symlinked_entrypoint_uses_profile_local_live_config(tmp_path: Path) -> None:
    profile_plugin_root = tmp_path / "profile" / "plugins" / "atn-plugin"
    profile_plugin_root.mkdir(parents=True)
    (profile_plugin_root / "__init__.py").symlink_to(ROOT / "__init__.py")
    (profile_plugin_root / "src").symlink_to(ROOT / "src", target_is_directory=True)
    (profile_plugin_root / "config.yaml").write_text(
        "live_transport:\n  unix_socket_path: relative.sock\n",
        encoding="utf-8",
    )

    module = load_entrypoint_from_path(profile_plugin_root / "__init__.py")
    ctx = FakePluginContext()
    module.register(ctx)

    raw = ctx.handlers["atn_daemon_status"]({})

    assert "live_transport.unix_socket_path must be absolute" in raw
    assert "explicit daemon client factory is required" not in raw


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
            "name: atn-plugin",
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
            "atn_stream_tail",
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
            "pure ATN discussion activation planner/doctor",
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
        + "    ctx.register_resource(name='atn_live_state', path='/tmp/unsupported')\n",
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
        + "        toolset='atn_plugin',\n"
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
        "from atn_plugin.tools import register_tools\n\n"
        "def register(ctx):\n"
        "    register_tools(ctx)\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="No module named 'atn_plugin'"):
        plugin_load_smoke.main(root=root)


def test_plugin_load_smoke_rejects_python312_only_runtime_syntax(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    protocol = root / "src" / "atn_plugin" / "protocol.py"
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
            'packages = ["src/atn_plugin"]',
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
    package = root / "src" / "atn_plugin" / "__init__.py"
    package.write_text(
        package.read_text(encoding="utf-8").replace(
            '"atn-plugin"',
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
    skill = root / "src" / "atn_plugin" / "bundled_skills" / "atn-plugin" / "SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8").replace("name: atn-plugin", "name: kan-plugin"),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="bundled skill atn-plugin"):
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
