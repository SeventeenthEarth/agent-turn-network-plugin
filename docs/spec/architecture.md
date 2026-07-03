# Plugin Architecture

## Components

```text
atn-plugin/
  plugin.yaml or equivalent manifest
  src/atn_plugin/
    protocol.py          # protocol constants, models, canonical envelopes
    errors.py            # structured daemon error decoding/redaction
    conformance.py       # conformance manifest guard
    client/              # explicit fake/injected daemon transport client
      stream.py          # stream frame / NDJSON / tail-response parser
      diagnostics.py     # diagnostics response decoder/redactor
    schemas.py           # fake/injected Hermes tool schemas
    tools.py             # JSON-string tool handlers
    discord_surface.py   # injected-only Discord target/send_message boundary
    slash_commands/      # future optional ATN slash-command wiring; unsupported
    health.py            # future live daemon compatibility checks
  tests/
    unit/
    integration/
    e2e/
  docs/
  Makefile
```

## Flow

```text
DAEMN-2 fake/injected transport
  -> Python ATN daemon client
    -> status/version parser, command envelope serializer,
       stream tail parser, or diagnostics decoder
    <- structured success/error/stream/diagnostics fixture

HPLUG-2 Hermes read-only tool
  -> plugin handler
    -> explicit fake/injected Python ATN daemon client
      -> status.read, diagnostics.read, or version.read + stream.tail fake transport operation
      <- structured success/error/diagnostics/stream fixture
    -> plugin renders JSON-string success or fail-closed error

DELRV-1 Hermes command-envelope tool
  -> plugin handler
    -> explicit fake/injected Python ATN daemon client
      -> command.submit fake transport operation
      <- structured success/error
    -> plugin renders JSON-string success or fail-closed error

CNDIS-1 Hermes command-envelope tool
  -> plugin handler
    -> explicit fake/injected Python ATN daemon client
      -> version.read feature probe for council.lifecycle or delivery_evidence
      -> command.submit fake transport operation
      <- structured success/error
    -> plugin renders JSON-string success or fail-closed error

CNDIS-2 injected Discord helper
  -> plugin handler
    -> validate dedicated Discord test target and visible live opt-in metadata
    -> explicit injected send_message callable
      <- Discord evidence pointer result
    -> plugin renders JSON-string success or fail-closed error
```

## Boundary rules

- The plugin calls the daemon protocol; it does not write control storage files.
- The plugin returns daemon errors as authoritative failures.
- Handlers have no shell, localhost, Hermes, Discord, KAB, auth, token, gateway, or CLI fallback; callers must inject a client factory explicitly for success paths.
- Stream tail reads first require positive `stream_frame` feature-group evidence from the injected transport before the `stream.tail` operation is attempted.
- CNDIS write-like command tools must pass an injected `version.read` feature-group probe before submit; missing `council.lifecycle` or `delivery_evidence` fails closed before transport submission.
- The Discord helper has no sender by default. It requires explicit sender injection and
  dedicated target metadata; it never infers daemon evidence from Discord state.
- Hermes restart/plugin reload must not affect daemon state.

## Hermes plugin surface

The plugin currently registers the manifest-declared fake/injected Hermes tools and no hooks or ATN slash commands:

- `atn_daemon_status` — fake/injected daemon status read;
- `atn_compatibility_diagnostics` — fake/injected diagnostics read with redaction;
- `atn_stream_tail` — fake/injected retained stream tail read that requires positive `stream_frame` compatibility before `stream.tail`.
- `atn_stream_ack` — fake/injected stream cursor ack that requires positive `stream.ack` compatibility before `stream.ack`.
- `atn_delegate_new` — fake/injected `delegate.new` command-envelope submission with caller-supplied request/idempotency metadata;
- `atn_delegate_action` — fake/injected closed-enum `delegate.*` action/review/delivery command-envelope submission. Its top-level `session_id` overrides/sets `payload.session_id` before submit.
- `atn_council_command` — fake/injected closed-enum `council.*` lifecycle command-envelope submission with `council.lifecycle` pre-probe and no plugin-owned council state;
- `atn_selected_participant_response` — fake/injected selected-member `council.speak`
  proof submission followed by selected-cursor ack only after submit succeeds;
