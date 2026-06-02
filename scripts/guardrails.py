from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = [
    "README.md",
    "00-overview.md",
    "01-architecture.md",
    "02-plugin-contract.md",
    "03-testing-strategy.md",
    "04-tooling.md",
    "05-discord-surface.md",
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
]
FORBIDDEN_PHRASES = ["`../kkachi-agent-network"]


def read_required_docs(root: Path) -> str:
    docs = root / "docs"
    missing = [name for name in REQUIRED_DOCS if not (docs / name).exists()]
    if missing:
        raise SystemExit(f"missing required docs: {missing}")
    return "\n".join((docs / name).read_text(encoding="utf-8") for name in REQUIRED_DOCS)


def read_all_docs(root: Path) -> str:
    docs = root / "docs"
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(docs.glob("*.md")))


def main(*, root: Path = ROOT) -> None:
    required_text = read_required_docs(root)
    all_docs_text = read_all_docs(root)

    for phrase in REQUIRED_PHRASES:
        if phrase not in required_text:
            raise SystemExit(f"missing plugin docs phrase: {phrase}")

    for phrase in FORBIDDEN_PHRASES:
        if phrase in all_docs_text:
            raise SystemExit(f"stale docs-relative sibling path found: {phrase}")

    print("docs-guardrails: ok")


if __name__ == "__main__":
    main()
