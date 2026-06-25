from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

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
    "atn-controld",
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
    "public ATN operator guidance",
    "provides_commands: []",
    "atn_session_status",
    "SKILL-2",
]
FORBIDDEN_OPERATOR_CLAIMS = [
    "installed-plugin smoke passes",
    "plugin-load smoke passes",
    "production activation is supported",
    "live plugin readiness is supported",
    "KAB readiness is supported",
    "atn_session_status is supported",
    "provides_commands: [kan",
]
BUNDLED_SKILL = "src/atn_plugin/bundled_skills/atn-plugin/SKILL.md"
ATN_PUBLIC_SCAN_SUFFIXES = {".md", ".py", ".toml", ".yaml"}


class ForbiddenTerm(NamedTuple):
    token: str
    category: str


class AllowedOccurrence(NamedTuple):
    path: str
    token: str
    line_contains: str
    reason: str


class ForbiddenInvariantClaim(NamedTuple):
    token: str
    category: str


FORBIDDEN_PUBLIC_TERMS = [
    ForbiddenTerm("KAN plugin", "legacy public plugin identity"),
    ForbiddenTerm("KAN tools", "legacy public tool identity"),
    ForbiddenTerm("KAN daemon", "legacy public daemon identity"),
    ForbiddenTerm("KAN compatibility", "legacy public compatibility identity"),
    ForbiddenTerm("KAN stream", "legacy public stream identity"),
    ForbiddenTerm("KAN session", "legacy public session identity"),
    ForbiddenTerm("kkachi_agent_network_plugin", "legacy package/import path"),
    ForbiddenTerm("src/kkachi_agent_network_plugin", "legacy package/import path"),
    ForbiddenTerm("kkachi-agent-network-plugin", "legacy package/repo label"),
    ForbiddenTerm("kan-plugin", "legacy bundled skill name"),
    ForbiddenTerm("kan-moderator", "legacy bundled skill name"),
    ForbiddenTerm("kan-participant", "legacy bundled skill name"),
    ForbiddenTerm("kan_daemon_status", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_compatibility_diagnostics", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_stream_tail", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_stream_ack", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_delegate_new", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_delegate_action", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_council_command", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_selected_participant_response", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_delivery_evidence", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_surface_render_projection", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_discussion_activation_plan", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_discord_send_message", "legacy Hermes tool alias"),
    ForbiddenTerm("kan_session_status", "legacy Hermes tool alias"),
    ForbiddenTerm("provides_commands: [kan", "legacy command-surface overclaim"),
    ForbiddenTerm("pure RUNFIX discussion activation planner/doctor", "active legacy task label"),
    ForbiddenTerm("legacy wrapper", "legacy compatibility claim"),
    ForbiddenTerm("compatibility alias", "legacy compatibility claim"),
    ForbiddenTerm("dual registration", "legacy compatibility claim"),
    ForbiddenTerm("fallback acceptance", "legacy compatibility claim"),
    ForbiddenTerm("live plugin readiness is supported", "unsupported live readiness claim"),
    ForbiddenTerm("KAB readiness is supported", "unsupported KAB readiness claim"),
    ForbiddenTerm(
        "gateway/auth/token/provider mutation is supported", "unsupported private config claim"
    ),
]

RUNFIX3_INVARIANT_CLAIMS = [
    ForbiddenInvariantClaim(
        "display-name labels satisfy exact-origin proof",
        "display-name labels do not satisfy exact-origin proof",
    ),
    ForbiddenInvariantClaim(
        "channel-name labels satisfy exact-origin proof",
        "channel-name labels do not satisfy exact-origin proof",
    ),
    ForbiddenInvariantClaim(
        "display-name labels prove origin",
        "display-name labels do not prove exact origin",
    ),
    ForbiddenInvariantClaim(
        "channel-name labels prove origin",
        "channel-name labels do not prove exact origin",
    ),
    ForbiddenInvariantClaim(
        "`selected_runner_pass` is a selection mode",
        "selected_runner_pass must remain evidence-derived",
    ),
    ForbiddenInvariantClaim(
        "`selected_runner_pass` is satisfied by fallback/manual speech",
        "fallback/manual speech must not satisfy selected_runner_pass",
    ),
    ForbiddenInvariantClaim(
        "`live_readiness=true` proves live-visible council readiness",
        "live_readiness must not be treated as live-visible readiness proof",
    ),
]

RUNFIX3_OWNER_MARKERS = {
    "docs/09-skill-and-operator-guide.md": "For RUNFIX3 live-thread semantics, this guide and `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md` are the normative procedure owners.",
    "src/atn_plugin/bundled_skills/atn-moderator/SKILL.md": "Canonical live-thread procedure owners for this topic:",
    "src/atn_plugin/bundled_skills/atn-plugin/SKILL.md": "This skill is boundary/cross-link only for RUNFIX3 live-thread semantics.",
    "docs/06-implementation-epics-tasks.md": "Mirror-only status row",
    "docs/10-live-transport-sot.md": "this SOT section remains traceability/status only and must not become another procedure owner.",
}
RUNFIX3_NORMATIVE_OWNER_PATHS = (
    "src/atn_plugin/bundled_skills/atn-moderator/SKILL.md",
    "docs/09-skill-and-operator-guide.md",
)
RUNFIX3_RULE_OWNER_ONLY_PATHS = RUNFIX3_NORMATIVE_OWNER_PATHS
RUNFIX3_RULE_IDS = tuple(f"RUNFIX3-R{index:02d}" for index in range(1, 11))
RUNFIX3_RULE_HEADING = "## ATN council moderation hard rules"
RUNFIX3_RULE_RE = re.compile(r"^\d+\. \[(RUNFIX3-R\d{2})\] (.+\S)$")


ALLOWED_PUBLIC_OCCURRENCES = [
    AllowedOccurrence(
        "docs/03-testing-strategy.md",
        "provides_commands: [kan",
        "rejects command-registering entrypoints or `provides_commands: [kan]`",
        "negative guardrail example, not a supported command surface",
    ),
    AllowedOccurrence(
        "docs/07-core-compatibility.md",
        "provides_commands: [kan",
        "Any `provides_commands: [kan]` historical alias or `register_command` drift fails local smoke.",
        "negative compatibility guardrail, not a supported command surface",
    ),
    AllowedOccurrence(
        "docs/07-core-compatibility.md",
        "provides_commands: [kan",
        "`provides_commands: [kan]` manifest",
        "negative plugin-load smoke fixture, not a supported command surface",
    ),
    AllowedOccurrence(
        "docs/04-tooling.md",
        "kan-plugin",
        "/references/kan-plugin-readiness-and-activation.md",
        "historical installed-profile reference path retained for KAS/KAH provenance",
    ),
    AllowedOccurrence(
        "docs/04-tooling.md",
        "kan-plugin",
        "SKILL-1 originally packaged the historical `kan-plugin` operator skill",
        "historical SKILL-1 provenance before ATN-005 rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_session_status",
        "`kan_session_status` is deferred because core `session.status.read`",
        "historical HPLUG-1/HPLUG-2 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_session_status",
        "`kan_session_status` remains deferred because matching core `session.status.read`",
        "historical HPLUG-2 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_stream_tail",
        "Implemented the fake/injected `kan_stream_tail` read-only plugin tool",
        "historical HPLUG-2 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_delegate_new",
        "`kan_delegate_new` -> `delegate.new`",
        "historical DELRV-1 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_delegate_action",
        "`kan_delegate_action` -> exact implemented",
        "historical DELRV-1 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_discord_send_message",
        "Added the injected-only `kan_discord_send_message` helper",
        "historical CNDIS-2 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan-plugin",
        "Historical row: added the then-current bundled `kan-plugin` skill surface",
        "historical SKILL-1 row before ATN skill rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_selected_participant_response",
        "fake/injected `kan_selected_participant_response` tool",
        "historical PARTC-002 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_selected_participant_response",
        "updates `kan_selected_participant_response` framing",
        "historical ARGUE-002 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_selected_participant_response",
        "ARGUE fields are preserved through `kan_selected_participant_response`",
        "historical RUNFIX-017 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_surface_render_projection",
        "pure/local `kan_surface_render_projection` rendering",
        "historical SURFD-001 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_surface_render_projection",
        "updates `kan_surface_render_projection` so visible rows render",
        "historical ARGUE-003 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_discussion_activation_plan",
        "Historical row: added pure/local `kan_discussion_activation_plan`",
        "historical RUNFIX-006 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_discussion_activation_plan",
        "Extended the existing pure/local `kan_discussion_activation_plan` dry-run tool",
        "historical RUNFIX-007 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_discussion_activation_plan",
        "Extended the existing pure/local `kan_discussion_activation_plan` and packaged",
        "historical RUNFIX-008 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_discussion_activation_plan",
        "implements local pre-`council.new` visible author guard proof in `kan_discussion_activation_plan`",
        "historical RUNFIX-015 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan_discussion_activation_plan",
        "extended the then-current `kan_discussion_activation_plan`, schema",
        "historical RUNFIX-019 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan-plugin",
        "bundled `kan-plugin`/`kan-moderator` skills",
        "historical RUNFIX-019 row before ATN skill rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "kan-moderator",
        "bundled `kan-plugin`/`kan-moderator` skills",
        "historical RUNFIX-019 row before ATN skill rename",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "legacy wrapper",
        "with no legacy wrapper",
        "negative ATN-005 no-wrapper proof, not a compatibility claim",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "dual registration",
        "with no legacy aliases, dual registration, or fallback acceptance",
        "negative ATN-005 no-dual-registration proof, not a compatibility claim",
    ),
    AllowedOccurrence(
        "docs/06-implementation-epics-tasks.md",
        "fallback acceptance",
        "with no legacy aliases, dual registration, or fallback acceptance",
        "negative ATN-005 no-fallback-acceptance proof, not a compatibility claim",
    ),
    AllowedOccurrence(
        "docs/10-live-transport-sot.md",
        "kan_discussion_activation_plan",
        "implemented as pure/local `kan_discussion_activation_plan`",
        "historical RUNFIX-006 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/10-live-transport-sot.md",
        "kan_discussion_activation_plan",
        "extends the pure/local `kan_discussion_activation_plan` with a pre-`council.new`",
        "historical RUNFIX-015 row before ATN tool rename",
    ),
    AllowedOccurrence(
        "docs/10-live-transport-sot.md",
        "kan_discussion_activation_plan",
        "extends `kan_discussion_activation_plan`, schema",
        "historical RUNFIX-019 row before ATN tool rename",
    ),
]


def read_required_docs(root: Path) -> str:
    docs = root / "docs"
    missing = [name for name in REQUIRED_DOCS if not (docs / name).exists()]
    if missing:
        raise SystemExit(f"missing required docs: {missing}")
    return "\n".join((docs / name).read_text(encoding="utf-8") for name in REQUIRED_DOCS)


def read_all_docs(root: Path) -> str:
    docs = root / "docs"
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(docs.glob("*.md")))


