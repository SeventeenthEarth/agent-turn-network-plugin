# AGENTS.md — KAN Plugin Local Agent Contract

<!-- KAS:MANAGED:BEGIN core-behavior -->
## KAS-managed baseline behavior

These repo-local instructions preserve the useful baseline guardrails from the
`andrej-karpathy-skills` `CLAUDE.md` lineage and adapt them for KAN plugin.
KAS-managed instruction content is policy guidance only. It does not authorize
profile mutation, auth/token changes, provider/model/gateway changes, KAH state
writes beyond the approved project workflow, KAB runtime mutation, commits,
pushes, live activation, Discord delivery, or deployment.

Operating principles:

- Think before coding: read the named source of truth, identify constraints,
  state evidence-backed assumptions, and surface real uncertainty instead of
  guessing.
- Simplicity first: prefer the smallest change that satisfies the task; do not
  add speculative features, compatibility layers, abstractions, or fallbacks.
- Surgical changes: touch only files required by the task, preserve unrelated
  project-local text, and do not reformat or refactor adjacent work.
- Goal-driven execution: turn the task into verifiable checks, run focused tests
  or KAH/KAS gates, read the results, and report exact evidence honestly.
- Artifact-first detail: keep chat/console output compact and point to durable
  artifacts when long plans, logs, diffs, reviews, or evidence are needed.

Layer boundaries:

- KAS owns task classification, workflow guidance, prompt policy, templates, and
  evidence expectations. It must not become a second KAH state system or a KAB
  runtime controller.
- KAH owns deterministic project state, schemas, artifacts, events, locks,
  diagnostics, and pass/fail/not_applicable gates. It must not judge prose
  quality, summarize policy, or rewrite instructions.
- KAB owns backend bridge/session/control behavior and retained backend
  execution evidence. It must not decide KAS task policy, silently substitute
  lanes, or mutate auth/token/provider/model/gateway settings without explicit
  authority.
<!-- KAS:MANAGED:END core-behavior -->

<!-- PROJECT:LOCAL:BEGIN -->

## Identity and scope

This repository is `kkachi-agent-network-plugin`, the Hermes plugin / participant-agent tool-surface lane for KAN.

- Blue commander: 마초 / `macho`
- Red reviewer: 서황 / `seohwang`
- Orange reviewer: 종회 / `jonghoe`
- Gray reviewer: 만총 / `manchong`
- Project ID for KAS/KAH: `kan-plugin`
- Repo path: `/Users/draccoon/Workspace/SeventeenthEarth/kkachi/kkachi-agent-network-plugin`
- Sibling control repo: `/Users/draccoon/Workspace/SeventeenthEarth/kkachi/kkachi-agent-network-control`

마초 owns KAN plugin technical direction, decomposition, sequencing, plan gates, implementation authorization, evidence synthesis, and Blue final reporting. This does not grant KAB/KAH/KAS-wide command authority and does not replace other Kkachi project commanders.

## Installed profile-local KAS suite

KAN plugin KAS skills are installed under the active Hermes profiles, not inside this repository:

```text
~/.hermes/profiles/macho/skills/kan-plugin/       # blue_commander, 18 skills
~/.hermes/profiles/seohwang/skills/kan-plugin/    # red_reviewer, review + verify
~/.hermes/profiles/jonghoe/skills/kan-plugin/     # orange_pm_reviewer, review
~/.hermes/profiles/manchong/skills/kan-plugin/    # gray_scribe, review + final-verify
```

The installed skills are profile-local semantic tailorings of KAS v0.1.3 for this repo. They are not KAS source promotion.

## KAH baseline

KAH v0.1.9 is the current local helper baseline for this repo. KAH project state is repo-local under `.kkachi/` and uses:

```text
commander: macho
redteam: seohwang
stack: python-plugin
backend_policy: stage=stage1_direct_codex_app_server_baseline; allowed=codex_app_server; project=kan-plugin; no_cli_fallback=true
execution_mode: kan-plugin-kas-development
sot_policy: plugin_sot_with_control_dependency_gates; repo_qualified_task_ids_required
```

Do not edit `.kkachi-workflow.yaml` directly when KAH graph proposal/apply is available. Use:

```bash
kkachi-agent-helper graph propose --candidate-file <repo-relative-candidate-graph> --reason <text> --json
kkachi-agent-helper graph apply --proposal <proposal-id> --approval <evidence-ref> --json
kkachi-agent-helper graph validate --json
```

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
5. Active KAH graph: `.kkachi-workflow.yaml`, validated with `kkachi-agent-helper graph validate --json`.
6. Candidate KAS policy note: `/Users/draccoon/Workspace/Hermes/17thHermes/40_outputs/projects/kkachi/2026-06-14-kas-policy-promotion-candidates.md`.

The candidate policy note is guidance only. Do not claim it is already promoted to KAS source.

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

Development-class work uses the active KAH graph:

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

Use explicit skipped-phase reasons for:

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
