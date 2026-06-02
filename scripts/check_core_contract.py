from __future__ import annotations

import json
import os
import re
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
CORE = Path(os.environ.get("KAN_CORE_REPO", PLUGIN.parent / "kkachi-agent-network")).resolve()
EXPECTED_PROTOCOL = "kan-protocol-v1alpha0"
REQUIRED_CORE_PHRASES = [
    EXPECTED_PROTOCOL,
    "Milestone unlock matrix",
    "make check-plugin-contract",
    "testdata/conformance/manifest.json",
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
    manifest = json.loads(require(manifest_path, "core conformance manifest"))
    if manifest.get("protocol_version") != EXPECTED_PROTOCOL:
        raise SystemExit(
            f"core manifest protocol mismatch: {manifest.get('protocol_version')} != {EXPECTED_PROTOCOL}"
        )

    cross = require(core / "docs" / "21-cross-repo-development.md", "core cross-repo development doc")
    dist = require(core / "docs" / "11-distribution-and-plugin.md", "core distribution/plugin doc")
    makefile = require(core / "Makefile", "core Makefile")
    compat = require(plugin / "docs" / "07-core-compatibility.md", "plugin core compatibility doc")

    for phrase in REQUIRED_CORE_PHRASES:
        if phrase not in cross:
            raise SystemExit(f"core cross-repo doc missing phrase: {phrase}")

    if not has_make_target(makefile, "check-plugin-contract"):
        raise SystemExit("core Makefile missing check-plugin-contract target")
    if EXPECTED_PROTOCOL not in compat:
        raise SystemExit("plugin compatibility doc does not declare expected protocol")
    if "conformance fixture version" not in dist and "conformance fixture" not in dist:
        raise SystemExit("core distribution doc does not describe conformance fixture handoff")

    print(f"check-core-contract: ok ({core})")


if __name__ == "__main__":
    main()
