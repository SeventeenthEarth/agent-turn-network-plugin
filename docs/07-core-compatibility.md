# Control Compatibility

## Goal

Let `kkachi-agent-network-plugin` develop independently from the Go control runtime while proving compatibility with the control daemon contract.

The control-side SOT is `../../kkachi-agent-network-control/docs/21-cross-repo-development.md`.

## Current supported control contract

| Field | Value |
| --- | --- |
| Control repo | `../../kkachi-agent-network-control` |
| Protocol version | `kan-protocol-v1alpha0` |
| Fixture manifest | `../../kkachi-agent-network-control/testdata/conformance/manifest.json` |
| Stability | draft, docs/scaffold/client-foundation plus fake/injected HPLUG-2 read-only status/diagnostics/stream-tail tools and HPLUG-3 unsupported slash-command documentation |
| Plugin behavior on mismatch | fail closed; no live fallback; affected tool returns `ok:false` |

## Compatibility checks

The plugin must check:

- daemon reachable;
- daemon protocol version supported;
- required daemon feature flags present;
- command envelope schema supported;
- stream frame schema supported;
- structured error schema supported;
- delivery evidence command path supported before Discord helper posts are marked complete.

## Parallel development modes

### Fake daemon mode

Default for unit and integration tests before the control daemon exists. Fake daemon responses are derived from the control conformance manifest and fixtures.

### Fixture mode

The Python client parses control fixtures without starting the real daemon. This is required for P1 and later.

### Future live local daemon mode

Not part of DAEMN-1. A later milestone may use a locally built `kkachi-agent-networkd` with disposable data home, but only when explicitly configured.

### Isolated Hermes/Discord mode

Uses disposable Hermes home/profile and dedicated Discord test target. It must never default to the current running Hermes gateway or active Discord thread.

## Plugin milestone matrix

| Plugin milestone | Control task gate checked | Allowed before control implementation | Release-ready requires |
| --- | --- | --- | --- |
| P0 Scaffold | BOOTS-001 plus control cross-repo docs and manifest exist | yes | root/docs/Makefile guardrails pass |
| P1 Python daemon client | DAEMN-002 version/features, command envelope, stream/error fixtures | yes, fake daemon | conformance tests against fixture manifest |
| P2 Hermes status/diagnostic tools | DAEMN-002 daemon status/session/stream fixtures | yes, fake daemon | implemented control status/stream contract |
| P3 Delegation/review tools | DELEG-001 delegation/review command fixtures | yes, fake/injected only | implemented control commands, fake-daemon coverage, review gates, and final evidence; no live-local/plugin-load readiness claim |
| P4 Council/Discord surface | COUNC-001 council fixtures plus DAEMN-002 delivery evidence fixtures | skeleton/fake only | isolated E2E target and delivery evidence contract |
| P5 Skill/distribution | TRANS-001/RELIA-001 implemented command matrix and release-readiness evidence | docs-only draft | compatibility matrix and install smoke tests |

## Cross-repo check command

```bash
make check-core-contract
```

This command checks that the sibling control repo exposes the expected docs, manifest, protocol version, and reciprocal `check-plugin-contract` target.

## Fail-closed rule

Plugin compatibility checks are safety gates. If the daemon reports an unsupported protocol version, missing required feature, malformed structured error, or missing delivery evidence command path, the plugin must not expose the affected write operation as safe. DAEMN-1 stops at an operator-friendly failure; it does not call a live daemon or CLI fallback.

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

## HPLUG-3 slash-command compatibility guard

Hermes host slash-command support exists through `PluginContext.register_command`, but KAN plugin slash commands are not compatible-ready. Control KAN must first provide daemon command authority, protocol fixtures, idempotency/error semantics, and delivery-evidence rules for the specific operation. Until then, `provides_commands: []` is the correct manifest state and no slash-command handler should be registered. See `docs/08-unsupported-surfaces.md` for the operator-facing unsupported-surface matrix and future binding checklist.
