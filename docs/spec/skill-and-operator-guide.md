# ATN Skill and Operator Guide

## Scope

The packaged ATN operator skills and local compatibility matrix remain the operator-facing guide for this repository. The bundled source now lives inside the Python package:

```text
src/atn_plugin/bundled_skills/atn-plugin/SKILL.md
src/atn_plugin/bundled_skills/atn-moderator/SKILL.md
src/atn_plugin/bundled_skills/atn-participant/SKILL.md
```

The package exposes import-safe resource helpers and the public ATN operator guidance. The bundled source is canonical and profile-local flat copies are not required.

This guide does not enable a live plugin, contact a daemon, modify the sibling
control repo, or prove production activation, live plugin readiness, or live
Discord readiness. The
smoke claim is exactly local isolated plugin-load smoke.

## Current plugin capability

The current plugin surface is fake/injected Hermes tools only:

- `atn_daemon_status`
- `atn_compatibility_diagnostics`
- `atn_stream_tail`
- `atn_stream_ack`
- `atn_delegate_new`
- `atn_delegate_action`
- `atn_council_command`
- `atn_selected_participant_response`
- `atn_delivery_evidence`
- `atn_surface_render_projection`
- `atn_discussion_activation_plan`
- `atn_discord_send_message`

`plugin.yaml` must continue to declare `provides_commands: []`. The root
entrypoint must not register ATN slash commands.

Unsupported in SKILL-2:

- `atn_session_status` or `session.status.read`;
- ATN slash commands through Hermes `register_command`;
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
   still goes through `atn_delivery_evidence`.
5. Treat `atn_surface_render_projection` output as a local projection over
   explicit daemon/control event JSON, not lifecycle authority. Use
   `visible_transcript` for operator-facing discussion text and keep raw
   cursor/event details in `audit_log`/`rows` evidence.
6. Treat `atn_discussion_activation_plan` output as a dry-run planner/doctor
   report only. It never proves live readiness or authorizes broad apply/pilot
   scope. For a Discord-origin `live_visible_thread` discussion whose start gate
   passes, `ready_to_start` means proceed to `council.new` without another
   approval prompt.
7. Treat ARGUE argument-graph support as static/fake/injected schema and tool
   contract coverage only. `claims[]`, `stance_links[]`, `contribution_type`,
   `new_axis_reason`, `evidence[]`, `hand_raise.intent`, `hand_raise.reason`,
   and `hand_raise.target_links[]` are preserved for daemon/control validation,
   while `responds_to_event_id` remains
   a legacy display hint that never overrides `stance_links[]`.

## Standard live-visible decision council default

For Discord-origin decision-bearing councils, the operator should use `standard_live_visible_decision_council` unless they explicitly select an exploratory or non-visible mode. The default means: `live_visible_thread`, exact `chat_id:thread_id` binding, bounded `max_discussion_turns`, selected-runner dispatch timeout defaulted to 120 seconds unless an approved alternative is recorded, participant readiness/freshness collection during attendance and grant-time operation, per-turn `poll` or hand-raise evaluation, multiple hand-raise candidates where available, `relevance` grant with a reason, selected-runner linked speech only, visible delivery proof per selected speech, one participant closeout per member after the discussion window, proposal, all required votes, visible moderator final synthesis, and terminal `council.finalize` with matching posted `surface_evidence`.

Do not set or request `turn_mode=selected_runner`; selected-speaker/selected-runner behavior is the lifecycle sequence above, not a storage metadata mode. Exploratory councils may explicitly opt out of proposal/vote, and non-visible councils still require explicit non-visible override evidence. Transcript/export-only, manual/fallback speech, or moderator reposting can be diagnostics only and must not satisfy selected-runner, visible-surface, vote, or final-closeout success labels.

## Daemon registry membership gate

Before any `council.new` for a live-visible or cross-team council, operator evidence must separate daemon registry authority from profile/Discord readiness. The selected moderator and each participant must be present/enabled in the loaded daemon registry, or the activation plan must provide `daemon_registry_membership.participants[]` entries showing an unambiguous planned control-owned reconcile for the exact approved roster. Discord allow-list membership, visible-author probes, gateway `running`, plugin tool visibility, and `DISCORD_ALLOW_BOTS=none` do not make a principal valid in the daemon registry.

