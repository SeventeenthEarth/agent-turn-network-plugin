# kkachi-agent-network-plugin Documentation

This directory is the source of truth for the **Python Hermes plugin adapter** for KAN.

Core daemon/CLI authority lives in `../../kkachi-agent-network/docs/`. The plugin is not the source of truth. It provides Hermes-facing tools, slash commands, skill guidance, and Discord visible-surface helpers over the daemon protocol contract.

## Documents

1. `00-overview.md` — plugin purpose, repo boundary, non-goals
2. `01-architecture.md` — Python plugin architecture and daemon boundary
3. `02-plugin-contract.md` — tool/slash-command/client compatibility contract
4. `03-testing-strategy.md` — plugin test layers and isolated E2E policy
5. `04-tooling.md` — Python packaging and Makefile target contract
6. `05-discord-surface.md` — Discord helper behavior and evidence rules
7. `06-implementation-epics.md` — plugin implementation roadmap
8. `07-core-compatibility.md` — core protocol compatibility, milestone matrix, and cross-repo checks

## Required Makefile targets

```bash
make test-prepare  # ruff format/check, mypy/typecheck, guardrails; no external resources
make test-unit     # Python unit tests
make test-int      # integration tests using fake daemon/Hermes/gateway only
make test-e2e      # real external tests only in isolated test environment
make test          # sequential: prepare -> unit -> int -> e2e
make check-core-contract  # verify companion core milestone/contract readiness
```

Until Python scaffolding exists, Makefile code checks may skip with an explicit message, but docs guardrails must still run.
