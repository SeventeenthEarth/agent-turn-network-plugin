# Unsupported Hermes Surfaces

## Purpose

This document records the current unsupported Hermes surfaces for `kkachi-agent-network-plugin` so operators do not confuse host capability with KAN plugin readiness.

Hermes currently provides a real plugin slash-command host API through `PluginContext.register_command(name, handler, description, args_hint)`. The KAN plugin still exposes no KAN slash commands. Its manifest must continue to declare `provides_commands: []` until a later task implements and verifies concrete slash-command handlers.

## Current KAN plugin exposure

Supported now:

- `kan_daemon_status` — read-only fake/injected daemon status tool.
- `kan_compatibility_diagnostics` — read-only fake/injected diagnostics tool with redaction.
- `kan_stream_tail` — read-only fake/injected retained stream tail tool with `stream_frame` pre-probe.
- `kan_delegate_new` — fake/injected `delegate.new` command-envelope submission tool with caller-supplied request/idempotency metadata.
- `kan_delegate_action` — fake/injected closed-enum `delegate.*` action/review/delivery command-envelope submission tool.
- `kan_council_command` — fake/injected closed-enum `council.*` lifecycle command-envelope submission tool with `council.lifecycle` pre-probe.
- `kan_delivery_evidence` — fake/injected closed-enum delivery-evidence command-envelope submission tool with `delivery_evidence` pre-probe.
- `kan_discord_send_message` — fake/injected Discord helper tool that requires an
  injected sender and dedicated test target; it returns Discord IDs only as evidence
  pointers and fails closed by default.

Unsupported now:

- KAN slash commands through `ctx.register_command`.
- Native Discord slash-command registration for KAN operations.
- Additional write-capable KAN tools beyond the DELRV-1/CNDIS-1 fake/injected command-envelope tools and the CNDIS-2 injected-only Discord helper.
- `kan_session_status` and any `session.status.read` surface.
- Live daemon discovery, localhost/socket/SSE/WebSocket transport, or CLI fallback.
- Default/live Hermes gateway/send_message delivery helpers, current-session/current-thread
  fallback, or Discord helper behavior that claims daemon-recorded evidence.
- Any Discord helper path that reads tokens, auth, gateway, credential, localhost, socket,
  CLI, current Hermes, or active user-thread state.
- Live Hermes plugin-load readiness, production activation, KAB readiness, or any
  claim broader than local isolated plugin-load smoke.

## Host capability versus plugin readiness

Hermes host evidence:

- `hermes_cli/plugins.py::PluginContext.register_command` can register in-session plugin slash commands for CLI and gateway sessions.
- Plugin command names are normalized, built-in command conflicts are rejected, and handlers receive raw argument strings.
- `hermes_cli/commands.py::COMMAND_REGISTRY` remains the built-in slash-command SOT.

KAN plugin readiness boundary:

- The plugin does not register slash commands; DELRV-1/CNDIS-1 command-envelope tools are Hermes tools, not slash-command bindings.
- The plugin is not installed/enabled as a live Hermes plugin in the active environment, so no live plugin command claim is valid.
- Free-form Discord replies or slash invocations must not become authoritative lifecycle transitions; daemon events remain the SOT.
- `kan_discord_send_message` does not change daemon evidence. Delivery evidence remains
  daemon-owned through `kan_delivery_evidence`; Discord IDs are evidence pointers only.

## Future binding requirements

Before a KAN slash command can be added, a later task must provide all of the following evidence:

1. A concrete command name and no-conflict mapping against Hermes built-ins.
2. A daemon-owned operation or CLI-equivalent command in the control KAN contract.
3. Fake or conformance fixtures for success, validation failure, duplicate/idempotent request, permission or compatibility failure, and malformed daemon payloads.
4. A fail-closed handler that returns a safe string/JSON response and never turns daemon failure into success.
5. No live daemon, Hermes, Discord, gateway, auth, token, localhost, socket, or CLI fallback unless that fallback is explicitly designed, approved, and tested.
6. Manifest update from `provides_commands: []` to the exact command names.
7. Unit and integration coverage for registration, dispatch, argument validation, conflict behavior, and redaction.
8. Isolated Hermes/gateway E2E coverage before any live plugin-load or Discord command readiness claim.

## Non-goals for HPLUG-3

HPLUG-3 is documentation only. It does not add command handlers, alter plugin registration code, change Hermes core, change KAN daemon/control behavior, or claim live install readiness.
