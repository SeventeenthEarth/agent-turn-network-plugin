# Compatibility And Operations

---

## Merged from `docs/spec/compatibility-and-operations.md`

# Control Compatibility

## Goal

Let `atn-plugin` develop independently from the Go control runtime while proving compatibility with the control daemon contract.

The control-side SOT is public-facing as `atn-control` and currently resolved through the local compatibility path `../../agent-turn-network-control/docs/spec/cross-repo-contract.md`. For live-local transport work, the control-side companion SOT is `../../agent-turn-network-control/docs/spec/live-transport-control-sot.md` and the plugin-side SOT is `docs/spec/live-transport-sot.md`. `plugin/LTRAN-001` is completed as docs-only SOT/mapping work; it does not implement live transport or claim live/production/Discord/gateway/auth/token/KAB/hidden CLI fallback readiness. `plugin/LTRAN-002` is completed as the first bounded implementation task for explicit Unix-socket `status.read` / `version.read` live smoke only.

## Current supported control contract

| Field | Value |
| --- | --- |
| Control repo | `atn-control` public label; `../../agent-turn-network-control` current local compatibility path |
| Protocol version | `atn-protocol-v1alpha0` |
| Fixture manifest | `../../agent-turn-network-control/testdata/conformance/manifest.json` |
| Stability | draft, docs/scaffold/client-foundation plus fake/injected HPLUG-2 read-only status/diagnostics/stream-tail tools, DELRV command tools, CNDIS council/delivery-evidence tools, ARGUE static argument-graph schema/tool contract coverage, HPLUG-3 unsupported slash-command documentation, SKILL-2 compatibility matrix, and local isolated plugin-load smoke |
| Plugin behavior on mismatch | fail closed; no live fallback; affected tool returns `ok:false` |

## Compatibility checks

The plugin must check:

- daemon reachable;
- daemon protocol version supported;
- required daemon feature flags present;
- command envelope schema supported;
- stream frame schema supported;
- structured error schema supported;
- `delivery_evidence` and `council.lifecycle` feature groups supported before CNDIS command submits are marked compatible;
- `control/ARGUE-002` static argument-graph command, event, and error fixtures exist before ARGUE schema/tool contract coverage is marked compatible;
- delivery evidence command path supported before Discord helper posts are marked complete.

## Parallel development modes

### Fake daemon mode

Default for unit and integration tests before the control daemon exists. Fake daemon responses are derived from the control conformance manifest and fixtures.

### Fixture mode

The Python client parses control fixtures without starting the real daemon. This is required for P1 and later.

### Explicit live local daemon mode

`LTRAN` live-local plugin work uses a locally built control daemon with disposable data home only when a plugin task explicitly configures live transport. Repo-qualified dependency evidence is recorded from control `docs/spec/live-transport-control-sot.md` and control `docs/roadmap.md`: `control/LTRAN-001`, `control/LTRAN-002`, and `control/LTRAN-003` are completed. `plugin/LTRAN-002` used that handoff evidence to implement the explicit `live_transport.unix_socket_path` status/version smoke slice, and `plugin/LTRAN-003` now proves bounded explicit Unix-socket `stream.tail`/`command.submit` equivalence against a disposable daemon with durable evidence at `docs/evidence/ltran-003-plugin-equivalence-evidence.json`. This is still not production activation, daemon discovery, live/default Discord, gateway/auth/token mutation, KAB readiness, long-lived member runtime readiness, broad command coverage, or a hidden CLI fallback.

### Isolated Hermes/Discord mode

Uses disposable Hermes home/profile and dedicated Discord test target. It must never default to the current running Hermes gateway or active Discord thread.

## Plugin milestone matrix

Historical pre-live plugin milestones keep their original `P0`/`P1` labels and completed task references for traceability. New post-Release live-local epics use five-letter uppercase epic IDs and three-digit task IDs. In cross-repo evidence, use repo-qualified references such as `control/LTRAN-001` and `plugin/LTRAN-001`.

| Plugin milestone | Control task gate checked | Allowed before control implementation | Release-ready requires |
| --- | --- | --- | --- |
| P0 Scaffold | BOOTS-001 plus control cross-repo docs and manifest exist | yes | root/docs/Makefile guardrails pass |
| P1 Python daemon client | DAEMN-002 version/features, command envelope, stream/error fixtures | yes, fake daemon | conformance tests against fixture manifest |
| P2 Hermes status/diagnostic tools | DAEMN-002 daemon status/session/stream fixtures | yes, fake daemon | implemented control status/stream contract |
| P3 Delegation/review tools | DELEG-001 delegation/review command fixtures | yes, fake/injected only | implemented control commands, fake-daemon coverage, review gates, and final evidence; no live-local/plugin-load readiness claim |
| P4 Council/Discord surface | COUNC-001 council fixtures plus DAEMN-002 delivery evidence fixtures | yes, fake/injected CNDIS tool-ready | isolated E2E target, Discord helper contract, and installed-plugin evidence before live Discord readiness |
| P5 Skill/distribution | TRANS-001/RELIA-001 implemented command matrix and release evidence | docs-only draft | compatibility matrix and local isolated plugin-load smoke |
| LTRAN Live daemon transport | control `LTRAN` complete | no; block until control `LTRAN` evidence exists | explicit configured live daemon transport and plugin/CLI/daemon equivalence evidence |
| PARTC Participant client path | control `MEMBR` complete | no; block until real participant invocation evidence exists | participant stream/write path and selected response proof through plugin/protocol client |
| SURFD Surface delivery | control `SURFD` complete | no; block until rendering/evidence contract exists | visible helper/rendering boundary with daemon event data and evidence pointers |

## SKILL-2 compatibility matrix

SKILL-2 records completed control `TRANS-001` and `RELIA-001` gates as unblock
evidence for this plugin matrix. The plugin does not reuse control `.kkachi/`
artifacts as plugin evidence; plugin evidence is the repository-local docs,
tests, and `make check-plugin-load-smoke` local isolated plugin-load smoke gate.

