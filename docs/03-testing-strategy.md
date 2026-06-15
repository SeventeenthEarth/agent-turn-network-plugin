# Testing Strategy

## Makefile target contract

| Target | Plugin meaning | External resources |
| --- | --- | --- |
| `test-prepare` | ruff format/check, mypy/typecheck, docs guardrails, Makefile contract check, bootstrap smoke check, local isolated plugin-load smoke check, static safety checks | forbidden |
| `test-unit` | pure Python units for schemas, error rendering, client request construction | forbidden |
| `test-int` | fake daemon, fake Hermes registry, fake send_message/gateway | forbidden |
| `test-e2e` | real daemon/Hermes/Discord only in isolated test environment | allowed only when configured |
| `test` | depends on the preparation, unit, integration, and E2E targets | follows each target |

## Unit tests

- tool schema shape and required fields;
- daemon client request construction and explicit injected-transport requirement;
- structured error rendering and redaction;
- compatibility/conformance manifest decision table, including the zero-fixture draft rule;
- secret redaction and safe logging;
- argv-only CLI fallback builder.

## Integration tests

Integration tests use mock/fake/stub components only:

- fake daemon injected transport with fixture responses;
- fake stream source with replay/follow frames;
- fake Hermes tool invocation context;
- fake `send_message`/gateway delivery function;
- copied/plugin-local draft conformance manifests from the control repo.

Integration tests must not contact real Hermes, live Discord, or the current daemon.

## E2E tests

E2E tests may use external resources only when explicitly configured for an isolated test environment:

- disposable `HERMES_HOME` or profile home;
- test-only daemon data home;
- dedicated Discord test guild/channel/thread or configured fake gateway;
- no writes to the current live Hermes gateway/session/thread;
- visible test labels and cleanup guidance.

When required environment variables are absent, E2E tests must skip with a clear reason. They must not silently fall back to production resources.

## Makefile drift checks

`make check-make-contract` verifies required single-line target declarations, `.PHONY` coverage, `make test` dependencies, preparation-gate dependencies, scoped tool commands, offline integration defaults, and isolated E2E environment variables. `make test-prepare` includes this check so target-contract drift is caught before tests run.

`make check-bootstrap-smoke` verifies fake/injected plugin bootstrap readiness: package import/metadata through the `src/` layout, plugin manifest shape with exactly `kan_daemon_status`, `kan_compatibility_diagnostics`, `kan_stream_tail`, `kan_stream_ack`, `kan_delegate_new`, `kan_delegate_action`, `kan_council_command`, `kan_selected_participant_response`, `kan_delivery_evidence`, `kan_surface_render_projection`, and `kan_discord_send_message`, explicit empty hook/command declarations, and root entrypoint registration of callable JSON-string handlers without hooks or slash commands.

`make check-plugin-load-smoke` verifies local isolated plugin-load smoke only. It copies repository-local plugin files into a temporary plugin home, loads the root `register(ctx)` entrypoint with a fake Hermes context, asserts the exact manifest-declared tools in order, asserts no hooks or commands, calls representative handlers without injected clients/senders and requires JSON `ok:false`, verifies live-looking environment variables do not change behavior, rejects command-registering entrypoints or `provides_commands: [kan]`, and checks wheel package inclusion plus bundled skill compatibility. It does not read a live Hermes profile, contact a daemon, open sockets, call KAB, contact Discord/gateway/auth/token/provider resources, or prove production activation.

Once the Python scaffold exists, missing `uv` or `pyproject.toml` is a fail-safe prerequisite error for code/test targets rather than a silent pass. Live external resources remain forbidden by default.

## DAEMN-1 fake-daemon coverage

DAEMN-1 tests are fake-only. Unit tests cover canonical envelope serialization, explicit idempotency metadata, unsupported protocol failures, missing feature failures, malformed response failures, structured error preservation/redaction, and conformance manifest fail-closed behavior. Integration tests use `StaticDaemonTransport` to simulate status/version reads, command success, command conflict, and malformed command responses. E2E coverage is limited to proving that live-looking environment variables do not create a live daemon fallback.

## DAEMN-2 fake stream and diagnostics coverage

DAEMN-2 remains fake-only by default:

- unit tests cover stream frame parsing from mappings and NDJSON lines, stream error-frame redaction, malformed frame/event/tail fail-closed cases, diagnostics decoding/redaction, malformed diagnostics fail-closed cases, and oversized frames/checks arrays;
- unit and integration tests prove `read_stream_tail()` requires positive `stream_frame` feature compatibility before `stream.tail` succeeds;
- integration tests use `StaticDaemonTransport` for stream tail and diagnostics success/malformed responses and assert the exact fake operation sequence;
- E2E no-live-fallback tests include live-looking daemon/stream/auth/token environment variables and still require explicit fake/injected transport behavior.

These tests do not open sockets, start a daemon, call the CLI, inspect Hermes runtime state, contact Discord/KAB/gateway/auth surfaces, or claim live stream readiness.

## HPLUG-2 read-only plugin tool coverage

HPLUG-2 remains fake/injected-only by default:

