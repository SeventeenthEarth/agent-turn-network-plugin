from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_make_contract.py"


def load_check_make_contract() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_make_contract", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_contract_with_makefile(
    check_make_contract: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    makefile: str,
) -> None:
    class FakeMakefile:
        def read_text(self, *, encoding: str) -> str:
            assert encoding == "utf-8"
            return makefile

    monkeypatch.setattr(check_make_contract, "MAKEFILE", FakeMakefile())
    check_make_contract.main()


def test_make_contract_accepts_repository_makefile() -> None:
    check_make_contract = load_check_make_contract()
    check_make_contract.main()


def test_make_contract_rejects_missing_e2e_isolation(monkeypatch: pytest.MonkeyPatch) -> None:
    check_make_contract = load_check_make_contract()
    makefile = check_make_contract.MAKEFILE.read_text(encoding="utf-8")
    broken = makefile.replace('DISCORD_TEST_TARGET="" ', "")

    with pytest.raises(SystemExit, match="Discord target isolation"):
        run_contract_with_makefile(check_make_contract, monkeypatch, broken)


def test_make_contract_rejects_marker_moved_to_comment(monkeypatch: pytest.MonkeyPatch) -> None:
    check_make_contract = load_check_make_contract()
    makefile = check_make_contract.MAKEFILE.read_text(encoding="utf-8")
    broken = makefile.replace(
        "\t@KAN_EXTERNAL=0 $(UV) run pytest tests/integration",
        "\t@$(UV) run pytest tests/integration",
    )
    broken += "\n# unrelated offline marker: KAN_EXTERNAL=0\n"

    with pytest.raises(SystemExit, match="test-int.*offline integration default"):
        run_contract_with_makefile(check_make_contract, monkeypatch, broken)


def test_make_contract_rejects_missing_require_uv_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    check_make_contract = load_check_make_contract()
    makefile = check_make_contract.MAKEFILE.read_text(encoding="utf-8")
    broken = makefile.replace("fmt: require-uv", "fmt:")

    with pytest.raises(SystemExit, match="fmt missing require-uv dependency"):
        run_contract_with_makefile(check_make_contract, monkeypatch, broken)


def test_make_contract_rejects_missing_bootstrap_smoke_require_uv_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    check_make_contract = load_check_make_contract()
    makefile = check_make_contract.MAKEFILE.read_text(encoding="utf-8")
    broken = makefile.replace("check-bootstrap-smoke: require-uv", "check-bootstrap-smoke:")

    with pytest.raises(SystemExit, match="check-bootstrap-smoke missing require-uv dependency"):
        run_contract_with_makefile(check_make_contract, monkeypatch, broken)


def test_target_dependencies_ignore_inline_comments() -> None:
    check_make_contract = load_check_make_contract()
    makefile = "test: test-prepare test-unit test-int test-e2e # all tiers\n"

    assert check_make_contract.target_dependencies(makefile, "test") == (
        "test-prepare",
        "test-unit",
        "test-int",
        "test-e2e",
    )


def test_target_dependencies_ignore_same_line_recipe() -> None:
    check_make_contract = load_check_make_contract()
    makefile = "fmt: require-uv ; $(UV) run ruff format --check .\n"

    assert check_make_contract.target_dependencies(makefile, "fmt") == ("require-uv",)
