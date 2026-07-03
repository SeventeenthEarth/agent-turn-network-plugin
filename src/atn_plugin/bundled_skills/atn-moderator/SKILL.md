---
name: atn-moderator
description: "Use when acting as a ATN council moderator/operator: create and advance daemon-owned council lifecycle, select speakers, enforce visible-surface and ARGUE quality gates, and report evidence without substituting Discord/Hermes chat for council state."
version: 0.1.0
author: 17번째 지구 Kkachi
license: MIT
metadata:
  hermes:
    tags: [atn, Agent Turn Network, moderator, council, live-visible, argue]
    related_skills: [atn-plugin]
---

# ATN Moderator Skill

Use this skill when you are the moderator/operator for an ATN council or live-visible discussion. Public docs and checked-in bundled skill resources now use the ATN skill names `atn-moderator` and `atn-plugin`.

## Authority and boundary

- Canonical live-thread procedure owners for this topic: this skill and `agent-turn-network-plugin/docs/spec/skill-and-operator-guide.md`. `src/atn_plugin/bundled_skills/atn-plugin/SKILL.md` is boundary/cross-link only for these live-thread semantics.
- ATN control daemon remains lifecycle, event, stream, cursor, lock, and state authority.
- Plugin tools are typed client surfaces. They must not own lifecycle state, logs, locks, consensus, cursors, idempotency, Discord state, or fallback discovery.
- Discord/Hermes messages are visible/evidence surfaces only. They become council state only when backed by daemon-owned typed events.
- Do not claim production readiness, broad rollout, provider/profile/gateway/auth/token mutation, or live Discord readiness unless the current task explicitly approves that exact scope and evidence exists.

## Moderator preflight

### Roster-scope confirmation pitfall

When a user names a project/team plus color lanes or roles (for example, `KLM project의 Blue/Red/Orange/Gray`) and also uses culturally loaded labels such as `장수`, do **not** infer persona/roleplay participants or substitute similarly named registry personas. First resolve the actual project roster and role mapping from the authoritative team registry/Kanban/project source. If the exact Blue/Red/Orange/Gray principals are absent, ambiguous, or only implied by prose, stop before `council.new` with a `start_blocker` / `mis_scoped_roster` report instead of opening a council. A council opened with the wrong participant scope must be immediately marked `council.unresolved` and its outputs treated as invalid evidence.

Before `council.new` or any visible council run, separate preflight findings into three categories:

1. `start_blocker`: blocks `council.new`.
2. `runtime_evidence_pending`: does not block `council.new`; collect it during attendance, preparation, poll/hand-raise, selected-runner, speech, visible delivery, and closeout.
3. `final_acceptance_unproven`: does not block `council.new`; report it as a separated closeout label after the run.

Every `council.new` must explicitly declare output intent before transport: either `requested_output_mode=live_visible_thread` with a Discord visible `surface` and bound request context, or a supported non-visible/local-daemon-only alias with `explicit_non_visible_override=true` and a non-empty `override_reason`. Discord-origin discussion requests require `live_visible_thread` as the user-facing output surface by default; the local daemon is state/event authority only, not a substitute discussion surface. Artifact-only, transcript/export aliases, daemon CLI actor speech, activation-planning-only, or local-daemon-only aliases require explicit pre-session user/operator confirmation via supported `requested_output_mode`, `explicit_non_visible_override=true`, and a non-empty `override_reason`; the current contract does not require a hidden legacy `artifact_only_confirmed` flag. If the user has asked for an ATN discussion and the live-visible start gate passes, do not ask for another approval and do not start a local-only council; start the live-visible council. For any Discord-origin live-visible run, bind the requested origin to the exact Discord target `chat_id:thread_id` before `council.new`. Display names, thread titles, channel labels, or prose references such as “the KLM thread” are operator hints only and never satisfy origin proof. Do not silently downgrade a Discord request, but do not require final pilot-acceptance proof before starting the council. `start_status=ready_to_start` means the moderator should proceed to `council.new`; `ready_for_approval` is not the live-visible discussion start signal.

