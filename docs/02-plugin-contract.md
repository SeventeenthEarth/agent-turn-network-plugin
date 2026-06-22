# Plugin Contract

## Compatibility source

The control repo owns protocol schemas and conformance fixtures. The plugin consumes that contract and proves compatibility through tests.

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

## Plugin/control equivalence

For every plugin write operation, there must be a documented equivalent daemon/CLI command in the control repo. Equivalence means same state transition, same validation, same idempotency behavior, and compatible structured errors.

## DAEMN-1 draft client foundation

DAEMN-1 implements only the import-safe Python client foundation. It requires an explicit fake or injected transport and does not open localhost sockets, call the control CLI, inspect Hermes runtime state, touch Discord/gateway/auth/token data, or expose Hermes plugin tools.

The foundation currently covers:

- status/version response parsing with supported-protocol and required-feature checks;
- deterministic command envelope serialization with caller-supplied request and idempotency identifiers;
- structured daemon error decoding that preserves command/session/event/request identifiers while redacting token/secret-like diagnostics;
- conformance manifest parsing where `fixtures: []` is accepted only for draft/scaffold stability and always forces `live_readiness: false`.

Live daemon support remains blocked until stable endpoint declarations and separate live-plugin evidence exist. Current plugin tools are fake/injected only and succeed only when a caller supplies an explicit `DaemonClient` transport.

## HPLUG-2 read-only Hermes tools

HPLUG-2 introduced three read-only Hermes tool schemas through the root plugin entrypoint and `plugin.yaml`:

- `hun_daemon_status` calls `DaemonClient.read_status()` through an explicit fake/injected client factory.
- `hun_compatibility_diagnostics` calls `DaemonClient.read_diagnostics(session_id=...)` through an explicit fake/injected client factory.
- `hun_stream_tail` calls `DaemonClient.read_stream_tail(session_id=..., member=..., since_cursor=..., limit=...)` through an explicit fake/injected client factory.

All handlers return JSON strings. Success envelopes include `ok: true`, `tool`, `protocol_version`, `live_readiness`, and `data`. Failure envelopes include `ok: false`, `tool`, `live_readiness: false`, and an operator-safe `error` object with `category`, `message`, and `retryable`.

Failure mapping is fail-closed:

- missing client factory or transport failure -> `unavailable`;
- unsupported protocol or missing feature groups -> `compatibility`;
- malformed daemon/fake payloads -> `protocol`;
- invalid tool arguments -> `validation`;
- structured daemon command/stream errors preserve daemon category/ids after redaction.

`hun_stream_tail` success data contains `frames` and `next_cursor`. Each frame includes cursor/replay metadata and an event envelope; stream payload/details are redacted with the same sensitive-key rules before Hermes receives them.

`hun_session_status` is deliberately not exposed in HPLUG-2 because the control conformance manifest still has `fixtures: []` and no `session.status.read` authority. It remains deferred until `DAEMN-002` or a later control task provides control fixture/protocol evidence.

## DELRV-1 delegation/review command-envelope tools

DELRV-1 adds fake/injected-only Hermes tool schemas for daemon-owned delegation and review command envelopes:

- `hun_delegate_new` builds and submits command envelope `delegate.new`.
- `hun_delegate_action` builds and submits a closed enum of exact implemented `delegate.*` action/review/delivery commands: `delegate.ack`, `delegate.message`, `delegate.clarify`, `delegate.answer_clarification`, `delegate.update`, `delegate.request_update`, `delegate.submit`, `delegate.review`, `delegate.review_question`, `delegate.review_answer`, `delegate.review_submit`, `delegate.revise`, `delegate.accept`, `delegate.escalate`, `delegate.escalation_flush`, `delegate.resolve_escalation`, `delegate.escalation_delivered`, `delegate.escalation_delivery_failed`.

Both tools require caller-supplied non-empty `request_id` and `idempotency_key`. The plugin does not generate hidden identifiers, cache/dedupe requests, own delegation lifecycle state, or perform daemon discovery. Local validation rejects `delegate.request`, top-level `review`, missing metadata, non-object payloads, and any command outside the closed enum before transport. Structured daemon failures such as `conflict` are preserved in the JSON error envelope.

