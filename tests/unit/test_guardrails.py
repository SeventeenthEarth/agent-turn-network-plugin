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
    (root / "plugin.yaml").write_text(
        "name: atn-plugin\n"
        "description: Agent Turn Network plugin fixture.\n"
        "provides_tools:\n"
        "  - atn_daemon_status\n"
        "provides_hooks: []\n"
        "provides_commands: []\n",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        '[project]\nname = "atn-plugin"\n',
        encoding="utf-8",
    )
    (root / "__init__.py").write_text(
        '"""Hermes directory plugin entrypoint for atn-plugin."""\n',
        encoding="utf-8",
    )
    skill = root / "src" / "atn_plugin" / "bundled_skills" / "atn-plugin"
    skill.mkdir(parents=True)
    package = root / "src" / "atn_plugin"
    (package / "__init__.py").write_text(
        '"""ATN plugin package fixture."""\n',
        encoding="utf-8",
    )
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: atn-plugin\n"
        "description: Use when testing bundled skill frontmatter.\n"
        "---\n"
        "# ATN Plugin Operator Skill\n",
        encoding="utf-8",
    )
    for name in REQUIRED_DOCS:
        (docs / name).write_text(f"# {name}\n", encoding="utf-8")
    required_text = "\n".join(
        [
            "plugin is not the source of truth",
            "atn-controld",
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
                "public ATN operator guidance",
                "provides_commands: []",
                "atn_session_status",
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
    skill = tmp_path / "src" / "atn_plugin" / "bundled_skills" / "atn-plugin" / "SKILL.md"
    skill.write_text("# ATN Plugin Operator Skill\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="bundled skill must start with YAML frontmatter"):
        guardrails.main(root=tmp_path)


@pytest.mark.parametrize(
    ("path", "text", "token"),
    [
        (
            "README.md",
            "Install kkachi_agent_network_plugin as a public import.\n",
            "kkachi_agent_network_plugin",
        ),
        (
            "__init__.py",
            '"""Registers legacy kan_stream_tail in the root packaged entrypoint."""\n',
            "kan_stream_tail",
        ),
        (
            "src/atn_plugin/schemas.py",
            '"""Hermes tool schemas for fake/injected KAN plugin surfaces."""\n',
            "KAN plugin",
        ),
        (
            "src/atn_plugin/schemas.py",
            'TOOL = {"name": "kan_stream_tail"}\n',
            "kan_stream_tail",
        ),
        (
            "src/atn_plugin/bundled_skills/atn-plugin/SKILL.md",
            "---\nname: atn-plugin\ndescription: stale\n---\nUse kan-plugin as an alias.\n",
            "kan-plugin",
        ),
        ("plugin.yaml", "provides_commands: [kan]\n", "provides_commands"),
        (
            "plugin.yaml",
            "description: pure RUNFIX discussion activation planner/doctor\n",
            "pure RUNFIX discussion activation planner/doctor",
        ),
        (
            "docs/00-overview.md",
            "The package keeps a legacy wrapper for compatibility.\n",
            "legacy wrapper",
        ),
        (
            "docs/00-overview.md",
            "gateway/auth/token/provider mutation is supported for operators.\n",
            "gateway/auth/token/provider mutation is supported",
        ),
    ],
)
def test_docs_guardrails_reject_stale_hun_public_terms(
    tmp_path: Path, path: str, text: str, token: str
) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")

    with pytest.raises(SystemExit, match="stale ATN public term found") as exc:
        guardrails.main(root=tmp_path)

    assert token in str(exc.value)


def test_docs_guardrails_allow_occurrence_specific_historical_provenance(
    tmp_path: Path,
) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    roadmap = tmp_path / "docs" / "06-implementation-epics-tasks.md"
    roadmap.write_text(
        "| HPLUG-2 | completed | Implemented the fake/injected "
        "`kan_stream_tail` read-only plugin tool with stream-frame compatibility. |\n",
        encoding="utf-8",
    )

    guardrails.main(root=tmp_path)


def test_docs_guardrails_reject_same_token_outside_allowed_occurrence(
    tmp_path: Path,
) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    roadmap = tmp_path / "docs" / "06-implementation-epics-tasks.md"
    roadmap.write_text(
        "New public docs should call `kan_stream_tail` directly.\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="kan_stream_tail"):
        guardrails.main(root=tmp_path)