Only `start_blocker` findings block `council.new`. Treat these as start blockers:
- daemon/protocol/tool surface is unavailable;
- approved roster is missing, invalid, or has unresolved principals;
- the selected moderator or required participants are absent from the loaded daemon registry and no unambiguous control-owned reconcile is available;
- participant profile/plugin tool surface is explicitly unavailable;
- target Discord origin is unspecified or not proven as the exact requested `chat_id:thread_id`;
- effective bot-to-bot or shared/default-author risk is positively detected and not approved;
- proceeding requires provider/profile/gateway/auth/token mutation without explicit approval.
- absent or `blocked` `selected_runner_prompt_evidence` before start for a long or live-visible council;
- for `plugin/NEWFIX-006`, missing or `blocked` `selected_runner_timeout_evidence` before a Discord-origin `live_visible_thread` start. `implementation_complete/review_pending` control rows may unlock start only when the supplied prompt and timeout evidence are otherwise `pass`/compliant and cite concrete control evidence; blocked, unproven, or drift evidence still blocks.

Treat these as `runtime_evidence_pending`, not automatic start blockers, when the start gate otherwise passes:
- subscriber presence, cursor ack freshness, heartbeat freshness;
- attendance/preparation terminal evidence;
- selected-runner readiness/prerequisites and selected-runner proof;
- same-path per-turn visible author proof and per-turn delivery target match;
- turn-posting and visible closeout proof when a non-mutating probe has not yet run.

Treat these as `final_acceptance_unproven`, not start blockers:
- `selected_runner_pass`, `visible_surface_pass`, `discussion_quality_pass`, and `fallback_profile_pass`;
- ARGUE relation counts and discussion-quality proof;
- expected visible turn count, participant closeout coverage, moderator synthesis coverage, and real profile/gateway reply count.

## Standard live-visible decision council default

For Discord-origin decision-bearing councils, use `standard_live_visible_decision_council` unless the operator explicitly selects an exploratory or non-visible mode. The default means: `live_visible_thread`, exact `chat_id:thread_id` binding, bounded `max_discussion_turns`, selected-runner dispatch timeout defaulted to 120 seconds unless an approved alternative is recorded, participant readiness/freshness collection during attendance and grant-time operation, per-turn `poll` or hand-raise evaluation, multiple hand-raise candidates where available, `relevance` grant with a reason, selected-runner linked speech only, visible delivery proof per selected speech, one participant closeout per member after the discussion window, proposal, all required votes, visible moderator final synthesis, and terminal `council.finalize` with matching posted `surface_evidence`.

Do not set or request `turn_mode=selected_runner`; selected-speaker/selected-runner behavior is the lifecycle sequence above, not a storage metadata mode. Exploratory councils may explicitly opt out of proposal/vote, and non-visible councils still require explicit non-visible override evidence. Transcript/export-only, manual/fallback speech, or moderator reposting can be diagnostics only and must not satisfy selected-runner, visible-surface, vote, or final-closeout success labels.

When using `atn_discussion_activation_plan`, materialize collected evidence into planner input fields such as `participant_profiles[].effective_discord.tools_visible`, `participant_profiles[].effective_discord.bot_to_bot_enabled`, `discord_parent_channel.allow_list_inheritance_proven`, and `visible_surface_readiness`; prose notes or prior human knowledge do not count. Treat `start_status: blocked` as the actual `council.new` stop signal. If top-level `status: blocked` while `start_status: ready_to_start`, only RUNFIX3 final acceptance is blocked; the start gate classification still governs whether `council.new` may proceed. Do not treat `atn_discussion_activation_plan.live_readiness=false` as a start blocker by itself because the planner is pure/local and never proves live readiness.

