# Plugin Architecture

## Components

```text
kkachi-agent-network-plugin/
  plugin.yaml or equivalent manifest
  src/kkachi_agent_network_plugin/
    protocol.py          # protocol constants, models, canonical envelopes
    errors.py            # structured daemon error decoding/redaction
    conformance.py       # conformance manifest guard
    client/              # explicit fake/injected daemon transport client
      stream.py          # stream frame / NDJSON / tail-response parser
      diagnostics.py     # diagnostics response decoder/redactor
    schemas.py           # fake/injected Hermes tool schemas
    tools.py             # JSON-string tool handlers
    slash_commands/      # future optional KAN slash-command wiring; unsupported
    discord_surface/     # future send_message/gateway helper wrappers
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
  -> Python KAN daemon client
    -> status/version parser, command envelope serializer,
       stream tail parser, or diagnostics decoder
    <- structured success/error/stream/diagnostics fixture

HPLUG-2 Hermes read-only tool
  -> plugin handler
    -> explicit fake/injected Python KAN daemon client
      -> status.read, diagnostics.read, or version.read + stream.tail fake transport operation
      <- structured success/error/diagnostics/stream fixture
    -> plugin renders JSON-string success or fail-closed error

DELRV-1 Hermes command-envelope tool
  -> plugin handler
    -> explicit fake/injected Python KAN daemon client
      -> command.submit fake transport operation
      <- structured success/error
    -> plugin renders JSON-string success or fail-closed error
```

## Boundary rules

- The plugin calls the daemon protocol; it does not write control storage files.
- The plugin returns daemon errors as authoritative failures.
- Handlers have no shell, localhost, Hermes, Discord, KAB, auth, token, gateway, or CLI fallback; callers must inject a client factory explicitly for success paths.
- Stream tail reads first require positive `stream_frame` feature-group evidence from the injected transport before the `stream.tail` operation is attempted.
- The plugin must pass a compatibility health check before exposing any future write tools as safe to use.
- Hermes restart/plugin reload must not affect daemon state.

## Hermes plugin surface

The plugin currently registers five fake/injected Hermes tools and no hooks or KAN slash commands:

- `kan_daemon_status` — fake/injected daemon status read;
- `kan_compatibility_diagnostics` — fake/injected diagnostics read with redaction;
- `kan_stream_tail` — fake/injected retained stream tail read that requires positive `stream_frame` compatibility before `stream.tail`.
- `kan_delegate_new` — fake/injected `delegate.new` command-envelope submission with caller-supplied request/idempotency metadata;
- `kan_delegate_action` — fake/injected closed-enum `delegate.*` action/review/delivery command-envelope submission. Its top-level `session_id` overrides/sets `payload.session_id` before submit.

Later tasks may provide:

- `kan_session_status` after control `session.status.read` fixture/protocol authority exists;
- council command tools matching implemented control commands;
- cursor/session diagnostic tools;
- transcript/export tools;
- KAN slash commands for common operations after control command contracts, conformance fixtures, safe handlers, manifest entries, and isolated Hermes/gateway smoke tests exist;
- bundled skill guidance;
- Discord surface helper tools that post visible messages through Hermes gateway/send_message and then record delivery evidence through daemon commands.

Hermes host support is not the blocker: `PluginContext.register_command()` can register plugin slash commands. The plugin still keeps `provides_commands: []` because DELRV-1 is a Hermes tool surface, not a slash-command binding; future slash commands need separate daemon-owned command semantics and isolated fail-closed tests.
