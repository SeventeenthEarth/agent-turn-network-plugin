# Control Compatibility

## Goal

Let `kkachi-agent-network-plugin` develop independently from the Go control runtime while proving compatibility with the control daemon contract.

The control-side SOT is `../../kkachi-agent-network-control/docs/21-cross-repo-development.md`. For live-local transport work, the control-side companion SOT is `../../kkachi-agent-network-control/docs/24-live-transport-control-sot.md` and the plugin-side SOT is `docs/10-live-transport-sot.md`. `plugin/LTRAN-001` is completed as docs-only SOT/mapping work; it does not implement live transport or claim live/production/Discord/gateway/auth/token/KAB/hidden CLI fallback readiness. `plugin/LTRAN-002` is completed as the first bounded implementation task for explicit Unix-socket `status.read` / `version.read` live smoke only.

## Current supported control contract

| Field | Value |
| --- | --- |
| Control repo | `../../kkachi-agent-network-control` |
| Protocol version | `hun-protocol-v1alpha0` |
| Fixture manifest | `../../kkachi-agent-network-control/testdata/conformance/manifest.json` |
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

`LTRAN` live-local plugin work uses a locally built `kkachi-agent-networkd` with disposable data home only when a plugin task explicitly configures live transport. Repo-qualified dependency evidence is recorded from control `docs/24-live-transport-control-sot.md` and control `docs/roadmap.md`: `control/LTRAN-001`, `control/LTRAN-002`, and `control/LTRAN-003` are completed. `plugin/LTRAN-002` used that handoff evidence to implement the explicit `live_transport.unix_socket_path` status/version smoke slice, and `plugin/LTRAN-003` now proves bounded explicit Unix-socket `stream.tail`/`command.submit` equivalence against a disposable daemon with durable evidence at `docs/evidence/ltran-003-plugin-equivalence-evidence.json`. This is still not production activation, daemon discovery, live/default Discord, gateway/auth/token mutation, KAB readiness, long-lived member runtime readiness, broad command coverage, or a hidden CLI fallback.

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
| Protocol `hun-protocol-v1alpha0` | Control conformance manifest declares the protocol | Supported for fake/injected client compatibility checks | `make check-core-contract`, `docs/07-core-compatibility.md`, `src/kkachi_agent_network_plugin/protocol.py` | Any other protocol fails closed before compatibility is claimed. |
| `version.read` | Control-supported compatibility probe | Used by stream, council, and delivery-evidence feature gates through injected clients | `tests/unit/test_status_version_client.py`, `tests/unit/test_tool_handlers.py`, `tests/integration/test_cndis_conformance.py` | `session.status.read` is not implemented or exposed. |
| Command/event envelope and structured error | Control-supported command envelope and daemon error contract | Supported through `kan_delegate_new`, `kan_delegate_action`, `kan_council_command`, and `kan_delivery_evidence` with caller-supplied request/idempotency IDs | `tests/unit/test_command_envelope.py`, `tests/unit/test_daemon_error_decoding.py`, `tests/integration/test_delegate_plugin_tools.py` | Unknown commands, malformed envelopes, missing IDs, or daemon structured failures return JSON `ok:false`; no local lifecycle or retry state is added. |
| Stream features | Control feature group `stream_frame` gates retained stream reads | `kan_stream_tail` supported only with positive injected `version.read` compatibility | `tests/unit/test_stream_frame_parsing.py`, `tests/integration/test_fake_daemon_stream_diagnostics.py` | Missing `stream_frame`, malformed frames, live sockets, SSE, WebSocket, CLI, or daemon discovery fail closed / remain unsupported. |
| Delegation/review fixtures | Control DELEG fixtures cover implemented `delegate.*` commands | `kan_delegate_new` and `kan_delegate_action` expose the closed implemented command set | `tests/integration/test_deleg_002_conformance.py`, `tests/unit/test_tool_handlers.py` | `delegate.request`, top-level `review`, generated IDs, plugin-owned dedupe, and live daemon fallback are unsupported. |
| Council lifecycle | Control `council.lifecycle` feature and COUNC fixtures exist | `kan_council_command` supports exact implemented `council.*` lifecycle commands through injected clients | `tests/integration/test_cndis_conformance.py`, `tests/unit/test_tool_handlers.py` | Missing feature probe or unsupported command returns `ok:false`; plugin owns no council state. |
| Council argument graph static contract | Control `ARGUE-002` static fixtures exist for argument-graph speech, hand-raise target links, legacy dual-field preservation, and invalid ARGUE examples | `kan_council_command` and explicit selected-response ARGUE pass-through preserve and locally validate deterministic `claims[]`, `stance_links[]`, `contribution_type`, `new_axis_reason`, `evidence[]`, and `hand_raise.target_links[]` shapes before transport where safe | `tests/unit/test_argue_tool_contract.py`, `tests/unit/test_selected_participant_response.py`, `tests/integration/test_cndis_conformance.py`, `make check-core-contract` | This is static/fake/injected contract coverage only; runtime validation/scoring, participant response generation, visible relation rendering, live Discord, daemon discovery, profile/gateway/auth/token/provider mutation, KAB readiness, and live pilot readiness remain unsupported. |
| Delivery evidence | Control `delivery_evidence` feature and command path exist | `kan_delivery_evidence` supports exact delivery-evidence commands through injected clients | `tests/integration/test_cndis_conformance.py`, `tests/unit/test_tool_handlers.py` | Discord IDs are evidence pointers only; plugin owns no delivery transitions and does not default-send Discord messages. |
| Discussion activation planner/doctor | RUNFIX requires explicit install-vs-activation planning before any apply/live-local pilot | `kan_discussion_activation_plan` builds a pure/local dry-run report from caller-provided evidence, classifies eligible/excluded/blocked profiles from explicit effective Discord evidence, excludes bot-to-bot-enabled profiles by default, emits eligible-only `allow_list_targets`, profile remediation, parent-channel proof state, fallback audit, keeps RUNFIX labels separate, and always returns `live_readiness: false` | `tests/unit/test_discussion_activation_planner.py`, `tests/unit/test_tool_handlers.py`, `tests/unit/test_tool_schemas.py` | No daemon startup, socket discovery, current Hermes/Discord/profile/gateway inspection, CLI fallback, Discord send/channel creation, profile/gateway/provider/auth/token/model mutation, live readiness, or activation apply. |
| `transcript.render` | Control-supported capability | Not exposed as a plugin tool in SKILL-2 | Control `TRANS-001` completion is recorded as unblock evidence only | No `kan_transcript_render` tool, command, hook, or live fallback is added. |
| `export.bundle` | Control-supported capability | Not exposed as a plugin tool in SKILL-2 | Control `TRANS-001`/`RELIA-001` completion is recorded as unblock evidence only | No `kan_export_bundle` tool, command, hook, or live fallback is added. |
| Packaged skill resource | Python package includes `bundled_skills/kan-plugin/SKILL.md` | Supported for import-safe package resource reads | `tests/unit/test_bundled_skills.py`, `make check-plugin-load-smoke` | The package does not install into the user's Hermes profile. |
| Local isolated plugin-load smoke | Hermes-compatible root `register(ctx)` entrypoint can be loaded with a fake context | Supported only as local isolated plugin-load smoke | `scripts/check_plugin_load_smoke.py`, `tests/unit/test_plugin_load_smoke.py`, `make check-plugin-load-smoke` | This is not production activation, live plugin readiness, KAB readiness, live Hermes readiness, or live Discord readiness. |
| Live-local daemon transport | `plugin/LTRAN-001` docs-only mapping complete; `control/LTRAN-001`, `control/LTRAN-002`, and `control/LTRAN-003` completed as dependency evidence | `plugin/LTRAN-002` supports explicit `live_transport.unix_socket_path` Unix-socket transport for `status.read` and `version.read` smoke only | `tests/unit/test_live_transport_config.py`, `tests/integration/test_live_unix_socket_transport.py`, `docs/10-live-transport-sot.md` | No-config, unsafe paths, localhost/TCP, CLI fallback, daemon discovery, Hermes gateway, auth/token, KAB, provider/profile mutation, stream/write support, equivalence proof, dedupe proof, hidden fallback, and production activation remain unsupported. |
| `kan_session_status` | No authoritative `session.status.read` plugin contract | Unsupported | Guardrails, schema tests, docs | Do not add `kan_session_status` or `session.status.read` support. |
| KAN slash commands | Hermes host can register commands, but plugin has no approved KAN command contract | Unsupported; `provides_commands: []` stays unchanged | `plugin.yaml`, bootstrap smoke, plugin-load smoke, docs guardrails | Any `provides_commands: [kan]` or `register_command` drift fails local smoke. |
| Native Discord slash commands | No supported plugin/native Discord slash-command contract | Unsupported | `docs/05-discord-surface.md`, `docs/08-unsupported-surfaces.md` | No native Discord command registration or gateway fallback. |
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

