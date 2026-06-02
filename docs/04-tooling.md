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
  skills/kkachi-agent-network/SKILL.md
  tests/unit/
  tests/integration/
  tests/e2e/
  docs/
  Makefile
```

## Makefile targets

`make test-prepare` runs formatting, lint, type checking, docs guardrails, and the Makefile target-contract check.

`make check-make-contract` verifies required single-line target declarations, `.PHONY` coverage, `make test` dependencies, preparation-gate dependencies, scoped tool commands, offline integration defaults, and isolated E2E environment variables.

`make test-unit` runs `pytest tests/unit`.

`make test-int` runs `pytest tests/integration` with fake daemon/Hermes/Discord components and `KAN_EXTERNAL=0`.

`make test-e2e` runs `pytest tests/e2e` only against an isolated test environment. It must not touch the current running Hermes or Discord environment.

`make test` depends on `test-prepare`, `test-unit`, `test-int`, and `test-e2e`; the preparation gate must complete before the test tiers under normal serial `make`.

After the Python scaffold exists, `uv` and `pyproject.toml` are required for code/test targets. Missing prerequisites fail with explicit messages instead of silently passing. Default integration and E2E targets still avoid live Hermes, Discord, daemon, and network resources.

## Bootstrap smoke tests

The first plugin scaffold PR should prove:

- plugin package imports;
- plugin manifest is valid;
- all declared tool handlers exist;
- handlers return JSON strings;
- fake daemon compatibility check works;
- `make test` succeeds without external resources.