For `hun_delegate_action`, the top-level `session_id` is authoritative: handlers always overwrite/set `payload.session_id` with that value before submitting the envelope. Remaining payload fields stay opaque for daemon-side validation.

This is fake/injected DELRV-1 readiness only. The tools use `DaemonClient.build_command_envelope(...)` and `submit_command(...)` through an injected client factory; they do not prove live daemon, installed Hermes plugin-load, slash-command, Discord, gateway, auth, token, socket, localhost, or CLI readiness.

## CNDIS-1 council and delivery-evidence command tools

CNDIS-1 adds fake/injected-only Hermes tool schemas for daemon-owned council lifecycle and delivery-evidence command envelopes:

- `hun_council_command` builds and submits a closed enum of exact implemented `council.*` commands: `council.new`, `council.request_attendance`, `council.attend`, `council.lock_agenda`, `council.prepare`, `council.ready`, `council.prepared_partial`, `council.poll`, `council.hand_raise`, `council.grant`, `council.speak`, `council.intervene`, `council.propose`, `council.revise`, `council.request_vote`, `council.vote`, `council.finalize`, and `council.unresolved`.
- `hun_delivery_evidence` builds and submits only `delegate.escalation_delivered` and `delegate.escalation_delivery_failed`. `hun_delegate_action` keeps accepting those commands for DELRV compatibility; `hun_delivery_evidence` is the clearer CNDIS surface.

Both tools require caller-supplied non-empty `request_id` and `idempotency_key`. The plugin does not generate IDs, cache/dedupe, own council lifecycle/consensus state, write logs/locks/cursors, or transition delivery evidence locally. The top-level `session_id` is authoritative and overwrites/sets `payload.session_id` before submit.

Before `command.submit`, `hun_council_command` calls injected `version.read` and requires `council.lifecycle`; `hun_delivery_evidence` requires `delivery_evidence`. Missing feature groups return `compatibility` before submit. Unknown commands, missing IDs, non-object payloads, and command-specific missing payload fields return `validation` before the client factory or submit path is used.

This is fake/injected CNDIS readiness only. It does not prove live daemon, installed Hermes plugin-load, slash-command, Discord helper/send_message, gateway, auth, token, socket, localhost, CLI, or KAB readiness.

## RUNFIX-006/RUNFIX-007 discussion activation planner/doctor

RUNFIX-006 added `hun_discussion_activation_plan` as a pure/local Hermes tool.
RUNFIX-007 keeps the same tool surface and extends the dry-run report for
Discord eligibility and bot-to-bot exclusion. The tool builds a deterministic
activation planner/doctor report from explicit caller-provided evidence only.
The input names control/RUNFIX-005 dependency evidence, plugin install/enabled/
tool visibility evidence, explicit daemon socket/config and compatibility
evidence, participant profiles, selected Discord parent-channel proof, planned
dry-run changes, rollback steps, verification commands, approval gates,
optional operator blockers, and separated RUNFIX evidence labels. Inputs may use
`plugin/RUNFIX-006` for compatibility or `plugin/RUNFIX-007` for the current
behavior; output includes `behavior_task_id: plugin/RUNFIX-007`.

The tool classifies participant profiles into eligible, excluded, and
blocked/unknown lists from `effective_discord` evidence, with legacy
`tools_visible` and `bot_to_bot_enabled` fields still accepted for compatibility.
Bot-to-bot-enabled profiles are excluded by default. Unknown or missing profile
eligibility or tool visibility blocks that profile. The report includes
eligible-only `allow_list_targets`, profile remediation, parent-channel proof
state, and a fallback audit rejecting hidden plugin-to-CLI subprocess fallback,
current Hermes/Discord inference, manual profile replies as full KAN success,
daemon startup/discovery, profile/gateway/provider/auth/token/model mutation,
`codex exec`, generic OpenAI SDK, raw app-server transport, and KAB
`native_codex`.