def normalize_markdown(text: str) -> str:
    return " ".join(text.split()).lower()


def extract_runfix3_hard_rules(text: str) -> dict[str, str]:
    rules: dict[str, str] = {}
    in_section = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped == RUNFIX3_RULE_HEADING:
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        match = RUNFIX3_RULE_RE.match(stripped)
        if match:
            rule_id, body = match.groups()
            rules[rule_id] = normalize_markdown(body)
    return rules


def public_scan_paths(root: Path) -> list[Path]:
    paths = [
        root / "README.md",
        root / "__init__.py",
        root / "plugin.yaml",
        root / "pyproject.toml",
    ]
    paths.extend(sorted((root / "docs").rglob("*.md")))
    source_root = root / "src" / "atn_plugin"
    paths.extend(
        path
        for path in sorted(source_root.rglob("*"))
        if path.is_file()
        and path.suffix in ATN_PUBLIC_SCAN_SUFFIXES
        and "__pycache__" not in path.parts
    )
    return paths


def is_allowed_public_occurrence(relative_path: str, token: str, line: str) -> bool:
    return any(
        entry.path == relative_path
        and entry.token == token
        and entry.line_contains in line
        and entry.reason
        for entry in ALLOWED_PUBLIC_OCCURRENCES
    )


def require_atn_public_terms(root: Path) -> None:
    for path in public_scan_paths(root):
        if not path.exists():
            continue
        relative_path = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for term in FORBIDDEN_PUBLIC_TERMS:
                if term.token not in line:
                    continue
                if is_allowed_public_occurrence(relative_path, term.token, line):
                    continue
                raise SystemExit(
                    "stale ATN public term found: "
                    f"{relative_path}:{line_number}: {term.token!r} ({term.category})"
                )


