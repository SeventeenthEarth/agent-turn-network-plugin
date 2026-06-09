# kkachi-agent-network-plugin Documentation

This directory is the source of truth for the **Python Hermes plugin adapter** for KAN.

Control daemon/CLI authority lives in `../../kkachi-agent-network-control/docs/`. The plugin is not the source of truth. Its current surface is fake/injected Hermes tools over the daemon protocol contract, including CNDIS council and delivery-evidence command submission plus an injected-only Discord helper. SKILL-1 adds a packaged operator skill and guide, but slash commands, live daemon discovery, installed-plugin smoke, and live/default Discord visible-surface wiring remain future task areas.

## Documents

1. `00-overview.md` — plugin purpose, repo boundary, non-goals
2. `01-architecture.md` — Python plugin architecture and daemon boundary
3. `02-plugin-contract.md` — tool/slash-command/client compatibility contract
4. `03-testing-strategy.md` — plugin test layers and isolated E2E policy
5. `04-tooling.md` — Python packaging and Makefile target contract
6. `05-discord-surface.md` — Discord helper behavior and evidence rules
7. `06-implementation-epics-tasks.md` — plugin implementation roadmap and task backlog
8. `07-core-compatibility.md` — control protocol compatibility, milestone matrix, and cross-repo checks
9. `08-unsupported-surfaces.md` — unsupported Hermes/plugin surfaces and future binding requirements
10. `09-skill-and-operator-guide.md` — bundled KAN skill install, enable, rollback, troubleshooting, and SKILL-2 smoke boundary

## Required Makefile targets

```bash
make test-prepare  # ruff format/check, mypy/typecheck, guardrails; no live external resources
make test-unit     # Python unit tests
make test-int      # integration tests using fake daemon/Hermes/gateway only
make test-e2e      # real external tests only in isolated test environment
make test          # sequential: prepare -> unit -> int -> e2e
make check-core-contract  # verify companion control milestone/contract readiness
```

Python package scaffolding, the minimal Hermes plugin manifest/entrypoint, and the packaged SKILL-1 operator skill now exist. Makefile code checks are active when `uv` and `pyproject.toml` are available; docs guardrails must always run.