Accepted planned reconcile evidence needs at least: `principal`, `in_loaded_registry: false`, `planned_reconcile: true`, `mapping_unambiguous: true`, and `wrapper_resolves: true`. Ambiguous mapping, disabled existing principals, unresolved wrappers, or missing loaded-registry evidence block before `council.new`; the control-owned reconcile also validates invalid/reserved principal ids before registry mutation. Do not downgrade to artifact-only or daemon CLI actor speech unless the operator explicitly approves that different mode before session creation. Registry membership persists across council sessions; subscription, heartbeat, cursor ack, attendance/preparation, and selected-runner readiness remain session-scoped runtime gates.

## ATN council moderation hard rules

For RUNFIX3 live-thread semantics, this guide and `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md` are the normative procedure owners. `src/atn_plugin/bundled_skills/atn-plugin/SKILL.md`, `docs/roadmap.md`, and `docs/spec/live-transport-sot.md` remain boundary/mirror surfaces for this topic. For any live ATN council, operator guidance must keep the discussion lifecycle-first, per-turn selected, daemon-event authoritative, and bound to the requested live thread. These rules do not authorize live daemon/runtime activation, Discord delivery, profile mutation, or live readiness by themselves. The numbered `[RUNFIX3-R##]` rule set below must stay text-identical with `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md`.

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

## Persistent participant runtime planning note

SSOT: `17thHermes:40_outputs/team/macho/atn/2026-07-04-atn-persistent-participant-runtime-design-sot.md`.

PRSLR is intended, after PRSLR-007 acceptance and explicit implementation gates, to change the standard council discussion runtime from per-turn fresh participant invocations to council-scoped persistent participant sessions. Until PRSLR tasks complete, operators must treat this as planned/default-off/local-only, not live readiness or an enabled runtime. The intended operator-facing contract is:

- every public speech must reach all-member cursor coverage;
- non-speakers observe deltas, while the speaker receives authored canonical commit/self-ack;
- each participant must answer the response window with `council.hand_raise` or first-class `council.drop`;
- all-responded windows close before the 120-second deadline;
- timeout non-response becomes daemon-owned `drop(auto=true, reason=timeout)`;
- observe/ack/cursor/rehydrate failures are runtime consistency failures, not drops;
- recovery is `rehydrate` only, and stateless fallback must not be reported as participant continuity;
- participant sessions are council-scoped only; cross-council reuse is prohibited;
- rehydrate/observe/ack failures default to whole participant runtime/council blocked; affected-member degraded continuation requires later explicit approval;
- plugin/operator guidance must not submit or synthesize daemon-owned `auto=true` timeout drops.

Plugin guidance may consume `persistent_participant_runtime_evidence` after control provides it, but it must not infer that evidence from visible messages, transcript/export rows, manual profile text, or fake local planner inputs.

A PRSLR operator report is not complete unless it shows the control-produced `persistent_participant_runtime_evidence` source and the following minimum fields: readiness label, evidence paths, session reuse reference or redacted handle hash, mode, omitted-full-history proof, `stateless_fallback=false`, all-member cursor coverage, response-window close reason and elapsed time, auto-drop/late-ignore accounting, rehydrate status or fail-close event, next owner/gate, and non-claims. Fake/injected plugin planner inputs may test rendering only; they do not prove runtime continuity.


## ARGUE relation-aware response guidance

ARGUE relation evidence is the structured link between visible participant speech
and the council claim graph. The plugin can preserve and locally render this
evidence, but the daemon/control contract remains the authority for validation,
append-time acceptance, event order, and lifecycle state.

A selected participant response in quality-required rehearsal or pilot evidence
should separate:

- `speech`: human-visible answer text only; do not include runtime warnings,
  wrapper logs, max-iteration summaries, tool diagnostics, or transport metadata;
- `claims[]`: concise claims introduced or restated by the participant;
- `stance_links[]`: explicit links from new claims to prior claim or event ids,
  with relation types such as support, challenge, refine, or synthesize;
- `contribution_type`: the main contribution category, such as support,
  challenge, refine, synthesize, risk_addition, decision_frame, or new_axis;
