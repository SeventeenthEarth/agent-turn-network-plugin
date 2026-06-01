# Plugin Architecture

## Components

```text
kkachi-agent-network-plugin/
  plugin.yaml or equivalent manifest
  src/kkachi_agent_network_plugin/
    client/              # Python daemon protocol client
    schemas.py           # Hermes tool schemas
    tools.py             # tool handlers returning JSON strings
    slash_commands/      # optional slash-command wiring
    discord_surface/     # send_message/gateway helper wrappers
    health.py            # daemon compatibility checks
    errors.py            # daemon error rendering
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
Hermes agent tool/slash command
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
- The plugin may shell out to `kkachi-agent-network` only for compatibility fallback or operator-equivalent diagnostics.
- The plugin must pass a compatibility health check before exposing write tools as safe to use.
- Hermes restart/plugin reload must not affect daemon state.

## Hermes plugin surface

The plugin may provide:

- daemon/session status tools;
- delegation and council command tools matching implemented core commands;
- stream/tail/cursor diagnostic tools;
- transcript/export tools;
- slash commands for common operations;
- bundled skill guidance;
- Discord surface helper tools that post visible messages through Hermes gateway/send_message and then record delivery evidence through daemon commands.
