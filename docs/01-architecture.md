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
- live transport according to `docs/10-live-transport-sot.md`, where the CLI is the main-agent control plane, the plugin is the participant-agent ATN client surface, member runtimes invoke real participant profiles, the daemon remains the only event/state authority, and companion control `LTRAN` / `MEMBR` / `SURFD` epics must complete before the matching plugin epics start;
- ATN slash commands for common operations after control command contracts, conformance fixtures, safe handlers, manifest entries, and isolated Hermes/gateway smoke tests exist;
- bundled skill guidance;
- live Discord helper wiring that posts visible messages through a dedicated Hermes
  gateway/send_message configuration and separately records delivery evidence through
  daemon commands.

Hermes host support is not the blocker: `PluginContext.register_command()` can register plugin slash commands. The plugin still keeps `provides_commands: []` because DELRV-1 is a Hermes tool surface, not a slash-command binding; future slash commands need separate daemon-owned command semantics and isolated fail-closed tests.
