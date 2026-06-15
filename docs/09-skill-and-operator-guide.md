# KAN Skill and Operator Guide

## Scope

The packaged KAN operator skill and local compatibility matrix remain the
operator-facing guide for `kkachi-agent-network-plugin`. The bundled skill lives
inside the Python package:

```text
src/kkachi_agent_network_plugin/bundled_skills/kan-plugin/SKILL.md
```

The package also exposes an import-safe resource helper in
`kkachi_agent_network_plugin.bundled_skills` so tests and installer checks can
read the bundled skill without writing to a Hermes profile.

This guide does not install the skill into the user's Hermes profile, enable a live
plugin, contact a daemon, modify the sibling control repo, or prove production
activation, KAB readiness, live plugin readiness, or live Discord readiness. The
smoke claim is exactly local isolated plugin-load smoke.

## Current plugin capability

The current plugin surface is fake/injected Hermes tools only:

- `kan_daemon_status`
- `kan_compatibility_diagnostics`
- `kan_stream_tail`
- `kan_stream_ack`
- `kan_delegate_new`
- `kan_delegate_action`
- `kan_council_command`
- `kan_selected_participant_response`
- `kan_delivery_evidence`
- `kan_surface_render_projection`
- `kan_discord_send_message`

`plugin.yaml` must continue to declare `provides_commands: []`. The root
entrypoint must not register KAN slash commands.

Unsupported in SKILL-2:

- `kan_session_status` or `session.status.read`;
- KAN slash commands through Hermes `register_command`;
- native Discord slash-command registration;
- live daemon discovery or localhost/socket/SSE/WebSocket transport;
- CLI fallback;
- current Hermes session, current Discord thread, gateway, auth, token, or
  credential discovery;
- default/live Discord sending;
- production activation, KAB readiness, live plugin readiness, or live Hermes
  plugin-load readiness claims.

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
5. Treat `kan_surface_render_projection` output as a local projection over
   explicit daemon/control event JSON, not lifecycle authority. Use
   `visible_transcript` for operator-facing discussion text and keep raw
   cursor/event details in `audit_log`/`rows` evidence.
6. Treat ARGUE argument-graph support as static/fake/injected schema and tool
   contract coverage only. `claims[]`, `stance_links[]`, `contribution_type`,
   `new_axis_reason`, `evidence[]`, and `hand_raise.target_links[]` are
   preserved for daemon/control validation, while `responds_to_event_id` remains
   a legacy display hint that never overrides `stance_links[]`.

## Install guidance

For SKILL-2, "install" means obtaining the packaged skill artifact from the
Python package or staging the repository plugin files in a disposable local
fixture. It is not a live profile mutation.

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

Do not use SKILL-2 to write into `/Users/draccoon/.hermes`, discover an active
profile, or enable a live Hermes plugin.

## Enable guidance

For SKILL-2, "enable" means making the packaged skill or plugin fixture
discoverable in an approved non-live operator profile or local test fixture.
Enabling the skill does not enable new plugin commands or live daemon behavior.

Before enabling, confirm:

- the package imports without runtime integrations;
- the root directory-plugin entrypoint loads from the staged repository without
  external `PYTHONPATH=<plugin>/src` help;
- `read_bundled_skill_text("kan-plugin")` returns the bundled `SKILL.md`;
- `plugin.yaml` still lists only the supported tool names and
  `provides_commands: []`;
- the operator guide and unsupported-surfaces docs still say fake/injected only;
- `make check-plugin-load-smoke` passes as local isolated plugin-load smoke only;
- local make gates pass.

## Rollback guidance

Rollback is local and reversible:

1. Remove the copied `kan-plugin` skill from the non-live profile or test
   fixture, or restore the previous copied text.
2. Restore the previous plugin package revision/version.
3. Confirm the profile no longer references the copied skill artifact.
4. Rerun local verification.

Do not delete live Hermes state, daemon storage, Discord messages, tokens,
gateway config, sockets, or localhost services as part of SKILL-2 rollback.

## Troubleshooting

| Symptom | Likely cause | Safe response |
| --- | --- | --- |
| Bundled skill cannot be found | Package data missing or wrong resource name | Use `bundled_skill_names()` and `read_bundled_skill_text("kan-plugin")`; verify the package contains `bundled_skills/kan-plugin/SKILL.md`. |
| Skill claims live readiness | Overclaiming docs or stale copied skill | Replace with the bundled skill text; SKILL-2 is fake/injected plus local isolated plugin-load smoke only. |
| Slash commands appear | Manifest or entrypoint drift | Restore `provides_commands: []` and verify the root entrypoint registers no commands. |
| `kan_session_status` appears | Unsupported session-status drift | Remove the surface until `session.status.read` fixture/protocol authority exists. |
| ARGUE fields are dropped or inferred from legacy pointers | Contract drift or hidden state inference | Preserve explicit argument-graph fields verbatim and treat `responds_to_event_id` as display-only; do not infer state from Discord/Hermes order. |
| ARGUE support is described as runtime scoring or live pilot readiness | Scope overclaim | Keep the claim to static/fake/injected schema and tool contract coverage; runtime validation/scoring, visible relation rendering, and live pilot work remain later tasks. |
| A handler tries localhost, a socket, CLI, gateway, auth, token, Discord, or KAB | No-live boundary violation | Fail closed and remove the fallback; default checks must use explicit fake/injected dependencies only. |
| Root plugin load fails with `No module named 'kkachi_agent_network_plugin'` | The directory entrypoint is not bootstrapping its bundled `src/` package path | Restore the root entrypoint path bootstrap and rerun `make check-plugin-load-smoke`; do not require operators to supply external `PYTHONPATH`. |
| Hermes Python 3.11 reports `invalid syntax` in package modules | Python 3.12-only syntax drift | Keep package/tooling metadata at Python `>=3.11`, avoid PEP 695 `type` aliases, and rerun the Python 3.11 syntax compatibility unit test. |
| Local isolated plugin-load smoke fails | Manifest, entrypoint, packaging, bundled skill, or fail-closed handler drift | Run `make check-plugin-load-smoke`, inspect the first mismatch, and restore exact tool order, zero hooks, zero commands, package inclusion, or handler JSON-string fail-closed behavior. |
| Live plugin-load readiness is requested | Out of SKILL-2 scope | Do not upgrade local isolated plugin-load smoke into a live Hermes/plugin/KAB readiness claim. |
| Live-looking environment variables are present | Host shell contamination | Ignore them for default tests; E2E defaults must not target active Hermes or Discord resources. |

## SKILL-2 smoke boundary

`make check-plugin-load-smoke` is the SKILL-2 local isolated plugin-load smoke
gate, strengthened by REL-PILOT-FIX-001. It creates a temporary plugin home from
repository-local files, loads the root `register(ctx)` entrypoint with a fake
Hermes context without adding external `PYTHONPATH=<plugin>/src` help, asserts
the exact manifest-declared tools in order, asserts no hooks or commands, calls
representative handlers without injected clients/senders and requires JSON
`ok:false`, verifies that live-looking environment variables do not change
behavior, rejects command overclaims, and checks wheel package plus bundled skill
compatibility.

This covers only local isolated plugin-load smoke. It does not prove production
activation, live plugin readiness, KAB readiness, live daemon discovery,
live/default Discord sending, a live Hermes profile install, or any
`provides_commands: []` change.