def require_runfix3_invariants(root: Path) -> None:
    for path in public_scan_paths(root):
        if not path.exists():
            continue
        relative_path = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for claim in RUNFIX3_INVARIANT_CLAIMS:
                if claim.token not in line:
                    continue
                raise SystemExit(
                    "RUNFIX3 invariant violation: "
                    f"{relative_path}:{line_number}: {claim.token!r} ({claim.category})"
                )


def require_runfix3_owner_markers(root: Path) -> None:
    for relative_path, phrase in RUNFIX3_OWNER_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            raise SystemExit(f"missing RUNFIX3 owner marker file: {relative_path}")
        text = path.read_text(encoding="utf-8")
        if phrase not in text:
            raise SystemExit(f"missing RUNFIX3 owner marker: {relative_path}: {phrase!r}")


def require_runfix3_hard_rule_parity(root: Path) -> None:
    owner_rules: dict[str, dict[str, str]] = {}
    for relative_path in RUNFIX3_NORMATIVE_OWNER_PATHS:
        text = (root / relative_path).read_text(encoding="utf-8")
        rules = extract_runfix3_hard_rules(text)
        if tuple(rules) != RUNFIX3_RULE_IDS:
            raise SystemExit(
                f"RUNFIX3 hard-rule set mismatch: {relative_path}: expected {RUNFIX3_RULE_IDS}, found {tuple(rules)}"
            )
        owner_rules[relative_path] = rules

    baseline_path = RUNFIX3_NORMATIVE_OWNER_PATHS[0]
    baseline_rules = owner_rules[baseline_path]
    for relative_path in RUNFIX3_NORMATIVE_OWNER_PATHS[1:]:
        rules = owner_rules[relative_path]
        if rules != baseline_rules:
            for rule_id in RUNFIX3_RULE_IDS:
                if rules.get(rule_id) != baseline_rules.get(rule_id):
                    raise SystemExit(
                        "RUNFIX3 hard-rule parity drift: "
                        f"{relative_path}:{rule_id}: {rules.get(rule_id)!r} != {baseline_path}:{rule_id}: {baseline_rules.get(rule_id)!r}"
                    )
            raise SystemExit(f"RUNFIX3 hard-rule parity drift: {relative_path}")

    for path in public_scan_paths(root):
        if not path.exists():
            continue
        relative_path = path.relative_to(root).as_posix()
        if relative_path in RUNFIX3_RULE_OWNER_ONLY_PATHS:
            continue
        text = path.read_text(encoding="utf-8")
        for rule_id in RUNFIX3_RULE_IDS:
            if rule_id in text:
                raise SystemExit(
                    f"RUNFIX3 rule id escaped owner surface: {relative_path}: {rule_id}"
                )


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
    if name != "atn-plugin":
        raise SystemExit(f"bundled skill name mismatch: {name!r}")
    description = frontmatter.get("description")
    if not isinstance(description, str) or not description or len(description) > 1024:
        raise SystemExit("bundled skill description must be a non-empty string <= 1024 chars")
    if not text[closing + len("\n---\n") :].strip():
        raise SystemExit("bundled skill body must be non-empty")


def main(*, root: Path = ROOT) -> None:
    required_text = read_required_docs(root)
    all_docs_text = read_all_docs(root)
    operator_guide = (root / "docs" / "09-skill-and-operator-guide.md").read_text(encoding="utf-8")

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
    require_atn_public_terms(root)
    require_runfix3_invariants(root)
    require_runfix3_owner_markers(root)
    require_runfix3_hard_rule_parity(root)

    print("docs-guardrails: ok")


if __name__ == "__main__":
    main()
