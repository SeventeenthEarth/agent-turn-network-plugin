---
name: kan-moderator
description: "Use when acting as a KAN council moderator/operator: create and advance daemon-owned council lifecycle, select speakers, enforce visible-surface and ARGUE quality gates, and report evidence without substituting Discord/Hermes chat for council state."
version: 0.1.0
author: 17번째 지구 Kkachi
license: MIT
metadata:
  hermes:
    tags: [kan, kkachi-agent-network, moderator, council, live-visible, argue]
    related_skills: [kan-plugin]
---

# KAN Moderator Skill

Use this skill when you are the moderator/operator for a KAN council or live-visible discussion. This is a role-focused companion to the canonical KAN discussion/operator skill `kan-plugin`.

## Authority and boundary

- Canonical KAN discussion/operator source: `kkachi-agent-network-plugin/src/kkachi_agent_network_plugin/bundled_skills/kan-plugin/SKILL.md`.
- KAN control daemon remains lifecycle, event, stream, cursor, lock, and state authority.
- Plugin tools are typed client surfaces. They must not own lifecycle state, logs, locks, consensus, cursors, idempotency, Discord state, or fallback discovery.
- Discord/Hermes messages are visible/evidence surfaces only. They become council state only when backed by daemon-owned typed events.
- Do not claim production readiness, broad rollout, provider/profile/gateway/auth/token mutation, or live Discord readiness unless the current task explicitly approves that exact scope and evidence exists.

## Moderator preflight

Before `council.new` or any visible council run, separate preflight findings into three categories:

1. `start_blocker`: blocks `council.new`.
2. `runtime_evidence_pending`: does not block `council.new`; collect it during attendance, preparation, poll/hand-raise, selected-runner, speech, visible delivery, and closeout.
3. `final_acceptance_unproven`: does not block `council.new`; report it as a separated closeout label after the run.

Discord-origin discussion requests default to `live_visible_thread`; artifact-only, transcript-only, export-only, or daemon CLI actor speech still requires explicit pre-session confirmation. Do not silently downgrade a Discord request, but do not require final pilot-acceptance proof before starting the council.

Only `start_blocker` findings block `council.new`. Treat these as start blockers:

- daemon/protocol/tool surface is unavailable;
- approved roster is missing, invalid, or has unresolved principals;
- the selected moderator or required participants are absent from the loaded daemon registry and no unambiguous control-owned reconcile is available;
- participant profile/plugin tool surface is explicitly unavailable;
- target Discord surface is unspecified;
- effective bot-to-bot or shared/default-author risk is positively detected and not approved;
- proceeding requires provider/profile/gateway/auth/token mutation without explicit approval.

Treat these as `runtime_evidence_pending`, not automatic start blockers, when the start gate otherwise passes:

- subscriber presence, cursor ack freshness, heartbeat freshness;
- attendance/preparation terminal evidence;
- selected-runner readiness/prerequisites and selected-runner proof;
- same-path per-turn visible author proof;
- turn-posting and visible closeout proof when a non-mutating probe has not yet run.

Treat these as `final_acceptance_unproven`, not start blockers:

- `selected_runner_pass`, `visible_surface_pass`, `discussion_quality_pass`, and `fallback_profile_pass`;
- ARGUE relation counts and discussion-quality proof;
- visible turn count and real profile/gateway reply count.

When using `kan_discussion_activation_plan`, materialize collected evidence into planner input fields such as `participant_profiles[].effective_discord.tools_visible`, `participant_profiles[].effective_discord.bot_to_bot_enabled`, `discord_parent_channel.allow_list_inheritance_proven`, and `visible_surface_readiness`; prose notes or prior human knowledge do not count. If the planner returns `status: blocked`, classify each blocker before acting: only `start_blocker` blocks `council.new`; runtime and final-acceptance evidence gaps remain tracked evidence. Do not treat `kan_discussion_activation_plan.live_readiness=false` as a start blocker by itself because the planner is pure/local and never proves live readiness.