- `new_axis_reason`: required for `contribution_type: "new_axis"` and only valid
  when the participant is opening a necessary new line of argument;
- `evidence[]`: source or observation pointers outside the visible speech text.

Operators should treat a non-opening speech as orphaned when sufficient local
context exists and it has neither a valid stance link to the prior claim graph
nor `contribution_type: "new_axis"` with a non-empty `new_axis_reason`. In
`quality_required`, the first orphan non-opening speech fails closed and blocks
`discussion_quality_pass`. In `quality_warn`, the same condition is warning-only
diagnostic evidence; the mechanical local lifecycle may pass while the
deliberation-quality gate still requires changes.

For selected-runner councils, every `council.hand_raise` must include a non-empty
`intent` or `reason`. Control derives the subsequent grant `stance_assignment`
only from the matching hand raise for the same member and turn; a caller-supplied
`grant.stance_assignment` is ignored and cannot repair a missing hand-raise
stance source.

Compact prior-claim graph targets should include `event_id`, optional
`claim_id`, and guidance-only fields such as `speaker`, `summary`, and
`available_stances`. Only caller-provided `event_id` and `claim_id` are local
validation authority. `responds_to_event_id`, prose, keywords, Discord order,
Hermes messages, `speaker`, `summary`, and `available_stances` never satisfy
relation validity by themselves.

Prompt target example:

```json
{
  "prior_claim_graph_targets": [
    {
      "event_id": "evt_speech_T01",
      "claim_id": "T01.C1",
      "speaker": "macho",
      "summary": "Canonical speech linkage is required before pilot acceptance.",
      "available_stances": ["support", "challenge", "refine", "synthesize"]
    }
  ]
}
```

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

## Runner stdout semantic framing contract

Selected-runner participant and moderator wrappers must emit exactly one compact JSONL object on stdout for the canonical semantic response. Use one line, no markdown fence, and no surrounding prose. Put runtime diagnostics, wrapper logs, and provider warnings on stderr or in structured evidence fields; never wrap them around the stdout semantic record.

Council speech runner stdout contract:

```json
{"type":"speech","payload":{"speech":"Visible participant answer only.","claims":[],"stance_links":[],"contribution_type":"support","new_axis_reason":null,"evidence":[]}}
```

Pretty/multiline JSON is compatibility input only: the control adapter may normalize it so real Hermes output does not fail solely on formatting, but prompts and bundled skills must still require compact JSONL. Delivery/fallback-only JSON remains adapter_command_mismatch, and malformed JSON remains malformed_or_missing_response.

`speech` is the only human-visible answer text. `claims[]`,
`stance_links[]`, `contribution_type`, `new_axis_reason`, and optional
`evidence[]` are structured evidence fields. Do not substitute a simulated role
prompt, fallback/manual reply, wrapper summary, or current Discord/Hermes
message for a selected participant response.

## Pilot harness notes

Use two separate verdicts when rehearsing ARGUE discussion quality:

1. Mechanical lifecycle pass: the local daemon/CLI/plugin flow completes, events
   are replayable, delivery/evidence pointers are reconstructable, and no plugin
   fallback or lifecycle-state ownership appears.
2. Discussion-quality pass: relation evidence is grounded, visible relation
   summaries from `atn_surface_render_projection` are readable, audit fields keep
   `claims[]`, `stance_links[]`, `contribution_type`, `event_id`, `turn`,
   `speaker`, and `speech`, participants engage non-immediate prior claims where
   appropriate, challenge/refine/synthesize relations appear when the scenario
   requires them, and runtime noise is absent from visible speech.

A live-local pilot needs explicit approval and evidence for the real participant
profiles, plugin enablement, daemon/CLI path, gateway/tool visibility, and any
visible Discord surface. Do not treat this operator guide, local isolated
plugin-load smoke, or fake/injected fixture harness as live readiness.

KAS does not install, own, activate, or gate ATN runtime/plugin/bundled-skill artifacts.
The ATN plugin package owns the bundled guidance source and exposes it through
Hermes plugin-qualified skills. ATN development and ATN use must not depend on
profile-local flat copies or profile-local KAS development phase skills being
present.


## RUNFIX post-pilot guardrails (RUNFIX-014/RUNFIX-015/RUNFIX-016 proof, RUNFIX-017 candidate)

