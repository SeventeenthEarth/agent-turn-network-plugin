---
name: hun-plugin
description: Use when operating the packaged hermes-unified-network-plugin Hermes adapter, explaining its current fake/injected tool surface, or preparing a non-live install/enable/rollback plan.
version: 0.1.0
author: 17번째 지구 Kkachi
license: MIT
metadata:
  hermes:
    tags: [hun-plugin, kkachi, hermes-plugin, operator-guide, no-live]
    related_skills: []
---

# ATN Plugin Operator Skill

Use this skill when an operator or agent needs to work with the public ATN plugin surface, explain its current safe surface, or prepare a non-live install/enable/rollback plan. ATN-005 still owns the checked-in bundled skill id/path rename, so this packaged resource remains under the current `hun-plugin` source path until that task lands.

## Current capability boundary

This skill is bundled with the Python package as documentation and operator
guidance. It does not install itself into a Hermes profile, enable a live
plugin, discover the current Hermes session, or run a daemon.

Supported plugin surfaces in the current package are fake/injected Hermes tools:

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

The plugin manifest must continue to declare `provides_commands: []`. ATN slash
commands, native Discord slash commands, `atn_session_status`, live daemon
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
5. Treat `atn_surface_render_projection` output as a local display projection
   over explicit daemon/control event JSON, never as lifecycle authority. Use
   `visible_transcript` for operator-facing discussion text and keep raw
   cursor/event details in `audit_log`/`rows` evidence.
6. Treat `atn_discussion_activation_plan` output as a dry-run planner/doctor
   report only. It can prepare an activation plan from explicit evidence, but
   it never proves live readiness. For a Discord-origin `live_visible_thread`
   discussion whose start gate passes, `ready_to_start` means the moderator
   should proceed to `council.new` without asking for another approval.
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

## Daemon registry membership gate

Before any `council.new` for a live-visible or cross-team council, operator evidence must separate daemon registry authority from profile/Discord readiness. The selected moderator and each participant must be present/enabled in the loaded daemon registry, or the activation plan must provide `daemon_registry_membership.participants[]` entries showing an unambiguous planned control-owned reconcile for the exact approved roster. Discord allow-list membership, visible-author probes, gateway `running`, plugin tool visibility, and `DISCORD_ALLOW_BOTS=none` do not make a principal valid in the daemon registry.

Accepted planned reconcile evidence needs at least: `principal`, `in_loaded_registry: false`, `planned_reconcile: true`, `mapping_unambiguous: true`, and `wrapper_resolves: true`. Ambiguous mapping, disabled existing principals, unresolved wrappers, or missing loaded-registry evidence block before `council.new`; the control-owned reconcile also validates invalid/reserved principal ids before registry mutation. Do not downgrade to artifact-only or daemon CLI actor speech unless the operator explicitly approves that different mode before session creation. Registry membership persists across council sessions; subscription, heartbeat, cursor ack, attendance/preparation, and selected-runner readiness remain session-scoped runtime gates.

## Moderator hard-rules location

The packaged ATN moderator role skill owns the council moderation hard rules.
Load the public ATN moderator guidance before moderating a live or
live-visible ATN council. Do not create or require a fourth packaged moderation
skill, external profile-local flat skill, or legacy `kan-*` bundled skill alias.

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

Operators should flag a non-opening speech as orphaned when sufficient local
context exists and it has neither a valid `stance_links[]` entry to the prior
claim graph nor `contribution_type: "new_axis"` with a non-empty
`new_axis_reason`. In `quality_required`, the first orphan non-opening speech
fails closed and blocks `discussion_quality_pass`. In `quality_warn`, the same
condition is warning-only diagnostic evidence even if the mechanical
daemon/CLI/plugin lifecycle completes.

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

Mechanical lifecycle pass means the local daemon/CLI/plugin path completed with
replayable events and evidence pointers. Discussion-quality pass additionally
requires grounded relation evidence, visible relation summaries from
`atn_surface_render_projection`, audit relation fields preserved in rows/logs,
non-immediate prior-claim engagement, challenge/refine/synthesize coverage where
relevant, and no runtime noise in visible speech.


## RUNFIX post-pilot guardrails (RUNFIX-014/RUNFIX-015/RUNFIX-016 proof, RUNFIX-017 candidate)

주유's 2026-06-19 rename-council handoff is registered as `RUNFIX-014` through `RUNFIX-017`. `control/RUNFIX-014` and `plugin/RUNFIX-015` have local implementation proof. `control/RUNFIX-016` has local implementation proof under KAH run `run-20260619T083649Z-d10e1f5cc20b` and local commit `9c15d22`. `plugin/RUNFIX-017` has local implementation proof under KAH run `run-20260619T101255Z-189d01ba8b8f` after official color review, Blue synthesis, and final KAH gate. Operators must treat the following as local proof, implementation-candidate evidence, or required planning/acceptance boundaries, not completed runtime capability:

