---
name: atn-plugin
description: Use when operating the packaged atn-plugin Hermes adapter, explaining its current fake/injected tool surface, or preparing a non-live install/enable/rollback plan.
version: 0.1.0
author: 17번째 지구 Kkachi
license: MIT
metadata:
  hermes:
    tags: [atn-plugin, kkachi, hermes-plugin, operator-guide, no-live]
    related_skills: []
---

# ATN Plugin Operator Skill

Use this skill when an operator or agent needs to work with the public ATN plugin surface, explain its current safe surface, or prepare a non-live install/enable/rollback plan. This packaged resource is the canonical checked-in ATN bundled skill.

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
6. Treat `atn_discussion_activation_plan` output as a dry-run planner/doctor report only. It can prepare an activation plan from explicit evidence, but it never proves live readiness. For RUNFIX3 live-visible start-gate behavior, output-mode handling, and downgrade decisions, use `atn-moderator/SKILL.md` and `docs/09-skill-and-operator-guide.md` rather than this boundary skill.
7. Treat ARGUE argument-graph support as static/fake/injected schema and tool contract coverage only. The plugin preserves explicit `claims[]`, `stance_links[]`, `contribution_type`, `new_axis_reason`, `evidence[]`, and `hand_raise.target_links[]` fields for daemon/control validation. `responds_to_event_id` remains a legacy display hint and never overrides `stance_links[]`.

## Daemon registry membership boundary

Daemon registry authority remains separate from profile/Discord readiness. For RUNFIX3 live-visible roster validation, planned reconcile requirements, and `council.new` start-gate handling, use `atn-moderator/SKILL.md` and `docs/09-skill-and-operator-guide.md`; this skill keeps only the plugin-surface boundary that registry evidence must come from explicit caller-provided inputs and control-owned reconcile outcomes, not inferred Discord/profile state.

## Moderator live-thread contract owner

For RUNFIX3 live-thread semantics, the normative procedure owners are `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md` and `agent-turn-network-plugin/docs/09-skill-and-operator-guide.md`.
Use this skill for plugin-surface boundaries and cross-links only. Do not create or require a fourth packaged moderation skill, external profile-local flat skill, or legacy `kan-*` bundled skill alias.

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

주유's 2026-06-19 rename-council handoff is registered as `RUNFIX-014` through `RUNFIX-017`. Those rows remain historical proof and dependency context only; they are not the current normative RUNFIX3 live-thread procedure source.

Historical proof references kept for provenance:
1. `control/RUNFIX-014` selected-runner accounting.
2. `plugin/RUNFIX-015` visible-author guard.
3. `control/RUNFIX-016` summary robustness.
4. `plugin/RUNFIX-017` ARGUE quality-required prompts.

For current live-thread report labels, expected turn accounting, selected-runner downgrade handling, and repair-forward versus unresolved closeout, use `atn-moderator/SKILL.md` and `docs/09-skill-and-operator-guide.md`.

## Required ATN companion skills

`atn-plugin` must ship the operator guidance needed to use its
tool surface. Do not leave ATN runtime/operator guidance as ops-only,
profile-local, or external-directory-only skills. The plugin package owns and
registers these bundled companion skills together as read-only, plugin-qualified
skills:

- `atn-plugin`: plugin/operator surface and hard boundaries;
- `atn-moderator`: council preflight, activation planning, lifecycle, visible-surface, and closeout duties;
- `atn-participant`: selected-speaker and participant response duties.

Canonical Hermes loads use the qualified names
`atn-plugin:atn-plugin`,
`atn-plugin:atn-moderator`, and
`atn-plugin:atn-participant`. Do not require flat
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

## Live-visible council contract boundary

This skill is boundary/cross-link only for RUNFIX3 live-thread semantics. For exact preflight, live-thread procedure, dialogue-mode requirements, lifecycle turn formula, selected-runner versus fallback reporting, content/audit separation, and repair-forward versus unresolved closeout, use:
- `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md`
- `agent-turn-network-plugin/docs/09-skill-and-operator-guide.md`

Plugin-surface boundaries for this topic:
- `atn_discussion_activation_plan` remains a dry-run/local planner-doctor surface from explicit caller-provided evidence only. It does not prove live readiness, inspect current Hermes/Discord state, start daemons, or mutate profiles/gateway/Discord/auth/token/provider/model settings.
- The plugin may carry evidence about exact Discord origin binding, visible-surface readiness, participant runtime readiness, and fallback disclosure, but it does not own the live-thread procedure.
- `selected_runner_pass` remains an evidence-derived label from the frozen control contract.
- Do not invent planner/schema/runtime fields or control enforcement semantics reserved for `plugin/RUNFIX3-003` or `control/RUNFIX3-004`.
- Preserve no-live boundaries: no hidden CLI fallback, no plugin-owned lifecycle state, no production/live-readiness claim, and no substitution of Discord/Hermes message order for daemon lifecycle authority.

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
  `atn_plugin/bundled_skills/atn-plugin/SKILL.md` and use the
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