- unit tests cover exact tool schema names, manifest declarations, root entrypoint registration, JSON-string handler success envelopes, fail-closed handler errors, diagnostics/stream redaction, stream-tail argument validation, and deferred absence of `kan_session_status`;
- integration tests use a fake Hermes context and `StaticDaemonTransport` to invoke `kan_daemon_status`, `kan_compatibility_diagnostics`, and `kan_stream_tail`, asserting the exact `status.read` / `diagnostics.read` / `version.read` + `stream.tail` operation sequence;
- E2E smoke tests run only with isolated `KAN_E2E=1` defaults and prove live-looking daemon/stream/Discord/token environment variables do not create live fallback behavior.

These tests do not claim installed-plugin loading, live daemon readiness, session-status support, slash commands, write tools, or Discord helper readiness.

## DELRV-1 delegation/review command-envelope coverage

DELRV-1 remains fake/injected-only by default:

- unit tests cover `kan_delegate_new` and `kan_delegate_action` schemas, exact closed `delegate.*` enum membership, absence of `delegate.request` and top-level `review`, caller-supplied `request_id`/`idempotency_key`, deterministic action `session_id` payload normalization, JSON-string success envelopes, validation failures before transport, structured daemon `conflict` preservation, malformed response protocol failures, and missing-client `unavailable` failures;
- integration tests use a fake Hermes context and `StaticDaemonTransport` to invoke the delegation handlers and assert exact `command.submit` envelopes;
- bootstrap tests assert the two DELRV-1 tools are declared while `provides_commands: []` remains unchanged.

These tests do not claim live daemon readiness, plugin-load readiness, slash commands, Discord/gateway delivery, or plugin-owned lifecycle/idempotency state.

## CNDIS-1 council and delivery-evidence coverage

CNDIS-1 remains fake/injected-only by default:

- unit tests cover `kan_council_command` and `kan_delivery_evidence` schemas, exact closed council and delivery-evidence enums, feature probes before submit, missing-feature compatibility failures before submit, caller-supplied `request_id`/`idempotency_key`, deterministic `session_id` payload normalization, command-specific payload validation before transport, duplicate idempotency pass-through without local dedupe, structured daemon error preservation, malformed response protocol failures, and missing-client `unavailable` behavior;
- integration tests use a fake Hermes context plus `StaticDaemonTransport` to invoke both handlers and assert exact `version.read` then `command.submit` sequencing;
- `tests/integration/test_cndis_conformance.py` consumes the sibling control conformance manifest and all COUNC-001 council request/response fixtures plus both delivery-evidence fixtures read-only, with fake transport only;
- bootstrap and core-contract tests assert the two CNDIS tools are declared while `provides_hooks: []` and `provides_commands: []` remain unchanged and the control manifest includes `delivery_evidence` and `council.lifecycle`.

These tests do not claim live daemon readiness, plugin-load readiness, slash commands, live/default Discord helper/send_message readiness, gateway delivery, or plugin-owned council/delivery-evidence state.

## CNDIS-2 injected Discord helper coverage

CNDIS-2 remains fake/injected-only by default:

- unit tests cover `discord_surface.py` target/result validation, missing sender failures,
  missing or non-dedicated target failures, current/active target rejection, live opt-in
  label/cleanup requirements, fake sender exactly-once behavior, and inert E2E config
  parsing from a supplied mapping;
- unit tool-handler tests cover `kan_discord_send_message` schema/handler fail-closed
  behavior, missing target validation before sender, active-target rejection before
  sender, and fake sender success envelopes;
- integration tests use a fake Hermes context and injected sender to invoke
  `kan_discord_send_message`, while separately proving the registered helper does not add
  hooks or slash commands;
- E2E tests run with `KAN_DISCORD_E2E=0` by default, set live-looking Discord/Hermes
  environment names, and still prove no live post occurs without an injected sender.

The opt-in E2E parser accepts a target only when `KAN_DISCORD_E2E=1`,
`DISCORD_TEST_TARGET` names a dedicated test target, `DISCORD_TEST_DEDICATED=1`, and
cleanup guidance is present. The accepted path asserts the visible label and cleanup
guidance but still does not perform a live send by default.

## DELRV-2 delegation/review conformance coverage

DELRV-2 adds fake-daemon coverage against the sibling control DELEG-002
fixture matrix:

- success cases load the control-owned `delegate.new`, `delegate.submit`,
  `delegate.review`, `delegate.review_submit`, and `delegate.accept` fixtures
  read-only and submit them through `StaticDaemonTransport` as `command.submit`
  envelopes;
- duplicate/idempotency coverage sends the duplicate `delegate.submit` action
  again and asserts daemon-returned command/event/request identity is preserved;
- permission/validation coverage consumes the DELEG-002 unauthorized actor,
  wrong review phase, and invalid verdict structured-error fixtures;
- retryable and malformed-response cases stay plugin-local because DELEG-002
  publishes no public retryable fixture or valid malformed-payload manifest
  entry.

These tests remain fake/injected-only. They do not start or discover a daemon,
call a CLI, open localhost/socket transport, contact Hermes, Discord, KAB,
gateway, auth, or token surfaces, add slash commands, or change
`provides_commands: []`.
