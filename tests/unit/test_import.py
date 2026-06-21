from __future__ import annotations

import tomllib
from pathlib import Path

import hermes_unified_network_plugin as plugin


def test_package_imports_with_stable_version_metadata() -> None:
    assert plugin.__version__ == "0.1.0"


def test_package_metadata_is_scaffold_only() -> None:
    assert plugin.package_metadata() == {
        "name": "hermes-unified-network-plugin",
        "module": "hermes_unified_network_plugin",
        "version": "0.1.0",
    }


def test_pyproject_uses_package_version_as_single_source_of_truth() -> None:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert "version" not in pyproject["project"]
    assert pyproject["project"]["dynamic"] == ["version"]
    assert pyproject["project"]["requires-python"] == ">=3.11"
    assert pyproject["tool"]["hatch"]["version"]["path"] == (
        "src/hermes_unified_network_plugin/__init__.py"
    )
    assert pyproject["tool"]["ruff"]["target-version"] == "py311"
    assert pyproject["tool"]["mypy"]["python_version"] == "3.11"
