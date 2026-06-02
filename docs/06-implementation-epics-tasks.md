# Plugin Implementation Epics and Tasks

## Scope

This roadmap and task backlog is for `kkachi-agent-network-plugin`. Core daemon/CLI roadmap lives in `../../kkachi-agent-network/docs/09-implementation-epics.md` and `../../kkachi-agent-network/docs/roadmap.md`.

Task status values are limited to:

- `planned`: accepted into the backlog but not started.
- `in_progress`: currently under an active implementation or docs run.
- `completed`: completed with verification evidence.
- `blocked`: blocked by an external dependency, missing input, unavailable fixture, or approval gate.

## KAS/Codex task sizing policy

Tasks after the SCAFF epic are sized as KAH/KAS execution slices for enterprise-style software development. A task should produce one reviewable capability with durable evidence, not just one file or internal component.

Each task should normally include:

- a task contract and plan captured before implementation;
- one Codex app-server implementation lane or an explicitly recorded no-backend/docs-only rationale;
- focused unit and integration coverage, with fake daemon or conformance fixtures where live core behavior is not available;
- documentation and roadmap updates for changed operator behavior;
- Red/Orange/Gray review when code or operator behavior changes, or narrower role review when the task is docs-only and 주군 explicitly narrows the reviewer set;
- feedback handling, final verification, and one commit after 주군 approval.

Split a task only when the dependency, approval gate, failure domain, or reviewer specialty is materially different. Do not split schema from handler, handler from error behavior, or client implementation from conformance coverage when those pieces are required to prove the same operator-facing capability.

## Core dependency gates

The plugin may develop ahead of `kkachi-agent-network` only when a task can be completed against docs, local fakes, or core conformance fixtures. When a task requires a core daemon capability, command, feature flag, fixture, or delivery-evidence path that does not exist yet, keep or move that task to `blocked` instead of inventing plugin-side fallback behavior.

Use `docs/07-core-compatibility.md` as the compatibility SOT. The short rule is:

- `SCAFF` can complete before core implementation because it is scaffold/docs/test harness work.
- `DAEMN` can progress with fixtures and fake daemon responses; live/client completion waits for stable core protocol fixtures and daemon status/version surfaces.
- `HPLUG` can define and test read-only plugin surfaces ahead of core only when matching fake responses or conformance fixtures exist; live tool completion waits for matching daemon/session/status/stream contracts.
- `DELRV` waits for implemented core delegation/review commands before non-skeleton completion.
- `CNDIS` waits for implemented council and delivery-evidence command paths before non-skeleton completion.
- `SKILL` waits for a real plugin-load/install path and a completed compatibility matrix before release-ready completion.

## SCAFF: Scaffold

Epic ID: `SCAFF`

Exit: `make test` and `make check-core-contract` pass without live Hermes, Discord, daemon, or network resources. `make check-core-contract` intentionally requires the local companion core repository, or `KAN_CORE_REPO`, so protocol drift is detected. This epic may claim scaffold readiness only; do not claim installed/working Hermes integration until an install/plugin-load smoke test exists in `SKILL`.

SCAFF intentionally used smaller tasks to validate KAH/KAS/Codex collaboration and review gates. Future epics use larger capability slices to reduce KAH overhead while preserving evidence, review, feedback, and approval gates.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| SCAFF-1 | Initialize Python package layout | completed | Created `pyproject.toml`, `src/` package layout, package metadata, and a minimal importable module with local-only scaffold tests and review evidence. |
| SCAFF-2 | Add plugin manifest and entrypoint | completed | Added `plugin.yaml` and a minimal no-op Hermes directory plugin entrypoint matching the documented plugin contract, with focused manifest/entrypoint tests and review evidence. |
| SCAFF-3 | Establish Makefile target contract | completed | Tightened Makefile target contract, added `check-make-contract` drift verification, preserved offline/isolated test defaults, and recorded review evidence. |
| SCAFF-4 | Add docs and contract guardrails | completed | Added import-safe docs/core contract guardrails, focused guardrail unit tests, all-doc stale sibling path scanning, and recorded review/verification evidence. |
| SCAFF-5 | Add bootstrap smoke tests | completed | Added `check-bootstrap-smoke`, bootstrap smoke unit coverage, Makefile contract drift checks for the target, and review/verification evidence. |

