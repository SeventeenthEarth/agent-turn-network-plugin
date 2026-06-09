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

Historical completed plugin tasks before the post-Release live-local work preserve their original short task IDs such as `SCAFF-1`, `DAEMN-1`, and `SKILL-2` for audit continuity. New post-Release cross-repo live-local epics introduced by this update use five-letter uppercase epic IDs and three-digit task IDs: `LTRAN-001`, `PARTC-001`, and `SURFD-001`. Control roadmap IDs use the same five-letter/three-digit convention. When a task ID is cited outside its repo-local roadmap, qualify it as `plugin/<task-id>` or `control/<task-id>`.

Use `docs/07-core-compatibility.md` as the compatibility SOT. The short rule is:

- `SCAFF` can complete before control implementation because it is scaffold/docs/test harness work; its upstream scaffold gate is `BOOTS-001`.
- `DAEMN` can progress with fixtures and fake daemon responses; live/client completion waits for stable control protocol fixtures and daemon status/version surfaces from `DAEMN-002`.
- `HPLUG` can define and test read-only plugin surfaces ahead of control only when matching fake responses or conformance fixtures exist; live tool completion waits for matching daemon/session/status/stream contracts from `DAEMN-002`.
- `DELRV` waits for implemented control delegation/review commands and fixtures from `DELEG-001` before non-skeleton completion.
- `CNDIS` waits for implemented council paths from `COUNC-001` and delivery-evidence command paths from `DAEMN-002` before non-skeleton completion.
- `SKILL` can complete the local compatibility matrix and local isolated plugin-load smoke once `TRANS-001`/`RELIA-001` evidence is recorded, but still cannot claim production activation, KAB readiness, live plugin readiness, live Discord readiness, or live daemon discovery without separate isolated/live tasks.
- `REL-PILOT-FIX` may repair local packaging/import blockers discovered by disposable profile pilots, but those repairs remain local activation-smoke evidence only unless a separately approved live-readiness task runs against live Hermes/Discord/daemon resources.

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
| DELRV-2 | Add delegation/review failure coverage | completed | Added fake-daemon integration tests for delegation/review success, duplicate/idempotency, permission/validation error, retryability preservation, and malformed response cases. Completed after kan-control `DELEG-002` conformance fixture matrix unblock, GLM Octo PASS, post-Octo Red/Orange/Gray re-review ACCEPT, and final verification evidence. |

## CNDIS: Council and Discord surface

Epic ID: `CNDIS`

Exit: council and delivery-evidence surfaces preserve core-owned state and evidence while providing safe Hermes/Discord operator UX in isolated test paths.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| CNDIS-1 | Add council and delivery-evidence plugin tools | completed | Expose implemented council command and delivery-evidence command surfaces through plugin tools while preserving daemon-owned logs, locks, cursors, and evidence transitions. Completed after kan-control `COUNC-001` council paths and `DAEMN-002` delivery-evidence command paths, local verification, first color review, official GLM Octo PASS, post-Octo feedback handling, and final Gray traceability follow-up acceptance. |
| CNDIS-2 | Add Discord helper and isolated E2E coverage | completed | Added the injected-only `kan_discord_send_message` helper and isolated no-live E2E coverage. It never defaults to live Discord or the current Hermes session; any real send path requires an injected sender, dedicated target metadata, visible labels, and cleanup guidance. Completed after local verification, first color review, official GLM Octo PASS, post-Octo feedback handling, and post-Octo Red/Orange/Gray re-review acceptance. |

## SKILL: Skill and distribution

Epic ID: `SKILL`

Exit: the plugin has operator-facing skill/docs, compatibility matrix, troubleshooting, and local isolated plugin-load smoke evidence. This exit is not a production activation, KAB readiness, live plugin readiness, or live Discord readiness claim.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| SKILL-1 | Add bundled KAN skill and operator docs | completed | Added the bundled `kan-plugin` skill surface, import-safe resource reader, install/enable/rollback documentation, troubleshooting guide, and docs/tests guardrails aligned with the plugin's actual fake/injected capabilities and unsupported surfaces. This does not claim installed-plugin or live readiness; SKILL-2 owns plugin-load smoke. Completed after KAH verification, Red/Orange/Gray review, Orange feedback handling and re-review, official GLM Octo PASS, final gate evidence, and 주군 commit approval. |
| SKILL-2 | Add compatibility matrix and plugin-load smoke | completed | Adds the compatibility matrix and `make check-plugin-load-smoke` local isolated plugin-load smoke gate after recording completed control `TRANS-001` and `RELIA-001` evidence as unblock sources. The smoke creates a temporary plugin home from repository files, loads `register(ctx)` with a fake Hermes context, asserts exact tool order, zero hooks, zero commands, fail-closed JSON handlers, live-looking environment inertness, negative command-overclaim fixtures, wheel package inclusion, and bundled skill compatibility. This is local isolated plugin-load smoke only; it does not claim production activation, KAB readiness, live plugin readiness, live daemon discovery, live/default Discord sending, or any change to `provides_commands: []`. Completed after verification, required reviews, final gates, and 주군 commit approval. |