| Surface or feature | Control / Hermes status | Plugin support | Evidence source | Unsupported or degraded behavior |
| --- | --- | --- | --- | --- |
| Protocol `atn-protocol-v1alpha0` | Control conformance manifest declares the protocol | Supported for fake/injected client compatibility checks | `make check-core-contract`, `docs/spec/compatibility-and-operations.md`, `src/atn_plugin/protocol.py` | Any other protocol fails closed before compatibility is claimed. |
| `version.read` | Control-supported compatibility probe | Used by stream, council, and delivery-evidence feature gates through injected clients | `tests/unit/test_status_version_client.py`, `tests/unit/test_tool_handlers.py`, `tests/integration/test_cndis_conformance.py` | `session.status.read` is not implemented or exposed. |
| Command/event envelope and structured error | Control-supported command envelope and daemon error contract | Supported through `atn_delegate_new`, `atn_delegate_action`, `atn_council_command`, and `atn_delivery_evidence` with caller-supplied request/idempotency IDs | `tests/unit/test_command_envelope.py`, `tests/unit/test_daemon_error_decoding.py`, `tests/integration/test_delegate_plugin_tools.py` | Unknown commands, malformed envelopes, missing IDs, or daemon structured failures return JSON `ok:false`; no local lifecycle or retry state is added. |
| Stream features | Control feature group `stream_frame` gates retained stream reads | `atn_stream_tail` supported only with positive injected `version.read` compatibility | `tests/unit/test_stream_frame_parsing.py`, `tests/integration/test_fake_daemon_stream_diagnostics.py` | Missing `stream_frame`, malformed frames, live sockets, SSE, WebSocket, CLI, or daemon discovery fail closed / remain unsupported. |
| Delegation/review fixtures | Control DELEG fixtures cover implemented `delegate.*` commands | `atn_delegate_new` and `atn_delegate_action` expose the closed implemented command set | `tests/integration/test_deleg_002_conformance.py`, `tests/unit/test_tool_handlers.py` | `delegate.request`, top-level `review`, generated IDs, plugin-owned dedupe, and live daemon fallback are unsupported. |
| Council lifecycle | Control `council.lifecycle` feature and COUNC fixtures exist | `atn_council_command` supports exact implemented `council.*` lifecycle commands through injected clients | `tests/integration/test_cndis_conformance.py`, `tests/unit/test_tool_handlers.py` | Missing feature probe or unsupported command returns `ok:false`; plugin owns no council state. |
| Council argument graph static contract | Control `ARGUE-002` static fixtures exist for argument-graph speech, hand-raise target links, legacy dual-field preservation, and invalid ARGUE examples | `atn_council_command` and explicit selected-response ARGUE pass-through preserve and locally validate deterministic `claims[]`, `stance_links[]`, `contribution_type`, `new_axis_reason`, `evidence[]`, and `hand_raise.target_links[]` shapes before transport where safe | `tests/unit/test_argue_tool_contract.py`, `tests/unit/test_selected_participant_response.py`, `tests/integration/test_cndis_conformance.py`, `make check-core-contract` | This is static/fake/injected contract coverage only; runtime validation/scoring, participant response generation, visible relation rendering, live Discord, daemon discovery, profile/gateway/auth/token/provider mutation, KAB readiness, and live pilot readiness remain unsupported. |
| Delivery evidence | Control `delivery_evidence` feature and command path exist | `atn_delivery_evidence` supports exact delivery-evidence commands through injected clients | `tests/integration/test_cndis_conformance.py`, `tests/unit/test_tool_handlers.py` | Discord IDs are evidence pointers only; plugin owns no delivery transitions and does not default-send Discord messages. |
| Discussion activation planner/doctor | RUNFIX requires explicit install-vs-activation planning before any apply/live-local pilot | `atn_discussion_activation_plan` builds a pure/local dry-run report from caller-provided evidence, classifies eligible/excluded/blocked profiles from explicit effective Discord evidence, excludes bot-to-bot-enabled profiles by default, emits eligible-only `allow_list_targets`, profile remediation, parent-channel proof state, fallback audit, keeps RUNFIX labels separate, and always returns `live_readiness: false` | `tests/unit/test_discussion_activation_planner.py`, `tests/unit/test_tool_handlers.py`, `tests/unit/test_tool_schemas.py` | No daemon startup, socket discovery, current Hermes/Discord/profile/gateway inspection, CLI fallback, Discord send/channel creation, profile/gateway/provider/auth/token/model mutation, live readiness, or activation apply. |
| `transcript.render` | Control-supported capability | Not exposed as a plugin tool in SKILL-2 | Control `TRANS-001` completion is recorded as unblock evidence only | No `atn_transcript_render` tool, command, hook, or live fallback is added. |
| `export.bundle` | Control-supported capability | Not exposed as a plugin tool in SKILL-2 | Control `TRANS-001`/`RELIA-001` completion is recorded as unblock evidence only | No `atn_export_bundle` tool, command, hook, or live fallback is added. |
| Packaged skill resource | Public ATN bundled skill names are `atn-plugin`, `atn-moderator`, and `atn-participant`; current checked-in package resources remain under `bundled_skills/atn-plugin/SKILL.md`, `bundled_skills/atn-moderator/SKILL.md`, and `bundled_skills/atn-participant/SKILL.md` until ATN-005 | Supported for import-safe package resource reads | `tests/unit/test_bundled_skills.py`, `make check-plugin-load-smoke` | The package does not install into the user's Hermes profile. |
| Local isolated plugin-load smoke | Hermes-compatible root `register(ctx)` entrypoint can be loaded with a fake context | Supported only as local isolated plugin-load smoke | `scripts/check_plugin_load_smoke.py`, `tests/unit/test_plugin_load_smoke.py`, `make check-plugin-load-smoke` | This is not production activation, live plugin readiness, KAB readiness, live Hermes readiness, or live Discord readiness. |
| Live-local daemon transport | `plugin/LTRAN-001` docs-only mapping complete; `control/LTRAN-001`, `control/LTRAN-002`, and `control/LTRAN-003` completed as dependency evidence | `plugin/LTRAN-002` supports explicit `live_transport.unix_socket_path` Unix-socket transport for `status.read` and `version.read` smoke only | `tests/unit/test_live_transport_config.py`, `tests/integration/test_live_unix_socket_transport.py`, `docs/spec/live-transport-sot.md` | No-config, unsafe paths, localhost/TCP, CLI fallback, daemon discovery, Hermes gateway, auth/token, KAB, provider/profile mutation, stream/write support, equivalence proof, dedupe proof, hidden fallback, and production activation remain unsupported. |
| `atn_session_status` | No authoritative `session.status.read` plugin contract | Unsupported | Guardrails, schema tests, docs | Do not add `atn_session_status` or `session.status.read` support. |
| ATN slash commands | Hermes host can register commands, but plugin has no approved ATN command contract | Unsupported; `provides_commands: []` stays unchanged | `plugin.yaml`, bootstrap smoke, plugin-load smoke, docs guardrails | Any `provides_commands: [kan]` historical alias or `register_command` drift fails local smoke. |
| Native Discord slash commands | No supported plugin/native Discord slash-command contract | Unsupported | `docs/spec/architecture.md`, `docs/spec/compatibility-and-operations.md` | No native Discord command registration or gateway fallback. |
| Live daemon discovery | No approved live/default daemon discovery path | Unsupported by default | E2E no-live-fallback tests, docs guardrails | No localhost, socket, provider, or CLI fallback. |
| Live/default Discord send | Sender must be explicitly injected and target must be dedicated test metadata | Unsupported by default | `tests/unit/test_discord_surface.py`, `tests/e2e/test_discord_surface_no_live.py` | Live-looking env vars do not create a sender or target. |
| KAB bridge | Out of scope for this direct Codex app-server lane | Unsupported | SKILL-2 task boundary and docs guardrails | No KAB bridge implementation or readiness claim. |
| Production Hermes activation | No production/live activation evidence in SKILL-2 | Unsupported | Operator guide and smoke boundary | Local isolated plugin-load smoke is the maximum claim. |

