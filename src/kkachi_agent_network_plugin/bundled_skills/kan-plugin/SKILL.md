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
   For Discord-origin council requests, assume the operator expects
   `live_visible_thread` output unless they explicitly confirm `artifact_only`,
   `daemon_cli_actor_speech`, transcript-only, or export-only mode before
   `council.new`. Do not quietly downgrade a Discord thread request to daemon
   CLI actor speech or transcript/export artifacts.
7. Treat ARGUE argument-graph support as static/fake/injected schema and tool
   contract coverage only. The plugin preserves explicit `claims[]`,
   `stance_links[]`, `contribution_type`, `new_axis_reason`, `evidence[]`, and
   `hand_raise.target_links[]` fields for daemon/control validation.
   `responds_to_event_id` remains a legacy display hint and never overrides
   `stance_links[]`.

## KAN council moderation hard rules

For any live KAN council, the moderator must preserve the daemon-governed
council loop. These rules are hard guardrails for operator guidance; they do not
authorize live daemon/runtime activation by themselves.

1. Do not predeclare or hard-code a complete live speaker order. A visible
   discussion must not become a fixed-order Discord/Hermes debate transcript.
2. Complete lifecycle prerequisites before turn discussion: `council.new`,
   `request_attendance`, terminal attendance records for required participants,
   `lock_agenda`, `prepare`, then `ready` or `prepared_partial` evidence.
3. For each turn, open a `poll` or hand-raise evaluation, evaluate the current
   hand raises, and record a justified daemon `speaker_selected` event before
   any participant speech.
4. Use `relevance` as the default selection mode. `targeted`, `random`,
   `moderator_direct`, and `role_order` remain valid only as per-turn
   `speaker_selected` selection modes with a reason; `role_order` also needs
   bounded round evidence. Do not ban `role_order`, but never use it as a
   predeclared full live debate order.
5. Discord/Hermes replies are not council state. They become council speech only
   when backed by typed daemon `speech` events.
6. If the moderator has a substantive opinion, record it as a participant-style
   turn rather than hiding it inside moderation text.
7. If a fixed-order flow starts by mistake before any `speech` event exists,
   cancel and restart. If `speech` already exists, repair forward with a
   moderator intervention and do not rewrite history.

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

Participant response template:

```json
{
  "speech": "Visible participant answer only; no wrapper logs or role-substitution text.",
  "claims": [
    {
      "claim_id": "T03.C1",
      "summary": "Canonical speech linkage is required before pilot acceptance.",
      "kind": "requirement"
    }
  ],
  "stance_links": [
    {
      "target_event_id": "evt_speech_T01",
      "target_claim_id": "T01.C1",
      "stance": "support",
      "rationale": "This preserves the prior traceability requirement."
    }
  ],
  "contribution_type": "support",
  "new_axis_reason": null,
  "evidence": [
    {
      "kind": "runner_log",
      "ref": "runner evidence pointer"
    }
  ]
}
```

`speech` is the only human-visible answer text. `claims[]`,
`stance_links[]`, `contribution_type`, `new_axis_reason`, and optional
`evidence[]` are structured evidence fields. Do not substitute a simulated role
prompt, fallback/manual reply, wrapper summary, or current Discord/Hermes
message for a selected participant response.

Mechanical lifecycle pass means the local daemon/CLI/plugin path completed with
replayable events and evidence pointers. Discussion-quality pass additionally
requires grounded relation evidence, visible relation summaries from
`kan_surface_render_projection`, audit relation fields preserved in rows/logs,
non-immediate prior-claim engagement, challenge/refine/synthesize coverage where
relevant, and no runtime noise in visible speech.


## RUNFIX post-pilot guardrails (planned RUNFIX-014..017)

주유's 2026-06-19 rename-council handoff is registered as `RUNFIX-014` through `RUNFIX-017`. Until those tasks are implemented and reviewed, operators must treat the following as required planning/acceptance boundaries, not completed runtime capability:

1. `control/RUNFIX-014` selected-runner accounting: a run with `runner_invocation_failed` followed by later canonical `speech` is lifecycle/fallback evidence, not `selected_runner_pass`. Reports must expose runner started/succeeded/failed counts and fallback/manual harness flags.
2. `plugin/RUNFIX-015` visible author guard: before `council.new`, same-path Discord author probes must prove each selected participant posts as the expected profile author. Evidence includes `profile`, expected author source (`registry_snapshot` or explicit approved profile-author map), `bot_id`, `username`, `source_env`, `posting_path`, per-turn Discord message id, selected member, profile author id, and `speech_event_id`. Shared/default or unexpected authors fail closed.
3. `control/RUNFIX-016` summary robustness: closeout/summary tooling must tolerate `payload.plugin_evidence`, dict/list `payload.evidence`, and missing optional evidence. A finalized lifecycle must not look failed because optional evidence has an alternate shape.
4. `plugin/RUNFIX-017` ARGUE quality-required prompts: non-opening quality-required speeches must link to prior claims through `stance_links[]` or justify `new_axis`; prompts should provide compact prior claim graph targets; in `quality_required`, the first orphan non-opening speech blocks `discussion_quality_pass`; warning-only behavior is reserved for `quality_warn`, and repeated-orphan counts remain diagnostic evidence.