## REL-PILOT-FIX: Release pilot activation repairs

Epic ID: `REL-PILOT-FIX`

Exit: disposable-profile activation blockers discovered by local pilots are captured as regression tests and local smoke coverage while preserving `provides_commands: []`, zero hooks, no live fallback, and no live Discord/Hermes/daemon readiness claim.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| REL-PILOT-FIX-001 | Repair root plugin activation blockers | completed | Repairs the root directory-plugin entrypoint so a cloned/staged repository can load its bundled `src/` package without external `PYTHONPATH`, replaces Python 3.12-only protocol type-alias syntax with Python 3.11-compatible aliases, lowers packaging/tooling metadata to Python `>=3.11`, and strengthens local smoke/unit coverage so production-style root entrypoint loading and Python 3.11 syntax compatibility fail fast. This remains local-only activation-smoke evidence and does not claim live Discord readiness, live daemon discovery, KAB readiness, or live Hermes production readiness. Completed after final gates, 주군 commit approval, and committed-HEAD disposable profile install verification. |

## LTRAN: Live daemon transport

Epic ID: `LTRAN`

Exit: the plugin has an explicit, locally verified live daemon transport that preserves daemon authority, keeps the CLI as the main-agent control plane, keeps the plugin as the participant-agent KAN client surface, and proves plugin reads/writes address the same daemon contract as the CLI. This exit is not production activation, live/default Discord delivery, gateway/auth/token mutation, or KAB bridge readiness.

SOT: `docs/10-live-transport-sot.md`. Control companion SOT: `../../kkachi-agent-network-control/docs/24-live-transport-control-sot.md`.

Dependency gate: complete the control `LTRAN` epic before starting the plugin `LTRAN` implementation epic. Do not switch from plugin `LTRAN` to control tasks mid-epic; if a missing control capability is discovered, block the plugin epic and open/complete the needed control epic before resuming plugin work.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| LTRAN-001 | Lock plugin live transport SOT and mapping | planned | Record the plugin-side daemon/plugin/CLI relationship, main-agent control-plane policy, participant-agent plugin path, operation mapping, ID/idempotency rules, non-scope boundaries, and the control companion SOT dependency. |
| LTRAN-002 | Add explicit plugin live daemon transport | planned | Add an explicit configured Unix-socket daemon client for plugin tools while preserving no-config fail-closed behavior and rejecting unsafe/missing/malformed/incompatible daemon paths without CLI, localhost, Discord, Hermes, gateway, auth, token, or KAB fallback. |
| LTRAN-003 | Prove plugin/CLI/daemon equivalence | planned | Run disposable data-home and disposable Hermes/plugin evidence showing CLI status/version/stream/write commands and plugin status/stream/participant-write tools address the same daemon with matching event/idempotency behavior. |

## PARTC: Participant client path

Epic ID: `PARTC`

Exit: participant agents can observe actionable daemon events and submit participant-originated council writes through the plugin/protocol-client path, with member runtime invocation evidence supplied by the completed control `MEMBR` epic. This exit does not claim always-on production runtimes or simulated role substitution.

SOT: `docs/10-live-transport-sot.md`. Control companion SOT: `../../kkachi-agent-network-control/docs/24-live-transport-control-sot.md`.

Dependency gate: complete the control `MEMBR` epic before starting plugin `PARTC`. Active task transfer between repos happens only at the epic boundary.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| PARTC-001 | Add participant stream and write coverage | planned | Add participant-focused stream/tail/follow/ack support as needed and prove `council.attend`, `council.ready`, `council.prepared_partial`, `council.hand_raise`, `council.speak`, and `council.vote` submit through plugin/protocol-client tools with command-id/idempotency coverage. |
| PARTC-002 | Prove selected participant response path | planned | In an isolated pilot, consume control `MEMBR` evidence that a real participant profile/wrapper responds to `speaker_selected`, then prove the resulting participant output is recorded as `council.speak` through the plugin/protocol-client path without simulated role substitution. |

## SURFD: Surface delivery

Epic ID: `SURFD`

Exit: the plugin-side visible-surface helper/rendering boundary can present daemon event data and record evidence pointers without becoming lifecycle state authority or enabling live/default Discord from plugin registration.

SOT: `docs/10-live-transport-sot.md`. Control companion SOT: `../../kkachi-agent-network-control/docs/24-live-transport-control-sot.md`.

Dependency gate: complete the control `SURFD` epic before starting plugin `SURFD`. Active task transfer between repos happens only at the epic boundary.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| SURFD-001 | Render daemon events to visible discussion surface | planned | Define and verify visible-surface rendering from daemon events, including speech/final-result posting and evidence-pointer handling, without treating visible messages as lifecycle state authority or enabling default live Discord from plugin registration. |
