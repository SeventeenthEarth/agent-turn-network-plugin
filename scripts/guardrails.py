from pathlib import Path
root = Path(__file__).resolve().parents[1]
docs = root / "docs"
required = ["README.md", "00-overview.md", "01-architecture.md", "02-plugin-contract.md", "03-testing-strategy.md", "04-tooling.md", "05-discord-surface.md", "07-core-compatibility.md"]
missing = [p for p in required if not (docs / p).exists()]
if missing:
    raise SystemExit(f"missing required docs: {missing}")
text = "\n".join(p.read_text(encoding="utf-8") for p in docs.glob("*.md"))
required_phrases = [
    "plugin is not the source of truth",
    "kkachi-agent-networkd",
    "test-prepare", "test-unit", "test-int", "test-e2e",
    "isolated test environment",
    "fail closed",
]
for phrase in required_phrases:
    if phrase not in text:
        raise SystemExit(f"missing plugin docs phrase: {phrase}")
forbidden_phrases = ["`../kkachi-agent-network"]
for phrase in forbidden_phrases:
    if phrase in text:
        raise SystemExit(f"stale docs-relative sibling path found: {phrase}")
print("docs-guardrails: ok")