## DAEMN: Python daemon client

Epic ID: `DAEMN`

Exit: the plugin has a fail-closed Python client foundation that can speak to the core daemon contract through fake daemon responses or conformance fixtures, with no live daemon required by default tests.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| DAEMN-1 | Implement core protocol client foundation | planned | Implement status/version reads, command envelope serialization, structured daemon error decoding, idempotency-ready request metadata, and conformance/fake-daemon tests for the minimum safe daemon client. Block any live-client claim until stable core status/version fixtures and protocol declarations exist. |
| DAEMN-2 | Implement stream and diagnostics client surfaces | planned | Implement stream frame parsing, malformed-frame protection, diagnostics response decoding, and fake-daemon coverage for tail/read-only diagnostic paths. Block live stream claims until the core stream/status contracts exist. |

## HPLUG: Hermes plugin surface

Epic ID: `HPLUG`

Exit: read-only Hermes plugin tools expose the daemon client safely through JSON-returning handlers with fail-closed errors, documented unsupported surfaces, and no hidden live-resource fallback.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| HPLUG-1 | Add read-only Hermes plugin tools | planned | Define schemas and implement fail-closed JSON-returning handlers for daemon status, session/status read surfaces, and compatibility diagnostics backed by DAEMN client fixtures. Do not split schema-only work from handler/error behavior unless core fixtures are unavailable and the task must be blocked. |
| HPLUG-2 | Add diagnostics and stream/tail plugin tools | planned | Expose diagnostics and stream/tail read surfaces through plugin tools with fake-stream tests, malformed-frame protection, and operator docs. Block any live stream claim until matching core stream contracts are available. |
| HPLUG-3 | Document unsupported slash-command bindings | planned | Record slash-command support status, unsupported Hermes surfaces, and future binding requirements. Keep docs-only unless Hermes provides a real slash-command binding path during the task. |

## DELRV: Delegation and review tools

Epic ID: `DELRV`

Exit: delegation and review plugin tools map to implemented core commands with idempotency, structured errors, fake-daemon coverage, and no plugin-owned state authority.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| DELRV-1 | Add delegation and review command tools | blocked | Map implemented core delegation/review commands into plugin tools, including request/response schemas, idempotency guarantees, duplicate handling, and error category preservation. Block until the corresponding core commands and fixtures exist. |
| DELRV-2 | Add delegation/review failure coverage | blocked | Add fake-daemon integration tests for delegation/review success, retry, duplicate, permission/error, and malformed response cases. Block until core fixtures define the expected command and error shapes. |

## CNDIS: Council and Discord surface

Epic ID: `CNDIS`

Exit: council and delivery-evidence surfaces preserve core-owned state and evidence while providing safe Hermes/Discord operator UX in isolated test paths.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| CNDIS-1 | Add council and delivery-evidence plugin tools | blocked | Expose implemented council command and delivery-evidence command surfaces through plugin tools while preserving daemon-owned logs, locks, cursors, and evidence transitions. Block until core council and delivery-evidence command paths exist. |
| CNDIS-2 | Add Discord helper and isolated E2E coverage | planned | Add Hermes gateway/send_message boundary helpers and gated isolated E2E coverage that never defaults to the live Discord or current Hermes session. Any real Discord target remains explicit opt-in with visible test labels and cleanup guidance. |

## SKILL: Skill and distribution

Epic ID: `SKILL`

Exit: the plugin has operator-facing skill/docs, compatibility matrix, troubleshooting, and install/plugin-load smoke evidence sufficient for release-readiness claims.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| SKILL-1 | Add bundled KAN skill and operator docs | planned | Add the bundled KAN skill surface, install/enable/rollback documentation, and troubleshooting guide aligned with the plugin's actual capabilities and unsupported surfaces. |
| SKILL-2 | Add compatibility matrix and plugin-load smoke | blocked | Record supported core protocol versions, Hermes expectations, unsupported/degraded combinations, and install/plugin-load smoke tests. Block release-ready completion until the real supported plugin-load path exists. |