## Cross-repo check command

```bash
make check-core-contract
```

This command checks that the sibling control repo exposes the expected docs, manifest, protocol version, and reciprocal `check-plugin-contract` target.

## Fail-closed rule

Plugin compatibility checks are safety gates. If the daemon reports an unsupported protocol version, missing required feature, malformed structured error, or missing delivery evidence/council lifecycle command path, the plugin must not expose the affected write operation as safe. DAEMN-1 stops at an operator-friendly failure; it does not call a live daemon or CLI fallback.

## DAEMN-1 manifest guard

The client foundation parses both the plugin-local draft manifest and the control conformance manifest. `fixtures: []` is valid only when `stability` is explicitly draft/scaffold-like. Empty fixtures always force `live_readiness: false`, even if a malformed manifest tries to claim otherwise. Unsupported protocol versions, missing required feature groups, malformed fixture lists, or non-boolean live-readiness values fail closed before any future live operation can be considered safe.

DAEMN-1 does not contact a live daemon. Status/version reads and command submission require an explicit fake or injected transport. No localhost, CLI, Hermes, Discord, KAB, auth, token, or gateway fallback is implemented.

## DAEMN-2 stream and diagnostics guard

DAEMN-2 adds fake/fixture-only stream tail parsing and diagnostics decoding. Stream tail reads are gated by a `version.read` compatibility probe that must report `stream_frame` in `feature_groups` before `stream.tail` is attempted. Missing `stream_frame`, unsupported protocol versions, malformed frames, malformed diagnostics payloads, unsupported frame/event schema versions, and oversized frame/check arrays fail closed.

This does not change live readiness. Control conformance fixtures are still draft/manifest-only, and live stream transport remains blocked/deferred until stable control stream/status fixtures and endpoint declarations exist.

## HPLUG-2 tool compatibility guard

HPLUG-2 exposes `atn_daemon_status`, `atn_compatibility_diagnostics`, and `atn_stream_tail` only through explicit fake/injected client factories. Missing factories, unsupported protocol versions, missing feature groups, malformed status/diagnostics/stream payloads, and sensitive diagnostics/stream payloads all fail closed or redact before returning JSON to Hermes.

`atn_stream_tail` inherits DAEMN-2 stream safety: it must receive positive `stream_frame` compatibility from `version.read` before `stream.tail` is attempted. `atn_session_status` is not exposed because no authoritative control fixture/protocol operation exists for `session.status.read`; this avoids plugin-owned state authority or schema-only overclaiming.

## DELRV-1 command-envelope compatibility guard

DELRV-1 exposes `atn_delegate_new` and `atn_delegate_action` only through explicit fake/injected client factories and the existing `command.submit` operation. `atn_delegate_new` always submits `delegate.new`. `atn_delegate_action` accepts only the exact implemented `delegate.*` action/review/delivery enum and rejects `delegate.request`, top-level `review`, and any unknown command before transport.

The plugin requires caller-supplied non-empty `request_id` and `idempotency_key`, does not generate hidden identifiers, does not cache/dedupe locally, and owns no delegation/review lifecycle state. The daemon remains authoritative for domain validation, idempotency semantics, duplicate handling, state transitions, and structured errors. Local validation maps to `validation`; missing injected clients map to `unavailable`; malformed daemon responses map to `protocol`; structured daemon failures such as `conflict` are preserved.

This is fake/injected compatibility only and does not change live readiness, installed plugin-load readiness, slash-command readiness, Discord/gateway readiness, or auth/token boundaries.

## CNDIS-1 council and delivery-evidence compatibility guard

