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
- `kan_surface_render_projection`
- `kan_discussion_activation_plan`
- `kan_discord_send_message`

The plugin manifest must continue to declare `provides_commands: []`. KAN slash
commands, native Discord slash commands, `kan_session_status`, live daemon
discovery, localhost/socket/SSE/WebSocket transports, CLI fallback, gateway auth,
token access, current-session lookup, production activation, KAB readiness, and
live plugin readiness are unsupported. The only plugin-load claim is local
isolated plugin-load smoke.

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
5. Treat `kan_surface_render_projection` output as a local display projection
   over explicit daemon/control event JSON, never as lifecycle authority. Use
   `visible_transcript` for operator-facing discussion text and keep raw
   cursor/event details in `audit_log`/`rows` evidence.
6. Treat `kan_discussion_activation_plan` output as a dry-run planner/doctor
   report only. It can prepare an approval-gated activation plan from explicit
   evidence, but it never proves live readiness.
7. Treat ARGUE argument-graph support as static/fake/injected schema and tool
   contract coverage only. The plugin preserves explicit `claims[]`,
   `stance_links[]`, `contribution_type`, `new_axis_reason`, `evidence[]`, and
   `hand_raise.target_links[]` fields for daemon/control validation.
   `responds_to_event_id` remains a legacy display hint and never overrides
   `stance_links[]`.

## ARGUE relation-aware response guidance

ARGUE relation evidence is the structured record that links a participant's
visible speech to the council claim graph. In quality-required rehearsal or
pilot evidence, a selected participant response should keep these parts
separate:

- `speech`: the human-visible answer only, with no runtime warnings, wrapper
  logs, max-iteration notices, or tool diagnostics rewritten as participant
  speech;
- `claims[]`: one or more concise claims introduced or restated by the
  participant;
- `stance_links[]`: explicit links from each new claim to prior claim/event ids,
  using relation types such as support, challenge, refine, or synthesize;
- `contribution_type`: the primary contribution category, including support,
  challenge, refine, synthesize, risk_addition, decision_frame, or new_axis;
- `new_axis_reason`: required when `contribution_type` is `new_axis`, and only
  appropriate when the participant is opening a necessary new line of argument;
- `evidence[]`: source or observation pointers outside visible speech text when
  the participant cites evidence.

Operators should flag a non-opening speech as orphaned when it has neither a
valid `stance_links[]` entry to the prior claim graph nor a valid `new_axis`
reason. Repeated ungrounded `new_axis` contributions are a discussion-quality
warning even if the mechanical daemon/CLI/plugin lifecycle completes.

Mechanical lifecycle pass means the local daemon/CLI/plugin path completed with
replayable events and evidence pointers. Discussion-quality pass additionally
requires grounded relation evidence, visible relation summaries from
`kan_surface_render_projection`, audit relation fields preserved in rows/logs,
non-immediate prior-claim engagement, challenge/refine/synthesize coverage where
relevant, and no runtime noise in visible speech.

Control/daemon fixtures and validation remain authoritative. Plugin rendering is
a local visible surface and evidence pointer, not lifecycle state. Live-local
pilots still require explicit profile/plugin/daemon/gateway/Discord approval and
evidence. KAS does not install, own, or activate KAN runtime/plugin/bundled-skill
artifacts.

## RUNFIX discussion activation guidance

`RUNFIX` work separates plugin install/load from KAN discussion activation. A plugin
install does not prove live council readiness. Before any live-local discussion
apply step, produce a dry-run activation plan with: explicit control daemon/socket
or config evidence, participant profiles, selected Discord parent channel,
eligible/excluded profile list, planned allow-list/config changes, rollback,
smoke checks, and the exact approval boundary.

Use `kan_discussion_activation_plan` for that planning/doctor report when a
structured tool surface is available. The tool consumes only explicit
caller-provided evidence, excludes bot-to-bot-enabled profiles by default,
blocks unknown tool visibility or eligibility, treats missing parent-channel
allow-list inheritance proof as a Hermes/gateway dependency, keeps RUNFIX labels
separate, and always keeps `live_readiness: false`.

KAN discussion channels are bot-to-bot-free by default. Profiles with effective
bot-to-bot enabled Discord behavior are excluded from KAN discussion allow-lists
unless a later explicit policy approves otherwise. If parent-channel allow-list
inheritance cannot be proven for new threads, stop with a gateway limitation and
do not claim no-restart thread readiness.

Reports must label fallback/manual profile evidence as `fallback_profile_pass`.
That evidence never equals selected-speaker runner success or KAN live discussion
readiness. Minimum readiness evidence remains approval-gated: selected-runner
invocation or durable failure from `speaker_selected`, canonical `speech` linkage,
visible-surface evidence, ARGUE relation counts/diagnostics, and explicit
production/non-scope disclaimers.

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
- ARGUE overclaims: do not describe local ARGUE schema/tool coverage or local
  visible relation rendering as runtime scoring, live Discord, production
  activation, live pilot readiness, or daemon/control validation authority.
- Plugin-load smoke requests: run `make check-plugin-load-smoke` and describe
  the result only as local isolated plugin-load smoke.

## Rollback guidance

Rollback is local and reversible: remove the copied skill file or disable the
profile entry that points at it, restore the previous plugin package version, and
rerun the local make gates. Do not delete live Hermes state or modify daemon
storage as part of SKILL-2 rollback.
