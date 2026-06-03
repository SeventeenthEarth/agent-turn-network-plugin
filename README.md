# kkachi-agent-network-plugin

`kkachi-agent-network-plugin` is the Python Hermes plugin adapter for KAN. In the current HPLUG-2 state it exposes three read-only Hermes plugin tools through fake/injected transports only: `kan_daemon_status`, `kan_compatibility_diagnostics`, and `kan_stream_tail`. The plugin still has no live daemon discovery, slash commands, Discord helpers, write tools, session-status tool, or installed-plugin smoke claim.

The plugin is not the source of truth. `kkachi-agent-networkd` owns `channel.jsonl`, SQLite projections, locks, replay, cursors, and state transitions.

## Repository boundary

- This repo: Python plugin code, fake/injected-transport daemon client foundation, Hermes tool schemas/handlers, future slash-command bindings, bundled skill material, fake-daemon integration tests, isolated plugin E2E tests.
- Core repo: Go daemon/CLI, protocol SOT, event/state/storage/security/recovery docs.
- Discord helper behavior must record delivery evidence back through typed daemon commands and must not move raw Discord tokens into the daemon.

## Documentation

Start at [`docs/README.md`](docs/README.md).

Key docs:

- [`docs/00-overview.md`](docs/00-overview.md) — plugin purpose and non-goals
- [`docs/01-architecture.md`](docs/01-architecture.md) — plugin architecture
- [`docs/02-plugin-contract.md`](docs/02-plugin-contract.md) — compatibility and fail closed behavior
- [`docs/03-testing-strategy.md`](docs/03-testing-strategy.md) — fake-only integration and isolated E2E policy
- [`docs/04-tooling.md`](docs/04-tooling.md) — Python tooling and Makefile contract

## Current state

HPLUG-2 fake/injected read-only plugin stage. Python package layout, build configuration, package metadata, tiered unit/integration/e2e tests, plugin manifest, root Hermes directory entrypoint, daemon status tool schema/handler, compatibility diagnostics tool schema/handler, and stream tail tool schema/handler are in place. Handlers return JSON strings, preserve fail-closed error categories, redact sensitive diagnostics/stream payloads, and require explicit fake/injected `DaemonClient` factories. `kan_stream_tail` preserves DAEMN-2 behavior by probing `version.read` for `stream_frame` compatibility before `stream.tail`. `kan_session_status` remains deferred until the core repo provides fixture/protocol authority for `session.status.read`. Slash commands, install smoke tests, live daemon support, and live Hermes integration remain pending later tasks.

## Test targets

```bash
make test-prepare  # ruff/mypy/docs guardrails; no live external resources
make test-unit     # unit tests for Python package scaffold and later plugin code
make test-int      # fake daemon/Hermes/Discord integration; no external resources
make test-e2e      # isolated Hermes/Discord test environment only
make test          # sequential all targets
make check-core-contract  # verify companion core milestone/contract readiness
```

`make test-e2e` must never target the currently running Hermes or active Discord thread by default.