1. `control/RUNFIX-014` selected-runner accounting: a run with `runner_invocation_failed` followed by later canonical `speech` is lifecycle/fallback evidence, not `selected_runner_pass`. Reports must expose runner started/succeeded/failed counts and fallback/manual harness flags.
2. `plugin/RUNFIX-015` visible author guard: plugin KAH run `run-20260619T071526Z-7d2ba33b07d5` adds local `atn_discussion_activation_plan` proof for pre-`council.new` visible-author validation. Explicit caller-provided same-path probes must prove each selected participant posts as the expected profile author. Evidence includes `profile`, expected author source (`registry_snapshot` or approved profile-author map), observed bot/user, `source_env`, `posting_path`, shared/default negative proof, shared-default-then-profile-local env precedence, per-turn Discord message id, selected member, profile author id, and `speech_event_id`. Shared/default or unexpected authors fail closed; the planner does not perform live Discord delivery or runtime/profile/provider/gateway/auth/token/model mutation.
3. `control/RUNFIX-016` summary robustness: KAH run `run-20260619T083649Z-d10e1f5cc20b` has local implementation proof that closeout/summary tooling tolerates `payload.plugin_evidence`, dict/list `payload.evidence`, and missing optional evidence. A finalized lifecycle must not look failed because optional evidence has an alternate shape; this remains fail-closed local proof evidence only, not runtime readiness.
4. `plugin/RUNFIX-017` ARGUE quality-required prompts: non-opening quality-required speeches with sufficient local context must link to caller-provided prior targets through valid `stance_links[]` or justify `contribution_type: "new_axis"` with `new_axis_reason`; prompts should provide compact prior claim graph targets; explicit `discussion_quality` evidence is required for the quality gate; in `quality_required`, the first orphan non-opening speech blocks `discussion_quality_pass`; warning-only behavior is reserved for `quality_warn`, and repeated-orphan counts remain diagnostic evidence.

Final reports must keep these fields separate: `lifecycle_pass`, `selected_runner_pass`, `visible_surface_pass`, `fallback_profile_pass`, `discussion_quality_pass`, `orphan_speech_count`, `linked_speech_count`, `stance_link_count`, `new_axis_count`, Discord visible turns posted, real profile/gateway replies, and shared/default author fallback status.

## Required ATN companion skills

`hermes-unified-network-plugin` must ship the operator guidance needed to use its
tool surface. Do not leave ATN runtime/operator guidance as ops-only,
profile-local, or external-directory-only skills. The plugin package owns and
registers these bundled companion skills together as read-only, plugin-qualified
skills:

- `atn-plugin`: plugin/operator surface and hard boundaries;
- `atn-moderator`: council preflight, activation planning, lifecycle, visible-surface, and closeout duties;
- `atn-participant`: selected-speaker and participant response duties.

Canonical Hermes loads use the qualified names
`hermes-unified-network-plugin:atn-plugin`,
`hermes-unified-network-plugin:atn-moderator`, and
`hermes-unified-network-plugin:atn-participant`. Do not require flat
profile-local copies for the normal ATN plugin path.

Treat a profile where plugin tools are enabled but these companion skills cannot
be loaded by plugin-qualified name, are stale, or are available only from an
unrelated external skill directory as incomplete ATN plugin activation. Fix the
plugin bundled-skill registration or package data instead of asking 주군 to
provide extra manual field-mapping instructions.

For `atn_discussion_activation_plan`, role skills must explicitly tell
moderators to materialize collected evidence into planner fields such as
`participant_profiles[].effective_discord.tools_visible`,
`participant_profiles[].effective_discord.bot_to_bot_enabled`,
`discord_parent_channel.allow_list_inheritance_proven`, and
`visible_surface_readiness`. If those mappings are missing from a bundled role
skill, patch the plugin package; do not blame the moderator profile for a
correct fail-closed `unknown` result.

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

For `live_visible_thread`, do not silently satisfy the request with artifact-only
or daemon CLI actor speech. Also do not require final pilot-acceptance evidence
before `council.new`. If the user has already asked for the ATN discussion and
the start gate passes, do not ask for another approval; start the council.
Classify findings into:

- `start_blocker`: blocks `council.new`;
- `runtime_evidence_pending`: collect during attendance, preparation,
  poll/hand-raise, selected-runner, speech, delivery, and closeout;
- `final_acceptance_unproven`: report as separated closeout labels.