- `atn_delivery_evidence` — fake/injected closed-enum `delegate.escalation_delivered` / `delegate.escalation_delivery_failed` command-envelope submission with `delivery_evidence` pre-probe and no plugin-owned delivery-evidence transitions.
- `atn_surface_render_projection` — pure/local visible-surface projection from daemon/control event data; cursor order is authority, speech requires matching `speaker_selected` floor-grant evidence, draft/vote/final closeout entries render into a clean `visible_transcript`, raw cursors/event ids remain in `audit_log`/`rows`, delivery pointers stay evidence-only, and `live_readiness` remains false.
- `atn_discussion_activation_plan` — pure/local RUNFIX dry-run planner/doctor from explicit caller-provided evidence; it classifies eligible, excluded, and blocked/unknown profiles from explicit effective Discord evidence, excludes bot-to-bot-enabled profiles by default, emits eligible-only `allow_list_targets`, profile remediation, parent-channel proof state, and fallback-audit rejection rows, keeps RUNFIX evidence labels separate, reports unproven parent-channel inheritance as a gateway blocker, performs no discovery or mutation, and keeps `live_readiness` false.
- `atn_discord_send_message` — fake/injected Discord helper that requires a dedicated
  test target and an injected `send_message` callable; it returns Discord IDs only as
  evidence pointers and fails closed without sender injection.

Later tasks may provide:

- `atn_session_status` after control `session.status.read` fixture/protocol authority exists;
- cursor/session diagnostic tools;
- transcript/export tools;
- live transport according to `docs/spec/live-transport-sot.md`, where the CLI is the main-agent control plane, the plugin is the participant-agent ATN client surface, member runtimes invoke real participant profiles, the daemon remains the only event/state authority, and companion control `LTRAN` / `MEMBR` / `SURFD` epics must complete before the matching plugin epics start;
- ATN slash commands for common operations after control command contracts, conformance fixtures, safe handlers, manifest entries, and isolated Hermes/gateway smoke tests exist;
- bundled skill guidance;
- live Discord helper wiring that posts visible messages through a dedicated Hermes
  gateway/send_message configuration and separately records delivery evidence through
  daemon commands.

Hermes host support is not the blocker: `PluginContext.register_command()` can register plugin slash commands. The plugin still keeps `provides_commands: []` because DELRV-1 is a Hermes tool surface, not a slash-command binding; future slash commands need separate daemon-owned command semantics and isolated fail-closed tests.

---

## Merged from `docs/spec/architecture.md`

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

CLI fallback is not implemented in DAEMN-1. If a later task adds one, it must be explicit, argv-only, equivalent to an operator running `atn-control` manually, and covered by tests.

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

- `atn_daemon_status` calls `DaemonClient.read_status()` through an explicit fake/injected client factory.
- `atn_compatibility_diagnostics` calls `DaemonClient.read_diagnostics(session_id=...)` through an explicit fake/injected client factory.
- `atn_stream_tail` calls `DaemonClient.read_stream_tail(session_id=..., member=..., since_cursor=..., limit=...)` through an explicit fake/injected client factory.

All handlers return JSON strings. Success envelopes include `ok: true`, `tool`, `protocol_version`, `live_readiness`, and `data`. Failure envelopes include `ok: false`, `tool`, `live_readiness: false`, and an operator-safe `error` object with `category`, `message`, and `retryable`.

Failure mapping is fail-closed:

- missing client factory or transport failure -> `unavailable`;
- unsupported protocol or missing feature groups -> `compatibility`;
- malformed daemon/fake payloads -> `protocol`;
- invalid tool arguments -> `validation`;
- structured daemon command/stream errors preserve daemon category/ids after redaction.

`atn_stream_tail` success data contains `frames` and `next_cursor`. Each frame includes cursor/replay metadata and an event envelope; stream payload/details are redacted with the same sensitive-key rules before Hermes receives them.

`atn_session_status` is deliberately not exposed in HPLUG-2 because the control conformance manifest still has `fixtures: []` and no `session.status.read` authority. It remains deferred until `DAEMN-002` or a later control task provides control fixture/protocol evidence.

## DELRV-1 delegation/review command-envelope tools

DELRV-1 adds fake/injected-only Hermes tool schemas for daemon-owned delegation and review command envelopes:

- `atn_delegate_new` builds and submits command envelope `delegate.new`.
- `atn_delegate_action` builds and submits a closed enum of exact implemented `delegate.*` action/review/delivery commands: `delegate.ack`, `delegate.message`, `delegate.clarify`, `delegate.answer_clarification`, `delegate.update`, `delegate.request_update`, `delegate.submit`, `delegate.review`, `delegate.review_question`, `delegate.review_answer`, `delegate.review_submit`, `delegate.revise`, `delegate.accept`, `delegate.escalate`, `delegate.escalation_flush`, `delegate.resolve_escalation`, `delegate.escalation_delivered`, `delegate.escalation_delivery_failed`.

Both tools require caller-supplied non-empty `request_id` and `idempotency_key`. The plugin does not generate hidden identifiers, cache/dedupe requests, own delegation lifecycle state, or perform daemon discovery. Local validation rejects `delegate.request`, top-level `review`, missing metadata, non-object payloads, and any command outside the closed enum before transport. Structured daemon failures such as `conflict` are preserved in the JSON error envelope.