주유's 2026-06-19 rename-council handoff is registered as `RUNFIX-014` through `RUNFIX-017`. `control/RUNFIX-014` and `plugin/RUNFIX-015` have local implementation proof. `control/RUNFIX-016` has local implementation proof under KAH run `run-20260619T083649Z-d10e1f5cc20b` and local commit `9c15d22`. `plugin/RUNFIX-017` has local implementation proof under KAH run `run-20260619T101255Z-189d01ba8b8f` after official color review, Blue synthesis, and final KAH gate. Operators must treat the following as local proof, implementation-candidate evidence, or required planning/acceptance boundaries, not completed runtime capability:

1. `control/RUNFIX-014` selected-runner accounting: control KAH run `run-20260619T051710Z-8e1f6efb61ec` provides local implementation proof that a run with `runner_invocation_failed` followed by later fallback/manual canonical `speech` is lifecycle/fallback evidence, not `selected_runner_pass`. Reports must consume the control accounting labels and expose runner started/succeeded/failed counts plus fallback/manual harness flags.
2. `plugin/RUNFIX-015` visible author guard: plugin KAH run `run-20260619T071526Z-7d2ba33b07d5` adds local `atn_discussion_activation_plan` proof for pre-`council.new` visible-author validation. Explicit caller-provided same-path probes must prove each selected participant posts as the expected profile author. Evidence includes `profile`, expected author source (`registry_snapshot` or approved profile-author map), observed bot/user, `source_env`, `posting_path`, shared/default negative proof, shared-default-then-profile-local env precedence, per-turn Discord message id, selected member, profile author id, and `speech_event_id`.
3. `control/RUNFIX-016` summary robustness: KAH run `run-20260619T083649Z-d10e1f5cc20b` has local implementation proof that closeout/summary tooling tolerates `payload.plugin_evidence`, dict/list `payload.evidence`, and missing optional evidence. A finalized lifecycle must not look failed because optional evidence has an alternate shape; this remains fail-closed local proof evidence only, not runtime readiness.
4. `plugin/RUNFIX-017` ARGUE quality-required prompts: non-opening quality-required speeches with sufficient local context must link to caller-provided prior targets through valid `stance_links[]` or justify `contribution_type: "new_axis"` with `new_axis_reason`; prompts should provide compact prior claim graph targets; explicit `discussion_quality` evidence is required for the quality gate; in `quality_required`, the first orphan non-opening speech blocks `discussion_quality_pass`; warning-only behavior is reserved for `quality_warn`, and repeated-orphan counts remain diagnostic evidence.

Final reports must keep these fields separate: `lifecycle_pass`, `selected_runner_pass`, `visible_surface_pass`, `fallback_profile_pass`, `discussion_quality_pass`, `orphan_speech_count`, `linked_speech_count`, `stance_link_count`, `new_axis_count`, exact origin `chat_id:thread_id` binding result, expected/posted visible turns by `max_discussion_turns + participant_count + 2`, participant closeout coverage, moderator synthesis coverage, Discord visible turns posted, real profile/gateway replies, shared/default author fallback status, and repair-forward versus unresolved closeout outcome.

## RUNFIX activation guidance

`RUNFIX` distinguishes plugin installation from live-local ATN discussion activation.

