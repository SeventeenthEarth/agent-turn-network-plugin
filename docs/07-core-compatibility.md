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
| Stability | draft, docs/scaffold only |
| Plugin behavior on mismatch | fail closed and direct operator to canonical CLI |

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

### Live local daemon mode

Uses a locally built `kkachi-agent-networkd` with disposable data home. This is allowed for plugin E2E only when explicitly configured.

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

Plugin compatibility checks are safety gates. If the daemon reports an unsupported protocol version, missing required feature, malformed structured error, or missing delivery evidence command path, the plugin must not expose the affected write operation as safe. It should return an operator-friendly failure and point to the canonical CLI fallback.