Missing parent-channel allow-list inheritance proof is reported as a
Hermes/gateway dependency blocker, not as a fallback to current-thread messages.
Thread-only, current-channel, or manual profile evidence is not accepted as
parent-channel inheritance proof unless explicit gateway evidence says it covers
parent inheritance.
The five RUNFIX labels (`lifecycle_pass`, `fallback_profile_pass`,
`selected_runner_pass`, `visible_surface_pass`, and `discussion_quality_pass`)
remain separate and default to `unproven` unless explicitly supplied.

This planner never proves live readiness. `hun_discussion_activation_plan` always
returns `live_readiness: false` and performs no environment reads, current
Hermes/Discord/profile/gateway inspection, socket discovery, CLI fallback,
daemon startup, Discord send/channel creation, profile/gateway/provider/auth/
token/model mutation, activation apply, or production readiness claim.

## CNDIS-2 injected Discord helper

CNDIS-2 adds `hun_discord_send_message` as a narrow injected-only Hermes tool wrapper over
`discord_surface.py`:

- callers must supply `content` and an explicit Discord target object;
- the target must set `dedicated_test_target: true` and must not point at current/active
  user or Hermes thread labels;
- when `live_opt_in: true`, the target must include a visible `label` and
  `cleanup_hint`;
- the handler requires an injected `send_message` callable and returns `unavailable` or
  `validation` failure JSON when injection/validation is missing;
- success data contains only Discord evidence pointers such as `message_id`,
  `channel_id`, optional `thread_id`, optional `message_ref`, label, and cleanup hint.

The helper never reads environment variables, opens live gateway/socket/CLI paths,
discovers the current Hermes session, uses auth/token/credential config, registers slash
commands, or records daemon delivery evidence by itself. If a caller wants daemon-owned
delivery evidence, it must still submit the existing fake/injected `hun_delivery_evidence`
command with Discord IDs treated only as evidence pointers.

## DAEMN-2 fake stream and diagnostics surfaces

DAEMN-2 extends the same explicit-transport boundary with fake/fixture-only stream and diagnostics client surfaces:

- `read_stream_tail()` probes `version.read` and requires positive `stream_frame` feature-group support before `stream.tail` is attempted;
- stream frames parse from mappings or NDJSON lines shaped as `{cursor, is_replay, event}` with the full event envelope from the control protocol docs;
- malformed stream data fails closed for invalid JSON, non-object roots, unknown explicit `kind`, missing/invalid cursor, invalid `is_replay`, missing/malformed event objects, unsupported frame/event schema versions, invalid optional sequence values, malformed payload/details objects, and oversized frame arrays;
- diagnostics responses decode checks through explicit fake/injected responses and redact token/secret-like details with the DAEMN-1 redaction rules;
- structured stream error frames and diagnostics errors preserve daemon categories and command/session/event/request identifiers while redacting sensitive diagnostics.

This is parser and fake-daemon readiness only. HPLUG-2 maps the existing fake/injected stream tail client into a Hermes tool, but live stream transport, socket/SSE/WebSocket/local daemon discovery, session-status exposure, and CLI fallback remain deferred.

## HPLUG-3 unsupported slash-command bindings

Hermes provides a plugin slash-command host API through `PluginContext.register_command(name, handler, description, args_hint)`. KAN plugin slash-command exposure remains unsupported. The plugin manifest must keep `provides_commands: []`, and the root entrypoint must not register command handlers until a later task supplies a concrete slash-command binding contract and isolated verification.

Future KAN slash-command bindings must preserve the same fail-closed boundary as tools: no live daemon discovery, Hermes, Discord, gateway, auth, token, localhost, socket, or CLI fallback unless explicitly designed and tested. A command must have daemon-owned state semantics, fake or conformance fixtures, duplicate/idempotency handling, structured error preservation, argument validation, redaction coverage, manifest declaration, and isolated Hermes/gateway smoke evidence before readiness is claimed.

See `docs/08-unsupported-surfaces.md` for the operator-facing unsupported-surface matrix and future binding checklist.
