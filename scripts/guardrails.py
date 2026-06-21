from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
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
REQUIRED_PHRASES = [
    "plugin is not the source of truth",
    "kkachi-agent-networkd",
    "test-prepare",
    "test-unit",
    "test-int",
    "test-e2e",
    "isolated test environment",
    "fail closed",
    "local isolated plugin-load smoke",
]
FORBIDDEN_PHRASES = ["`../kkachi-agent-network"]
REQUIRED_OPERATOR_PHRASES = [
    "Rollback",
    "Troubleshooting",
    "No-live defaults",
    "registers these read-only plugin-provided skills",
    "provides_commands: []",
    "kan_session_status",
    "SKILL-2",
]
FORBIDDEN_OPERATOR_CLAIMS = [
    "installed-plugin smoke passes",
    "plugin-load smoke passes",
    "production activation is supported",
    "live plugin readiness is supported",
    "KAB readiness is supported",
    "kan_session_status is supported",
    "provides_commands: [kan",
]
BUNDLED_SKILL = "src/hermes_unified_network_plugin/bundled_skills/kan-plugin/SKILL.md"


def read_required_docs(root: Path) -> str:
    docs = root / "docs"
    missing = [name for name in REQUIRED_DOCS if not (docs / name).exists()]
    if missing:
        raise SystemExit(f"missing required docs: {missing}")
    return "\n".join((docs / name).read_text(encoding="utf-8") for name in REQUIRED_DOCS)


def read_all_docs(root: Path) -> str:
    docs = root / "docs"
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(docs.glob("*.md")))


def require_bundled_skill_frontmatter(root: Path) -> None:
    skill_path = root / BUNDLED_SKILL
    if not skill_path.exists():
        raise SystemExit(f"missing bundled skill: {BUNDLED_SKILL}")
    text = skill_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit("bundled skill must start with YAML frontmatter")
    closing = text.find("\n---\n", 4)
    if closing == -1:
        raise SystemExit("bundled skill frontmatter is not closed")
    frontmatter = yaml.safe_load(text[4:closing])
    if not isinstance(frontmatter, dict):
        raise SystemExit("bundled skill frontmatter must be a YAML mapping")
    name = frontmatter.get("name")
    if name != "kan-plugin":
        raise SystemExit(f"bundled skill name mismatch: {name!r}")
    description = frontmatter.get("description")
    if not isinstance(description, str) or not description or len(description) > 1024:
        raise SystemExit("bundled skill description must be a non-empty string <= 1024 chars")
    if not text[closing + len("\n---\n") :].strip():
        raise SystemExit("bundled skill body must be non-empty")


def main(*, root: Path = ROOT) -> None:
    required_text = read_required_docs(root)
    all_docs_text = read_all_docs(root)
    operator_guide = (root / "docs" / "09-skill-and-operator-guide.md").read_text(
        encoding="utf-8"
    )

    for phrase in REQUIRED_PHRASES:
        if phrase not in required_text:
            raise SystemExit(f"missing plugin docs phrase: {phrase}")

    for phrase in REQUIRED_OPERATOR_PHRASES:
        if phrase not in operator_guide:
            raise SystemExit(f"missing operator guide phrase: {phrase}")

    for phrase in FORBIDDEN_PHRASES:
        if phrase in all_docs_text:
            raise SystemExit(f"stale docs-relative sibling path found: {phrase}")

    for phrase in FORBIDDEN_OPERATOR_CLAIMS:
        if phrase in operator_guide:
            raise SystemExit(f"operator guide overclaims unsupported surface: {phrase}")

    require_bundled_skill_frontmatter(root)

    print("docs-guardrails: ok")


if __name__ == "__main__":
    main()
