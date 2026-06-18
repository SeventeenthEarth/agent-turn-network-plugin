# Tooling

## Baseline decisions

| Item | Decision |
| --- | --- |
| Language | Python |
| Minimum Python | `>=3.11` to match Hermes Python 3.11 runtime compatibility |
| Package manager | `uv` preferred for development |
| Build backend | `hatchling` or current Hermes-compatible Python packaging |
| Source layout | `src/kkachi_agent_network_plugin/` |
| Test runner | `pytest` |
| Async tests | `pytest-asyncio` when stream/client async is introduced |
| Lint/format | `ruff check`, `ruff format` |
| Type checker | `mypy` |
| Operator entrypoint | `Makefile` |

## Target layout

```text
kkachi-agent-network-plugin/
  pyproject.toml
  plugin.yaml
  src/kkachi_agent_network_plugin/
  tests/unit/
  tests/integration/
  tests/e2e/
  docs/
  Makefile
```

## KAS / KAH workflow hygiene

Kan-plugin KAS workflow guidance is maintained in the installed Hermes profile KAS reference, not in a project-local `skills/` directory:

```text
/Users/draccoon/.hermes/profiles/hwangchung/skills/kkachi-orchestrate/references/kan-plugin-readiness-and-activation.md
```

Before a KAH/KAS task starts, refresh CodeGraph with `codegraph index <repo>` when `.codegraph/` exists. If the repository has source but no `.codegraph/`, run `codegraph init -i <repo>`. For a completely empty bootstrap project, record a deferred CodeGraph reason in `codegraph-evidence.md`, then run `codegraph init -i <repo>` after source files exist and before final verification.

The project `.gitignore` must include `.kkachi/`, `.codegraph/`, `.omx/`, `.omc/`, and `.claude-octopus/` so local KAH, CodeGraph, and review-tool state stays out of source control. The `.kkachi-workflow.yaml` graph may opt into KAH checks with `codegraph.evidence` and `gitignore.contains_all` gates.

## Makefile targets

`make test-prepare` runs formatting, lint, type checking, docs guardrails, the Makefile target-contract check, the bootstrap smoke check, and the local isolated plugin-load smoke check.

`make check-make-contract` verifies required single-line target declarations, `.PHONY` coverage, `make test` dependencies, preparation-gate dependencies, scoped tool commands, offline integration defaults, and isolated E2E environment variables.

`make check-bootstrap-smoke` verifies the package import/metadata, fake/injected plugin manifest shape, exact tool registrations, callable handler presence, and root directory-plugin entrypoint availability without registering hooks or KAN slash commands.

`make check-plugin-load-smoke` verifies local isolated plugin-load smoke. It creates a temporary plugin home from repository-local files, loads the root entrypoint through a fake Hermes registration context without externally adding `<plugin>/src` to `PYTHONPATH`, checks exact tool order, zero hooks, zero commands, handler JSON-string fail-closed behavior without injected clients/senders, live-looking environment inertness, negative command-overclaim fixtures, wheel package inclusion, Python 3.11 syntax compatibility, and bundled skill compatibility. It does not inspect or mutate the user's Hermes profile and does not contact daemon, Discord, KAB, gateway, auth, token, provider, localhost, socket, CLI, or network resources.

`make test-unit` runs `pytest tests/unit`.

`make test-int` runs `pytest tests/integration` with fake daemon/Hermes/Discord components and `KAN_EXTERNAL=0`.

`make test-e2e` runs `pytest tests/e2e` with `KAN_E2E=1`, `KAN_DISCORD_E2E=0`, an isolated `HERMES_HOME`, and an empty `DISCORD_TEST_TARGET` by default. It must not touch the current running Hermes or Discord environment.

`make test` depends on `test-prepare`, `test-unit`, `test-int`, and `test-e2e`; the preparation gate must complete before the test tiers under normal serial `make`.

After the Python scaffold exists, `uv` and `pyproject.toml` are required for code/test targets. Missing prerequisites fail with explicit messages instead of silently passing. Default integration and E2E targets still avoid live Hermes, Discord, daemon, and network resources.

## Guardrail scripts

`make docs-guardrails` runs `scripts/guardrails.py`. The script is import-safe for unit testing, verifies the required docs set and required project phrases, and scans all `docs/*.md` files for stale docs-relative sibling paths. It does not duplicate Makefile target structure checks; `make check-make-contract` owns Makefile structure.

