from __future__ import annotations

import json
import os
import re
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
CONTROL_REPO = (
    os.environ.get("HUN_CONTROL_REPO")
    or os.environ.get("HUN_CORE_REPO")
    or os.environ.get("KAN_CONTROL_REPO")
    or os.environ.get("KAN_CORE_REPO")
)
CORE = Path(CONTROL_REPO or PLUGIN.parent / "agent-turn-network-control").resolve()
EXPECTED_PROTOCOL = "hun-protocol-v1alpha0"
PUBLIC_CONTROL_PROTOCOL = "atn-protocol-v1alpha0"
REQUIRED_CONTROL_PHRASES = [
    PUBLIC_CONTROL_PROTOCOL,
    "Milestone unlock matrix",
    "make check-plugin-contract",
    "testdata/conformance/manifest.json",
]
REQUIRED_CONTROL_FEATURE_GROUPS = ["delivery_evidence", "council.lifecycle"]
REQUIRED_ARGUE_FIXTURES = [
    "fixtures/command/council-speak-argument-graph-request.json",
    "fixtures/command/council-hand-raise-argument-graph-request.json",
    "fixtures/event/argument-graph-opening-new-axis-council.json",
    "fixtures/event/argument-graph-support-prior-council.json",
    "fixtures/event/argument-graph-multi-link-council.json",
    "fixtures/event/argument-graph-synthesize-council.json",
    "fixtures/event/argument-graph-dual-field-speech-council.json",
    "fixtures/event/argument-graph-legacy-only-speech-council.json",
    "fixtures/event/argument-graph-hand-raise-target-links-council.json",
    "fixtures/error/argument-graph-invalid-stance.json",
    "fixtures/error/argument-graph-new-axis-missing-reason.json",
    "fixtures/error/argument-graph-synthesize-single-target.json",
    "fixtures/error/argument-graph-quality-required-missing-claims.json",
    "fixtures/error/argument-graph-quality-required-orphan-speech.json",
]


def require(path: Path, label: str) -> str:
    if not path.exists():
        raise SystemExit(f"missing {label}: {path}")
    return path.read_text(encoding="utf-8")


def has_make_target(makefile: str, target: str) -> bool:
    return re.search(rf"^{re.escape(target)}\s*:", makefile, re.MULTILINE) is not None


def main(*, plugin: Path = PLUGIN, core: Path = CORE) -> None:
    plugin = plugin.resolve()
    core = core.resolve()

    manifest_path = core / "testdata" / "conformance" / "manifest.json"
    manifest = json.loads(require(manifest_path, "control conformance manifest"))
    if manifest.get("protocol_version") != EXPECTED_PROTOCOL:
        raise SystemExit(
            f"control manifest protocol mismatch: {manifest.get('protocol_version')} != {EXPECTED_PROTOCOL}"
        )
    feature_groups = manifest.get("required_feature_groups")
    if not isinstance(feature_groups, list):
        raise SystemExit("control manifest required_feature_groups must be a list")
    missing_feature_groups = [
        feature for feature in REQUIRED_CONTROL_FEATURE_GROUPS if feature not in feature_groups
    ]
    if missing_feature_groups:
        raise SystemExit(
            f"control manifest missing required CNDIS feature groups: {missing_feature_groups}"
        )
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list):
        raise SystemExit("control manifest fixtures must be a list")
    missing_argue_fixtures = [
        fixture for fixture in REQUIRED_ARGUE_FIXTURES if fixture not in fixtures
    ]
    if missing_argue_fixtures:
        raise SystemExit(f"control manifest missing ARGUE fixtures: {missing_argue_fixtures}")

    cross = require(core / "docs" / "21-cross-repo-development.md", "control cross-repo development doc")
    dist = require(core / "docs" / "11-distribution-and-plugin.md", "control distribution/plugin doc")
    makefile = require(core / "Makefile", "control Makefile")
    compat = require(plugin / "docs" / "07-core-compatibility.md", "plugin control compatibility doc")

    for phrase in REQUIRED_CONTROL_PHRASES:
        if phrase not in cross:
            raise SystemExit(f"control cross-repo doc missing phrase: {phrase}")

    if not has_make_target(makefile, "check-plugin-contract"):
        raise SystemExit("control Makefile missing check-plugin-contract target")
    if PUBLIC_CONTROL_PROTOCOL not in compat:
        raise SystemExit("plugin compatibility doc does not declare public protocol")
    if "conformance fixture version" not in dist and "conformance fixture" not in dist:
        raise SystemExit("control distribution doc does not describe conformance fixture handoff")

    print(f"check-core-contract: ok ({core})")


if __name__ == "__main__":
    main()