CNDIS-1 exposes `atn_council_command` and `atn_delivery_evidence` only through explicit fake/injected client factories and the existing `command.submit` operation. `atn_council_command` accepts only the implemented `council.*` enum from COUNC-001. `atn_delivery_evidence` accepts only `delegate.escalation_delivered` and `delegate.escalation_delivery_failed`.

Before submit, `atn_council_command` requires injected `version.read` to report `council.lifecycle`; `atn_delivery_evidence` requires `delivery_evidence`. Missing feature groups fail closed with `compatibility` before `command.submit`.

The plugin requires caller-supplied non-empty `request_id` and `idempotency_key`, does not generate hidden identifiers, does not cache/dedupe locally, and owns no logs, locks, cursors, council lifecycle/consensus state, or delivery-evidence transitions. The daemon remains authoritative for domain validation, idempotency semantics, duplicate handling, state transitions, and structured errors.

CNDIS conformance coverage consumes the sibling control repo's COUNC-001 council fixtures and delivery-evidence fixtures read-only from `testdata/conformance`; it asserts the exact `version.read` then `command.submit` operation sequence through `StaticDaemonTransport`. This is fake/injected compatibility only and does not change live readiness, installed plugin-load readiness, slash-command readiness, Discord helper/gateway readiness, KAB readiness, or auth/token boundaries.

## ARGUE-001 argument-graph static contract guard

ARGUE-001 consumes the sibling control repo's `control/ARGUE-002` static fixtures
read-only from `testdata/conformance`. The plugin accepts and preserves
ARGUE-capable `council.speak` and `council.hand_raise` payload fields:
`claims[]`, `stance_links[]`, `contribution_type`, `new_axis_reason`,
`evidence[]`, and `hand_raise.payload.target_links[]`.

Local validation is intentionally deterministic and shape-only: claim ids and
summaries must be non-empty, claim ids must be unique within a speech, claim
kind / stance / contribution enums must match the SOT, `new_axis` requires
`new_axis_reason`, and `synthesize` requires at least two `stance_links` before
transport. Legacy `responds_to_event_id` is accepted only as a display hint; it
does not rewrite, infer, or override `stance_links[]`.

This guard does not implement `control/ARGUE-003` runtime validation/scoring,
`plugin/ARGUE-002` participant response generation or runtime-noise handling,
`plugin/ARGUE-003` visible relation rendering, live daemon discovery, hidden CLI
fallback, Hermes/Discord state inference, profile/gateway/auth/token/provider
mutation, KAB readiness, production activation, or live pilot readiness.

## ARGUE-002 selected participant response guard

ARGUE-002 extends `atn_selected_participant_response` with local deterministic
pre-transport validation for selected participant speech. The handler preserves
caller-supplied IDs, selected participant provenance checks, ARGUE speech fields,
and the existing `council.speak` submit-before-selected-cursor-ack sequence.

Runtime/system noise is rejected before transport when visible speech begins
with conservative wrapper/log markers such as `WARNING:`, traceback headers,
runtime warning prefixes, max-iteration notices, or tool/runner diagnostics.
Normal participant disagreement that merely discusses a warning is not rejected.

Optional `caller_validation_context` is caller-provided and non-authoritative.
It may check selected member/event/cursor consistency, prior claim references,
and quality-required orphan speech only when the caller marks local context as
sufficient. When the context is absent or ambiguous, the plugin does not infer
state from Discord/Hermes order or plugin memory; daemon validation/scoring
remains authoritative.

This guard does not implement `plugin/ARGUE-003` visible relation rendering,
`control/ARGUE-004/005`, live control compatibility, live daemon discovery,
hidden CLI fallback, Discord/Hermes state inference, profile/gateway/auth/token
provider mutation, KAB readiness, production activation, or live pilot readiness.

## DELRV-2 DELEG-002 conformance guard

DELRV-2 consumes the sibling control repo's DELEG-002 conformance fixture matrix
read-only from `testdata/conformance`. The plugin-side tests adapt valid
control command fixtures into fake `command.submit` transport responses to
verify plugin pass-through behavior. The control repo remains authoritative for
command semantics, permission rules, validation messages, and structured-error
shapes.

The covered success matrix is `delegate.new`, `delegate.submit`,
`delegate.review`, `delegate.review_submit`, and `delegate.accept`. Duplicate
coverage sends the duplicate submit through the fake transport again and asserts
the plugin preserves the daemon-returned command/event/request identity instead
of serving a local cache. Error coverage consumes the DELEG-002 unauthorized
actor, wrong review phase, and invalid verdict fixtures.

Retryability and malformed fake-daemon responses remain plugin-local negative
inputs unless a future control task publishes corresponding valid fixtures.
Malformed success/error envelopes still map to `protocol`. This guard does not
add live daemon discovery, localhost/socket transport, CLI fallback, Hermes,
Discord, KAB, gateway, auth, token behavior, slash commands, installed
plugin-load readiness, or any change to `provides_commands: []`.

## HPLUG-3 slash-command compatibility guard

Hermes host slash-command support exists through `PluginContext.register_command`, but ATN plugin slash commands are not compatible-ready. Control ATN must first provide daemon command authority, protocol fixtures, idempotency/error semantics, and delivery-evidence rules for the specific operation. Until then, `provides_commands: []` is the correct manifest state and no slash-command handler should be registered. See `docs/spec/compatibility-and-operations.md` for the operator-facing unsupported-surface matrix and future binding checklist.

## SKILL-2 local isolated plugin-load guard

SKILL-2 adds `make check-plugin-load-smoke` as a bounded local isolated
plugin-load smoke gate. The gate creates a temporary plugin home from
repository-local files, loads the root `__init__.py::register(ctx)` entrypoint
with a fake Hermes context, asserts the exact manifest-declared tool registrations
in manifest order, asserts no hooks and no commands, checks handler callability,
and calls representative handlers without injected clients/senders to require
JSON-string `ok:false` fail-closed responses. It also checks that live-looking
environment variables do not change local behavior, rejects a fake
`provides_commands: [kan]` manifest, rejects a command-registering entrypoint,
and verifies wheel package inclusion plus bundled skill compatibility.

