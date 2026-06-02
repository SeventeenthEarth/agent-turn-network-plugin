# Plugin Implementation Epics and Tasks

## Scope

This roadmap and task backlog is for `kkachi-agent-network-plugin`. Core daemon/CLI roadmap lives in `../../kkachi-agent-network/docs/09-implementation-epics.md` and `../../kkachi-agent-network/docs/roadmap.md`.

Task status values are limited to:

- `planned`: accepted into the backlog but not started.
- `in_progress`: currently under an active implementation or docs run.
- `completed`: completed with verification evidence.
- `blocked`: blocked by an external dependency, missing input, unavailable fixture, or approval gate.

## Core dependency gates

The plugin may develop ahead of `kkachi-agent-network` only when a task can be completed against docs, local fakes, or core conformance fixtures. When a task requires a core daemon capability, command, feature flag, fixture, or delivery-evidence path that does not exist yet, keep or move that task to `blocked` instead of inventing plugin-side fallback behavior.

Use `docs/07-core-compatibility.md` as the compatibility SOT. The short rule is:

- `SCAFF` can complete before core implementation because it is scaffold/docs/test harness work.
- `DAEMN` can progress with fixtures and fake daemon responses; live/client completion waits for stable core protocol fixtures and daemon status/version surfaces.
- `HPLUG` can define schemas and read-only handlers ahead of core, but tool completion waits for matching daemon/session/status/stream contracts.
- `DELRV` waits for implemented core delegation/review commands before non-skeleton completion.
- `CNDIS` waits for implemented council and delivery-evidence command paths before non-skeleton completion.
- `SKILL` waits for a real plugin-load/install path and a completed compatibility matrix before release-ready completion.

## SCAFF: Scaffold

Epic ID: `SCAFF`

Exit: `make test` and `make check-core-contract` pass without live Hermes, Discord, daemon, or network resources. `make check-core-contract` intentionally requires the local companion core repository, or `KAN_CORE_REPO`, so protocol drift is detected. This epic may claim scaffold readiness only; do not claim installed/working Hermes integration until an install/plugin-load smoke test exists in `SKILL`.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| SCAFF-1 | Initialize Python package layout | completed | Created `pyproject.toml`, `src/` package layout, package metadata, and a minimal importable module with local-only scaffold tests and review evidence. |
| SCAFF-2 | Add plugin manifest and entrypoint | completed | Added `plugin.yaml` and a minimal no-op Hermes directory plugin entrypoint matching the documented plugin contract, with focused manifest/entrypoint tests and review evidence. |
| SCAFF-3 | Establish Makefile target contract | completed | Tightened Makefile target contract, added `check-make-contract` drift verification, preserved offline/isolated test defaults, and recorded review evidence. |
| SCAFF-4 | Add docs and contract guardrails | completed | Added import-safe docs/core contract guardrails, focused guardrail unit tests, all-doc stale sibling path scanning, and recorded review/verification evidence. |
| SCAFF-5 | Add bootstrap smoke tests | completed | Added `check-bootstrap-smoke`, bootstrap smoke unit coverage, Makefile contract drift checks for the target, and review/verification evidence. |

## DAEMN: Python daemon client

Epic ID: `DAEMN`

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| DAEMN-1 | Implement daemon status/version client | planned | Implement the client call that reads daemon status and version compatibility information. |
| DAEMN-2 | Build command envelope serializer | planned | Build the command envelope object/serializer used by plugin tools to talk to the core daemon. |
| DAEMN-3 | Decode structured daemon errors | planned | Map daemon error payloads into stable plugin-facing error categories that fail closed. |
| DAEMN-4 | Parse daemon stream frames | planned | Implement stream frame parsing for tail/diagnostic surfaces with malformed-frame protection. |
| DAEMN-5 | Add core conformance fixture tests | planned | Test the Python client against core conformance fixtures; mark blocked if required core fixtures are not available. |

## HPLUG: Hermes plugin surface

Epic ID: `HPLUG`

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| HPLUG-1 | Define Hermes tool schemas | planned | Add schemas for daemon status, session status, diagnostics, and available read-only surfaces. |
| HPLUG-2 | Implement fail-closed tool handlers | planned | Implement handlers that return structured JSON and preserve daemon/plugin error categories; block handlers whose core contracts are missing. |
| HPLUG-3 | Add diagnostic and stream/tail tools | planned | Expose diagnostics and stream/tail read surfaces without unsafe mutation or hidden fallback behavior; block live claims until core stream/status contracts exist. |
| HPLUG-4 | Add slash-command bindings where supported | planned | Add slash-command bindings only where Hermes support exists and document unsupported surfaces explicitly. |

## DELRV: Delegation and review tools

Epic ID: `DELRV`

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| DELRV-1 | Map core delegation commands | planned | Add plugin tools that match implemented core delegation commands; mark blocked until the corresponding core commands and fixtures exist. |
| DELRV-2 | Map core review commands | planned | Add plugin tools that match implemented core review commands; mark blocked until stable core request/response fixtures exist. |
| DELRV-3 | Preserve idempotency guarantees | planned | Ensure retry-safe operations preserve idempotency keys, duplicate handling, and clear result states. |
| DELRV-4 | Preserve error categories | planned | Keep core error categories visible to Hermes operators without collapsing them into generic failures. |
| DELRV-5 | Add fake-daemon integration tests | planned | Add integration tests using a fake daemon for delegation/review paths and failure cases. |

## CNDIS: Council and Discord surface

Epic ID: `CNDIS`

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| CNDIS-1 | Add council command tools | planned | Expose implemented council command surfaces through plugin tools; mark blocked until core council commands exist. |
| CNDIS-2 | Add Discord surface helper | planned | Add a helper for Discord-facing delivery through Hermes gateway/send_message boundaries. |
| CNDIS-3 | Record delivery evidence | planned | Record delivery evidence through daemon commands; mark blocked until the core delivery-evidence command path exists. |
| CNDIS-4 | Add gated isolated E2E tests | planned | Add E2E tests gated by explicit environment variables so default test runs remain offline and deterministic. |

## SKILL: Skill and distribution

Epic ID: `SKILL`

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| SKILL-1 | Add bundled KAN skill | planned | Add the bundled KAN skill surface and keep its instructions aligned with plugin capabilities. |
| SKILL-2 | Add install and enable docs | planned | Document local install, enablement, configuration, and safe rollback for the plugin. |
| SKILL-3 | Add compatibility matrix | planned | Record supported core protocol versions, Hermes expectations, and unsupported/degraded combinations. |
| SKILL-4 | Add install/plugin-load smoke tests | planned | Add smoke tests proving the plugin can be installed or loaded in the supported Hermes path; mark blocked until that path is implemented. |
| SKILL-5 | Add operator troubleshooting guide | planned | Document common operator failures, evidence to collect, and safe recovery steps. |
