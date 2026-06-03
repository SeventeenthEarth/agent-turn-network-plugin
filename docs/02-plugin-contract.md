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

## HPLUG-2 read-only Hermes tools

HPLUG-2 exposes exactly three Hermes tool schemas through the root plugin entrypoint and `plugin.yaml`:

- `kan_daemon_status` calls `DaemonClient.read_status()` through an explicit fake/injected client factory.
- `kan_compatibility_diagnostics` calls `DaemonClient.read_diagnostics(session_id=...)` through an explicit fake/injected client factory.
- `kan_stream_tail` calls `DaemonClient.read_stream_tail(session_id=..., member=..., since_cursor=..., limit=...)` through an explicit fake/injected client factory.

All handlers return JSON strings. Success envelopes include `ok: true`, `tool`, `protocol_version`, `live_readiness`, and `data`. Failure envelopes include `ok: false`, `tool`, `live_readiness: false`, and an operator-safe `error` object with `category`, `message`, and `retryable`.

Failure mapping is fail-closed:

- missing client factory or transport failure -> `unavailable`;
- unsupported protocol or missing feature groups -> `compatibility`;
- malformed daemon/fake payloads -> `protocol`;
- invalid tool arguments -> `validation`;
- structured daemon command/stream errors preserve daemon category/ids after redaction.

`kan_stream_tail` success data contains `frames` and `next_cursor`. Each frame includes cursor/replay metadata and an event envelope; stream payload/details are redacted with the same sensitive-key rules before Hermes receives them.

`kan_session_status` is deliberately not exposed in HPLUG-2 because the core conformance manifest still has `fixtures: []` and no `session.status.read` authority. It remains deferred until core fixture/protocol evidence exists.

## DAEMN-2 fake stream and diagnostics surfaces

DAEMN-2 extends the same explicit-transport boundary with fake/fixture-only stream and diagnostics client surfaces:

- `read_stream_tail()` probes `version.read` and requires positive `stream_frame` feature-group support before `stream.tail` is attempted;
- stream frames parse from mappings or NDJSON lines shaped as `{cursor, is_replay, event}` with the full event envelope from the core protocol docs;
- malformed stream data fails closed for invalid JSON, non-object roots, unknown explicit `kind`, missing/invalid cursor, invalid `is_replay`, missing/malformed event objects, unsupported frame/event schema versions, invalid optional sequence values, malformed payload/details objects, and oversized frame arrays;
- diagnostics responses decode checks through explicit fake/injected responses and redact token/secret-like details with the DAEMN-1 redaction rules;
- structured stream error frames and diagnostics errors preserve daemon categories and command/session/event/request identifiers while redacting sensitive diagnostics.

This is parser and fake-daemon readiness only. HPLUG-2 maps the existing fake/injected stream tail client into a Hermes tool, but live stream transport, socket/SSE/WebSocket/local daemon discovery, session-status exposure, and CLI fallback remain deferred.

## HPLUG-3 unsupported slash-command bindings

Hermes provides a plugin slash-command host API through `PluginContext.register_command(name, handler, description, args_hint)`. KAN plugin command exposure remains unsupported in HPLUG-3. The plugin manifest must keep `provides_commands: []`, and the root entrypoint must not register command handlers until a later task supplies a concrete KAN daemon command contract.

Future KAN slash-command bindings must preserve the same fail-closed boundary as tools: no live daemon discovery, Hermes, Discord, gateway, auth, token, localhost, socket, or CLI fallback unless explicitly designed and tested. A command must have daemon-owned state semantics, fake or conformance fixtures, duplicate/idempotency handling, structured error preservation, argument validation, redaction coverage, manifest declaration, and isolated Hermes/gateway smoke evidence before readiness is claimed.

See `docs/08-unsupported-surfaces.md` for the operator-facing unsupported-surface matrix and future binding checklist.