Final reports must keep these fields separate: `lifecycle_pass`, `selected_runner_pass`, `visible_surface_pass`, `fallback_profile_pass`, `discussion_quality_pass`, `orphan_speech_count`, `linked_speech_count`, `stance_link_count`, `new_axis_count`, Discord visible turns posted, real profile/gateway replies, and shared/default author fallback status.

## Live-visible council preflight

When the request arrives in Discord and the user asks agents to "discuss" or run
a council, default to live visible thread output. Before creating the session,
distinguish the mode in the task brief:

- `live_visible_thread`: selected-speaker/profile-send or approved fallback
  poster path will post each turn to the Discord thread or disclosed
  parent-channel fallback;
- `daemon_cli_actor_speech`: lifecycle/evidence-only actor speech; Discord
  turn-by-turn visibility is not guaranteed;
- `artifact_only`: transcript/export artifacts only.

If `live_visible_thread` cannot be proven, fail closed before session creation
instead of silently running artifact-only. Required preflight evidence:

- Discord thread id, or approved parent-channel fallback with `fallback_reason`;
- turn-posting probe for selected-speaker/profile-send or the approved fallback
  poster;
- visible closeout probe;
- `real_profile_gateway_replies: true`;
- `cli_actor_speech_only: false`.

Final reports must not equate transcript/export success with a visible Discord
discussion. Report these fields separately: `KAN lifecycle finalized`,
`Discord visible turns posted: N/expected`, `real profile/gateway replies`, and
`CLI actor speech only`.

## RUNFIX visible pilot guidance

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
caller-provided evidence, classifies profiles from effective Discord evidence,
excludes bot-to-bot-enabled profiles by default, blocks unknown tool visibility
or eligibility, emits eligible-only `allow_list_targets`, profile remediation,
parent-channel proof state, and fallback-audit rejection rows, treats missing
parent-channel allow-list inheritance proof as a Hermes/gateway dependency,
keeps RUNFIX labels separate, and always keeps `live_readiness: false`.

For `plugin/RUNFIX-012`, the planner also consumes explicit
`participant_runtime_readiness` from `control/RUNFIX-011` diagnostics. Required
classes are control task/status/evidence ref, subscriber presence, cursor ack
freshness, heartbeat freshness, attendance and preparation terminal evidence,
selected-runner readiness/prerequisites, and visible-surface proof as a separate
class. Gateway liveness, transcript/export artifacts, parent-channel fallback
alone, and manual/fallback profile text are diagnostic only; they are not
participant runtime readiness, selected-runner success, live readiness, or
production readiness.

KAN discussion channels are bot-to-bot-free by default. Profiles with effective
bot-to-bot enabled Discord behavior are excluded from KAN discussion allow-lists
unless a later explicit policy approves otherwise. Visible-pilot surface policy
is thread-preferred and parent-channel fallback allowed: first create or use a
dedicated thread under the approved parent channel, then fall back to the parent
channel only when thread creation/posting is unsupported. If the fallback is
used, record the fallback reason in the task brief, KAN surface metadata,
visible closeout, and final report; do not silently normalize channel-only
operation or treat it as no-restart thread readiness.

Reports must label fallback/manual profile evidence as `fallback_profile_pass`.
That evidence never equals selected-speaker runner success or KAN live discussion
readiness. Minimum readiness evidence remains approval-gated: selected-runner
invocation from `speaker_selected`, selected-runner submitted canonical `speech`
linkage, visible-surface evidence, ARGUE relation counts/diagnostics, and explicit
production/non-scope disclaimers. Durable runner failure is a terminal-failure
diagnostic and blocks `selected_runner_pass` / live-readiness claims unless a
later task explicitly proves a new selected-runner success path.

For `plugin/RUNFIX-008`, `kan_discussion_activation_plan` exposes an
`operator_evidence_report` from explicit caller-provided `operator_evidence`
only. The report includes runner evidence, canonical
`speaker_selected -> speech linkage`, participant response fields, ARGUE counts,
RUNFIX labels, and fallback disclosure. Missing or ambiguous runner, ARGUE, or
canonical-link evidence remains `unproven`/`blocked`; fallback/manual profile
text is diagnostic-only and never full KAN success.

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
