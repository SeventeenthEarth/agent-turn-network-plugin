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
    schemas.py           # future Hermes tool schemas
    tools.py             # future tool handlers returning JSON strings
    slash_commands/      # future optional slash-command wiring
    discord_surface/     # future send_message/gateway helper wrappers
    health.py            # future live daemon compatibility checks
  skills/kkachi-agent-network/SKILL.md
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

Future Hermes agent tool/slash command
  -> plugin handler
    -> Python KAN daemon client
      -> kkachi-agent-networkd protocol endpoint
        -> daemon validates and appends typed event
      <- structured success/error
    -> plugin renders JSON/tool response
```

## Boundary rules

- The plugin calls the daemon protocol; it does not write core storage files.
- The plugin returns daemon errors as authoritative failures.
- DAEMN-2 has no shell, localhost, Hermes, Discord, KAB, auth, token, or gateway fallback; callers must inject a transport explicitly.
- Stream tail reads first require positive `stream_frame` feature-group evidence from the injected transport before the `stream.tail` operation is attempted.
- The plugin must pass a compatibility health check before exposing any future write tools as safe to use.
- Hermes restart/plugin reload must not affect daemon state.

## Hermes plugin surface

The plugin currently registers no Hermes tools or hooks. Later tasks may provide:

- daemon/session status tools;
- delegation and council command tools matching implemented core commands;
- stream/tail/cursor diagnostic tools;
- transcript/export tools;
- slash commands for common operations;
- bundled skill guidance;
- Discord surface helper tools that post visible messages through Hermes gateway/send_message and then record delivery evidence through daemon commands.