HPLUG-2 exposes `kan_daemon_status`, `kan_compatibility_diagnostics`, and `kan_stream_tail` only through explicit fake/injected client factories. Missing factories, unsupported protocol versions, missing feature groups, malformed status/diagnostics/stream payloads, and sensitive diagnostics/stream payloads all fail closed or redact before returning JSON to Hermes.

`kan_stream_tail` inherits DAEMN-2 stream safety: it must receive positive `stream_frame` compatibility from `version.read` before `stream.tail` is attempted. `kan_session_status` is not exposed because no authoritative control fixture/protocol operation exists for `session.status.read`; this avoids plugin-owned state authority or schema-only overclaiming.

## DELRV-1 command-envelope compatibility guard

DELRV-1 exposes `kan_delegate_new` and `kan_delegate_action` only through explicit fake/injected client factories and the existing `command.submit` operation. `kan_delegate_new` always submits `delegate.new`. `kan_delegate_action` accepts only the exact implemented `delegate.*` action/review/delivery enum and rejects `delegate.request`, top-level `review`, and any unknown command before transport.

The plugin requires caller-supplied non-empty `request_id` and `idempotency_key`, does not generate hidden identifiers, does not cache/dedupe locally, and owns no delegation/review lifecycle state. The daemon remains authoritative for domain validation, idempotency semantics, duplicate handling, state transitions, and structured errors. Local validation maps to `validation`; missing injected clients map to `unavailable`; malformed daemon responses map to `protocol`; structured daemon failures such as `conflict` are preserved.

