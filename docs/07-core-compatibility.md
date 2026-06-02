# Core Compatibility

## Goal

Let `kkachi-agent-network-plugin` develop independently from the Go core while proving compatibility with the core daemon contract.

The core-side SOT is `../../kkachi-agent-network/docs/21-cross-repo-development.md`.

## Current supported core contract

| Field | Value |
| --- | --- |
| Core repo | `../../kkachi-agent-network` |
| Protocol version | `kan-protocol-v1alpha0` |
| Fixture manifest | `../../kkachi-agent-network/testdata/conformance/manifest.json` |
| Stability | draft, docs/scaffold/client-foundation only |
| Plugin behavior on mismatch | fail closed; no DAEMN-1 live fallback or tool exposure |

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

Default for unit and integration tests before the core daemon exists. Fake daemon responses are derived from the core conformance manifest and fixtures.

### Fixture mode

The Python client parses core fixtures without starting the real daemon. This is required for P1 and later.

### Future live local daemon mode

Not part of DAEMN-1. A later milestone may use a locally built `kkachi-agent-networkd` with disposable data home, but only when explicitly configured.

### Isolated Hermes/Discord mode

Uses disposable Hermes home/profile and dedicated Discord test target. It must never default to the current running Hermes gateway or active Discord thread.

## Plugin milestone matrix

| Plugin milestone | Core milestone checked | Allowed before core implementation | Release-ready requires |
| --- | --- | --- | --- |
| P0 Scaffold | core cross-repo docs and manifest exist | yes | root/docs/Makefile guardrails pass |
| P1 Python daemon client | version/features, command envelope, stream/error fixtures | yes, fake daemon | conformance tests against fixture manifest |
| P2 Hermes status/diagnostic tools | daemon status/session/stream fixtures | yes, fake daemon | implemented core status/stream contract |
| P3 Delegation/review tools | delegation/review command fixtures | skeleton only | implemented core commands and fake+live-local tests |
| P4 Council/Discord surface | council + delivery evidence fixtures | skeleton/fake only | isolated E2E target and delivery evidence contract |
| P5 Skill/distribution | implemented command matrix | docs-only draft | compatibility matrix and install smoke tests |

## Cross-repo check command

```bash
make check-core-contract
```

This command checks that the sibling core repo exposes the expected docs, manifest, protocol version, and reciprocal `check-plugin-contract` target.

## Fail-closed rule

Plugin compatibility checks are safety gates. If the daemon reports an unsupported protocol version, missing required feature, malformed structured error, or missing delivery evidence command path, the plugin must not expose the affected write operation as safe. DAEMN-1 stops at an operator-friendly failure; it does not call a live daemon or CLI fallback.

## DAEMN-1 manifest guard

The client foundation parses both the plugin-local draft manifest and the core conformance manifest. `fixtures: []` is valid only when `stability` is explicitly draft/scaffold-like. Empty fixtures always force `live_readiness: false`, even if a malformed manifest tries to claim otherwise. Unsupported protocol versions, missing required feature groups, malformed fixture lists, or non-boolean live-readiness values fail closed before any future live operation can be considered safe.

DAEMN-1 does not contact a live daemon. Status/version reads and command submission require an explicit fake or injected transport. No localhost, CLI, Hermes, Discord, KAB, auth, token, or gateway fallback is implemented.

## DAEMN-2 stream and diagnostics guard

DAEMN-2 adds fake/fixture-only stream tail parsing and diagnostics decoding. Stream tail reads are gated by a `version.read` compatibility probe that must report `stream_frame` in `feature_groups` before `stream.tail` is attempted. Missing `stream_frame`, unsupported protocol versions, malformed frames, malformed diagnostics payloads, unsupported frame/event schema versions, and oversized frame/check arrays fail closed.

This does not change live readiness. Core conformance fixtures are still draft/manifest-only, and live stream transport remains blocked/deferred until stable core stream/status fixtures and endpoint declarations exist.
