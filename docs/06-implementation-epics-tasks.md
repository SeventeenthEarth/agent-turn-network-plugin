# Plugin Implementation Epics and Tasks

## Scope

This roadmap and task backlog is for `kkachi-agent-network-plugin`. Control daemon/CLI roadmap lives in `../../kkachi-agent-network-control/docs/09-implementation-epics.md` and `../../kkachi-agent-network-control/docs/roadmap.md`.

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

## Control dependency gates

The plugin may develop ahead of `kkachi-agent-network-control` only when a task can be completed against docs, local fakes, or control conformance fixtures. When a task requires a control daemon capability, command, feature flag, fixture, or delivery-evidence path that does not exist yet, keep or move that task to `blocked` instead of inventing plugin-side fallback behavior.

Control roadmap IDs use five-letter uppercase epic slugs and `{EPIC}-001` task IDs. Plugin epic/task IDs are unchanged; the mappings below name only upstream control gates.

Use `docs/07-core-compatibility.md` as the compatibility SOT. The short rule is:

- `SCAFF` can complete before control implementation because it is scaffold/docs/test harness work; its upstream scaffold gate is `BOOTS-001`.
- `DAEMN` can progress with fixtures and fake daemon responses; live/client completion waits for stable control protocol fixtures and daemon status/version surfaces from `DAEMN-002`.
- `HPLUG` can define and test read-only plugin surfaces ahead of control only when matching fake responses or conformance fixtures exist; live tool completion waits for matching daemon/session/status/stream contracts from `DAEMN-002`.
- `DELRV` waits for implemented control delegation/review commands and fixtures from `DELEG-001` before non-skeleton completion.
- `CNDIS` waits for implemented council paths from `COUNC-001` and delivery-evidence command paths from `DAEMN-002` before non-skeleton completion.
- `SKILL` waits for a real plugin-load/install path plus completed compatibility/release evidence from `TRANS-001`/`RELIA-001` before release-ready completion.

## SCAFF: Scaffold

Epic ID: `SCAFF`

Exit: `make test` and `make check-core-contract` pass without live Hermes, Discord, daemon, or network resources. `make check-core-contract` intentionally requires the local companion control repository, `KAN_CONTROL_REPO`, or legacy `KAN_CORE_REPO`, so protocol drift is detected. This epic may claim scaffold readiness only; do not claim installed/working Hermes integration until an install/plugin-load smoke test exists in `SKILL`.

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
| DAEMN-1 | Implement control protocol client foundation | completed | Implemented status/version reads, command envelope serialization, structured daemon error decoding, idempotency-ready request metadata, and conformance/fake-daemon tests for the minimum safe daemon client. This is fake/injected transport only; live-client readiness remains blocked until stable control status/version fixtures and protocol declarations exist. |
| DAEMN-2 | Implement stream and diagnostics client surfaces | completed | Implemented stream frame parsing, malformed-frame protection, diagnostics response decoding, and fake-daemon coverage for tail/read-only diagnostic paths. Stream tail reads require positive `stream_frame` feature compatibility before `stream.tail` runs. Live stream claims remain blocked until the core stream/status contracts exist. |

## HPLUG: Hermes plugin surface

Epic ID: `HPLUG`

Exit: read-only Hermes plugin tools expose the daemon client safely through JSON-returning handlers with fail-closed errors, documented unsupported surfaces, and no hidden live-resource fallback.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| HPLUG-1 | Add read-only Hermes plugin tools | completed | Defined schemas and implemented fail-closed JSON-returning handlers for daemon status and compatibility diagnostics backed by DAEMN client fixtures. `kan_session_status` is deferred because core `session.status.read` fixture/protocol authority is not available. Closure review: Red `t_bd2965d2`, Orange `t_b18e05d5`, Gray `t_42ad6902` ACCEPT. |
| HPLUG-2 | Add session status and stream/tail plugin tools | completed | Implemented the fake/injected `kan_stream_tail` read-only plugin tool with stream-frame compatibility probing, malformed-frame protection, JSON-string fail-closed handler coverage, and operator docs. `kan_session_status` remains deferred because matching core `session.status.read` fixture/protocol authority is not available. Final closure reviews: Red `t_51358e60` ACCEPT, Orange `t_c6e67e69` ACCEPT, Gray `t_4fcec3cd` ACCEPT. |
| HPLUG-3 | Document unsupported slash-command bindings | completed | Recorded unsupported Hermes/KAN surfaces and future binding requirements while keeping `provides_commands: []` and avoiding live/install readiness claims. Closure reviews: Red `t_588e6985` ACCEPT, Orange `t_c66d72c8` ACCEPT, Gray `t_c2f2e318` ACCEPT after sidecar cleanup. |

## DELRV: Delegation and review tools

Epic ID: `DELRV`

Exit: delegation and review plugin tools map to implemented control commands with idempotency, structured errors, fake-daemon coverage, and no plugin-owned state authority.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| DELRV-1 | Add delegation and review command tools | completed | Implemented and locally verified fake/injected-only `kan_delegate_new` -> `delegate.new` and `kan_delegate_action` -> exact implemented `delegate.*` action/review/delivery command-envelope tools. The plugin requires caller-supplied `request_id`/`idempotency_key`, rejects `delegate.request`, top-level `review`, and non-enum commands before transport, preserves structured daemon errors, keeps `provides_commands: []`, and does not claim live daemon/plugin-load/release readiness. Completion evidence: KAH `run-20260605T182154Z-3fbf63b18b6e`, local `make test-prepare`, `make check-core-contract`, and `make test` pass after optimize, first color review, GLM Octo feedback handling, post-Octo re-review, final KAH gate pass, and 주군 commit approval. |
| DELRV-2 | Add delegation/review failure coverage | blocked | Add fake-daemon integration tests for delegation/review success, retry, duplicate, permission/error, and malformed response cases. Block until `DELEG-001` fixtures define the expected command and error shapes. |

## CNDIS: Council and Discord surface

Epic ID: `CNDIS`

Exit: council and delivery-evidence surfaces preserve core-owned state and evidence while providing safe Hermes/Discord operator UX in isolated test paths.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| CNDIS-1 | Add council and delivery-evidence plugin tools | blocked | Expose implemented council command and delivery-evidence command surfaces through plugin tools while preserving daemon-owned logs, locks, cursors, and evidence transitions. Block until `COUNC-001` council paths and `DAEMN-002` delivery-evidence command paths exist. |
| CNDIS-2 | Add Discord helper and isolated E2E coverage | planned | Add Hermes gateway/send_message boundary helpers and gated isolated E2E coverage that never defaults to the live Discord or current Hermes session. Any real Discord target remains explicit opt-in with visible test labels and cleanup guidance. |

## SKILL: Skill and distribution

Epic ID: `SKILL`

Exit: the plugin has operator-facing skill/docs, compatibility matrix, troubleshooting, and install/plugin-load smoke evidence sufficient for release-readiness claims.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| SKILL-1 | Add bundled KAN skill and operator docs | planned | Add the bundled KAN skill surface, install/enable/rollback documentation, and troubleshooting guide aligned with the plugin's actual capabilities and unsupported surfaces. |
| SKILL-2 | Add compatibility matrix and plugin-load smoke | blocked | Record supported control protocol versions, Hermes expectations, unsupported/degraded combinations, and install/plugin-load smoke tests. Block release-ready completion until the real supported plugin-load path exists and `TRANS-001`/`RELIA-001` compatibility evidence is available. |