- Plugin install/load proves only that the packaged plugin surface can be discovered and its declared tools can be used in the approved Hermes profile.
- Discussion activation requires an explicit dry-run plan before any apply step. The `atn_discussion_activation_plan` tool can build the planner/doctor report from caller-provided evidence: control daemon/socket/config evidence, participant profile list, selected Discord parent channel, effective Discord profile eligibility, planned allow-list/config changes, rollback, smoke commands, and approval boundary.
- Profiles with effective bot-to-bot enabled Discord behavior are excluded from ATN discussion allow-lists by default. Report every excluded profile and reason/remediation; `allow_list_targets` must include eligible profiles only.
- Visible-pilot surface policy is thread-preferred and parent-channel fallback allowed. Create or use a dedicated thread under the approved parent channel first. If thread creation/posting is unsupported, use the approved parent channel directly as a fallback, but record `fallback_reason` in the task brief, ATN surface metadata, visible closeout, and final report. Parent-channel fallback is not no-restart thread readiness, and manual participant messages remain diagnostic-only unless canonical ATN event linkage is also proven.
- Discord-origin council requests require `live_visible_thread` output as the user-facing surface by default. The local daemon remains lifecycle/event/state authority only; it is not a substitute discussion surface. Bind that request to the exact origin `chat_id:thread_id`; display-name labels do not satisfy proof. If the operator explicitly asks for `artifact_only`, `daemon_cli_actor_speech`, `activation_planning_only`, local-daemon-only aliases (`local-daemon-only`/`local_daemon_only`), or transcript/export aliases (`transcript/export-only`/`transcript_export_only`) output, record a supported `requested_output_mode`, `explicit_non_visible_override=true`, and a non-empty `override_reason` before `council.new`; no hidden legacy `artifact_only_confirmed` flag is required by the current contract. Otherwise classify preflight findings before session creation. When the user has already asked for the ATN discussion and the start gate passes, do not ask for another approval and do not start a local-only council; proceed to live-visible `council.new`.
- Use three preflight categories. `start_blocker` blocks `council.new`; `runtime_evidence_pending` is collected during attendance, preparation, selected-runner, speech, delivery, and closeout; `final_acceptance_unproven` is reported as separated closeout labels. Only `start_blocker` findings block `council.new`.
- `start_blocker` findings are unavailable daemon/protocol/tool surface, missing or invalid roster, unresolved registry principals with no unambiguous control-owned reconcile, explicitly unavailable profile/plugin tool surface, missing exact Discord origin proof, positively detected bot-to-bot or shared/default-author risk without approval, or unapproved provider/profile/gateway/auth/token mutation.
- Missing selected-runner proof, participant runtime freshness, same-path per-turn author linkage, delivery target match, visible turn counts, ARGUE relation counts, participant closeouts, moderator synthesis, or discussion-quality proof are not automatic start blockers. Track them as `runtime_evidence_pending` or `final_acceptance_unproven`, then report them separately at closeout.
- NEXFIX content-plane exception: for long or live-visible councils, absent or `blocked` `selected_runner_prompt_evidence` before start is a `start_blocker` because it proves the selected-runner prompt-envelope contract is unavailable or inadequate before the operator intentionally starts a context-sensitive discussion. For `plugin/NEWFIX-006`, the prompt own-history proof must consume the `control/NEWFIX-004` extension of `selected_runner_prompt_evidence`, and Discord-origin `live_visible_thread` `selected_runner_timeout_evidence` must consume `control/NEWFIX-005`. Review-pending control dependency rows may start only when the supplied evidence is otherwise `pass`/compliant and concrete; blocked, unproven, drifted, fallback/manual, or missing control evidence remains a start blocker.
- Before starting a live visible council, collect non-mutating probes when feasible: exact thread binding, or approved parent-channel fallback with `fallback_reason`, turn-posting probe for the selected-speaker/profile-send path or approved fallback poster, visible closeout probe, `real_profile_gateway_replies: true`, and `cli_actor_speech_only: false`. If these are missing because no probe has been run yet, collect the probe before asking the user; if collecting it requires profile/provider/gateway/auth/token mutation, stop for explicit approval.
- Gateway liveness, transcript/export artifacts, parent-channel fallback alone, and manual/fallback profile text are diagnostics only. They must not be substituted for participant runtime readiness, selected-runner proof, visible-surface proof, exact origin proof, `live_readiness`, or production readiness.
- Fallback/manual participant messages may be useful diagnostic evidence, but they must be labeled `fallback_profile_pass` and must not be reported as selected-speaker runner success or ATN live discussion readiness. A selected-runner downgrade is diagnostic/fallback only and does not claim `selected_runner_pass`.
- `atn_discussion_activation_plan` always keeps `live_readiness: false`; it must not read env vars, inspect current Hermes/Discord/profile/gateway state, open sockets, shell out, start daemons, mutate profiles/gateway/Discord/auth/token/provider/model settings, or infer readiness from missing evidence. Do not treat `atn_discussion_activation_plan.live_readiness=false` as a `council.new` blocker by itself. Treat `start_status: blocked` as the actual `council.new` stop signal. If top-level `status: blocked` while `start_status: ready_to_start`, the discussion start gate passed but RUNFIX3 acceptance remains blocked in `runfix3_acceptance_status`.
- Minimum live-local acceptance evidence remains evidence-gated and includes: `runner_invocation_started` from `speaker_selected`, selected-runner submitted canonical `speech` linkage, visible-surface evidence, ARGUE relation counts/diagnostics, eligible-profile-only allow-list evidence, the exact origin `chat_id:thread_id`, expected/posted visible turns by `max_discussion_turns + participant_count + 2`, participant closeouts, moderator synthesis, and explicit no-claim language for production activation. These labels gate acceptance/live-readiness claims, not the basic `council.new` start gate or a second approval prompt. Durable runner failure is a terminal-failure diagnostic and blocks `selected_runner_pass` / live-readiness claims unless a later task explicitly proves a new selected-runner success path.
- For `plugin/LVCOR-005`, one-pass acceptance proof is local explicit evidence only and requires both finalized-success rows `15/4/21` and `5/2/9`. `T20` is only the `15 + 4 + 1` terminal synthesis instance, not a general rule. Success-like rows must prove exact visible-turn count equality, zero runnerless/manual selected turns, complete participant closeouts, and `terminal_phase=finalized`; `unresolved_terminal_blocked` is blocker-path evidence only.
- Visible turns must remain participant-to-participant dialogue, and visible prompt/speech content must stay separated from audit/control identifiers. If drift or metadata leakage cannot be repaired forward after canonical speech exists, close unresolved rather than reporting a normal successful closeout.

