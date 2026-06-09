# kkachi-agent-network-plugin Documentation

This directory is the source of truth for the **Python Hermes plugin adapter** for KAN.

Control daemon/CLI authority lives in `../../kkachi-agent-network-control/docs/`. The plugin is not the source of truth. Its current surface is fake/injected Hermes tools over the daemon protocol contract, including CNDIS council and delivery-evidence command submission plus an injected-only Discord helper. SKILL-2 adds a packaged operator skill guide, compatibility matrix, and local isolated plugin-load smoke gate, but slash commands, live daemon discovery, production activation, KAB bridge behavior, and live/default Discord visible-surface wiring remain unsupported.

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
10. `09-skill-and-operator-guide.md` — bundled KAN skill install, enable, rollback, troubleshooting, and local isolated plugin-load smoke boundary
11. `10-live-transport-sot.md` — plugin-side live transport SOT for `LTRAN` / `PARTC` / `SURFD`: main-agent CLI control, participant-agent plugin transport, member runtime response flow, daemon authority boundaries, and control companion SOT dependencies

## Required Makefile targets

```bash
make test-prepare  # ruff format/check, mypy/typecheck, guardrails; no live external resources
make check-plugin-load-smoke  # local isolated plugin-load smoke; no live external resources
make test-unit     # Python unit tests
make test-int      # integration tests using fake daemon/Hermes/gateway only
make test-e2e      # real external tests only in isolated test environment
make test          # sequential: prepare -> unit -> int -> e2e
make check-core-contract  # verify companion control milestone/contract readiness
```

Python package scaffolding, the minimal Hermes plugin manifest/entrypoint, the packaged operator skill, and the local isolated plugin-load smoke gate now exist. Makefile code checks are active when `uv` and `pyproject.toml` are available; docs guardrails must always run.
