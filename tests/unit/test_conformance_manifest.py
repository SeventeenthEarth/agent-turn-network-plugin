from __future__ import annotations

from pathlib import Path

import pytest

from kkachi_agent_network_plugin.conformance import (
    load_conformance_manifest,
    parse_conformance_manifest,
)
from kkachi_agent_network_plugin.errors import DaemonCompatibilityError

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_DRAFT_MANIFEST = (
    ROOT
    / "src"
    / "kkachi_agent_network_plugin"
    / "testdata"
    / "conformance"
    / "manifest.draft.json"
)
CORE_MANIFEST = (
    ROOT.parent / "kkachi-agent-network-control" / "testdata" / "conformance" / "manifest.json"
)

BASE_MANIFEST = {
    "manifest_version": 1,
    "protocol_version": "kan-protocol-v1alpha0",
    "stability": "draft-docs-scaffold",
    "fixtures": [],
    "required_feature_groups": ["version_features", "command_envelope", "structured_error"],
}


def test_plugin_local_zero_fixture_manifest_is_draft_only_and_not_live_ready() -> None:
    manifest = load_conformance_manifest(PLUGIN_DRAFT_MANIFEST)

    assert manifest.protocol_version == "kan-protocol-v1alpha0"
    assert manifest.fixtures == ()
    assert manifest.live_readiness is False


def test_core_zero_fixture_manifest_is_allowed_only_as_draft_scaffold() -> None:
    manifest = load_conformance_manifest(CORE_MANIFEST)

    assert manifest.fixtures == ()
    assert manifest.live_readiness is False


def test_zero_fixture_manifest_without_draft_stability_fails_closed() -> None:
    with pytest.raises(DaemonCompatibilityError, match=r"fixtures=\[\] is allowed only"):
        parse_conformance_manifest({**BASE_MANIFEST, "stability": "stable"})


def test_empty_fixtures_force_live_readiness_false_even_when_manifest_claims_true() -> None:
    manifest = parse_conformance_manifest({**BASE_MANIFEST, "live_readiness": True})

    assert manifest.live_readiness is False


@pytest.mark.parametrize(
    "manifest",
    [
        {**BASE_MANIFEST, "protocol_version": "wrong"},
        {**BASE_MANIFEST, "stability": ""},
        {**BASE_MANIFEST, "fixtures": "not-list"},
        {**BASE_MANIFEST, "fixtures": [""]},
        {**BASE_MANIFEST, "required_feature_groups": ["version_features"]},
        {**BASE_MANIFEST, "live_readiness": "yes"},
        {**BASE_MANIFEST, "manifest_version": True},
    ],
)
def test_malformed_or_unsupported_manifest_fails_closed(manifest: dict[str, object]) -> None:
    with pytest.raises(DaemonCompatibilityError):
        parse_conformance_manifest(manifest)
