# AGENTS.md — KAN Plugin Local Agent Contract

<!-- KAS:MANAGED:BEGIN core-behavior -->
## KAS-managed baseline behavior

These repo-local instructions preserve the useful baseline guardrails from the
`andrej-karpathy-skills` `CLAUDE.md` lineage and adapt them for KAN plugin.
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

- KAN plugin repository source, tests, and docs are sufficient for ordinary
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

This repository is `kkachi-agent-network-plugin`, the Hermes plugin / participant-agent tool-surface lane for KAN.

- Blue commander: 마초 / `macho`
- Red reviewer: 서황 / `seohwang`
- Orange reviewer: 종회 / `jonghoe`
- Gray reviewer: 만총 / `manchong`
- Repo path: `/Users/draccoon/Workspace/SeventeenthEarth/kkachi/kkachi-agent-network-plugin`
- Sibling control repo: `/Users/draccoon/Workspace/SeventeenthEarth/kkachi/kkachi-agent-network-control`

마초 owns KAN plugin technical direction, decomposition, sequencing, plan gates, implementation authorization, evidence synthesis, and Blue final reporting. This does not grant KAB/KAH/KAS-wide command authority and does not replace other Kkachi project commanders.

## Optional development helpers

Profile-local Kkachi/KAS phase skills are development conveniences, not project
requirements and not KAN runtime/operator skills. Do not mention or require profile-local phase-skill names in this repository's product docs or install path.
Ordinary direct edits, tests, docs updates, and reviews may proceed from the repo
SOT and the commands documented here.

When an explicitly selected workflow helper is available, `.kkachi/` and
`.kkachi-workflow.yaml` may be used as evidence/state helpers. If those helpers
are unavailable, record the direct-development evidence instead of blocking the
work solely because KAS/KAH is absent.

## Authority order

Use this order when claims conflict:

1. 주군's current instruction.
2. Team registry SOT: `/Users/draccoon/Workspace/Hermes/17thHermes/01_references/team/team-agent-registry.yaml`.
3. KAN plugin SOT:
   - `docs/11-council-argument-graph-sot.md`
   - `docs/10-live-transport-sot.md`
   - `docs/06-implementation-epics-tasks.md`
   - `docs/02-plugin-contract.md`
   - `docs/01-architecture.md`
   - `docs/07-core-compatibility.md`
   - `docs/09-skill-and-operator-guide.md`
4. KAN control dependency SOT:
   - `../kkachi-agent-network-control/docs/25-council-argument-graph-sot.md`
   - `../kkachi-agent-network-control/docs/24-live-transport-control-sot.md`
   - `../kkachi-agent-network-control/docs/roadmap.md`
5. Optional workflow helper state under `.kkachi/` only when that helper is explicitly selected and available.

## Plugin/control boundary

The durable KAN runtime relationship is:

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
intake -> sot -> roadmap -> task-classification -> plan -> vet -> ask -> implement -> enhance-test -> ai-slop-cleaner -> optimize -> docs-update -> verify -> color-review -> color-adjust -> octo-review -> octo-adjudication -> post-octo-adjust -> final
```

Plan-stage default:

1. Produce plan evidence.
2. Blue performs direct vet.
3. Red performs official durable Kanban plan review.
4. Requested changes return to the same planner lane.
5. Implementation starts only after Blue + Red plan acceptance and the ask/authorization gate.

Orange/Gray are not default plan-stage participants unless task-specific authority, risk, or 주군 requires them. They are normal participants for implementation/final color review.

Color review rules:

- Official KAN plugin color review uses 서황 Red, 종회 Orange, 만총 Gray, and Blue synthesis by 마초.
- `delegate_task`, temporary helpers, and Octo/helper output are not official Red/Orange/Gray evidence.
- Color review converges through Blue synthesis, selected implementer-lane adjustment, rerun verification, and re-review until no valid requested changes remain.
- GLM Octo is one official external review event unless waived or separately scoped. Octo feedback is adjudicated by Blue + color reviewers; valid findings then route through the selected implementer lane.

## Task classification

Use full development spine for implementation or durable behavior changes.

If an optional workflow graph is used, record explicit skipped-phase reasons for:

- `docs_only`
- `research_evidence`
- `simple_command_report`
- `bootstrap_config`
- `collaboration_review`

Do not silently force implementation phases on read-only work, and do not silently skip required phases for implementation work.

## Backend and Codex boundary

Stage 1 KAN plugin implementation uses the local Codex app-server path when a backend lane is needed:

```text
openai_codex.Codex / CodexConfig
  -> codex app-server --listen stdio://
```

Do not substitute `codex exec` for a lane labeled `codex app-server`. If the app-server SDK path is unavailable, report a blocker instead of falling back silently.

## Verification commands

Use the repo Makefile targets rather than raw broad pytest when possible:

```bash
kkachi-agent-helper graph validate --json
kkachi-agent-helper project doctor --json
kkachi-agent-skills doctor --workflow-graph --project /Users/draccoon/Workspace/SeventeenthEarth/kkachi/kkachi-agent-network-plugin --json
make test-prepare
make check-core-contract
make test
```

`make test` expands to the project tiered targets and avoids duplicate-test-name import mismatch pitfalls seen with raw broad pytest in related KAN plugin workflows.

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