For `atn_delegate_action`, the top-level `session_id` is authoritative: handlers always overwrite/set `payload.session_id` with that value before submitting the envelope. Remaining payload fields stay opaque for daemon-side validation.

This is fake/injected DELRV-1 readiness only. The tools use `DaemonClient.build_command_envelope(...)` and `submit_command(...)` through an injected client factory; they do not prove live daemon, installed Hermes plugin-load, slash-command, Discord, gateway, auth, token, socket, localhost, or CLI readiness.

## CNDIS-1 council and delivery-evidence command tools

CNDIS-1 adds fake/injected-only Hermes tool schemas for daemon-owned council lifecycle and delivery-evidence command envelopes:

- `atn_council_command` builds and submits a closed enum of exact implemented `council.*` commands: `council.new`, `council.request_attendance`, `council.attend`, `council.lock_agenda`, `council.prepare`, `council.ready`, `council.prepared_partial`, `council.poll`, `council.hand_raise`, `council.grant`, `council.speak`, `council.intervene`, `council.propose`, `council.revise`, `council.request_vote`, `council.vote`, `council.finalize`, and `council.unresolved`.
- `atn_delivery_evidence` builds and submits only `delegate.escalation_delivered` and `delegate.escalation_delivery_failed`. `atn_delegate_action` keeps accepting those commands for DELRV compatibility; `atn_delivery_evidence` is the clearer CNDIS surface.

Both tools require caller-supplied non-empty `request_id` and `idempotency_key`. The plugin does not generate IDs, cache/dedupe, own council lifecycle/consensus state, write logs/locks/cursors, or transition delivery evidence locally. The top-level `session_id` is authoritative and overwrites/sets `payload.session_id` before submit.

Before `command.submit`, `atn_council_command` calls injected `version.read` and requires `council.lifecycle`; `atn_delivery_evidence` requires `delivery_evidence`. Missing feature groups return `compatibility` before submit. Unknown commands, missing IDs, non-object payloads, command-specific missing payload fields, missing or malformed nested `payload.payload.turn`, and legacy nested `payload.payload.round` on turn-bearing `council.poll`/`council.hand_raise`/`council.grant`/`council.speak` payloads return `validation` before the client factory is called or transport is opened.

For explicitly configured live Unix socket transport, `command.submit` is represented as the canonical daemon command in `command` with the original command payload in `params`; structured `council.lock_agenda` payload fields such as `decision_question`, `success_criteria`, and `out_of_scope_policy` are preserved under `params.payload` for daemon authority. The live socket mapping keeps daemon `payload.command_id` as the only daemon command-id authority. It accepts public `idempotency_key` only when it is exactly `payload.command_id` or `idem-{payload.command_id}`; any other value fails closed before socket connect with operator guidance rather than generating a local ID, deduping locally, or falling back to CLI.

This is fake/injected CNDIS readiness only. It does not prove live daemon, installed Hermes plugin-load, slash-command, Discord helper/send_message, gateway, auth, token, socket, localhost, CLI, or KAB readiness.

## RUNFIX-006/RUNFIX-007 discussion activation planner/doctor

RUNFIX-006 added `atn_discussion_activation_plan` as a pure/local Hermes tool.
RUNFIX-007 keeps the same tool surface and extends the dry-run report for
Discord eligibility and bot-to-bot exclusion. ATN-005 keeps the tool public
surface ATN-aligned while preserving historical RUNFIX/control task IDs only as
evidence provenance and dependency labels. The tool builds a deterministic
activation planner/doctor report from explicit caller-provided evidence only.
The input names historical control/RUNFIX dependency evidence, ATN plugin
install/enabled/tool visibility evidence, explicit daemon socket/config and
compatibility evidence, participant profiles, selected Discord parent-channel
proof, planned dry-run changes, rollback steps, verification commands, approval
gates, optional operator blockers, and separated evidence labels. Inputs may use
`plugin/ATN-005` for the ATN evidence-model check; older `plugin/RUNFIX-*` task
IDs remain historical planner behavior selectors, not legacy public tool aliases.

The tool classifies participant profiles into eligible, excluded, and
blocked/unknown lists from explicit `effective_hermes` profile visibility
evidence, with historical `effective_discord`, `tools_visible`, and
`bot_to_bot_enabled` fields still accepted only as input compatibility.
Bot-to-bot-enabled profiles are excluded by default. Unknown or missing profile
eligibility or tool visibility blocks that profile. The report includes
eligible-only `allow_list_targets`, profile remediation, parent-channel proof
state, and a fallback audit rejecting hidden plugin-to-CLI subprocess fallback,
current Hermes/Discord inference, manual profile replies as full ATN success,
daemon startup/discovery, profile/gateway/provider/auth/token/model mutation,
`codex exec`, generic OpenAI SDK, raw app-server transport, and KAB
`native_codex`.

