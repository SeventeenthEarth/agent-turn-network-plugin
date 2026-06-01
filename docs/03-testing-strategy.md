# Testing Strategy

## Makefile target contract

| Target | Plugin meaning | External resources |
| --- | --- | --- |
| `test-prepare` | ruff format/check, mypy/typecheck, docs guardrails, static safety checks | forbidden |
| `test-unit` | pure Python units for schemas, error rendering, client request construction | forbidden |
| `test-int` | fake daemon, fake Hermes registry, fake send_message/gateway | forbidden |
| `test-e2e` | real daemon/Hermes/Discord only in isolated test environment | allowed only when configured |
| `test` | sequentially runs all four targets | follows each target |

## Unit tests

- tool schema shape and required fields;
- daemon client request construction;
- structured error rendering;
- compatibility check decision table;
- secret redaction and safe logging;
- argv-only CLI fallback builder.

## Integration tests

Integration tests use mock/fake/stub components only:

- fake daemon HTTP/socket server with fixture responses;
- fake stream source with replay/follow frames;
- fake Hermes tool invocation context;
- fake `send_message`/gateway delivery function;
- copied or vendored conformance fixtures from the core repo.

Integration tests must not contact real Hermes, live Discord, or the current daemon.

## E2E tests

E2E tests may use external resources only when explicitly configured for an isolated test environment:

- disposable `HERMES_HOME` or profile home;
- test-only daemon data home;
- dedicated Discord test guild/channel/thread or configured fake gateway;
- no writes to the current live Hermes gateway/session/thread;
- visible test labels and cleanup guidance.

When required environment variables are absent, E2E tests must skip with a clear reason. They must not silently fall back to production resources.
