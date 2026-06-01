# Plugin Implementation Epics

## Scope

This roadmap is for `kkachi-agent-network-plugin`. Core daemon/CLI roadmap lives in `../../kkachi-agent-network/docs/09-implementation-epics.md` and `../../kkachi-agent-network/docs/roadmap.md`.

## Epic P0: Scaffold

- Create Python package layout.
- Add plugin manifest/entrypoint.
- Add Makefile with required targets.
- Add docs guardrails.
- Add bootstrap smoke tests.

Exit: `make test` and `make check-core-contract` pass without external resources. P0 may claim scaffold readiness only; do not claim installed/working Hermes integration until an install/plugin-load smoke test exists in P5.

## Epic P1: Python daemon client

- Implement status/version compatibility call.
- Implement command envelope builder.
- Implement structured error decoding.
- Implement stream frame parser.
- Add conformance tests against core fixtures.

## Epic P2: Hermes plugin surface

- Add tool schemas and handlers for daemon/session status.
- Add diagnostic and stream/tail tools.
- Add slash-command bindings where Hermes supports them.
- Ensure handlers return JSON and fail closed.

## Epic P3: Delegation/review tools

- Add tools matching implemented core delegation/review commands.
- Preserve idempotency and error categories.
- Add fake-daemon integration tests.

## Epic P4: Council and Discord surface

- Add council command tools.
- Add Discord surface helper using Hermes gateway/send_message.
- Record delivery evidence through daemon commands.
- Add isolated E2E tests gated by explicit test environment variables.

## Epic P5: Skill and distribution

- Add bundled KAN skill.
- Add install/enable docs.
- Add compatibility matrix.
- Add install/plugin-load smoke tests.
- Add operator troubleshooting guide.
