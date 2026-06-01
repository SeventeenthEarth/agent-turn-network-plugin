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

`make test-prepare` runs formatting, lint, type checking, and docs guardrails.

`make test-unit` runs `pytest tests/unit`.

`make test-int` runs `pytest tests/integration` with fake daemon/Hermes/Discord components and `KAN_EXTERNAL=0`.

`make test-e2e` runs `pytest tests/e2e` only against an isolated test environment. It must not touch the current running Hermes or Discord environment.

`make test` runs all targets sequentially.

## Bootstrap smoke tests

The first plugin scaffold PR should prove:

- plugin package imports;
- plugin manifest is valid;
- all declared tool handlers exist;
- handlers return JSON strings;
- fake daemon compatibility check works;
- `make test` succeeds without external resources.
