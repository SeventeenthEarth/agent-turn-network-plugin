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


def test_plugin_load_smoke_rejects_wheel_package_drift(
    plugin_load_smoke: ModuleType,
    tmp_path: Path,
) -> None:
    root = copy_repo_fixture(tmp_path)
    pyproject = root / "pyproject.toml"
    pyproject.write_text(
        pyproject.read_text(encoding="utf-8").replace(
            'packages = ["src/kkachi_agent_network_plugin"]',
            'packages = ["src/other_package"]',
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="wheel package inclusion mismatch"):
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