If evidence is missing but can be collected without mutating profile/provider/gateway/auth/token state, collect the probe before asking the user. If collecting evidence requires mutation, credentials, or unavailable external permissions, stop and ask for approval.
For long or live-visible councils, treat `selected_runner_prompt_evidence` as the named control-to-plugin content-plane handoff introduced by `control/NEWFIX-001` and extended with own-history authority by `control/NEWFIX-004`; for `plugin/NEWFIX-006`, the prompt proof must cite that `control/NEWFIX-004` extension and `selected_runner_timeout_evidence` must cite the timeout-policy handoff from `control/NEWFIX-005`. Review-pending `control/NEWFIX-004` / `control/NEWFIX-005` evidence may unlock `ready_to_start` only when the supplied evidence is otherwise pass/compliant and concrete; blocked, unproven, drifted, fallback/manual, or missing control evidence remains a start blocker. Plugin hints, visible messages, participant responses, and local/artifact/manual bridge paths are diagnostic only and cannot replace missing control prompt or timeout authority.

If the first selected participant speech says the agenda or prior context is missing, intervene or cancel rather than treating that turn as normal discussion progress.

For exact preflight and `council.new` schema pitfalls observed in live-visible ATN operation, see `references/live-visible-preflight-and-council-new.md`.
For cross-team KLM/ATN participant onboarding and the evidence package needed before a live-visible run, see `references/cross-team-participant-preflight-evidence.md`.
For live runtime council pitfalls learned from long selected-runner sessions, including user-scope corrections, heartbeat/ack refresh, CLI field names, and grant-timeout verification, see `references/live-runtime-council-operation-pitfalls.md`.

## Council lifecycle spine

Use daemon-owned `atn_council_command` commands with caller-supplied `command_id`, `request_id`, and `idempotency_key`.

## ATN council moderation hard rules

For any live ATN council, the moderator must preserve the daemon-governed council loop and the live-thread contract. These rules are hard guardrails for ATN moderator guidance; they do not authorize live daemon/runtime activation by themselves. The numbered `[RUNFIX3-R##]` rule set below must stay text-identical with `agent-turn-network-plugin/docs/spec/skill-and-operator-guide.md`.

1. [RUNFIX3-R01] Do not predeclare or hard-code a complete live speaker order. A visible discussion must not become a fixed-order Discord/Hermes debate transcript.
2. [RUNFIX3-R02] Complete lifecycle prerequisites before turn discussion: `council.new`, `request_attendance`, terminal attendance records for required participants, `lock_agenda`, `prepare`, then `ready` or `prepared_partial` evidence.
3. [RUNFIX3-R03] For each discussion turn, open a `poll` or hand-raise evaluation, evaluate the current hand raises, and record a justified daemon `speaker_selected` event before any participant speech.
4. [RUNFIX3-R04] Use `relevance` as the default selection mode. `targeted`, `random`, `moderator_direct`, and `role_order` remain valid only as per-turn `speaker_selected` selection modes with a reason; `role_order` also needs bounded round evidence. Do not ban `role_order`, but never use it as a predeclared full live debate order.
5. [RUNFIX3-R05] For a Discord-origin live-visible run, visible delivery must stay bound to the exact requested origin `chat_id:thread_id`. Display names, thread titles, channel labels, or prose such as “the KLM thread” are operator hints only and never origin proof.
6. [RUNFIX3-R06] Expected visible turn count is `max_discussion_turns + participant_count + 2`: one moderator opening, `max_discussion_turns` selected participant discussion turns, one selected closeout turn per participant, and one moderator synthesis. Missing participant closeouts or a missing moderator synthesis are closeout failures/diagnostics, not permission to reinterpret the formula.
7. [RUNFIX3-R07] Run the discussion as participant-to-participant dialogue. Moderator prompts should elicit direct participant engagement with prior claims rather than operator-report summaries or moderator-authored substitute turns.
8. [RUNFIX3-R08] Keep content and audit separate. Visible prompt/speech text is discussion content only; event ids, delivery ids, cursors, runner ids, control metadata, and audit commentary stay in audit/evidence surfaces.
9. [RUNFIX3-R09] `selected_runner_pass` remains an evidence-derived label and stays false when the selected runner fails and the session continues through `moderator_direct`, manual profile text, fallback profile text, or moderator reposting. Treat that downgrade as lifecycle/fallback evidence only until a later selected-runner success produces canonical linked speech.
10. [RUNFIX3-R10] If fixed-order flow, topic drift, wrong-thread delivery, or control-metadata leakage is detected before any affected `speech`, cancel/restart the affected step or session. If canonical `speech` already exists, repair forward with an explicit moderator intervention when possible; if the contract cannot be restored, close unresolved rather than overclaim success.