This smoke gate does not read or mutate a live Hermes profile, contact
atn-controld, open sockets, use localhost, call a CLI, discover
providers, use auth/token/gateway material, contact Discord, call KAB, prove
production activation, or prove live plugin readiness. The smoke claim is only
local isolated plugin-load smoke.

---

## Merged legacy testing/tooling content

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

`make check-bootstrap-smoke` verifies fake/injected plugin bootstrap readiness: package import/metadata through the `src/` layout, plugin manifest shape with exactly `atn_daemon_status`, `atn_compatibility_diagnostics`, `atn_stream_tail`, `atn_stream_ack`, `atn_delegate_new`, `atn_delegate_action`, `atn_council_command`, `atn_selected_participant_response`, `atn_delivery_evidence`, `atn_surface_render_projection`, `atn_discussion_activation_plan`, and `atn_discord_send_message`, explicit empty hook/command declarations, and root entrypoint registration of callable JSON-string handlers without hooks or slash commands.

`make check-plugin-load-smoke` verifies local isolated plugin-load smoke only. It copies repository-local plugin files into a temporary plugin home, loads the root `register(ctx)` entrypoint with a fake Hermes context, asserts the exact manifest-declared ATN tools in order, asserts current checked-in package metadata and bundled skill names, asserts no hooks, commands, or resources, calls representative handlers without injected clients/senders and requires JSON `ok:false`, verifies live-looking environment variables do not change behavior, rejects command-registering entrypoints or `provides_commands: [kan]`, and checks wheel package inclusion plus bundled skill compatibility. It does not read a live Hermes profile, contact a daemon, open sockets, call KAB, contact Discord/gateway/auth/token/provider resources, or prove production activation.

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

- unit tests cover exact tool schema names, manifest declarations, root entrypoint registration, JSON-string handler success envelopes, fail-closed handler errors, diagnostics/stream redaction, stream-tail argument validation, and deferred absence of `atn_session_status`;
- integration tests use a fake Hermes context and `StaticDaemonTransport` to invoke `atn_daemon_status`, `atn_compatibility_diagnostics`, and `atn_stream_tail`, asserting the exact `status.read` / `diagnostics.read` / `version.read` + `stream.tail` operation sequence;
- E2E smoke tests run only with isolated `KAN_E2E=1` defaults and prove live-looking daemon/stream/Discord/token environment variables do not create live fallback behavior.

These tests do not claim installed-plugin loading, live daemon readiness, session-status support, slash commands, write tools, or Discord helper readiness.

## DELRV-1 delegation/review command-envelope coverage

DELRV-1 remains fake/injected-only by default:

- unit tests cover `atn_delegate_new` and `atn_delegate_action` schemas, exact closed `delegate.*` enum membership, absence of `delegate.request` and top-level `review`, caller-supplied `request_id`/`idempotency_key`, deterministic action `session_id` payload normalization, JSON-string success envelopes, validation failures before transport, structured daemon `conflict` preservation, malformed response protocol failures, and missing-client `unavailable` failures;
- integration tests use a fake Hermes context and `StaticDaemonTransport` to invoke the delegation handlers and assert exact `command.submit` envelopes;
- bootstrap tests assert the two DELRV-1 tools are declared while `provides_commands: []` remains unchanged.

These tests do not claim live daemon readiness, plugin-load readiness, slash commands, Discord/gateway delivery, or plugin-owned lifecycle/idempotency state.

## CNDIS-1 council and delivery-evidence coverage

CNDIS-1 remains fake/injected-only by default:

- unit tests cover `atn_council_command` and `atn_delivery_evidence` schemas, exact closed council and delivery-evidence enums, feature probes before submit, missing-feature compatibility failures before submit, caller-supplied `request_id`/`idempotency_key`, deterministic `session_id` payload normalization, command-specific payload validation before transport, turn-bearing lifecycle `payload.turn` preservation with fail-closed legacy `payload.round` rejection, duplicate idempotency pass-through without local dedupe, structured daemon error preservation, malformed response protocol failures, and missing-client `unavailable` behavior;
- integration tests use a fake Hermes context plus `StaticDaemonTransport` to invoke both handlers and assert exact `version.read` then `command.submit` sequencing plus full council fixture payload preservation;
- `tests/integration/test_cndis_conformance.py` consumes the sibling control conformance manifest and all COUNC-001 council request/response fixtures plus both delivery-evidence fixtures read-only, with fake transport only, and asserts turn-bearing golden envelopes carry `payload.turn` without emitting `payload.round`;
- bootstrap and core-contract tests assert the two CNDIS tools are declared while `provides_hooks: []` and `provides_commands: []` remain unchanged and the control manifest includes `delivery_evidence` and `council.lifecycle`.

These tests do not claim live daemon readiness, plugin-load readiness, slash commands, live/default Discord helper/send_message readiness, gateway delivery, or plugin-owned council/delivery-evidence state.

## CNDIS-2 injected Discord helper coverage

CNDIS-2 remains fake/injected-only by default:

- unit tests cover `discord_surface.py` target/result validation, missing sender failures,
  missing or non-dedicated target failures, current/active target rejection, live opt-in
  label/cleanup requirements, fake sender exactly-once behavior, and inert E2E config
  parsing from a supplied mapping;
- unit tool-handler tests cover `atn_discord_send_message` schema/handler fail-closed
  behavior, missing target validation before sender, active-target rejection before
  sender, and fake sender success envelopes;
- integration tests use a fake Hermes context and injected sender to invoke
  `atn_discord_send_message`, while separately proving the registered helper does not add
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

---

## Merged legacy testing/tooling content

# Tooling

## Baseline decisions

