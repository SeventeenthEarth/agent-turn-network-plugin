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

RUNFIX3_RULE_LINES = [
    "1. [RUNFIX3-R01] Do not predeclare or hard-code a complete live speaker order. "
    "A visible discussion must not become a fixed-order Discord/Hermes debate transcript.",
    "2. [RUNFIX3-R02] Complete lifecycle prerequisites before turn discussion: "
    "`council.new`, `request_attendance`, terminal attendance records for required "
    "participants, `lock_agenda`, `prepare`, then `ready` or `prepared_partial` evidence.",
    "3. [RUNFIX3-R03] For each discussion turn, open a `poll` or hand-raise evaluation, "
    "evaluate the current hand raises, and record a justified daemon `speaker_selected` "
    "event before any participant speech.",
    "4. [RUNFIX3-R04] Use `relevance` as the default selection mode. `targeted`, "
    "`random`, `moderator_direct`, and `role_order` remain valid only as per-turn "
    "`speaker_selected` selection modes with a reason; `role_order` also needs bounded "
    "round evidence. Do not ban `role_order`, but never use it as a predeclared full "
    "live debate order.",
    "5. [RUNFIX3-R05] For a Discord-origin live-visible run, visible delivery must stay "
    "bound to the exact requested origin `chat_id:thread_id`. Display names, thread "
    "titles, channel labels, or prose such as “the KLM thread” are operator hints only "
    "and never origin proof.",
    "6. [RUNFIX3-R06] Expected visible turn count is `max_discussion_turns + "
    "participant_count + 2`: one moderator opening, `max_discussion_turns` selected "
    "participant discussion turns, one selected closeout turn per participant, and one "
    "moderator synthesis. Missing participant closeouts or a missing moderator synthesis "
    "are closeout failures/diagnostics, not permission to reinterpret the formula.",
    "7. [RUNFIX3-R07] Run the discussion as participant-to-participant dialogue. "
    "Moderator prompts should elicit direct participant engagement with prior claims "
    "rather than operator-report summaries or moderator-authored substitute turns.",
    "8. [RUNFIX3-R08] Keep content and audit separate. Visible prompt/speech text is "
    "discussion content only; event ids, delivery ids, cursors, runner ids, control "
    "metadata, and audit commentary stay in audit/evidence surfaces.",
    "9. [RUNFIX3-R09] `selected_runner_pass` remains an evidence-derived label and stays "
    "false when the selected runner fails and the session continues through "
    "`moderator_direct`, manual profile text, fallback profile text, or moderator "
    "reposting. Treat that downgrade as lifecycle/fallback evidence only until a later "
    "selected-runner success produces canonical linked speech.",
    "10. [RUNFIX3-R10] If fixed-order flow, topic drift, wrong-thread delivery, or "
    "control-metadata leakage is detected before any affected `speech`, cancel/restart "
    "the affected step or session. If canonical `speech` already exists, repair forward "
    "with an explicit moderator intervention when possible; if the contract cannot be "
    "restored, close unresolved rather than overclaim success.",
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
    moderator_skill = root / "src" / "atn_plugin" / "bundled_skills" / "atn-moderator"
    moderator_skill.mkdir(parents=True)
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
        "# ATN Plugin Operator Skill\n"
        "This skill is boundary/cross-link only for RUNFIX3 live-thread semantics.\n",
        encoding="utf-8",
    )
    (moderator_skill / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: atn-moderator",
                "description: Use when testing moderator ownership markers.",
                "---",
                "# ATN Moderator Skill",
                "Canonical live-thread procedure owners for this topic: this skill and "
                "`agent-turn-network-plugin/docs/09-skill-and-operator-guide.md`.",
                "## ATN council moderation hard rules",
                "The numbered `[RUNFIX3-R##]` rule set below must stay text-identical with "
                "`agent-turn-network-plugin/docs/09-skill-and-operator-guide.md`.",
                *RUNFIX3_RULE_LINES,
            ]
        )
        + "\n",
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
                "## ATN council moderation hard rules",
                "For RUNFIX3 live-thread semantics, this guide and "
                "`src/atn_plugin/bundled_skills/atn-moderator/SKILL.md` are the normative "
                "procedure owners.",
                "The numbered `[RUNFIX3-R##]` rule set below must stay text-identical with "
                "`src/atn_plugin/bundled_skills/atn-moderator/SKILL.md`.",
                *RUNFIX3_RULE_LINES,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (docs / "06-implementation-epics-tasks.md").write_text(
        "Mirror-only status row:\n",
        encoding="utf-8",
    )
    (docs / "10-live-transport-sot.md").write_text(
        "this SOT section remains traceability/status only and must not become "
        "another procedure owner.\n",
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


def test_docs_guardrails_reject_missing_runfix3_owner_marker(tmp_path: Path) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    plugin_skill = tmp_path / "src" / "atn_plugin" / "bundled_skills" / "atn-plugin" / "SKILL.md"
    plugin_skill.write_text(
        plugin_skill.read_text(encoding="utf-8").replace(
            "This skill is boundary/cross-link only for RUNFIX3 live-thread semantics.\n",
            "",
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="missing RUNFIX3 owner marker"):
        guardrails.main(root=tmp_path)


def test_docs_guardrails_reject_runfix3_rule_parity_drift(tmp_path: Path) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    guide = tmp_path / "docs" / "09-skill-and-operator-guide.md"
    guide.write_text(
        guide.read_text(encoding="utf-8").replace(
            "operator hints only and never origin proof",
            "operator hints only and never exact-origin proof",
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="RUNFIX3 hard-rule parity drift"):
        guardrails.main(root=tmp_path)


def test_docs_guardrails_reject_runfix3_rule_id_outside_owner(tmp_path: Path) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    epics = tmp_path / "docs" / "06-implementation-epics-tasks.md"
    epics.write_text(
        epics.read_text(encoding="utf-8") + "[RUNFIX3-R01] leaked mirror rule id\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="RUNFIX3 rule id escaped owner surface"):
        guardrails.main(root=tmp_path)


def test_docs_guardrails_reject_runfix3_rule_id_in_nested_docs_evidence(tmp_path: Path) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    evidence = tmp_path / "docs" / "evidence" / "runfix3-nested-proof.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("[RUNFIX3-R01] leaked nested evidence rule id\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="RUNFIX3 rule id escaped owner surface"):
        guardrails.main(root=tmp_path)


@pytest.mark.parametrize(
    ("path", "text", "token"),
    [
        (
            "docs/09-skill-and-operator-guide.md",
            "\ndisplay-name labels satisfy exact-origin proof.\n",
            "display-name labels satisfy exact-origin proof",
        ),
        (
            "src/atn_plugin/bundled_skills/atn-plugin/SKILL.md",
            "\n`selected_runner_pass` is a selection mode.\n",
            "`selected_runner_pass` is a selection mode",
        ),
        (
            "docs/09-skill-and-operator-guide.md",
            "\n`selected_runner_pass` is satisfied by fallback/manual speech.\n",
            "`selected_runner_pass` is satisfied by fallback/manual speech",
        ),
        (
            "docs/00-overview.md",
            "\n`live_readiness=true` proves live-visible council readiness.\n",
            "`live_readiness=true` proves live-visible council readiness",
        ),
    ],
)
def test_docs_guardrails_reject_runfix3_invariant_violation(
    tmp_path: Path, path: str, text: str, token: str
) -> None:
    guardrails = load_guardrails()
    write_docs(tmp_path)
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    target.write_text(existing + text, encoding="utf-8")

    with pytest.raises(SystemExit, match="RUNFIX3 invariant violation") as exc:
        guardrails.main(root=tmp_path)

    assert token in str(exc.value)


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
        "Mirror-only status row:\n"
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
