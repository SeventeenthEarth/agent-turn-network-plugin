# KAN Skill and Operator Guide

## Scope

The packaged KAN operator skills and local compatibility matrix remain the
operator-facing guide for `kkachi-agent-network-plugin`. The bundled skills live
inside the Python package:

```text
src/kkachi_agent_network_plugin/bundled_skills/kan-plugin/SKILL.md
src/kkachi_agent_network_plugin/bundled_skills/kan-moderator/SKILL.md
src/kkachi_agent_network_plugin/bundled_skills/kan-participant/SKILL.md
```

The package exposes import-safe resource helpers and registers these read-only plugin-provided skills when Hermes loads the plugin. Canonical activation loads them by plugin-qualified names such as `kkachi-agent-network-plugin:kan-plugin`, `kkachi-agent-network-plugin:kan-moderator`, and `kkachi-agent-network-plugin:kan-participant`; it must not require profile-local flat copies. The bundled source remains canonical; ops external skill directories are not required for KAN plugin use.

This guide does not enable a live plugin, contact a daemon, modify the sibling
control repo, or prove production activation, live plugin readiness, or live
Discord readiness. The
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
- `kan_discussion_activation_plan`
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
6. Treat `kan_discussion_activation_plan` output as a dry-run planner/doctor
   report only. It may classify readiness for explicit approval, but it never
   proves live readiness or authorizes apply/pilot scope.
7. Treat ARGUE argument-graph support as static/fake/injected schema and tool
   contract coverage only. `claims[]`, `stance_links[]`, `contribution_type`,
   `new_axis_reason`, `evidence[]`, and `hand_raise.target_links[]` are
   preserved for daemon/control validation, while `responds_to_event_id` remains
   a legacy display hint that never overrides `stance_links[]`.

## Daemon registry membership gate

Before any `council.new` for a live-visible or cross-team council, operator evidence must separate daemon registry authority from profile/Discord readiness. The selected moderator and each participant must be present/enabled in the loaded daemon registry, or the activation plan must provide `daemon_registry_membership.participants[]` entries showing an unambiguous planned control-owned reconcile for the exact approved roster. Discord allow-list membership, visible-author probes, gateway `running`, plugin tool visibility, and `DISCORD_ALLOW_BOTS=none` do not make a principal valid in the daemon registry.

Accepted planned reconcile evidence needs at least: `principal`, `in_loaded_registry: false`, `planned_reconcile: true`, `mapping_unambiguous: true`, and `wrapper_resolves: true`. Ambiguous mapping, disabled existing principals, unresolved wrappers, or missing loaded-registry evidence block before `council.new`; the control-owned reconcile also validates invalid/reserved principal ids before registry mutation. Do not downgrade to artifact-only or daemon CLI actor speech unless the operator explicitly approves that different mode before session creation. Registry membership persists across council sessions; subscription, heartbeat, cursor ack, attendance/preparation, and selected-runner readiness remain session-scoped runtime gates.

## KAN council moderation hard rules

For any live KAN council, operator guidance must keep the discussion
lifecycle-first, per-turn selected, and daemon-event authoritative. These rules
do not authorize live daemon/runtime activation, Discord delivery, profile
mutation, or live readiness by themselves.

1. Do not predeclare or hard-code a complete live speaker order. A Discord or
   Hermes-visible council must not be run as a fixed-order simulated debate.
2. Complete lifecycle prerequisites before turn discussion: `council.new`,
   `request_attendance`, terminal attendance records for required participants,
   `lock_agenda`, `prepare`, then `ready` or `prepared_partial` evidence.
3. For each turn, open a `poll` or hand-raise evaluation, evaluate current hand
   raises, and record a justified daemon `speaker_selected` event before
   participant speech.
4. Use `relevance` as the default selection mode. `targeted`, `random`,
   `moderator_direct`, and `role_order` are allowed only as per-turn
   `speaker_selected` modes with a reason; `role_order` also needs bounded round
   evidence. Do not ban `role_order`, but never use it as a predeclared full
   live debate order.
5. Discord/Hermes replies are not council state. They become council speech only
   when backed by typed daemon `speech` events.
6. Moderator substantive opinions must be recorded as participant-style turns,
   not hidden in moderation text.
7. If a fixed-order flow starts by mistake before any `speech` event exists,
   cancel and restart. If `speech` already exists, repair forward with a
   moderator intervention and do not rewrite history.

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
   summaries from `kan_surface_render_projection` are readable, audit fields keep
   `claims[]`, `stance_links[]`, `contribution_type`, `event_id`, `turn`,
   `speaker`, and `speech`, participants engage non-immediate prior claims where
   appropriate, challenge/refine/synthesize relations appear when the scenario
   requires them, and runtime noise is absent from visible speech.

A live-local pilot needs explicit approval and evidence for the real participant
profiles, plugin enablement, daemon/CLI path, gateway/tool visibility, and any
visible Discord surface. Do not treat this operator guide, local isolated
plugin-load smoke, or fake/injected fixture harness as live readiness.

