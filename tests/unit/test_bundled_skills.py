from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from kkachi_agent_network_plugin.bundled_skills import (
    BUNDLED_SKILL_NAME,
    BUNDLED_SKILL_NAMES,
    bundled_skill_names,
    bundled_skill_resource,
    read_bundled_skill_text,
)

ROOT = Path(__file__).resolve().parents[2]


def test_bundled_kan_skill_resource_is_import_safe_and_readable() -> None:
    assert bundled_skill_names() == ("kan-plugin", "kan-moderator", "kan-participant")
    assert BUNDLED_SKILL_NAME == "kan-plugin"
    assert bundled_skill_names() == BUNDLED_SKILL_NAMES

    for name in bundled_skill_names():
        resource = bundled_skill_resource(name)
        text = read_bundled_skill_text(name)
        assert resource.name == "SKILL.md"
        assert f"name: {name}" in text

    text = read_bundled_skill_text("kan-plugin")
    assert "# KAN Plugin Operator Skill" in text
    assert "does not install itself into a Hermes profile" in text
    assert "provides_commands: []" in text
    assert "kan_session_status" in text
    assert "ARGUE argument-graph support as static/fake/injected" in text
    assert "Participant response template" in text
    assert "speaker_selected -> speech linkage" in text
    assert "live_visible_thread" in text
    assert "CLI actor speech only" in text
    assert "Discord visible turns posted: N/expected" in text
    assert "SKILL-2" in text


def test_bundled_kan_skill_ships_council_moderation_hard_rules() -> None:
    skill_text = read_bundled_skill_text("kan-plugin")
    guide_text = (ROOT / "docs" / "09-skill-and-operator-guide.md").read_text(encoding="utf-8")

    for text in [skill_text, guide_text]:
        normalized = " ".join(text.split())
        assert "KAN council moderation hard rules" in normalized
        assert "Do not predeclare or hard-code a complete live speaker order" in normalized
        assert "`council.new`" in normalized
        assert "`request_attendance`" in normalized
        assert "terminal attendance records" in normalized
        assert "`lock_agenda`" in normalized
        assert "`prepare`" in normalized
        assert "`ready` or `prepared_partial`" in normalized
        assert "poll" in normalized
        assert "hand-raise evaluation" in normalized
        assert "justified daemon `speaker_selected` event" in normalized
        assert "`relevance` as the default selection mode" in normalized
        for selection_mode in ["`targeted`", "`random`", "`moderator_direct`", "`role_order`"]:
            assert selection_mode in normalized
        assert "Do not ban `role_order`" in normalized
        assert "Discord/Hermes replies are not council state" in normalized
        assert "typed daemon `speech` events" in normalized
        assert "participant-style turn" in normalized
        assert "cancel and restart" in normalized
        assert "repair forward with a moderator intervention" in normalized


def test_bundled_kan_skill_has_valid_hermes_frontmatter() -> None:
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
        read_bundled_skill_text("../kan-plugin")


def test_bundled_skill_and_operator_docs_do_not_overclaim_unsupported_surfaces() -> None:
    skill_text = read_bundled_skill_text("kan-plugin")
    guide_text = (ROOT / "docs" / "09-skill-and-operator-guide.md").read_text(encoding="utf-8")
    combined = f"{skill_text}\n{guide_text}"

    for phrase in [
        "installed-plugin smoke passes",
        "plugin-load smoke passes",
        "production activation is supported",
        "live plugin readiness is supported",
        "KAB readiness is supported",
        "kan_session_status is supported",
        "provides_commands: [kan",
        "live daemon discovery is supported",
        "uses the current Hermes session",
    ]:
        assert phrase not in combined

    assert "fake/injected" in combined
    assert "No-live defaults" in combined
    assert "local isolated plugin-load smoke" in guide_text