For `plugin/RUNFIX-008`, `atn_discussion_activation_plan` also exposes an `operator_evidence_report` from explicit caller-provided `operator_evidence` only:

- `runner_evidence`: selected member, `speaker_selected` event id, `runner_invocation_started_ref`, and any durable runner failure evidence;
- `canonical_speaker_selected_to_speech`: canonical `speaker_selected -> speech` linkage with matching selected member;
- `participant_response`: `speech`, `claims[]`, `stance_links[]`, `contribution_type`, `new_axis_reason`, and optional `evidence[]`;
- `argue_counts`: speech presence plus counts for `claims[]`, `stance_links[]`, `new_axis`, optional `evidence[]`, and contribution types;
- `fallback_disclosure`: `fallback_profile_pass` is diagnostic-only, `full_atn_success` remains false, and missing evidence must be named.

For `plugin/RUNFIX-010`, the report also separates live-visible UX from daemon evidence:

- `requested_output_mode`: Discord-origin requests require `live_visible_thread` by default; non-visible output modes such as `artifact_only`, `daemon_cli_actor_speech`, `activation_planning_only`, local-daemon-only aliases, or transcript/export aliases require a supported `requested_output_mode`, `explicit_non_visible_override=true`, and non-empty `override_reason` before session creation;
- `visible_surface_readiness_report`: exact origin binding result, surface binding, turn delivery probe, visible closeout probe, real profile/gateway replies, CLI-actor-only status, and expected/posted turn counts;
- `final_report_contract`: final reports must separately state `ATN lifecycle finalized`, `Discord visible turns posted: N/expected`, `real profile/gateway replies`, `CLI actor speech only`, participant closeout coverage, moderator synthesis coverage, and repair-forward versus unresolved closeout.

For `plugin/RUNFIX3-003`, the report adds `runfix3_live_thread_proof_report` for separate RUNFIX3 acceptance axes: selected-runner proof chain, participant closeout coverage, moderator synthesis coverage, per-turn delivery-target proof, prompt-envelope proof, dialogue-mode proof, drift status, and final fail-closed proof status. The top-level output now keeps `start_status` separate from overall `status`, and exposes `runfix3_acceptance_status` so `ready_to_start` cannot be mistaken for accepted RUNFIX3 proof.

Missing or ambiguous runner, ARGUE, canonical-link, or origin-binding evidence remains `unproven`/`blocked`. Manual/fallback profile text can explain a blocker, but it is never selected-runner success, discussion-quality success, or live readiness.

For `plugin/RUNFIX-012`, the report adds
`participant_runtime_readiness_report` from explicit caller-provided
`participant_runtime_readiness` only:

