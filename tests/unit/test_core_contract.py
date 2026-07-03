from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_core_contract.py"
PROTOCOL = "atn-protocol-v1alpha0"


def load_check_core_contract() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_core_contract", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_contract_fixture(
    root: Path, *, protocol: str = PROTOCOL, include_plugin_protocol: bool = True
) -> tuple[Path, Path]:
    plugin = root / "plugin"
    core = root / "core"
    (plugin / "docs" / "spec").mkdir(parents=True)
    (core / "docs" / "spec").mkdir(parents=True)
    (core / "testdata" / "conformance").mkdir(parents=True)

    check_core_contract = load_check_core_contract()
    (core / "testdata" / "conformance" / "manifest.json").write_text(
        json.dumps(
            {
                "protocol_version": protocol,
                "required_feature_groups": ["delivery_evidence", "council.lifecycle"],
                "fixtures": list(check_core_contract.REQUIRED_ARGUE_FIXTURES),
            }
        ),
        encoding="utf-8",
    )
    (core / "docs" / "spec" / "cross-repo-contract.md").write_text(
        "\n".join(
            [
                protocol,
                "Milestone unlock matrix",
                "make check-plugin-contract",
                "testdata/conformance/manifest.json",
                "conformance fixture handoff",
            ]
        ),
        encoding="utf-8",
    )
    (core / "Makefile").write_text("check-plugin-contract:\n\t@echo ok\n", encoding="utf-8")
    (plugin / "docs" / "spec" / "compatibility-and-operations.md").write_text(
        PROTOCOL if include_plugin_protocol else "missing protocol declaration",
        encoding="utf-8",
    )
    return plugin, core


def test_core_contract_accepts_complete_local_fixture(tmp_path: Path) -> None:
    check_core_contract = load_check_core_contract()
    plugin, core = write_contract_fixture(tmp_path)

    check_core_contract.main(plugin=plugin, core=core)


def test_core_contract_rejects_protocol_mismatch(tmp_path: Path) -> None:
    check_core_contract = load_check_core_contract()
    plugin, core = write_contract_fixture(tmp_path, protocol="wrong-protocol")

    with pytest.raises(SystemExit, match="control manifest protocol mismatch"):
        check_core_contract.main(plugin=plugin, core=core)


def test_core_contract_rejects_missing_plugin_protocol_declaration(tmp_path: Path) -> None:
    check_core_contract = load_check_core_contract()
    plugin, core = write_contract_fixture(tmp_path, include_plugin_protocol=False)

    with pytest.raises(
        SystemExit, match="plugin compatibility doc does not declare public protocol"
    ):
        check_core_contract.main(plugin=plugin, core=core)


def test_core_contract_rejects_makefile_target_only_in_comment(tmp_path: Path) -> None:
    check_core_contract = load_check_core_contract()
    plugin, core = write_contract_fixture(tmp_path)
    (core / "Makefile").write_text(
        "# check-plugin-contract:\ncheck-plugin-contract-v2:\n\t@echo wrong\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="control Makefile missing check-plugin-contract target"):
        check_core_contract.main(plugin=plugin, core=core)


def test_core_contract_rejects_missing_cndis_feature_groups(tmp_path: Path) -> None:
    check_core_contract = load_check_core_contract()
    plugin, core = write_contract_fixture(tmp_path)
    (core / "testdata" / "conformance" / "manifest.json").write_text(
        json.dumps(
            {
                "protocol_version": PROTOCOL,
                "required_feature_groups": ["delivery_evidence"],
                "fixtures": list(check_core_contract.REQUIRED_ARGUE_FIXTURES),
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="missing required CNDIS feature groups"):
        check_core_contract.main(plugin=plugin, core=core)


def test_core_contract_rejects_missing_argue_fixtures(tmp_path: Path) -> None:
    check_core_contract = load_check_core_contract()
    plugin, core = write_contract_fixture(tmp_path)
    (core / "testdata" / "conformance" / "manifest.json").write_text(
        json.dumps(
            {
                "protocol_version": PROTOCOL,
                "required_feature_groups": ["delivery_evidence", "council.lifecycle"],
                "fixtures": ["fixtures/command/council-speak-request.json"],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="control manifest missing ARGUE fixtures"):
        check_core_contract.main(plugin=plugin, core=core)
