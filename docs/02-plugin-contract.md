# Plugin Contract

## Compatibility source

The core repo owns protocol schemas and conformance fixtures. The plugin consumes that contract and proves compatibility through tests.

Required compatibility checks:

- daemon reachable;
- daemon protocol version supported;
- required feature flags present;
- command envelope schema supported;
- stream frame schema supported;
- structured error schema supported.

If any required check fails, the plugin fails closed and does not expose the affected operation as safe. DAEMN-1 does not call or suggest a plugin-side CLI fallback.

## Tool handler rules

Hermes tool handlers must:

- accept structured arguments;
- call the Python daemon client, not private storage files;
- return JSON strings;
- preserve daemon `command_id`, `event_id`, `session_id`, and error category fields;
- never turn daemon failure into success;
- avoid raw token/secrets in logs and responses.

## CLI fallback rule

CLI fallback is not implemented in DAEMN-1. If a later task adds one, it must be explicit, argv-only, equivalent to an operator running `kkachi-agent-network` manually, and covered by tests.

## Plugin/core equivalence

For every plugin write operation, there must be a documented equivalent daemon/CLI command in the core repo. Equivalence means same state transition, same validation, same idempotency behavior, and compatible structured errors.

## DAEMN-1 draft client foundation

DAEMN-1 implements only the import-safe Python client foundation. It requires an explicit fake or injected transport and does not open localhost sockets, call the core CLI, inspect Hermes runtime state, touch Discord/gateway/auth/token data, or expose Hermes plugin tools.

The foundation currently covers:

- status/version response parsing with supported-protocol and required-feature checks;
- deterministic command envelope serialization with caller-supplied request and idempotency identifiers;
- structured daemon error decoding that preserves command/session/event/request identifiers while redacting token/secret-like diagnostics;
- conformance manifest parsing where `fixtures: []` is accepted only for draft/scaffold stability and always forces `live_readiness: false`.

Live daemon support and plugin tool readiness remain blocked until stable core fixtures and endpoint declarations exist.

## DAEMN-2 fake stream and diagnostics surfaces

DAEMN-2 extends the same explicit-transport boundary with fake/fixture-only stream and diagnostics client surfaces:

- `read_stream_tail()` probes `version.read` and requires positive `stream_frame` feature-group support before `stream.tail` is attempted;
- stream frames parse from mappings or NDJSON lines shaped as `{cursor, is_replay, event}` with the full event envelope from the core protocol docs;
- malformed stream data fails closed for invalid JSON, non-object roots, unknown explicit `kind`, missing/invalid cursor, invalid `is_replay`, missing/malformed event objects, unsupported frame/event schema versions, invalid optional sequence values, malformed payload/details objects, and oversized frame arrays;
- diagnostics responses decode checks through explicit fake/injected responses and redact token/secret-like details with the DAEMN-1 redaction rules;
- structured stream error frames and diagnostics errors preserve daemon categories and command/session/event/request identifiers while redacting sensitive diagnostics.

This is parser and fake-daemon readiness only. Live stream transport, socket/SSE/WebSocket/local daemon discovery, Hermes tool exposure, and CLI fallback remain deferred.
