# kkachi-agent-network-plugin

`kkachi-agent-network-plugin` is the Python Hermes plugin adapter for KAN. In the current DAEMN-1 state it contains an import-safe Python daemon-client foundation exercised only through fake/injected transports; Hermes tools, slash commands, Discord helpers, and live daemon support remain unexposed future surfaces.

The plugin is not the source of truth. `kkachi-agent-networkd` owns `channel.jsonl`, SQLite projections, locks, replay, cursors, and state transitions.

## Repository boundary

- This repo: Python plugin code, fake/injected-transport daemon client foundation, future Hermes tool schemas/handlers, future slash-command bindings, bundled skill material, fake-daemon integration tests, isolated plugin E2E tests.
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

DAEMN-1 draft foundation stage. Python package layout, build configuration, package metadata, tiered unit/integration/e2e test infrastructure, plugin manifest, and minimal no-op Hermes directory entrypoint are in place. The daemon client foundation now supports status/version parsing, deterministic command envelopes, structured error decoding, and conformance-manifest guards through explicit fake/injected transports only. Real plugin tools, slash commands, install smoke tests, live daemon support, and live Hermes integration remain pending later tasks.

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
