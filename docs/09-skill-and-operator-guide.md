# KAN Skill and Operator Guide

## Scope

SKILL-1 adds a packaged KAN operator skill and this local operator guide for
`kkachi-agent-network-plugin`. The bundled skill lives inside the Python package:

```text
src/kkachi_agent_network_plugin/bundled_skills/kan-plugin/SKILL.md
```

The package also exposes an import-safe resource helper in
`kkachi_agent_network_plugin.bundled_skills` so future installers and tests can
read the bundled skill without writing to a Hermes profile.

SKILL-1 does not install the skill into the user's Hermes profile, enable a live
plugin, run plugin-load smoke, contact a daemon, or modify the sibling control
repo. Plugin-load smoke belongs to SKILL-2 after the real supported install/load
path exists.

## Current plugin capability

The current plugin surface is fake/injected Hermes tools only:

- `kan_daemon_status`
- `kan_compatibility_diagnostics`
- `kan_stream_tail`
- `kan_delegate_new`
- `kan_delegate_action`
- `kan_council_command`
- `kan_delivery_evidence`
- `kan_discord_send_message`

`plugin.yaml` must continue to declare `provides_commands: []`. The root
entrypoint must not register KAN slash commands.

Unsupported in SKILL-1:

- `kan_session_status` or `session.status.read`;
- KAN slash commands through Hermes `register_command`;
- native Discord slash-command registration;
- live daemon discovery or localhost/socket/SSE/WebSocket transport;
- CLI fallback;
- current Hermes session, current Discord thread, gateway, auth, token, or
  credential discovery;
- default/live Discord sending;
- installed-plugin or live Hermes plugin-load readiness claims.

## No-live defaults

Default verification and operator rehearsal are local only:

1. Use fake Hermes contexts, `StaticDaemonTransport`, local conformance fixtures,
   or an explicitly injected Discord sender.
2. Do not read the active Hermes profile, active Discord target, daemon socket,
   localhost service, KAB bridge runtime, gateway state, auth material, or tokens.
3. Do not create plugin-owned lifecycle state, idempotency state, council state,
   logs, locks, cursors, or delivery-evidence transitions.
4. Treat Discord IDs as evidence pointers only. Daemon-owned delivery evidence
   still goes through `kan_delivery_evidence`.

## Install guidance

For SKILL-1, "install" means obtaining the packaged skill artifact from the
Python package. It is not a live profile mutation.

Recommended inspection path:

```python
from kkachi_agent_network_plugin.bundled_skills import read_bundled_skill_text

skill_text = read_bundled_skill_text("kan-plugin")
```

Manual operator install, when a later approved workflow allows profile writes:

1. Build or install the Python package from the reviewed plugin revision.
2. Read the packaged `kan-plugin/SKILL.md` with the import-safe helper.
3. Copy that exact text into the approved Hermes profile skill location.
4. Record the source package version and git revision in the operator change log.
5. Run local verification before making any operator-readiness claim.

Do not use SKILL-1 to write into `/Users/draccoon/.hermes`, discover an active
profile, or enable a live Hermes plugin.

## Enable guidance

For SKILL-1, "enable" means making the packaged skill discoverable in an
approved non-live operator profile or test fixture. Enabling the skill does not
enable new plugin commands or live daemon behavior.

Before enabling, confirm:

- the package imports without runtime integrations;
- `read_bundled_skill_text("kan-plugin")` returns the bundled `SKILL.md`;
- `plugin.yaml` still lists only the supported tool names and
  `provides_commands: []`;
- the operator guide and unsupported-surfaces docs still say fake/injected only;
- local make gates pass.

## Rollback guidance

Rollback is local and reversible:

1. Remove the copied `kan-plugin` skill from the non-live profile or test
   fixture, or restore the previous copied text.
2. Restore the previous plugin package revision/version.
3. Confirm the profile no longer references the SKILL-1 artifact.
4. Rerun local verification.

Do not delete live Hermes state, daemon storage, Discord messages, tokens,
gateway config, sockets, or localhost services as part of SKILL-1 rollback.

## Troubleshooting

| Symptom | Likely cause | Safe response |
| --- | --- | --- |
| Bundled skill cannot be found | Package data missing or wrong resource name | Use `bundled_skill_names()` and `read_bundled_skill_text("kan-plugin")`; verify the package contains `bundled_skills/kan-plugin/SKILL.md`. |
| Skill claims live readiness | Overclaiming docs or stale copied skill | Replace with the bundled SKILL-1 text; SKILL-1 is fake/injected only. |
| Slash commands appear | Manifest or entrypoint drift | Restore `provides_commands: []` and verify the root entrypoint registers no commands. |
| `kan_session_status` appears | Unsupported session-status drift | Remove the surface until `session.status.read` fixture/protocol authority exists. |
| A handler tries localhost, a socket, CLI, gateway, auth, token, Discord, or KAB | No-live boundary violation | Fail closed and remove the fallback; default checks must use explicit fake/injected dependencies only. |
| Plugin-load smoke is requested | SKILL-2 scope | Do not claim it from SKILL-1; wait for the supported install/load path and SKILL-2 evidence. |
| Live-looking environment variables are present | Host shell contamination | Ignore them for default tests; E2E defaults must not target active Hermes or Discord resources. |

## SKILL-2 smoke boundary

SKILL-2 is blocked until the real supported plugin-load/install path and
compatibility evidence are available. A future SKILL-2 smoke test may prove live
Hermes plugin loading only after it has:

- an approved isolated profile/home;
- no access to the current active Hermes session or Discord thread;
- explicit daemon/control compatibility evidence;
- exact expected tool/command registration assertions;
- cleanup and rollback instructions.

Until then, SKILL-1 verification proves only the packaged skill resource,
operator docs, manifest/entrypoint guardrails, and local fake/injected test
contract.
