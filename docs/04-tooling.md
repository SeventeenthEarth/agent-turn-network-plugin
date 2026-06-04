# Tooling

## Baseline decisions

| Item | Decision |
| --- | --- |
| Language | Python |
| Minimum Python | `>=3.12` unless Hermes runtime requires otherwise |
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

`make test-prepare` runs formatting, lint, type checking, docs guardrails, the Makefile target-contract check, and the bootstrap smoke check.

`make check-make-contract` verifies required single-line target declarations, `.PHONY` coverage, `make test` dependencies, preparation-gate dependencies, scoped tool commands, offline integration defaults, and isolated E2E environment variables.

`make check-bootstrap-smoke` verifies the package import/metadata, HPLUG-2/HPLUG-3 plugin manifest shape, exact read-only tool registrations, callable handler presence, and root directory-plugin entrypoint availability without registering hooks or KAN slash commands.

`make test-unit` runs `pytest tests/unit`.

`make test-int` runs `pytest tests/integration` with fake daemon/Hermes/Discord components and `KAN_EXTERNAL=0`.

`make test-e2e` runs `pytest tests/e2e` only against an isolated test environment. It must not touch the current running Hermes or Discord environment.

`make test` depends on `test-prepare`, `test-unit`, `test-int`, and `test-e2e`; the preparation gate must complete before the test tiers under normal serial `make`.

After the Python scaffold exists, `uv` and `pyproject.toml` are required for code/test targets. Missing prerequisites fail with explicit messages instead of silently passing. Default integration and E2E targets still avoid live Hermes, Discord, daemon, and network resources.

## Guardrail scripts

`make docs-guardrails` runs `scripts/guardrails.py`. The script is import-safe for unit testing, verifies the required docs set and required project phrases, and scans all `docs/*.md` files for stale docs-relative sibling paths. It does not duplicate Makefile target structure checks; `make check-make-contract` owns Makefile structure.

`make check-core-contract` runs `scripts/check_core_contract.py`. The script is import-safe for unit testing and verifies the local companion control repo, `KAN_CONTROL_REPO`, or legacy `KAN_CORE_REPO`, exposes the expected conformance manifest protocol, cross-repo development phrases, distribution fixture handoff wording, reciprocal `check-plugin-contract` Makefile target, and matching plugin compatibility declaration.

## Bootstrap smoke tests

SCAFF-5 delivers a scaffold smoke gate for the first plugin scaffold PR. It proves:

- the plugin package imports through the `src/` layout and exposes stable metadata;
- the plugin manifest is a YAML mapping with the expected name, version, standalone kind, exact `provides_tools: [kan_daemon_status, kan_compatibility_diagnostics, kan_stream_tail]`, and explicit empty `provides_hooks: []` / `provides_commands: []` declarations;
- the root directory-plugin entrypoint exposes `register(ctx)`;
- the HPLUG-2/HPLUG-3 entrypoint registers callable read-only JSON-string handlers and does not register hooks or KAN slash commands;
- `make test` succeeds without live Hermes, Discord, daemon, or network resources.

DAEMN-1 added fake daemon compatibility probes for the client foundation only. At that stage, full plugin-bootstrap checks that required real declared tool handlers and handler JSON-string return contracts were deferred. HPLUG-2 now enables those checks for the three read-only JSON-string handlers.

SCAFF-5 introduced smoke coverage in `scripts/check_bootstrap_smoke.py` and `tests/unit/test_bootstrap_smoke.py`; HPLUG-2 updates it for the three read-only tool registrations, and HPLUG-3 keeps the explicit empty command surface while documenting future slash-command requirements. This proves manifest/entrypoint/handler-contract readiness only; it does not claim installed Hermes plugin loading.

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
- `plugin.yaml`, the root entrypoint, and bootstrap smoke tests now declare exactly three read-only tools and still no hooks or commands.