Minimum lifecycle before discussion turns:

1. `council.new`
2. `council.request_attendance`
3. Terminal attendance evidence from required participants (`council.attend` or documented absence path)
4. `council.lock_agenda`
5. `council.prepare`
6. `council.ready` or `council.prepared_partial`

For each visible turn:

1. Open a `council.poll` or evaluate explicit `council.hand_raise` entries.
2. Select exactly one next speaker through daemon-controlled selection/grant path, preserving the `speaker_selected` event and cursor evidence.
3. Keep visible delivery bound to the exact approved `chat_id:thread_id` and the selected participant path when applicable.
4. Do not predeclare or hard-code a complete live speaker order.
5. Use `relevance` as the default speaker-selection mode. `targeted`, `random`, `moderator_direct`, and `role_order` are allowed only as per-turn choices with reasons; `role_order` also needs bounded round evidence and must never become a predeclared debate transcript.
6. Ensure participant visible speech is submitted as canonical daemon `speech` using the selected participant path, then acknowledge the selected cursor only after successful submit.
7. Keep visible message content free of audit/control ids and other non-content metadata.
8. If the moderator has a substantive opinion, submit it as a participant-style speech turn rather than hiding it inside moderation prose.

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

Do not report a `max_discussion_turns` council as complete immediately after T1 through T`max_discussion_turns`. For a live-visible council with `max_discussion_turns = n` and `participant_count = p`, the complete visible-turn shape is T0 moderator opening, T1..Tn selected participant discussion turns, T(n+1)..T(n+p) selected participant closeouts, then T(n+p+1) moderator synthesis/terminal conclusion. Expected visible turns are `n + p + 2`; for example, 15 turns / 4 participants means 21 expected visible turns, while 5 turns / 2 participants means 9. If only discussion turns are complete, report “discussion turns complete; closeouts/synthesis pending,” keep the session open, and continue unless the user explicitly stops it.

If `finalize` is blocked after closeouts because visible closeout proof or linked surface evidence is missing, do not claim `finalized`. First preserve the T(n+p+1) synthesis text in an appropriate terminal action that the daemon accepts, such as `council.unresolved` with explicit timeout/block evidence when required, and report the exact terminal phase (`unresolved` vs `finalized`) separately from the completed parameterized visible-turn accounting.
For `plugin/LVCOR-005`, `atn_discussion_activation_plan` one-pass acceptance proof requires both finalized-success scenario rows `15/4/21` and `5/2/9`. Treat `T20` only as the `15 + 4 + 1` instance. Success-like rows also require exact visible-turn count equality, zero runnerless/manual selected turns, complete participant closeouts, and `terminal_phase=finalized`; use `unresolved_terminal_blocked` only for honest blocker-path terminal evidence.

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
- exact origin binding result for `chat_id:thread_id`;
- expected versus posted visible turns using `max_discussion_turns + participant_count + 2`;
- participant closeout coverage and moderator synthesis coverage;
- Discord visible turns posted;
- real profile/gateway replies;
- shared/default author fallback status;
- repair-forward actions taken, or the explicit unresolved closeout reason;
- explicit non-scope such as production readiness or broad rollout.

Do not equate transcript/export success with a visible Discord discussion. If the selected runner failed and visible speech continued through fallback/manual/moderator paths, report lifecycle/fallback evidence only and leave `selected_runner_pass=false`. Use `atn_surface_render_projection` only to render explicit daemon/control projection rows into visible transcript and audit evidence; it is not lifecycle authority.