- `control_dependency`: must identify `control/RUNFIX-011` with local proof
  status and evidence ref;
- `subscriber_presence`, `cursor_ack_freshness`, and `heartbeat_freshness`:
  prove a runtime is subscribed and current from control diagnostics;
- `attendance_terminal` and `preparation_terminal`: expose terminal success or
  timeout/failure evidence; timeout/failure remains diagnostic and blocks
  readiness;
- `selected_runner_readiness`: requires selected-runner readiness and
  prerequisites;
- `visible_surface_proof`: remains separate from participant runtime evidence.

`start_status=ready_to_start` is the live-visible discussion start signal: the moderator should proceed to `council.new` when the user already requested the discussion and no `start_blocker` remains. `ready_for_approval` is not the live-visible discussion start signal; it is only for bounded apply/mutation or activation-planning scope. The top-level `status` may still be `blocked` when `runfix3_acceptance_status=blocked`, which means RUNFIX3 final acceptance is still fail-closed even though the `council.new` start gate passed.

Neither status means `live_readiness`, live Discord delivery, production activation, or broad rollout.

## Install guidance



For SKILL-2, "install" means obtaining the packaged skill artifact from the
Python package or staging the repository plugin files in a disposable local
fixture. It is not a live profile mutation.

Recommended inspection path:

```python
from atn_plugin.bundled_skills import read_bundled_skill_text

skill_text = read_bundled_skill_text("atn-plugin")
```

Manual operator install, when a later approved workflow allows profile writes:

1. Build or install the Python package from the reviewed plugin revision.
2. Read the packaged `atn-plugin/SKILL.md` with the import-safe helper.
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
- `read_bundled_skill_text("atn-plugin")` returns the bundled `SKILL.md`;
- `plugin.yaml` still lists only the supported tool names and
  `provides_commands: []`;
- the operator guide and unsupported-surfaces docs still say fake/injected only;
- `make check-plugin-load-smoke` passes as local isolated plugin-load smoke only;
- local make gates pass.

## Rollback guidance

Rollback is local and reversible:

1. Restore the previous plugin package revision/version or disable the plugin in
   the non-live profile/test fixture.
2. Confirm plugin-qualified bundled skill loads no longer reference the reverted
   package revision.
3. Rerun local verification.

Do not delete live Hermes state, daemon storage, Discord messages, tokens,
gateway config, sockets, or localhost services as part of SKILL-2 rollback.

## Troubleshooting

| Symptom | Likely cause | Safe response |
| --- | --- | --- |
| Bundled skill cannot be found | Package data missing or wrong resource name | Use `bundled_skill_names()` and `read_bundled_skill_text("atn-plugin")`; verify the package contains `bundled_skills/atn-plugin/SKILL.md`. |
| Skill claims live readiness | Overclaiming docs or stale bundled skill text | Restore the bundled skill text from the package source; SKILL-2 is fake/injected plus local isolated plugin-load smoke only. |
| Slash commands appear | Manifest or entrypoint drift | Restore `provides_commands: []` and verify the root entrypoint registers no commands. |
| `atn_session_status` appears | Unsupported session-status drift | Remove the surface until `session.status.read` fixture/protocol authority exists. |
| ARGUE fields are dropped or inferred from legacy pointers | Contract drift or hidden state inference | Preserve explicit argument-graph fields verbatim and treat `responds_to_event_id` as display-only; do not infer state from Discord/Hermes order. |
| ARGUE support is described as runtime scoring or live pilot readiness | Scope overclaim | Keep local ARGUE schema/tool coverage and local visible relation rendering bounded to fake/injected fixtures and evidence display; runtime validation/scoring, live Discord, production activation, and live-local pilot readiness require separate explicit approval and evidence. |
| A handler tries localhost, a socket, CLI, gateway, auth, token, Discord, or KAB | No-live boundary violation | Fail closed and remove the fallback; default checks must use explicit fake/injected dependencies only. |
| Root plugin load fails with `No module named 'atn_plugin'` | The directory entrypoint is not bootstrapping its bundled `src/` package path | Restore the root entrypoint path bootstrap and rerun `make check-plugin-load-smoke`; do not require operators to supply external `PYTHONPATH`. |
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
