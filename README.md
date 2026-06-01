# kkachi-agent-network-plugin

`kkachi-agent-network-plugin` is the Python Hermes plugin adapter for KAN. It exposes Hermes tools/slash commands/skill guidance and optional Discord visible-surface helpers over the Go daemon in `../kkachi-agent-network`.

The plugin is not the source of truth. `kkachi-agent-networkd` owns `channel.jsonl`, SQLite projections, locks, replay, cursors, and state transitions.

## Repository boundary

- This repo: Python plugin code, Python daemon client, Hermes tool schemas/handlers, slash-command bindings, bundled skill material, fake-daemon integration tests, isolated plugin E2E tests.
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

Documentation/scaffold stage. Python source scaffolding is not created yet, so Makefile code checks skip with explicit messages while docs guardrails still run.

## Test targets

```bash
make test-prepare  # ruff/mypy/docs guardrails; no external resources
make test-unit     # unit tests; currently docs-only scaffold pass
make test-int      # fake daemon/Hermes/Discord integration; no external resources
make test-e2e      # isolated Hermes/Discord test environment only
make test          # sequential all targets
make check-core-contract  # verify companion core milestone/contract readiness
```

`make test-e2e` must never target the currently running Hermes or active Discord thread by default.