`make check-core-contract` runs `scripts/check_core_contract.py`. The script is import-safe for unit testing and verifies the local companion control repo, `KAN_CONTROL_REPO`, or legacy `KAN_CORE_REPO`, exposes the expected conformance manifest protocol, cross-repo development phrases, distribution fixture handoff wording, reciprocal `check-plugin-contract` Makefile target, and matching plugin compatibility declaration.

## Bundled skill resources

SKILL-1 packaged the `kan-plugin` operator skill under
`src/kkachi_agent_network_plugin/bundled_skills/kan-plugin/SKILL.md` and exposes
`kkachi_agent_network_plugin.bundled_skills.read_bundled_skill_text(...)` for
tests and installer checks. SKILL-2 verifies that resource in the local
isolated plugin-load smoke gate.

The helper reads package resources only. It does not install into a Hermes
profile, discover current-session state, contact live Hermes/Discord/daemon
resources, mutate the sibling control repo, or alter `plugin.yaml`. Operator
install, enable, rollback, troubleshooting, no-live defaults, and the SKILL-2
local isolated plugin-load smoke boundary are documented in `docs/09-skill-and-operator-guide.md`.

## Bootstrap smoke tests

SCAFF-5 delivers a scaffold smoke gate for the first plugin scaffold PR. It proves:

- the plugin package imports through the `src/` layout and exposes stable metadata;
- the plugin manifest is a YAML mapping with the expected name, version, standalone kind, exact `provides_tools: [kan_daemon_status, kan_compatibility_diagnostics, kan_stream_tail, kan_stream_ack, kan_delegate_new, kan_delegate_action, kan_council_command, kan_selected_participant_response, kan_delivery_evidence, kan_surface_render_projection, kan_discussion_activation_plan, kan_discord_send_message]`, and explicit empty `provides_hooks: []` / `provides_commands: []` declarations;
- the root directory-plugin entrypoint exposes `register(ctx)`;
- the entrypoint registers callable fake/injected JSON-string handlers and does not register hooks or KAN slash commands;
- `make test` succeeds without live Hermes, Discord, daemon, or network resources.

DAEMN-1 added fake daemon compatibility probes for the client foundation only. At that stage, full plugin-bootstrap checks that required real declared tool handlers and handler JSON-string return contracts were deferred. HPLUG-2 now enables those checks for the three read-only JSON-string handlers.

SCAFF-5 introduced smoke coverage in `scripts/check_bootstrap_smoke.py` and `tests/unit/test_bootstrap_smoke.py`; HPLUG-2 updated it for the three read-only tool registrations, DELRV-1 extended it for the two delegation/review command-envelope tools, CNDIS-1 extended it for the council and delivery-evidence command tools, and CNDIS-2 extends it for the injected-only Discord helper while keeping the explicit empty slash-command surface. This proves manifest/entrypoint/handler-contract readiness only.

SKILL-2 adds `scripts/check_plugin_load_smoke.py` and `tests/unit/test_plugin_load_smoke.py` as a bounded local isolated plugin-load smoke gate. REL-PILOT-FIX-001 strengthened it so the repository plugin surface must be discovered and loaded in a temporary fake Hermes context without test-side `PYTHONPATH` help; the root entrypoint owns adding its bundled `src/` path before importing runtime modules. The gate also fails closed for unsupported live surfaces. It is not production activation, live plugin readiness, KAB readiness, or live Hermes/Discord evidence.

REL-PILOT-FIX-001 also adds Python 3.11 syntax compatibility coverage. `pyproject.toml` declares `requires-python = ">=3.11"`, Ruff targets `py311`, mypy type checks as Python 3.11, and unit tests parse repository Python sources with `ast.parse(..., feature_version=(3, 11))` so Python 3.12-only syntax such as PEP 695 `type` aliases cannot re-enter unnoticed.

## DAEMN-1 client modules

The DAEMN-1 implementation is import-safe and dependency-free:

- `protocol.py` owns protocol constants, status/version/result models, canonical JSON, and command envelopes.
- `errors.py` owns structured daemon error decoding and redaction.
- `conformance.py` owns conformance manifest parsing and the draft zero-fixture guard.
- `client/daemon.py` owns status/version reads and command submission through an explicit transport.
- `client/transport.py` provides the transport protocol and a static fake transport for tests.

There is no live daemon, Hermes, Discord, KAB, auth, token, gateway, localhost, or CLI fallback in these modules.

## DAEMN-2 client modules

