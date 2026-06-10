---
name: kan-plugin
description: Use when operating the packaged kkachi-agent-network-plugin Hermes adapter, explaining its current fake/injected tool surface, or preparing a non-live install/enable/rollback plan.
version: 0.1.0
author: 17번째 지구 Kkachi
license: MIT
metadata:
  hermes:
    tags: [kan-plugin, kkachi, hermes-plugin, operator-guide, no-live]
    related_skills: []
---

# KAN Plugin Operator Skill

Use this skill when an operator or agent needs to work with the packaged
`kkachi-agent-network-plugin` Hermes adapter, explain its current safe surface,
or prepare a non-live install/enable/rollback plan.

## Current capability boundary

This skill is bundled with the Python package as documentation and operator
guidance. It does not install itself into a Hermes profile, enable a live
plugin, discover the current Hermes session, or run a daemon.

Supported plugin surfaces in the current package are fake/injected Hermes tools:

- `kan_daemon_status`
- `kan_compatibility_diagnostics`
- `kan_stream_tail`
- `kan_stream_ack`
- `kan_delegate_new`
- `kan_delegate_action`
- `kan_council_command`
- `kan_selected_participant_response`
- `kan_delivery_evidence`
- `kan_discord_send_message`

The plugin manifest must continue to declare `provides_commands: []`. KAN slash
commands, native Discord slash commands, `kan_session_status`, live daemon
discovery, localhost/socket/SSE/WebSocket transports, CLI fallback, gateway auth,
token access, current-session lookup, production activation, KAB readiness, and
live plugin readiness are unsupported in SKILL-2. The only plugin-load claim is
local isolated plugin-load smoke.

## No-live defaults

Default work must stay local and fake/injected only:

1. Use local tests, fake Hermes contexts, `StaticDaemonTransport`, or explicit
   injected senders.
2. Do not contact Hermes, Discord, a daemon, gateway, auth, token, socket,
   localhost, network, KAB bridge runtime, or the sibling control repo as a
   mutable target.
3. Do not create plugin-owned lifecycle, idempotency, council, delivery-evidence,
   or Discord state. The control daemon remains the source of truth.
4. Treat Discord IDs as evidence pointers only; delivery evidence still belongs
   to daemon-owned command envelopes.

## Operator workflow

1. Inspect `plugin.yaml` and confirm the tool list plus
   `provides_commands: []`.
2. Read `docs/09-skill-and-operator-guide.md` for install, enable, rollback,
   troubleshooting, and the SKILL-2 local isolated plugin-load smoke boundary.
3. Run local verification before claiming the packaged skill/docs are usable:

   ```bash
   HOME=/Users/draccoon make test-prepare
   HOME=/Users/draccoon make check-plugin-load-smoke
   HOME=/Users/draccoon make check-core-contract
   HOME=/Users/draccoon make test
   ```

4. If any command fails, report the exact command and reason. Do not claim live
   readiness, production activation, KAB readiness, or live plugin readiness
   from these local checks.

## Troubleshooting prompts

- Missing bundled skill: verify package data under
  `kkachi_agent_network_plugin/bundled_skills/kan-plugin/SKILL.md` and use the
  import-safe resource helper instead of profile writes.
- Unexpected slash commands: inspect the manifest and root entrypoint; the
  expected command surface is empty.
- Live-looking environment variables: ignore them for default verification.
  Tests must not fall back to the current Hermes/Discord/daemon environment.
- Session status requests: keep `kan_session_status` deferred until the control
  contract publishes `session.status.read` fixture/protocol authority.
- Plugin-load smoke requests: run `make check-plugin-load-smoke` and describe
  the result only as local isolated plugin-load smoke.

## Rollback guidance

Rollback is local and reversible: remove the copied skill file or disable the
profile entry that points at it, restore the previous plugin package version, and
rerun the local make gates. Do not delete live Hermes state or modify daemon
storage as part of SKILL-2 rollback.
