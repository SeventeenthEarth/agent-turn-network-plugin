from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "guardrails.py"

REQUIRED_DOCS = [
    "README.md",
    "00-overview.md",
    "01-architecture.md",
    "02-plugin-contract.md",
    "03-testing-strategy.md",
    "04-tooling.md",
    "05-discord-surface.md",
    "08-unsupported-surfaces.md",
    "09-skill-and-operator-guide.md",
    "07-core-compatibility.md",
]


def load_guardrails() -> ModuleType:
    spec = importlib.util.spec_from_file_location("guardrails", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_docs(root: Path, *, include_fail_closed: bool = True) -> None:
    docs = root / "docs"
    docs.mkdir()
    skill = root / "src" / "hermes_unified_network_plugin" / "bundled_skills" / "kan-plugin"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: kan-plugin\n"
        "description: Use when testing bundled skill frontmatter.\n"
        "---\n"
        "# KAN Plugin Operator Skill\n",
        encoding="utf-8",
    )
    for name in REQUIRED_DOCS:
        (docs / name).write_text(f"# {name}\n", encoding="utf-8")
    required_text = "\n".join(
        [
            "plugin is not the source of truth",
            "kkachi-agent-networkd",
            "test-prepare test-unit test-int test-e2e",
            "isolated test environment",
            "local isolated plugin-load smoke",
            "fail closed" if include_fail_closed else "",
        ]
    )
    (docs / "README.md").write_text(required_text, encoding="utf-8")
    (docs / "09-skill-and-operator-guide.md").write_text(
        "\n".join(
            [
                "No-live defaults",
                "Rollback",
                "Troubleshooting",
                "registers these read-only plugin-provided skills",
                "provides_commands: []",
                "hun_session_status",
                "SKILL-2",
            ]
        ),
        encoding="utf-8",
    )


def test_docs_guardrails_accept_complete_docs(tmp_path: Path) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)

    guardrails.main(root=tmp_path)


def test_docs_guardrails_reject_missing_required_phrase(tmp_path: Path) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path, include_fail_closed=False)

    with pytest.raises(SystemExit, match="missing plugin docs phrase: fail closed"):
        guardrails.main(root=tmp_path)


def test_docs_guardrails_reject_stale_sibling_path(tmp_path: Path) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    overview = tmp_path / "docs" / "00-overview.md"
    overview.write_text("stale `../kkachi-agent-network path", encoding="utf-8")

    with pytest.raises(SystemExit, match="stale docs-relative sibling path"):
        guardrails.main(root=tmp_path)


def test_docs_guardrails_reject_stale_sibling_path_in_extra_doc(tmp_path: Path) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    (tmp_path / "docs" / "06-implementation-epics-tasks.md").write_text(
        "stale `../kkachi-agent-network path",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="stale docs-relative sibling path"):
        guardrails.main(root=tmp_path)


def test_docs_guardrails_reject_operator_guide_overclaim(tmp_path: Path) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    guide = tmp_path / "docs" / "09-skill-and-operator-guide.md"
    guide.write_text(
        guide.read_text(encoding="utf-8") + "\nplugin-load smoke passes\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="operator guide overclaims unsupported surface"):
        guardrails.main(root=tmp_path)


def test_docs_guardrails_reject_bundled_skill_without_frontmatter(tmp_path: Path) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    skill = (
        tmp_path
        / "src"
        / "hermes_unified_network_plugin"
        / "bundled_skills"
        / "kan-plugin"
        / "SKILL.md"
    )
    skill.write_text("# KAN Plugin Operator Skill\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="bundled skill must start with YAML frontmatter"):
        guardrails.main(root=tmp_path)