Only `start_blocker` findings block `council.new`: unavailable
daemon/protocol/tool surface, missing or invalid roster, unresolved registry
principals with no unambiguous control-owned reconcile, explicitly unavailable
profile/plugin tool surface, missing target Discord surface, positively detected
bot-to-bot or shared/default-author risk without approval, or unapproved
provider/profile/gateway/auth/token mutation.

Do not treat missing selected-runner proof, participant runtime freshness,
same-path per-turn author linkage, visible turn counts, ARGUE relation counts,
or discussion-quality proof as automatic start blockers. Track them as
`runtime_evidence_pending` or `final_acceptance_unproven` and report them
separately at closeout.

Do not treat `atn_discussion_activation_plan.live_readiness=false` as a
`council.new` blocker by itself. The planner is a pure/local doctor and never
proves live readiness. If its `status` is `blocked`, classify each blocker:
only `start_blocker` findings stop session creation. If evidence is missing but
can be collected without profile/provider/gateway/auth/token mutation, collect
the probe before asking the user.

Final reports must not equate transcript/export success with a visible Discord
discussion. Report these fields separately: `ATN lifecycle finalized`,
`Discord visible turns posted: N/expected`, `real profile/gateway replies`, and
`CLI actor speech only`.

## RUNFIX visible pilot guidance

Control/daemon fixtures and validation remain authoritative. Plugin rendering is
a local visible surface and evidence pointer, not lifecycle state. Live-local
pilots still require explicit profile/plugin/daemon/gateway/Discord approval and
evidence. KAS does not install, own, or activate ATN runtime/plugin/bundled-skill
artifacts.

## RUNFIX discussion activation guidance

`RUNFIX` work separates plugin install/load from ATN discussion activation. A plugin
install does not prove live council readiness. Before any live-local discussion
apply step, produce a dry-run activation plan with: explicit control daemon/socket
or config evidence, participant profiles, selected Discord parent channel,
eligible/excluded profile list, planned allow-list/config changes, rollback,
smoke checks, and the exact approval boundary.

Use `atn_discussion_activation_plan` for that planning/doctor report when a
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

ATN discussion channels are bot-to-bot-free by default. Profiles with effective
bot-to-bot enabled Discord behavior are excluded from ATN discussion allow-lists
unless a later explicit policy approves otherwise. Visible-pilot surface policy
is thread-preferred and parent-channel fallback allowed: first create or use a
dedicated thread under the approved parent channel, then fall back to the parent
channel only when thread creation/posting is unsupported. If the fallback is
used, record the fallback reason in the task brief, ATN surface metadata,
visible closeout, and final report; do not silently normalize channel-only
operation or treat it as no-restart thread readiness.

Reports must label fallback/manual profile evidence as `fallback_profile_pass`.
That evidence never equals selected-speaker runner success or ATN live discussion
readiness. Minimum acceptance/live-readiness evidence remains evidence-gated, not
start-approval-gated: selected-runner
invocation from `speaker_selected`, selected-runner submitted canonical `speech`
linkage, visible-surface evidence, ARGUE relation counts/diagnostics, and explicit
production/non-scope disclaimers. Durable runner failure is a terminal-failure
diagnostic and blocks `selected_runner_pass` / live-readiness claims unless a
later task explicitly proves a new selected-runner success path.

For `plugin/RUNFIX-008`, `atn_discussion_activation_plan` exposes an
`operator_evidence_report` from explicit caller-provided `operator_evidence`
only. The report includes runner evidence, canonical
`speaker_selected -> speech linkage`, participant response fields, ARGUE counts,
RUNFIX labels, and fallback disclosure. Missing or ambiguous runner, ARGUE, or
canonical-link evidence remains `unproven`/`blocked`; fallback/manual profile
text is diagnostic-only and never full ATN success.

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
  `hermes_unified_network_plugin/bundled_skills/hun-plugin/SKILL.md` and use the
  import-safe resource helper instead of profile writes.
- Unexpected slash commands: inspect the manifest and root entrypoint; the
  expected command surface is empty.
- Live-looking environment variables: ignore them for default verification.
  Tests must not fall back to the current Hermes/Discord/daemon environment.
- Session status requests: keep `atn_session_status` deferred until the control
  contract publishes `session.status.read` fixture/protocol authority.
- ARGUE overclaims: do not describe local ARGUE schema/tool coverage or local
  visible relation rendering as runtime scoring, live Discord, production
  activation, live pilot readiness, or daemon/control validation authority.
- Plugin-load smoke requests: run `make check-plugin-load-smoke` and describe
  the result only as local isolated plugin-load smoke.

## Rollback guidance

Rollback is local and reversible: restore the previous plugin package version or
disable the plugin, then rerun the local make gates. Do not delete live Hermes
state, mutate profile-local skill directories, or modify daemon storage as part
of SKILL-2 rollback.