DAEMN-2 stays synchronous, import-safe, and dependency-free:

- `client/stream.py` parses stream frames from mappings or NDJSON lines and parses fake `stream.tail` responses.
- `client/diagnostics.py` decodes fake diagnostics responses and applies the existing sensitive-data redaction rules.
- `client/daemon.py` exposes `read_stream_tail()` and `read_diagnostics()` through the existing explicit transport boundary. `read_stream_tail()` performs a `version.read` compatibility probe and requires `stream_frame` support before a stream operation runs.
- `client/transport.py` deep-copies static fake responses so nested stream/diagnostics fixtures cannot leak mutation between calls.

No async test dependency is introduced because DAEMN-2 does not implement live streaming, socket/SSE/WebSocket clients, or daemon discovery.


## HPLUG-2 plugin modules

HPLUG-2 maps DAEMN-2 stream-tail support into the plugin layer without adding dependencies:

- `schemas.py` declares `kan_stream_tail` with required `session_id`/`member`, optional `since_cursor`, bounded `limit`, and `additionalProperties: false`.
- `tools.py` validates stream-tail args before transport, requires explicit `client_factory`, calls `read_stream_tail()`, serializes frames/events into JSON, and redacts sensitive payload/details values.
- `plugin.yaml`, the root entrypoint, and bootstrap smoke tests include these read-only tools and still no hooks or slash commands.

## DELRV-1 plugin modules

DELRV-1 maps exact daemon-owned delegation/review command names into fake/injected Hermes tools without adding dependencies:

- `schemas.py` declares `kan_delegate_new` and `kan_delegate_action`; the action schema uses a closed enum for implemented `delegate.*` commands and omits `delegate.request` / top-level `review`.
- `tools.py` validates required caller-supplied `request_id` and `idempotency_key`, builds command envelopes through `DaemonClient.build_command_envelope(...)`, submits via `submit_command(...)`, preserves structured daemon errors, and does not generate IDs or keep lifecycle/idempotency state.
- `kan_delegate_action` always overwrites/sets `payload.session_id` from the top-level `session_id` before submit.
- `plugin.yaml`, the root entrypoint, and bootstrap smoke tests declare the two DELRV-1 tools while preserving `provides_commands: []`.

No live daemon discovery, localhost/socket transport, Hermes/Discord/gateway/auth/token access, or CLI fallback is introduced.

## CNDIS-1 plugin modules

CNDIS-1 maps exact daemon-owned council and delivery-evidence command names into fake/injected Hermes tools without adding dependencies:

- `protocol.py` declares `delivery_evidence` and `council.lifecycle` feature groups and required feature tuples.
- `client/daemon.py` exposes `require_feature_groups(...)`, which performs injected `version.read` only and fails closed before submit on missing features.
- `schemas.py` declares `kan_council_command` and `kan_delivery_evidence` with closed enums and `additionalProperties: false`.
- `tools.py` validates command-specific payload fields, preserves caller-supplied `request_id`/`idempotency_key`, normalizes top-level `session_id` into the command payload, probes required features, and submits through the explicit fake/injected client.
- `plugin.yaml`, the root entrypoint, and bootstrap smoke tests declare the two CNDIS-1 tools while preserving `provides_hooks: []` and `provides_commands: []`.

No live daemon discovery, localhost/socket transport, Hermes/Discord/gateway/auth/token/KAB access, CLI fallback, plugin-owned logs/locks/cursors, council lifecycle/consensus state, idempotency/dedupe, or delivery-evidence transitions are introduced.

## CNDIS-2 Discord helper module

CNDIS-2 adds `discord_surface.py` and the `kan_discord_send_message` schema/handler
without adding dependencies:

- `discord_surface.py` defines typed target/result objects, a `SendMessageFn` protocol,
  `send_discord_message(...)`, and inert `e2e_config_from_env(...)` parsing from an
  explicitly supplied mapping;
- `schemas.py` declares a target-gated `kan_discord_send_message` tool schema;
- `tools.py` requires an injected sender and renders fail-closed JSON when the sender,
  target, dedicated-test marker, visible live label, or cleanup hint is missing;
- `plugin.yaml`, the root entrypoint, and bootstrap smoke tests declare the helper tool
  while preserving `provides_hooks: []` and `provides_commands: []`.

No environment read, live Discord discovery, Hermes current-session lookup, gateway/auth
token usage, native Discord slash command, KAN slash command, or daemon delivery-evidence
transition is introduced.