KAS does not install, own, activate, or gate KAN runtime/plugin/bundled-skill artifacts.
The KAN plugin package owns the bundled guidance source and exposes it through
Hermes plugin-qualified skills. KAN development and KAN use must not depend on
profile-local flat copies or profile-local KAS development phase skills being
present.


## RUNFIX post-pilot guardrails (RUNFIX-014/RUNFIX-015/RUNFIX-016 proof, RUNFIX-017 candidate)

주유's 2026-06-19 rename-council handoff is registered as `RUNFIX-014` through `RUNFIX-017`. `control/RUNFIX-014` and `plugin/RUNFIX-015` have local implementation proof. `control/RUNFIX-016` has local implementation proof under KAH run `run-20260619T083649Z-d10e1f5cc20b` and local commit `9c15d22`. `plugin/RUNFIX-017` has local implementation proof under KAH run `run-20260619T101255Z-189d01ba8b8f` after official color review, Blue synthesis, and final KAH gate. Operators must treat the following as local proof, implementation-candidate evidence, or required planning/acceptance boundaries, not completed runtime capability:

1. `control/RUNFIX-014` selected-runner accounting: control KAH run `run-20260619T051710Z-8e1f6efb61ec` provides local implementation proof that a run with `runner_invocation_failed` followed by later fallback/manual canonical `speech` is lifecycle/fallback evidence, not `selected_runner_pass`. Reports must consume the control accounting labels and expose runner started/succeeded/failed counts plus fallback/manual harness flags.
2. `plugin/RUNFIX-015` visible author guard: plugin KAH run `run-20260619T071526Z-7d2ba33b07d5` adds local `kan_discussion_activation_plan` proof for pre-`council.new` visible-author validation. Explicit caller-provided same-path probes must prove each selected participant posts as the expected profile author. Evidence includes `profile`, expected author source (`registry_snapshot` or approved profile-author map), observed bot/user, `source_env`, `posting_path`, shared/default negative proof, shared-default-then-profile-local env precedence, per-turn Discord message id, selected member, profile author id, and `speech_event_id`. Shared/default or unexpected authors fail closed; the planner does not perform live Discord delivery or runtime/profile/provider/gateway/auth/token/model mutation.
3. `control/RUNFIX-016` summary robustness: KAH run `run-20260619T083649Z-d10e1f5cc20b` has local implementation proof that closeout/summary tooling tolerates `payload.plugin_evidence`, dict/list `payload.evidence`, and missing optional evidence. A finalized lifecycle must not look failed because optional evidence has an alternate shape; this remains fail-closed local proof evidence only, not runtime readiness.
4. `plugin/RUNFIX-017` ARGUE quality-required prompts: non-opening quality-required speeches with sufficient local context must link to caller-provided prior targets through valid `stance_links[]` or justify `contribution_type: "new_axis"` with `new_axis_reason`; prompts should provide compact prior claim graph targets; explicit `discussion_quality` evidence is required for the quality gate; in `quality_required`, the first orphan non-opening speech blocks `discussion_quality_pass`; warning-only behavior is reserved for `quality_warn`, and repeated-orphan counts remain diagnostic evidence.

Final reports must keep these fields separate: `lifecycle_pass`, `selected_runner_pass`, `visible_surface_pass`, `fallback_profile_pass`, `discussion_quality_pass`, `orphan_speech_count`, `linked_speech_count`, `stance_link_count`, `new_axis_count`, Discord visible turns posted, real profile/gateway replies, and shared/default author fallback status.

## RUNFIX activation guidance

`RUNFIX` distinguishes plugin installation from live-local KAN discussion activation.