If evidence is missing but can be collected without mutating profile/provider/gateway/auth/token state, collect the probe before asking the user. If collecting evidence requires mutation, credentials, or unavailable external permissions, stop and ask for approval.

For exact preflight and `council.new` schema pitfalls observed in live-visible KAN operation, see `references/live-visible-preflight-and-council-new.md`.
For cross-team KLM/KAN participant onboarding and the evidence package needed before a live-visible run, see `references/cross-team-participant-preflight-evidence.md`.

## Council lifecycle spine

Use daemon-owned `kan_council_command` commands with caller-supplied `command_id`, `request_id`, and `idempotency_key`.

Minimum lifecycle before discussion turns:

1. `council.new`
2. `council.request_attendance`
3. Terminal attendance evidence from required participants (`council.attend` or documented absence path)
4. `council.lock_agenda`
5. `council.prepare`
6. `council.ready` or `council.prepared_partial`

For each turn:

1. Open a `council.poll` or evaluate explicit `council.hand_raise` entries.
2. Select exactly one next speaker through daemon-controlled selection/grant path, preserving the `speaker_selected` event and cursor evidence.
3. Do not predeclare or hard-code a complete live speaker order.
4. Use `relevance` as the default speaker-selection mode. `targeted`, `random`, `moderator_direct`, and `role_order` are allowed only as per-turn choices with reasons; `role_order` also needs bounded round evidence and must never become a predeclared debate transcript.
5. Ensure participant visible speech is submitted as canonical daemon `speech` using the selected participant path, then acknowledge the selected cursor only after successful submit.
6. If the moderator has a substantive opinion, submit it as a participant-style speech turn rather than hiding it inside moderation prose.

If a fixed-order flow starts by mistake before any `speech` event exists, cancel and restart. If `speech` already exists, repair forward with a moderator intervention and never rewrite history.

## Runner stdout semantic framing contract

Selected-runner participant and moderator wrappers must emit exactly one compact JSONL object on stdout for the canonical semantic response. Use one line, no markdown fence, and no surrounding prose. Put runtime diagnostics, wrapper logs, and provider warnings on stderr or in structured evidence fields; never wrap them around the stdout semantic record.

Council speech runner stdout contract:

```json
{"type":"speech","payload":{"speech":"Visible participant answer only.","claims":[],"stance_links":[],"contribution_type":"support","new_axis_reason":null,"evidence":[]}}
```

Pretty/multiline JSON is compatibility input only: the control adapter may normalize it so real Hermes output does not fail solely on formatting, but prompts and bundled skills must still require compact JSONL. Delivery/fallback-only JSON remains adapter_command_mismatch, and malformed JSON remains malformed_or_missing_response.

## ARGUE and quality gate

For quality-required councils, require each non-opening speech with sufficient local context to include either:

- valid `stance_links[]` to caller-provided prior `event_id` / optional `claim_id`; or
- `contribution_type: "new_axis"` with a non-empty `new_axis_reason`.

Keep these fields separate in evidence:

- `speech`: visible answer only;
- `claims[]`;
- `stance_links[]`;
- `contribution_type`;
- `new_axis_reason`;
- optional `evidence[]`.

In `quality_required`, the first orphan non-opening speech blocks `discussion_quality_pass`. In `quality_warn`, the same condition is diagnostic/warning only.

## Closeout and reporting

Final moderator closeout must separate:

- `lifecycle_pass`;
- `selected_runner_pass`;
- `visible_surface_pass`;
- `fallback_profile_pass`;
- `discussion_quality_pass`;
- `orphan_speech_count`;
- `linked_speech_count`;
- `stance_link_count`;
- `new_axis_count`;
- Discord visible turns posted;
- real profile/gateway replies;
- shared/default author fallback status;
- explicit non-scope such as production readiness or broad rollout.

Do not equate transcript/export success with a visible Discord discussion. Use `kan_surface_render_projection` only to render explicit daemon/control projection rows into visible transcript and audit evidence; it is not lifecycle authority.