Missing parent-channel allow-list inheritance proof is reported as a
Hermes/gateway dependency blocker, not as a fallback to current-thread messages.
Thread-only, current-channel, or manual profile evidence is not accepted as
parent-channel inheritance proof unless explicit gateway evidence says it covers
parent inheritance.
The five historical evidence labels (`lifecycle_pass`, `fallback_profile_pass`,
`selected_runner_pass`, `visible_surface_pass`, and `discussion_quality_pass`)
remain separate and default to `unproven` unless explicitly supplied.
The ATN-005 report also exposes an activation evidence-model summary that keeps
plugin install/tool visibility, daemon socket/config compatibility, profile/
gateway visibility, visible-surface readiness, selected-runner/runtime proof, and
final live-readiness claim as separate axes.

This planner never proves live readiness. `atn_discussion_activation_plan` always
returns `live_readiness: false` and performs no environment reads, current
Hermes/Discord/profile/gateway inspection, socket discovery, CLI fallback,
daemon startup, Discord send/channel creation, profile/gateway/provider/auth/
token/model mutation, activation apply, or production readiness claim.

## CNDIS-2 injected Discord helper

CNDIS-2 adds `atn_discord_send_message` as a narrow injected-only Hermes tool wrapper over
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
delivery evidence, it must still submit the existing fake/injected `atn_delivery_evidence`
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

Hermes provides a plugin slash-command host API through `PluginContext.register_command(name, handler, description, args_hint)`. ATN plugin slash-command exposure remains unsupported. The plugin manifest must keep `provides_commands: []`, and the root entrypoint must not register command handlers until a later task supplies a concrete slash-command binding contract and isolated verification.

Future ATN slash-command bindings must preserve the same fail-closed boundary as tools: no live daemon discovery, Hermes, Discord, gateway, auth, token, localhost, socket, or CLI fallback unless explicitly designed and tested. A command must have daemon-owned state semantics, fake or conformance fixtures, duplicate/idempotency handling, structured error preservation, argument validation, redaction coverage, manifest declaration, and isolated Hermes/gateway smoke evidence before readiness is claimed.

See `docs/spec/compatibility-and-operations.md` for the operator-facing unsupported-surface matrix and future binding checklist.

---

## Merged from `docs/spec/architecture.md`

# Discord Surface

## Purpose

The plugin may provide a Discord visible surface for ATN council sessions through an
injected Hermes gateway/send_message boundary. Discord is for human-visible
discussion/evidence, not canonical state.

## Rules

- Discord message IDs, channel IDs, and thread IDs are evidence pointers.
- `channel.jsonl` in the control daemon remains the SOT.
- `atn_discord_send_message` is an injected-only helper. It requires a caller-supplied
  `send_message` callable plus an explicit dedicated test target; without the injected
  sender it returns a fail-closed JSON error and does not post.
- The helper does not read environment variables, discover current Hermes sessions,
  inspect active Discord threads, open gateway/socket/CLI connections, or use tokens.
- The plugin records delivery success/failure only through fake/injected
  `atn_delivery_evidence` command submission. Discord message IDs, channel IDs, and
  thread IDs remain evidence pointers; they are not daemon state.
- The daemon must not require raw Discord tokens.
- Free-form Discord replies are never parsed as authoritative lifecycle transitions.
- ATN slash-command invocations are not supported in HPLUG-3/CNDIS-1. Native Discord slash commands may only become supported after a later task proves the Hermes command binding, ATN daemon command contract, delivery-evidence path, and isolated Discord test target.

CNDIS-1 supports council and delivery-evidence command tools through explicit fake/injected daemon clients only. It does not post to Discord, call Hermes gateway/send_message, or infer delivery evidence from live Discord state.

CNDIS-2 adds only the injected helper boundary. It still does not claim live Discord
readiness, active Hermes session delivery, gateway configuration, daemon-recorded evidence,
or ATN/KAB slash-command support.

## Testing

Unit and integration tests use fake gateway/send_message functions. E2E tests default to
`KAN_DISCORD_E2E=0` and no sender, so they cannot post. A live-post path must set all of
the following explicitly:

- `KAN_DISCORD_E2E=1`
- `DISCORD_TEST_TARGET=<dedicated test channel id>`
- `DISCORD_TEST_DEDICATED=1`
- `DISCORD_TEST_CLEANUP_HINT=<operator cleanup instruction>`
- optional `DISCORD_TEST_THREAD=<dedicated test thread id>`
- optional `DISCORD_TEST_LABEL=<visible test label>`; otherwise the helper uses
  `[Kkachi CNDIS-2 isolated E2E]`

Missing opt-in, current/active target labels, non-dedicated targets, missing cleanup
guidance, or missing injected sender all fail closed. Tests must never default to the
active user thread.