| Item | Decision |
| --- | --- |
| Language | Python |
| Minimum Python | `>=3.11` to match Hermes Python 3.11 runtime compatibility |
| Package manager | `uv` preferred for development |
| Build backend | `hatchling` or current Hermes-compatible Python packaging |
| Source layout | `src/atn_plugin/` |
| Test runner | `pytest` |
| Async tests | `pytest-asyncio` when stream/client async is introduced |
| Lint/format | `ruff check`, `ruff format` |
| Type checker | `mypy` |
| Operator entrypoint | `Makefile` |

## Target layout

```text
atn-plugin/
  pyproject.toml
  plugin.yaml
  src/atn_plugin/
  tests/unit/
  tests/integration/
  tests/e2e/
  docs/
  Makefile
```

## KAS / KAH workflow hygiene

Historical KAS workflow guidance for this plugin lane is maintained in the installed Hermes profile KAS reference, not in a project-local `skills/` directory:

```text
/Users/draccoon/.hermes/profiles/hwangchung/skills/kkachi-orchestrate/references/atn-plugin-readiness-and-activation.md
```

Before a KAH/KAS task starts, refresh CodeGraph with `codegraph index <repo>` when `.codegraph/` exists. If the repository has source but no `.codegraph/`, run `codegraph init -i <repo>`. For a completely empty bootstrap project, record a deferred CodeGraph reason in `codegraph-evidence.md`, then run `codegraph init -i <repo>` after source files exist and before final verification.

The project `.gitignore` must include `.kkachi/`, `.codegraph/`, `.omx/`, `.omc/`, and `.claude-octopus/` so local KAH, CodeGraph, and review-tool state stays out of source control. The `.kkachi-workflow.yaml` graph may opt into KAH checks with `codegraph.evidence` and `gitignore.contains_all` gates.

## Makefile targets

`make test-prepare` runs formatting, lint, type checking, docs guardrails, the Makefile target-contract check, the bootstrap smoke check, and the local isolated plugin-load smoke check.

`make check-make-contract` verifies required single-line target declarations, `.PHONY` coverage, `make test` dependencies, preparation-gate dependencies, scoped tool commands, offline integration defaults, and isolated E2E environment variables.

`make check-bootstrap-smoke` verifies the package import/metadata, fake/injected plugin manifest shape, exact tool registrations, callable handler presence, and root directory-plugin entrypoint availability without registering hooks or ATN slash commands.

`make check-plugin-load-smoke` verifies local isolated plugin-load smoke. It creates a temporary plugin home from repository-local files, loads the root entrypoint through a fake Hermes registration context without externally adding `<plugin>/src` to `PYTHONPATH`, checks exact public ATN tool order, current checked-in package metadata/resource ids, zero hooks, zero commands, zero registered resources, handler JSON-string fail-closed behavior without injected clients/senders, live-looking environment inertness, negative command-overclaim fixtures, wheel package inclusion, Python 3.11 syntax compatibility, and bundled skill compatibility. It does not inspect or mutate the user's Hermes profile and does not contact daemon, Discord, KAB, gateway, auth, token, provider, localhost, socket, CLI, or network resources.

`make test-unit` runs `pytest tests/unit`.

`make test-int` runs `pytest tests/integration` with fake daemon/Hermes/Discord components and `KAN_EXTERNAL=0`.

`make test-e2e` runs `pytest tests/e2e` with `KAN_E2E=1`, `KAN_DISCORD_E2E=0`, an isolated `HERMES_HOME`, and an empty `DISCORD_TEST_TARGET` by default. It must not touch the current running Hermes or Discord environment.

`make test` depends on `test-prepare`, `test-unit`, `test-int`, and `test-e2e`; the preparation gate must complete before the test tiers under normal serial `make`.

After the Python scaffold exists, `uv` and `pyproject.toml` are required for code/test targets. Missing prerequisites fail with explicit messages instead of silently passing. Default integration and E2E targets still avoid live Hermes, Discord, daemon, and network resources.

## Guardrail scripts

`make docs-guardrails` runs `scripts/guardrails.py`. The script is import-safe for unit testing, verifies the required docs set and required project phrases, scans all `docs/*.md` files for stale docs-relative sibling paths, and scans public/package surfaces for stale legacy package, tool, skill, manifest, command, compatibility, and unsupported live/private-config claims. Historical/provenance/safety-boundary exceptions must be path-, token-, and line-specific with a recorded reason. It does not duplicate Makefile target structure checks; `make check-make-contract` owns Makefile structure.

`make check-core-contract` runs `scripts/check_core_contract.py`. The script is import-safe for unit testing and verifies the local companion control repo, `ATN_CONTROL_REPO`, exposes the expected conformance manifest protocol, cross-repo development phrases, distribution fixture handoff wording, reciprocal `check-plugin-contract` Makefile target, and matching plugin compatibility declaration.

## Bundled skill resources

SKILL-1 originally packaged the `atn-plugin` operator skill. The bundled source now lives under `src/atn_plugin/bundled_skills/` with
`atn_plugin.bundled_skills.read_bundled_skill_text(...)` as
the import-safe reader used by tests and installer checks. SKILL-2 verifies
those resources in the local isolated plugin-load smoke gate.

The helper reads package resources only. It does not install into a Hermes
profile, discover current-session state, contact live Hermes/Discord/daemon
resources, mutate the sibling control repo, or alter `plugin.yaml`. Operator
install, enable, rollback, troubleshooting, no-live defaults, and the SKILL-2
local isolated plugin-load smoke boundary are documented in `docs/spec/skill-and-operator-guide.md`.

## Bootstrap smoke tests

SCAFF-5 delivers a scaffold smoke gate for the first plugin scaffold PR. It proves:

