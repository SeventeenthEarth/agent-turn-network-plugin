from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from kkachi_agent_network_plugin.bundled_skills import (
    BUNDLED_SKILL_NAME,
    bundled_skill_names,
    bundled_skill_resource,
    read_bundled_skill_text,
)

ROOT = Path(__file__).resolve().parents[2]


def test_bundled_kan_skill_resource_is_import_safe_and_readable() -> None:
    assert bundled_skill_names() == ("kan-plugin",)
    assert BUNDLED_SKILL_NAME == "kan-plugin"

    resource = bundled_skill_resource("kan-plugin")
    text = read_bundled_skill_text("kan-plugin")

    assert resource.name == "SKILL.md"
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


def test_bundled_kan_skill_has_valid_hermes_frontmatter() -> None:
    text = read_bundled_skill_text("kan-plugin")

    assert text.startswith("---\n")
    closing = text.find("\n---\n", 4)
    assert closing != -1
    frontmatter = yaml.safe_load(text[4:closing])

    assert frontmatter["name"] == "kan-plugin"
    assert frontmatter["description"].startswith("Use when operating")
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