This is fake/injected compatibility only and does not change live readiness, installed plugin-load readiness, slash-command readiness, Discord/gateway readiness, or auth/token boundaries.

## CNDIS-1 council and delivery-evidence compatibility guard

CNDIS-1 exposes `kan_council_command` and `kan_delivery_evidence` only through explicit fake/injected client factories and the existing `command.submit` operation. `kan_council_command` accepts only the implemented `council.*` enum from COUNC-001. `kan_delivery_evidence` accepts only `delegate.escalation_delivered` and `delegate.escalation_delivery_failed`.

Before submit, `kan_council_command` requires injected `version.read` to report `council.lifecycle`; `kan_delivery_evidence` requires `delivery_evidence`. Missing feature groups fail closed with `compatibility` before `command.submit`.

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

ARGUE-002 extends `kan_selected_participant_response` with local deterministic
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

Hermes host slash-command support exists through `PluginContext.register_command`, but KAN plugin slash commands are not compatible-ready. Control KAN must first provide daemon command authority, protocol fixtures, idempotency/error semantics, and delivery-evidence rules for the specific operation. Until then, `provides_commands: []` is the correct manifest state and no slash-command handler should be registered. See `docs/08-unsupported-surfaces.md` for the operator-facing unsupported-surface matrix and future binding checklist.

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
kkachi-agent-networkd, open sockets, use localhost, call a CLI, discover
providers, use auth/token/gateway material, contact Discord, call KAB, prove
production activation, or prove live plugin readiness. The smoke claim is only
local isolated plugin-load smoke.