- the plugin package imports through the `src/` layout and exposes stable metadata;
- the plugin manifest is a YAML mapping with the expected name, version, standalone kind, exact `provides_tools: [atn_daemon_status, atn_compatibility_diagnostics, atn_stream_tail, atn_stream_ack, atn_delegate_new, atn_delegate_action, atn_council_command, atn_selected_participant_response, atn_delivery_evidence, atn_surface_render_projection, atn_discussion_activation_plan, atn_discord_send_message]`, and explicit empty `provides_hooks: []` / `provides_commands: []` declarations;
- the root directory-plugin entrypoint exposes `register(ctx)`;
- the entrypoint registers callable fake/injected JSON-string handlers and does not register hooks or ATN slash commands;
- `make test` succeeds without live Hermes, Discord, daemon, or network resources.

DAEMN-1 added fake daemon compatibility probes for the client foundation only. At that stage, full plugin-bootstrap checks that required real declared tool handlers and handler JSON-string return contracts were deferred. HPLUG-2 now enables those checks for the three read-only JSON-string handlers.

SCAFF-5 introduced smoke coverage in `scripts/check_bootstrap_smoke.py` and `tests/unit/test_bootstrap_smoke.py`; HPLUG-2 updated it for the three read-only tool registrations, DELRV-1 extended it for the two delegation/review command-envelope tools, CNDIS-1 extended it for the council and delivery-evidence command tools, and CNDIS-2 extends it for the injected-only Discord helper while keeping the explicit empty slash-command surface. This proves manifest/entrypoint/handler-contract readiness only.

SKILL-2 adds `scripts/check_plugin_load_smoke.py` and `tests/unit/test_plugin_load_smoke.py` as a bounded local isolated plugin-load smoke gate. REL-PILOT-FIX-001 strengthened it so the repository plugin surface must be discovered and loaded in a temporary fake Hermes context without test-side `PYTHONPATH` help; the root entrypoint owns adding its bundled `src/` path before importing runtime modules. ATN-005 further locks the isolated surface to the checked-in ATN manifest/package/tool/skill names, zero hooks, zero commands, and zero registered resources. The gate also fails closed for unsupported live surfaces. It is not production activation, live plugin readiness, KAB readiness, or live Hermes/Discord evidence.

REL-PILOT-FIX-001 also adds Python 3.11 syntax compatibility coverage. `pyproject.toml` declares `requires-python = ">=3.11"`, Ruff targets `py311`, mypy type checks as Python 3.11, and unit tests parse repository Python sources with `ast.parse(..., feature_version=(3, 11))` so Python 3.12-only syntax such as PEP 695 `type` aliases cannot re-enter unnoticed.

## DAEMN-1 client modules

The DAEMN-1 implementation is import-safe and dependency-free:

- `protocol.py` owns protocol constants, status/version/result models, canonical JSON, and command envelopes.
- `errors.py` owns structured daemon error decoding and redaction.
- `conformance.py` owns conformance manifest parsing and the draft zero-fixture guard.
- `client/daemon.py` owns status/version reads and command submission through an explicit transport.
- `client/transport.py` provides the transport protocol and a static fake transport for tests.

There is no live daemon, Hermes, Discord, KAB, auth, token, gateway, localhost, or CLI fallback in these modules.

## DAEMN-2 client modules

DAEMN-2 stays synchronous, import-safe, and dependency-free:

- `client/stream.py` parses stream frames from mappings or NDJSON lines and parses fake `stream.tail` responses.
- `client/diagnostics.py` decodes fake diagnostics responses and applies the existing sensitive-data redaction rules.
- `client/daemon.py` exposes `read_stream_tail()` and `read_diagnostics()` through the existing explicit transport boundary. `read_stream_tail()` performs a `version.read` compatibility probe and requires `stream_frame` support before a stream operation runs.
- `client/transport.py` deep-copies static fake responses so nested stream/diagnostics fixtures cannot leak mutation between calls.

No async test dependency is introduced because DAEMN-2 does not implement live streaming, socket/SSE/WebSocket clients, or daemon discovery.


## HPLUG-2 plugin modules

HPLUG-2 maps DAEMN-2 stream-tail support into the plugin layer without adding dependencies:

- `schemas.py` declares `atn_stream_tail` with required `session_id`/`member`, optional `since_cursor`, bounded `limit`, and `additionalProperties: false`.
- `tools.py` validates stream-tail args before transport, requires explicit `client_factory`, calls `read_stream_tail()`, serializes frames/events into JSON, and redacts sensitive payload/details values.
- `plugin.yaml`, the root entrypoint, and bootstrap smoke tests include these read-only tools and still no hooks or slash commands.

## DELRV-1 plugin modules

DELRV-1 maps exact daemon-owned delegation/review command names into fake/injected Hermes tools without adding dependencies:

- `schemas.py` declares `atn_delegate_new` and `atn_delegate_action`; the action schema uses a closed enum for implemented `delegate.*` commands and omits `delegate.request` / top-level `review`.
- `tools.py` validates required caller-supplied `request_id` and `idempotency_key`, builds command envelopes through `DaemonClient.build_command_envelope(...)`, submits via `submit_command(...)`, preserves structured daemon errors, and does not generate IDs or keep lifecycle/idempotency state.
- `atn_delegate_action` always overwrites/sets `payload.session_id` from the top-level `session_id` before submit.
- `plugin.yaml`, the root entrypoint, and bootstrap smoke tests declare the two DELRV-1 tools while preserving `provides_commands: []`.

No live daemon discovery, localhost/socket transport, Hermes/Discord/gateway/auth/token access, or CLI fallback is introduced.

## CNDIS-1 plugin modules

CNDIS-1 maps exact daemon-owned council and delivery-evidence command names into fake/injected Hermes tools without adding dependencies:

- `protocol.py` declares `delivery_evidence` and `council.lifecycle` feature groups and required feature tuples.
- `client/daemon.py` exposes `require_feature_groups(...)`, which performs injected `version.read` only and fails closed before submit on missing features.
- `schemas.py` declares `atn_council_command` and `atn_delivery_evidence` with closed enums and `additionalProperties: false`.
- `tools.py` validates command-specific payload fields, preserves caller-supplied `request_id`/`idempotency_key`, normalizes top-level `session_id` into the command payload, probes required features, and submits through the explicit fake/injected client.
- `plugin.yaml`, the root entrypoint, and bootstrap smoke tests declare the two CNDIS-1 tools while preserving `provides_hooks: []` and `provides_commands: []`.