- Plugin install/load proves only that the packaged plugin surface can be discovered and its declared tools can be used in the approved Hermes profile.
- Discussion activation requires an explicit dry-run plan before any apply step. The `kan_discussion_activation_plan` tool can build the planner/doctor report from caller-provided evidence: control daemon/socket/config evidence, participant profile list, selected Discord parent channel, effective Discord profile eligibility, planned allow-list/config changes, rollback, smoke commands, and approval boundary.
- Profiles with effective bot-to-bot enabled Discord behavior are excluded from KAN discussion allow-lists by default. Report every excluded profile and reason/remediation; `allow_list_targets` must include eligible profiles only.
- Visible-pilot surface policy is thread-preferred and parent-channel fallback allowed. Create or use a dedicated thread under the approved parent channel first. If thread creation/posting is unsupported, use the approved parent channel directly as a fallback, but record `fallback_reason` in the task brief, KAN surface metadata, visible closeout, and final report. Parent-channel fallback is not no-restart thread readiness, and manual participant messages remain diagnostic-only unless canonical KAN event linkage is also proven.
- Discord-origin council requests default to `live_visible_thread` output. Do not silently satisfy a Discord thread request with artifact-only daemon CLI actor speech. If the operator explicitly asks for `artifact_only`, `daemon_cli_actor_speech`, or transcript/export-only output, record that confirmation before `council.new`; otherwise fail closed before session creation when live visible output cannot be proven.
- Before starting a live visible council, record `visible_surface_readiness`: bound thread or approved parent-channel fallback with `fallback_reason`, turn-posting probe for the selected-speaker/profile-send path or approved fallback poster, visible closeout probe, `real_profile_gateway_replies: true`, and `cli_actor_speech_only: false`. Missing runner/profile-send, Discord target, profile allow-list, or gateway posting proof blocks the live visible council rather than downgrading to artifact-only.
- For `plugin/RUNFIX-012`, also provide explicit `participant_runtime_readiness` from `control/RUNFIX-011` diagnostics. Required classes are control task/status/evidence ref, subscriber presence, cursor ack freshness, heartbeat freshness, attendance and preparation terminal evidence, selected-runner readiness/prerequisites, and visible-surface proof as a separate evidence class.
- Gateway liveness, transcript/export artifacts, parent-channel fallback alone, and manual/fallback profile text are diagnostics only. They must not be substituted for participant runtime readiness, selected-runner proof, visible-surface proof, `live_readiness`, or production readiness.
- Fallback/manual participant messages may be useful diagnostic evidence, but they must be labeled `fallback_profile_pass` and must not be reported as selected-speaker runner success or KAN live discussion readiness.
- `kan_discussion_activation_plan` always keeps `live_readiness: false`; it must not read env vars, inspect current Hermes/Discord/profile/gateway state, open sockets, shell out, start daemons, mutate profiles/gateway/Discord/auth/token/provider/model settings, or infer readiness from missing evidence.

Minimum live-local readiness evidence remains approval-gated and includes: `runner_invocation_started` from `speaker_selected`, selected-runner submitted canonical `speech` linkage, visible-surface evidence, ARGUE relation counts/diagnostics, eligible-profile-only allow-list evidence, and explicit no-claim language for production activation. Durable runner failure is a terminal-failure diagnostic and blocks `selected_runner_pass` / live-readiness claims unless a later task explicitly proves a new selected-runner success path.

For `plugin/RUNFIX-008`, `kan_discussion_activation_plan` also exposes an
`operator_evidence_report` from explicit caller-provided `operator_evidence`
only:

- `runner_evidence`: selected member, `speaker_selected` event id,
  `runner_invocation_started_ref`, and any durable runner failure evidence;
- `canonical_speaker_selected_to_speech`: canonical
  `speaker_selected -> speech` linkage with matching selected member;
- `participant_response`: `speech`, `claims[]`, `stance_links[]`,
  `contribution_type`, `new_axis_reason`, and optional `evidence[]`;
- `argue_counts`: speech presence plus counts for `claims[]`,
  `stance_links[]`, `new_axis`, optional `evidence[]`, and contribution types;
- `fallback_disclosure`: `fallback_profile_pass` is diagnostic-only,
  `full_kan_success` remains false, and missing evidence must be named.

For `plugin/RUNFIX-010`, the report also separates live-visible UX from daemon
evidence:

- `requested_output_mode`: Discord-origin requests default to
  `live_visible_thread` unless explicitly confirmed as `artifact_only` or
  `daemon_cli_actor_speech` before session creation;
- `visible_surface_readiness_report`: surface binding, turn delivery probe,
  visible closeout probe, real profile/gateway replies, CLI-actor-only status,
  and expected/posted turn counts;
- `final_report_contract`: final reports must separately state
  `KAN lifecycle finalized`, `Discord visible turns posted: N/expected`,
  `real profile/gateway replies`, and `CLI actor speech only`.

Missing or ambiguous runner, ARGUE, or canonical-link evidence remains
`unproven`/`blocked`. Manual/fallback profile text can explain a blocker, but it
is never selected-runner success, discussion-quality success, or live readiness.

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

`ready_for_approval` is only a bounded planner/operator status. It never means
`live_readiness`, live Discord delivery, production activation, or broad rollout.

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
| Bundled skill cannot be found | Package data missing or wrong resource name | Use `bundled_skill_names()` and `read_bundled_skill_text("kan-plugin")`; verify the package contains `bundled_skills/kan-plugin/SKILL.md`. |
| Skill claims live readiness | Overclaiming docs or stale bundled skill text | Restore the bundled skill text from the package source; SKILL-2 is fake/injected plus local isolated plugin-load smoke only. |
| Slash commands appear | Manifest or entrypoint drift | Restore `provides_commands: []` and verify the root entrypoint registers no commands. |
| `kan_session_status` appears | Unsupported session-status drift | Remove the surface until `session.status.read` fixture/protocol authority exists. |
| ARGUE fields are dropped or inferred from legacy pointers | Contract drift or hidden state inference | Preserve explicit argument-graph fields verbatim and treat `responds_to_event_id` as display-only; do not infer state from Discord/Hermes order. |
| ARGUE support is described as runtime scoring or live pilot readiness | Scope overclaim | Keep local ARGUE schema/tool coverage and local visible relation rendering bounded to fake/injected fixtures and evidence display; runtime validation/scoring, live Discord, production activation, and live-local pilot readiness require separate explicit approval and evidence. |
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
