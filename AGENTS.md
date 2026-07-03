# AGENTS.md — ATN Plugin Local Agent Contract

<!-- KAS:MANAGED:BEGIN core-behavior -->
## KAS-managed baseline behavior

These repo-local instructions preserve the useful baseline guardrails from the
`andrej-karpathy-skills` `CLAUDE.md` lineage and adapt them for the ATN plugin repository.
These repo-local instructions are optional development guardrails only. They do
not make KAS, KAH, KAB, or any profile-local skill suite a prerequisite for
working on this repository, and they do not authorize profile mutation,
auth/token changes, provider/model/gateway changes, commits, pushes, live
activation, Discord delivery, or deployment.

Operating principles:

- Think before coding: read the named source of truth, identify constraints,
  state evidence-backed assumptions, and surface real uncertainty instead of
  guessing.
- Simplicity first: prefer the smallest change that satisfies the task; do not
  add speculative features, compatibility layers, abstractions, or fallbacks.
- Surgical changes: touch only files required by the task, preserve unrelated
  project-local text, and do not reformat or refactor adjacent work.
- Goal-driven execution: turn the task into verifiable checks, run focused tests
  or explicitly approved project gates, read the results, and report exact
  evidence honestly.
- Artifact-first detail: keep chat/console output compact and point to durable
  artifacts when long plans, logs, diffs, reviews, or evidence are needed.

Layer boundaries:

- ATN plugin repository source, tests, and docs are sufficient for ordinary
  development. Optional Kkachi workflow helpers may record evidence or reviews
  when explicitly selected, but absence of those helpers or profile-local phase
  skills must not block normal code/docs work.
- The plugin remains a Hermes participant-agent tool surface; the control daemon
  remains lifecycle/event/state authority.
- Backend or workflow helpers must not silently substitute lanes or mutate
  auth/token/provider/model/gateway settings without explicit authority.
<!-- KAS:MANAGED:END core-behavior -->

<!-- PROJECT:LOCAL:BEGIN -->

## Identity and scope

This repository is `atn-plugin`, the Hermes plugin / participant-agent tool-surface lane for ATN.

- Blue commander: 마초 / `macho`
- Red reviewer: 서황 / `seohwang`
- Orange reviewer: 종회 / `jonghoe`
- Gray reviewer: 만총 / `manchong`
- Repo path: `/Users/draccoon/Workspace/SeventeenthEarth/agent-turn-network/agent-turn-network-plugin`
- Sibling control repo: `/Users/draccoon/Workspace/SeventeenthEarth/agent-turn-network/agent-turn-network-control`

마초 owns ATN plugin technical direction, decomposition, sequencing, plan gates, implementation authorization, evidence synthesis, and Blue final reporting. This does not grant KAB/KAH/KAS-wide command authority and does not replace other project commanders.

## Optional development helpers

Profile-local Kkachi/KAS phase skills are development conveniences, not project
requirements and not ATN runtime/operator skills. Do not mention or require profile-local phase-skill names in this repository's product docs or install path.
Ordinary direct edits, tests, docs updates, and reviews may proceed from the repo
SOT and the commands documented here.

When an explicitly selected workflow helper is available, `.kkachi/` and the
local ignored `.kkachi-workflow.yaml` may be used as evidence/state helpers. If those helpers
are unavailable, record the direct-development evidence instead of blocking the
work solely because KAS/KAH is absent.

## Authority order

Use this order when claims conflict:

1. 주군's current instruction.
2. Team registry SOT: `/Users/draccoon/Workspace/Hermes/17thHermes/01_references/team/team-agent-registry.yaml`.
3. ATN plugin SOT:
   - `docs/spec/council-argument-graph-sot.md`
   - `docs/spec/live-transport-sot.md`
   - `docs/roadmap.md`
   - `docs/spec/architecture.md`
   - `docs/spec/compatibility-and-operations.md`
   - `docs/spec/skill-and-operator-guide.md`
4. ATN control dependency SOT:
   - `../agent-turn-network-control/docs/spec/council-argument-graph-sot.md`
   - `../agent-turn-network-control/docs/spec/live-transport-control-sot.md`
   - `../agent-turn-network-control/docs/roadmap.md`
5. Optional workflow helper state under `.kkachi/` only when that helper is explicitly selected and available.

## Plugin/control boundary

The durable ATN runtime relationship is:

```text
main agent / operator
  -> CLI control plane
  -> daemon event/state authority
  -> participant runtimes
  -> participant agents
  -> plugin/protocol-client typed writes
  -> daemon event/state authority
  -> visible surface rendering / evidence pointers
```

Rules:

- The plugin is the participant-agent Hermes tool surface.
- The daemon remains lifecycle, event, and state authority.
- The CLI is the main-agent/operator control plane.
- The plugin must not hide a CLI subprocess fallback.
- The plugin must not treat Discord/Hermes messages as lifecycle state.
- The plugin must not auto-start daemons, infer Discord targets, mutate live profiles, mutate gateway/auth/token/provider settings, or claim production/live Discord readiness without explicit 주군 approval and evidence.
- Visible messages and Discord IDs are evidence pointers only, not lifecycle state authority.
- Repo-qualified task IDs are required across repo boundaries: `plugin/<task-id>` and `control/<task-id>`.

## Current workflow spine

Development-class work may use the optional workflow graph when explicitly selected:

```text
intake -> sot -> roadmap -> task-classification -> plan -> vet -> ask -> implement -> enhance-test -> ai-slop-cleaner -> optimize -> docs -> verify -> review -> request-feedback-1 -> handle-feedback-1 -> mar-review -> second-color-review -> final
```

The local applied graph id is `graph-kkachi-project-kkachi-agent-network-plugin-kas-v017-kah-v013-20260621` and the KAH apply event is `evt-002514`. That graph is historical local workflow state; current local toolchain metadata is `.kkachi/toolchain.yaml` and is refreshed for KAS v0.2.0 / KAH v0.2.0, with KAT v0.1.0 test-runner config in `.kkachi/tester.yaml`.

Plan-stage default:

1. Produce plan evidence.
2. Blue performs direct vet.
3. Red/Orange perform official durable Kanban plan review when KAS/KAH roadmap policy requires it.
4. Requested changes return to the same planner lane.
5. Implementation starts only after required plan acceptance and the ask/authorization gate.

Gray is not a default plan-stage participant unless task-specific authority, risk, or 주군 requires it. Orange is the default PM/operator-value plan reviewer when KAS/KAH roadmap policy requires Red/Orange plan vet. Orange/Gray are normal participants for implementation/final color review.

Color review rules:

- Official ATN plugin color review uses 서황 Red, 종회 Orange, 만총 Gray, and Blue synthesis by 마초.
- `delegate_task`, temporary helpers, and helper output are not official Red/Orange/Gray evidence.
- Color review converges through Blue synthesis, selected implementer-lane adjustment, rerun verification, and re-review until no valid requested changes remain.
- MAR review is the default independent review lane for development/implementation tasks unless 주군 explicitly waives or replaces it before start; required roles are `logic`, `security`, `arch`, `cve`, and `test_adequacy`.
- Post-MAR color review is required for development/implementation tasks unless the task classification records a concrete not-applicable reason.

## Task classification

Use full development spine for implementation or durable behavior changes.

If an optional workflow graph is used, record explicit skipped-phase reasons for:

- `docs_only`
- `research_evidence`
- `simple_command_report`
- `bootstrap_config`
- `collaboration_review`

Do not silently force implementation phases on read-only work, and do not silently skip required phases for implementation work.

## Backend and GJC boundary

For KAS/KAH v0.2 local development in this ATN plugin repo, use the GAJAE GJC delegated-execution lane as the default backend policy:

```text
KAS/KAH phase planning -> GJC delegated execution through KAH wrapper -> candidate design/plan/implementation artifacts
```

KAB remains non-primary unless a later task explicitly selects KAB runtime/session control. Do not use direct `codex app-server` as the default backend lane or as a silent fallback for v0.2 ATN work. Legacy Codex app-server evidence remains historical only and is not current backend-policy authority.

## Verification commands

Use the repo Makefile targets rather than raw broad pytest when possible:

```bash
HOME=/Users/draccoon /Users/draccoon/.local/bin/kkachi-agent-helper-toolchain graph validate --file .kkachi-workflow.yaml --json
HOME=/Users/draccoon /Users/draccoon/.local/bin/kkachi-agent-helper-toolchain project doctor --json
HOME=/Users/draccoon /Users/draccoon/.local/bin/kkachi-agent-skills-toolchain doctor --project . --workflow-graph --json
HOME=/Users/draccoon kkachi-agent-tester run test-prepare
HOME=/Users/draccoon kkachi-agent-tester run check-core-contract
HOME=/Users/draccoon kkachi-agent-tester run test
HOME=/Users/draccoon make test
```

`make test` expands to the project tiered targets and avoids duplicate-test-name import mismatch pitfalls seen with raw broad pytest in related ATN plugin workflows.

## Reporting requirements

Reports to 주군 must separate:

- changed files and profile-local skills;
- commands run and real outputs;
- evidence paths;
- assumptions and blockers;
- accepted risks and rejected points;
- non-scope boundaries;
- remaining approvals needed.

Do not report live readiness, runtime activation, Discord delivery, gateway/provider/auth/token mutation, commit, push, production readiness, KAB readiness, or broad rollout unless 주군 explicitly approved that exact scope and current evidence exists.
<!-- PROJECT:LOCAL:END -->