No live daemon discovery, localhost/socket transport, Hermes/Discord/gateway/auth/token/KAB access, CLI fallback, plugin-owned logs/locks/cursors, council lifecycle/consensus state, idempotency/dedupe, or delivery-evidence transitions are introduced.

## CNDIS-2 Discord helper module

CNDIS-2 adds `discord_surface.py` and the `atn_discord_send_message` schema/handler
without adding dependencies:

- `discord_surface.py` defines typed target/result objects, a `SendMessageFn` protocol,
  `send_discord_message(...)`, and inert `e2e_config_from_env(...)` parsing from an
  explicitly supplied mapping;
- `schemas.py` declares a target-gated `atn_discord_send_message` tool schema;
- `tools.py` requires an injected sender and renders fail-closed JSON when the sender,
  target, dedicated-test marker, visible live label, or cleanup hint is missing;
- `plugin.yaml`, the root entrypoint, and bootstrap smoke tests declare the helper tool
  while preserving `provides_hooks: []` and `provides_commands: []`.

No environment read, live Discord discovery, Hermes current-session lookup, gateway/auth
token usage, native Discord slash command, ATN slash command, or daemon delivery-evidence
transition is introduced.

---

## Merged from `docs/spec/compatibility-and-operations.md`

# Unsupported Hermes Surfaces

## Purpose

This document records the current unsupported Hermes surfaces for `atn-plugin` so operators do not confuse host capability with ATN plugin readiness.

Hermes currently provides a real plugin slash-command host API through `PluginContext.register_command(name, handler, description, args_hint)`. The ATN plugin still exposes no ATN slash commands. Its manifest must continue to declare `provides_commands: []` until a later task implements and verifies concrete slash-command handlers.

## Current ATN plugin exposure

Supported now:

- `atn_daemon_status` — read-only fake/injected daemon status tool.
- `atn_compatibility_diagnostics` — read-only fake/injected diagnostics tool with redaction.
- `atn_stream_tail` — read-only fake/injected retained stream tail tool with `stream_frame` pre-probe.
- `atn_delegate_new` — fake/injected `delegate.new` command-envelope submission tool with caller-supplied request/idempotency metadata.
- `atn_delegate_action` — fake/injected closed-enum `delegate.*` action/review/delivery command-envelope submission tool.
- `atn_council_command` — fake/injected closed-enum `council.*` lifecycle command-envelope submission tool with `council.lifecycle` pre-probe.
- `atn_delivery_evidence` — fake/injected closed-enum delivery-evidence command-envelope submission tool with `delivery_evidence` pre-probe.
- `atn_discord_send_message` — fake/injected Discord helper tool that requires an
  injected sender and dedicated test target; it returns Discord IDs only as evidence
  pointers and fails closed by default.

Unsupported now:

- ATN slash commands through `ctx.register_command`.
- Native Discord slash-command registration for ATN operations.
- Additional write-capable ATN tools beyond the DELRV-1/CNDIS-1 fake/injected command-envelope tools and the CNDIS-2 injected-only Discord helper.
- `atn_session_status` and any `session.status.read` surface.
- Live daemon discovery, localhost/socket/SSE/WebSocket transport, or CLI fallback.
- Default/live Hermes gateway/send_message delivery helpers, current-session/current-thread
  fallback, or Discord helper behavior that claims daemon-recorded evidence.
- Any Discord helper path that reads tokens, auth, gateway, credential, localhost, socket,
  CLI, current Hermes, or active user-thread state.
- Live Hermes plugin-load readiness, production activation, KAB readiness, or any
  claim broader than local isolated plugin-load smoke.

## Host capability versus plugin readiness

Hermes host evidence:

- `hermes_cli/plugins.py::PluginContext.register_command` can register in-session plugin slash commands for CLI and gateway sessions.
- Plugin command names are normalized, built-in command conflicts are rejected, and handlers receive raw argument strings.
- `hermes_cli/commands.py::COMMAND_REGISTRY` remains the built-in slash-command SOT.

ATN plugin readiness boundary:

- The plugin does not register slash commands; DELRV-1/CNDIS-1 command-envelope tools are Hermes tools, not slash-command bindings.
- The plugin is not installed/enabled as a live Hermes plugin in the active environment, so no live plugin command claim is valid.
- Free-form Discord replies or slash invocations must not become authoritative lifecycle transitions; daemon events remain the SOT.
- `atn_discord_send_message` does not change daemon evidence. Delivery evidence remains
  daemon-owned through `atn_delivery_evidence`; Discord IDs are evidence pointers only.

## Future binding requirements

Before a ATN slash command can be added, a later task must provide all of the following evidence:

1. A concrete command name and no-conflict mapping against Hermes built-ins.
2. A daemon-owned operation or CLI-equivalent command in the control ATN contract.
3. Fake or conformance fixtures for success, validation failure, duplicate/idempotent request, permission or compatibility failure, and malformed daemon payloads.
4. A fail-closed handler that returns a safe string/JSON response and never turns daemon failure into success.
5. No live daemon, Hermes, Discord, gateway, auth, token, localhost, socket, or CLI fallback unless that fallback is explicitly designed, approved, and tested.
6. Manifest update from `provides_commands: []` to the exact command names.
7. Unit and integration coverage for registration, dispatch, argument validation, conflict behavior, and redaction.
8. Isolated Hermes/gateway E2E coverage before any live plugin-load or Discord command readiness claim.

## Non-goals for HPLUG-3

HPLUG-3 is documentation only. It does not add command handlers, alter plugin registration code, change Hermes core, change ATN daemon/control behavior, or claim live install readiness.
