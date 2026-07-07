from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from atn_plugin.bundled_skills import (
    BUNDLED_SKILL_NAME,
    BUNDLED_SKILL_NAMES,
    bundled_skill_names,
    bundled_skill_resource,
    read_bundled_skill_text,
)

ROOT = Path(__file__).resolve().parents[2]
RUNFIX3_RULE_IDS = tuple(f"RUNFIX3-R{index:02d}" for index in range(1, 11))
RUNFIX3_RULE_RE = re.compile(r"^\d+\. \[(RUNFIX3-R\d{2})\] (.+\S)$")


def normalize_markdown(text: str) -> str:
    return " ".join(text.split()).lower()


def extract_runfix3_hard_rules(text: str) -> dict[str, str]:
    rules: dict[str, str] = {}
    in_section = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped == "## ATN council moderation hard rules":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        match = RUNFIX3_RULE_RE.match(stripped)
        if match:
            rule_id, body = match.groups()
            rules[rule_id] = normalize_markdown(body)
    return rules


def bundled_skill_text(name: str) -> str:
    return read_bundled_skill_text(name)


def test_bundled_hun_runfix3_002_normative_procedure_has_correct_owners() -> None:
    moderator_text = bundled_skill_text("atn-moderator")
    guide_text = (ROOT / "docs" / "spec" / "skill-and-operator-guide.md").read_text(
        encoding="utf-8"
    )
    plugin_text = bundled_skill_text("atn-plugin")

    assert "Canonical live-thread procedure owners for this topic:" in moderator_text
    assert (
        "For RUNFIX3 live-thread semantics, this guide and "
        "`src/atn_plugin/bundled_skills/atn-moderator/SKILL.md` "
        "are the normative procedure owners." in guide_text
    )

    moderator_rules = extract_runfix3_hard_rules(moderator_text)
    guide_rules = extract_runfix3_hard_rules(guide_text)
    assert tuple(moderator_rules) == RUNFIX3_RULE_IDS
    assert tuple(guide_rules) == RUNFIX3_RULE_IDS
    assert moderator_rules == guide_rules

    assert (
        "This skill is boundary/cross-link only for RUNFIX3 live-thread semantics." in plugin_text
    )
    mirror_epics = (ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")
    mirror_sot = (ROOT / "docs" / "spec" / "live-transport-sot.md").read_text(encoding="utf-8")
    assert "Mirror-only status row" in mirror_epics
    assert (
        "this SOT section remains traceability/status only and must not become another "
        "procedure owner." in mirror_sot
    )

    for rule_id in RUNFIX3_RULE_IDS:
        assert rule_id not in plugin_text
        assert rule_id not in mirror_epics
        assert rule_id not in mirror_sot

    for reference_path in sorted(
        (ROOT / "src" / "atn_plugin" / "bundled_skills" / "atn-moderator" / "references").glob(
            "*.md"
        )
    ):
        reference_text = reference_path.read_text(encoding="utf-8")
        assert "normative procedure owners" not in reference_text.lower()
        assert not any(rule_id in reference_text for rule_id in RUNFIX3_RULE_IDS)


def test_bundled_hun_skill_resource_is_import_safe_and_readable() -> None:
    assert bundled_skill_names() == ("atn-plugin", "atn-moderator", "atn-participant")
    assert BUNDLED_SKILL_NAME == "atn-plugin"
    assert bundled_skill_names() == BUNDLED_SKILL_NAMES
    assert not {"kan-plugin", "kan-moderator", "kan-participant"} & set(bundled_skill_names())

    for name in bundled_skill_names():
        resource = bundled_skill_resource(name)
        text = read_bundled_skill_text(name)
        assert resource.name == "SKILL.md"
        assert f"name: {name}" in text

    text = read_bundled_skill_text("atn-plugin")
    assert "# ATN Plugin Operator Skill" in text
    assert "does not install itself into a Hermes profile" in text
    assert "provides_commands: []" in text
    assert "atn_session_status" in text
    assert "ARGUE argument-graph support as static/fake/injected" in text
    assert "Participant response template" in text
    assert "boundary/cross-link only" in text
    assert "atn-moderator/SKILL.md" in text
    assert "dry-run planner/doctor report only" in text
    assert "selected_runner_pass` remains an evidence-derived label" in text
    assert "SKILL-2" in text


def test_bundled_hun_moderator_skill_ships_council_moderation_hard_rules() -> None:
    plugin_text = read_bundled_skill_text("atn-plugin")
    moderator_text = read_bundled_skill_text("atn-moderator")
    guide_text = (ROOT / "docs" / "spec" / "skill-and-operator-guide.md").read_text(
        encoding="utf-8"
    )

    assert "For RUNFIX3 live-thread semantics, the normative procedure owners are" in plugin_text
    assert "Do not predeclare or hard-code a complete live speaker order" not in plugin_text

    for text in [moderator_text, guide_text]:
        normalized = " ".join(text.split())
        assert "ATN council moderation hard rules" in normalized
        assert "[RUNFIX3-R##]" in normalized

    hard_rules = extract_runfix3_hard_rules(moderator_text)
    assert tuple(hard_rules) == RUNFIX3_RULE_IDS
    assert (
        "do not predeclare or hard-code a complete live speaker order" in hard_rules["RUNFIX3-R01"]
    )
    assert "`council.new`" in hard_rules["RUNFIX3-R02"]
    assert "`request_attendance`" in hard_rules["RUNFIX3-R02"]
    assert "justified daemon `speaker_selected` event" in hard_rules["RUNFIX3-R03"]
    assert "`relevance` as the default selection mode" in hard_rules["RUNFIX3-R04"]
    for selection_mode in ["`targeted`", "`random`", "`moderator_direct`", "`role_order`"]:
        assert selection_mode in hard_rules["RUNFIX3-R04"]
    assert "`chat_id:thread_id`" in hard_rules["RUNFIX3-R05"]
    assert "operator hints only and never origin proof" in hard_rules["RUNFIX3-R05"]
    assert "`max_discussion_turns + participant_count + 2`" in hard_rules["RUNFIX3-R06"]
    assert "participant-to-participant dialogue" in hard_rules["RUNFIX3-R07"]
    assert "operator-report summaries" in hard_rules["RUNFIX3-R07"]
    assert "content and audit separate" in hard_rules["RUNFIX3-R08"]
    assert (
        "`selected_runner_pass` remains an evidence-derived label and stays false"
        in hard_rules["RUNFIX3-R09"]
    )
    assert "repair forward" in hard_rules["RUNFIX3-R10"]
    assert "close unresolved" in hard_rules["RUNFIX3-R10"]


def test_bundled_hun_skills_define_runner_jsonl_framing_contract() -> None:
    plugin_text = read_bundled_skill_text("atn-plugin")
    moderator_text = read_bundled_skill_text("atn-moderator")
    participant_text = read_bundled_skill_text("atn-participant")
    guide_text = (ROOT / "docs" / "spec" / "skill-and-operator-guide.md").read_text(
        encoding="utf-8"
    )
    combined = "\n".join([plugin_text, moderator_text, participant_text, guide_text])
    normalized = " ".join(combined.split())

    assert "Runner stdout semantic framing contract" in normalized
    assert "exactly one compact JSONL object on stdout" in normalized
    assert "no markdown fence" in normalized
    assert "no surrounding prose" in normalized
    assert "Pretty/multiline JSON is compatibility input only" in normalized
    assert "Delivery/fallback-only JSON remains adapter_command_mismatch" in normalized
    assert "malformed JSON remains malformed_or_missing_response" in normalized


def test_bundled_hun_prslr013_live_selected_runner_schema_echo_closeout_guardrails() -> None:
    plugin_text = read_bundled_skill_text("atn-plugin")
    moderator_text = read_bundled_skill_text("atn-moderator")
    participant_text = read_bundled_skill_text("atn-participant")
    guide_text = (ROOT / "docs" / "spec" / "skill-and-operator-guide.md").read_text(
        encoding="utf-8"
    )
    bundled_texts = [plugin_text, moderator_text, participant_text]
    combined = "\n".join([*bundled_texts, guide_text])
    normalized = " ".join(combined.split())
    claim_kind_sentence = (
        "Allowed `claims[].kind` values: `observation`, `requirement`, `risk`, "
        "`decision_frame`, `evidence`, `open_question`, `proposal`."
    )

    for text in [*bundled_texts, guide_text]:
        normalized_text = " ".join(text.split())
        assert claim_kind_sentence in normalized_text
        assert "unsupported `claims[].kind`" in normalized_text
        assert "must fail before canonical `speech` submission" in normalized_text
    assert "unsupported `claims[].kind`" in normalized
    assert "must fail before canonical `speech` submission" in normalized
    assert "do not record a second runnerless `council.speak`" in normalized
    assert "visible_delivery_echo" in normalized
    assert "surface_evidence.references_event_id" in normalized
    assert "surface_evidence.message_id" in normalized
    assert "claims=[] visible-delivery echo" in normalized
    assert "participant closeout for every required member" in normalized
    assert "proposal and required votes" in normalized
    assert "terminal `council.finalize`" in normalized


def test_bundled_hun_newfix002_packaged_skill_contract_is_present() -> None:
    moderator_text = read_bundled_skill_text("atn-moderator")
    participant_text = read_bundled_skill_text("atn-participant")
    guide_text = (ROOT / "docs" / "spec" / "skill-and-operator-guide.md").read_text(
        encoding="utf-8"
    )

    assert "NEXFIX content-plane exception" in guide_text
    assert "selected_runner_timeout_evidence" in guide_text
    assert "control/NEWFIX-004" in guide_text
    assert "absent or `blocked` `selected_runner_prompt_evidence` before start" in moderator_text
    assert "implementation_complete/review_pending` control rows may unlock start" in moderator_text
    assert "control/NEWFIX-004` extension" in moderator_text
    assert (
        "Plugin hints, visible messages, participant responses, and "
        "local/artifact/manual bridge paths are diagnostic only and "
        "cannot replace missing control prompt or timeout authority." in moderator_text
    )
    assert (
        "intervene or cancel rather than treating that turn as normal discussion progress."
        in moderator_text
    )
    assert "fail closed instead of inventing generic substantive speech" in participant_text
    assert 'current control-compatible compact JSONL `type: "speech"` contract' in participant_text
    assert "selected_runner_context_missing" in participant_text


def test_bundled_hun_skill_has_valid_hermes_frontmatter() -> None:
    for name in bundled_skill_names():
        text = read_bundled_skill_text(name)
        assert text.startswith("---\n")
        closing = text.find("\n---\n", 4)
        assert closing != -1
        frontmatter = yaml.safe_load(text[4:closing])

        assert frontmatter["name"] == name
        assert isinstance(frontmatter["description"], str)
        assert len(frontmatter["description"]) <= 1024
        assert frontmatter["version"] == "0.1.0"
        assert frontmatter["metadata"]["hermes"]["tags"]


def test_bundled_skill_reader_rejects_unknown_names() -> None:
    with pytest.raises(ValueError, match="unknown bundled skill"):
        read_bundled_skill_text("../atn-plugin")
    for stale_name in ["kan-plugin", "kan-moderator", "kan-participant"]:
        with pytest.raises(ValueError, match="unknown bundled skill"):
            read_bundled_skill_text(stale_name)


def test_bundled_skill_and_operator_docs_do_not_overclaim_unsupported_surfaces() -> None:
    skill_text = read_bundled_skill_text("atn-plugin")
    guide_text = (ROOT / "docs" / "spec" / "skill-and-operator-guide.md").read_text(
        encoding="utf-8"
    )
    combined = f"{skill_text}\n{guide_text}"

    for phrase in [
        "installed-plugin smoke passes",
        "plugin-load smoke passes",
        "production activation is supported",
        "live plugin readiness is supported",
        "KAB readiness is supported",
        "atn_session_status is supported",
        "provides_commands: [kan",
        "live daemon discovery is supported",
        "uses the current Hermes session",
    ]:
        assert phrase not in combined

    assert "fake/injected" in combined
    assert "No-live defaults" in combined
    assert "local isolated plugin-load smoke" in guide_text
