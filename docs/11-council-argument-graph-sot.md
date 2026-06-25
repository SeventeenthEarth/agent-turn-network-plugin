# Plugin Council Argument Graph SOT

Status: Blue-authored plugin SOT draft for `ARGUE` implementation planning. This document is the plugin-side durable source of truth for ATN council discussion-quality surfaces. It is not an implementation-complete claim and does not enable live/default/production runtime behavior by itself.

Date: 2026-06-15
Owner: 마초 / `macho` for the bounded ATN plugin lane
Companion control SOT: `../../agent-turn-network-control/docs/25-council-argument-graph-sot.md`

## 1. Purpose

ATN council discussions must preserve evidence that participants engage each other's claims rather than only producing valid-looking turn logs. The control daemon owns event/state authority and validation, but the plugin owns the Hermes participant-agent tool surface that receives selected participant responses, submits council writes, and renders visible discussion evidence.

This plugin SOT makes the plugin side independently complete for `ARGUE` work. A reader should be able to implement or review the plugin tasks from this document without opening the control SOT first, while still treating the control SOT and fixtures as the authority for daemon protocol semantics.

The failed quality pattern this SOT prevents is:

```text
participant agents are selected and submit speech,
but plugin schemas, prompts, handlers, or visible rendering do not require or preserve
how each speech supports, challenges, refines, extends, questions, or synthesizes prior claims.
```

## 2. Authority and boundary

### 2.1 ATN independence

ATN is independent of KAS. KAS does not install, own, or activate ATN control, ATN plugin, ATN bundled operator guidance, or ATN participant profile state.

### 2.2 Plugin authority

`hermes-unified-network-plugin` owns:

- Hermes participant-agent tool schemas and handlers;
- daemon-client submission of typed council command envelopes;
- local argument-graph argument validation before a command is submitted, where the validation can be performed from caller-provided selected-event/projection context;
- selected participant response framing for `atn_selected_participant_response`;
- fail-closed filtering of runtime warning/noise before it becomes visible `speech` text;
- visible surface rendering of daemon-provided relation evidence;
- packaged ATN operator guidance bundled in this plugin package.

The plugin must not become a second lifecycle state authority, must not infer council state from Discord order, and must not hide CLI/daemon fallback behavior.

### 2.3 Control dependency

`agent-turn-network-control` owns:

- daemon event/state authority;
- canonical protocol schemas and conformance fixtures;
- append-time validation for `claims[]`, `stance_links[]`, `contribution_type`, and `new_axis_reason`;
- session-level `discussion_quality` mode behavior;
- moderator policy and scoring hooks;
- transcript/export/projection semantics that define machine-readable relation evidence.

The plugin must consume control fixtures rather than inventing incompatible daemon-owned shapes. Plugin tasks may progress against docs and fakes only when the task explicitly records that the relevant control fixture or daemon behavior is not yet available.

### 2.4 Profile activation boundary

Actual Hermes profile plugin enablement, participant profile refresh, gateway restart, Discord delivery, or profile-local copying/registering of packaged operator guidance is an explicit activation flow. It is not implied by this SOT and requires separate approval and evidence.

## 3. Design principle

The durable plugin requirement is: **participant-facing tool calls and visible rendering must preserve meaningful engagement with the prior claim graph**.

Allowed and desired behavior:

- A selected participant may support a claim from several turns earlier.
- A selected participant may challenge one prior claim while extending another.
- A selected participant may synthesize several prior claims into a decision frame.
- A selected participant may open a new axis only when it provides a reason.

Rejected behavior in quality-required plugin paths:

- schemas that accept a post-opening speech with no relation evidence and no justified `new_axis`;
- participant-response prompts that ask for a generic mini-essay instead of structured claim engagement;
- plugin handlers that turn runtime warnings, max-iteration notices, or wrapper metadata into visible participant speech;
- visible renderers that drop `claims[]` or `stance_links[]` even when the daemon projection supplies them;
- plugin-side inference of relations from Discord replies, timestamps, or message order.

## 4. Core concepts the plugin must support

### 4.1 Claim

A `claim` is a concise assertion or decision-relevant point made by a council participant in a `speech` event.

Minimum shape accepted by ARGUE-capable plugin surfaces:

```json
{
  "claim_id": "T03.C1",
  "summary": "Fail-closed validation is required before visible pilot acceptance.",
  "kind": "requirement"
}
```

Plugin rules:

- `claim_id` must be a non-empty string unique within the current speech payload.
- Preferred local form is `T<turn>.C<n>` for human readability, but the plugin must preserve any daemon-accepted string rather than rewriting it.
- After daemon append, the canonical reference is `(speech.event_id, claim_id)`.
- `summary` must be a non-empty concise string for visible rendering and review.
- If `kind` is present, the plugin accepts only: `observation`, `requirement`, `risk`, `decision_frame`, `evidence`, `open_question`, `proposal`.

### 4.2 Stance link

A `stance_link` records how the current speech relates to an earlier speech or claim.

Minimum shape accepted by ARGUE-capable plugin surfaces:

```json
{
  "target_event_id": "evt_speech_T02",
  "target_claim_id": "T02.C1",
  "stance": "challenge",
  "rationale": "The cost concern is valid, but it does not justify accepting an unverifiable pilot."
}
```

Plugin rules:

- `target_event_id` must be a non-empty string.
- `target_claim_id` is required when selected-event/projection context exposes claims for the target speech; it may be omitted only for legacy speech that has no claim extraction.
- The plugin may validate target existence/order only from caller-provided selected-event/projection context or control fixtures. It must not read private daemon storage or infer target order from Discord messages.
- `rationale` is required in quality-required plugin paths.

Allowed `stance` values:

- `support`
- `challenge`
- `refine`
- `extend`
- `synthesize`
- `question`
- `risk_addition`
- `decision_frame`

`new_axis` is not a stance link because it has no prior target. It is represented as `contribution_type: "new_axis"` with `new_axis_reason`.

### 4.3 Legacy `responds_to_event_id` relationship

Existing `speech.payload.responds_to_event_id` is a coarse compatibility pointer. `stance_links[]` is the argument-graph relation authority for new ARGUE-capable plugin clients.

Plugin rules:

- If both fields are present, `responds_to_event_id` must either equal one `stance_links[].target_event_id` or be treated as a legacy display hint with no validation authority.
- New quality-aware plugin validation and rendering must use `stance_links[]` rather than inferring stance from `responds_to_event_id`.
- Existing readers may continue displaying `responds_to_event_id`, but plugin export/render paths must not drop `stance_links[]`.
- `control/ARGUE-002` must publish fixtures for legacy-only and dual-field speech so `plugin/ARGUE-001` can preserve compatibility without inventing control-owned semantics.

### 4.4 Contribution type

`contribution_type` records the primary role of the current speech.

Allowed values:

- `support`
- `challenge`
- `refine`
- `extend`
- `synthesize`
- `question`
- `risk_addition`
- `decision_frame`
- `new_axis`

Plugin rules:

- One primary `contribution_type` is required in quality-required plugin paths.
- `contribution_type: "synthesize"` requires at least two valid stance links when the plugin has enough context to validate locally; otherwise the daemon must be allowed to reject it.
- `contribution_type: "new_axis"` requires non-empty `new_axis_reason`.

### 4.5 Orphan speech

An orphan speech is a non-opening speech that has neither:

- a valid `stance_links[]` entry to the prior claim graph, nor
- `contribution_type: "new_axis"` with a valid `new_axis_reason`.

In compatibility/default paths, the plugin may submit orphan speech if the daemon mode allows it. In quality-required plugin paths, the plugin must reject orphan speech before submission when the selected-event/projection context is sufficient to identify it.

## 5. Plugin schema requirements

### 5.1 `atn_council_command`

`atn_council_command` must allow ARGUE-capable `council.hand_raise` and `council.speak` payloads without weakening existing command-envelope rules.

For `council.speak`, the plugin must accept and preserve these additive speech fields:

```json
{
  "claims": [
    {
      "claim_id": "T03.C1",
      "summary": "Fail-closed traceability is required before pilot acceptance.",
      "kind": "requirement"
    }
  ],
  "stance_links": [
    {
      "target_event_id": "evt_T01_speech",
      "target_claim_id": "T01.C1",
      "stance": "support",
      "rationale": "Traceability is the right acceptance axis."
    }
  ],
  "contribution_type": "support",
  "new_axis_reason": null,
  "evidence": []
}
```

For `council.hand_raise`, the plugin must accept and preserve preferred ARGUE target links:

```json
{
  "intent": "challenge",
  "target_links": [
    {
      "target_event_id": "evt_T02_speech",
      "target_claim_id": "T02.C1",
      "stance": "challenge"
    }
  ],
  "relevance": 5,
  "urgency": 4,
  "evidence_summary": "Cost concern conflicts with fail-closed pilot criteria."
}
```

`target_event_ids[]` and `target_claim_ids[]`, if present for compatibility, are display hints only and must not be treated as independent parallel arrays for validation.

### 5.2 `atn_selected_participant_response`

`atn_selected_participant_response` is the most important plugin-side ARGUE surface because it turns participant-agent output into a daemon `council.speak` command.

The tool must require or receive enough context to prove:

- selected session id and selected participant/member id;
- selected event id / selected cursor;
- selected turn, when available;
- available prior claim graph or daemon projection summary;
- selected moderator reason or graph need, when available;
- participant response speech text separated from wrapper/runtime metadata;
- participant-provided `claims[]`, `stance_links[]`, `contribution_type`, and optional `new_axis_reason` in quality-required mode.

Fail-closed conditions:

- selected participant identity does not match the caller-supplied selected-event/provenance context;
- speech text is empty after wrapper/runtime metadata is removed;
- speech text contains visible runtime warning/noise prefixes such as warning logs, max-iteration notices, or tool-run diagnostics;
- quality-required mode is declared and required relation fields are missing or malformed;
- `contribution_type: "new_axis"` lacks `new_axis_reason`;
- `contribution_type: "synthesize"` has fewer than two stance links when local context is available;
- provided target claim ids contradict caller-provided prior-claim context;
- handler would need to infer lifecycle state from Discord/Hermes message order.

The handler may submit only after local validation passes. It must ack the selected cursor only after the `council.speak` submit succeeds, preserving the existing PARTC selected-response rule.

### 5.3 Tool response envelopes

ARGUE-capable plugin handlers must keep existing JSON-string response envelopes:

- success: `ok: true`, `tool`, `live_readiness`, `data`;
- failure: `ok: false`, `tool`, `live_readiness: false`, `error.category`, `error.message`, and `error.retryable`.

ARGUE validation failures should use `validation` unless the failure is due to missing control feature/fixture compatibility, in which case `compatibility` is appropriate.

## 6. Participant response framing

Packaged plugin guidance and future participant prompts must instruct selected participants to produce:

1. concise visible speech;
2. one or more explicit claims when quality mode requires claims;
3. stance links to specific prior event/claim ids when responding to prior claims;
4. `contribution_type` from the allowed vocabulary;
5. `new_axis_reason` only when opening a necessary new axis;
6. evidence pointers outside the speech text when evidence is referenced.

The participant prompt must not pre-script a full round-robin `TURN_PLAN` for all speakers. It may summarize unresolved graph needs and ask the selected participant to address the relevant claim ids.

## 7. Visible rendering requirements

`atn_surface_render_projection` must render daemon/control projection data without becoming lifecycle authority.

Minimum human rendering for an ARGUE speech row:

```text
T03 방통 — challenge
↳ support T01.C1 주유: Traceability is the right acceptance axis.
↳ challenge T02.C1 사마의: Cost risk shapes rollout but does not remove evidence requirements.
Claim T03.C1: Fail-closed traceability is required before pilot acceptance.
```

Minimum machine/audit fields preserved in rendered rows or audit output:

- `event_id`
- `turn`
- `speaker`
- `speech`
- `claims[]`
- `stance_links[]`
- `contribution_type`
- quality diagnostics, if supplied by the daemon projection

Renderer rules:

- sort by daemon cursor/order authority only;
- do not infer links from Discord replies, timestamps, or message order;
- preserve relation fields in audit output even if the human-visible text is compact;
- visibly mark daemon-supplied quality warnings without rewriting speech text;
- keep `live_readiness: false` unless a separately approved live task proves otherwise.

## 8. Packaged operator guidance requirements

The bundled plugin operator guidance must explain:

- what ARGUE relation evidence is;
- how selected participants should format relation-aware responses;
- how operators can identify orphan speech or repeated ungrounded new-axis behavior;
- that control/daemon fixtures and validation are authoritative;
- that plugin rendering is a visible surface and evidence pointer, not lifecycle state;
- that profile activation and live Discord pilots remain separate approval-gated flows.

Guidance must not say KAS installs, owns, or activates ATN artifacts.

## 9. Conformance fixture dependency

Control must publish fixtures covering at least:

1. valid opening `new_axis` with reason;
2. valid support to a prior claim several turns earlier;
3. valid challenge to one prior claim and support of another in the same speech;
4. valid synthesize with two or more prior targets;
5. valid dual-field speech containing both legacy `responds_to_event_id` and ARGUE `stance_links[]`;
6. valid `hand_raise.payload.target_links[]` pairing event id, claim id, and intended stance;
7. invalid future reference;
8. invalid cross-session reference;
9. invalid unknown `target_claim_id`;
10. invalid `new_axis` without reason;
11. invalid synthesize with fewer than two targets;
12. invalid quality-required missing or empty `claims[]` after the opening window when `require_claims` is true;
13. invalid runtime/system-noise speech payload such as warning prefixes or max-iteration noise when it would become visible speech;
14. quality-required orphan speech after opening;
15. quality-warn orphan speech accepted with diagnostics;
16. visible transcript/export preserving relation graph fields.

Plugin tasks must consume these fixtures for schema, handler, and rendering tests. If a plugin task runs before a fixture exists, it must use a clearly labeled local fake fixture and keep live/control compatibility completion blocked until control evidence exists.

## 10. Plugin ARGUE implementation DAG

The plugin-side DAG is sequentially downstream from control where control-owned protocol authority is required:

```text
control/ARGUE-001  Council argument graph SOT and roadmap/index links
  -> control/ARGUE-002  Protocol shape and conformance fixtures
      -> plugin/ARGUE-001  Plugin schema/client/tool contract updates
  -> control/ARGUE-003  Daemon/CLI validation and moderator scoring hooks
      -> plugin/ARGUE-002  Participant response generation and fail-closed handler behavior
  -> control/ARGUE-004  Transcript/export/projection relation preservation
      -> plugin/ARGUE-003  Visible relation rendering
  -> control/ARGUE-005  Control integration verification gate
      + plugin/ARGUE-004  Packaged operator guidance and pilot harness notes
          -> ARGUE-LIVE-001  Approved live-local quality pilot
```

Sequential development order does not make the plugin documentation optional. The plugin SOT, roadmap, docs index, and docs map must exist before plugin implementation tasks start, so downstream implementers do not rely on control-doc-only context.

## 11. Plugin task acceptance criteria

### 11.1 `plugin/ARGUE-001` schema/client/tool contract updates

Acceptance requires:

- plugin schemas allow and preserve `claims[]`, `stance_links[]`, `contribution_type`, `new_axis_reason`, `evidence[]`, and `hand_raise.target_links[]`;
- local validation rejects malformed ARGUE fields before transport when deterministically checkable;
- legacy `responds_to_event_id` remains a compatibility display hint and does not override `stance_links[]`;
- fake/conformance tests cover valid and invalid ARGUE payloads;
- docs and operator guidance identify unsupported/live boundaries.

### 11.2 `plugin/ARGUE-002` participant response generation and fail-closed handler behavior

Acceptance requires:

- `atn_selected_participant_response` frames selected participant output into structured ARGUE fields;
- selected participant identity/provenance is checked against caller-provided selection context;
- runtime warning/noise text fails closed before visible speech submission;
- quality-required orphan speech fails closed when local context is sufficient;
- selected cursor ack occurs only after speak submit succeeds;
- no CLI fallback, Discord-state inference, profile mutation, gateway/auth/token/provider mutation, or live readiness claim is introduced.

### 11.3 `plugin/ARGUE-003` visible relation rendering

Acceptance requires:

- `atn_surface_render_projection` renders human-readable relation summaries;
- audit output preserves machine-readable relation fields;
- daemon-supplied quality diagnostics are shown without rewriting speech;
- renderer remains pure/local and uses daemon cursor/order authority only;
- tests cover multi-claim support/challenge/synthesis and orphan-warning rendering.

### 11.4 `plugin/ARGUE-004` packaged operator guidance and pilot harness notes

Acceptance requires:

- bundled operator guidance explains ARGUE response formatting and review signals;
- pilot harness notes distinguish mechanical lifecycle pass from discussion-quality pass;
- docs state that live-local pilot requires explicit profile/plugin/daemon/gateway/Discord approval and evidence;
- no KAS install/ownership claim is introduced.

## 12. Discussion-quality pilot criteria

A future visible live-local pilot may claim discussion-quality success only when evidence shows:

- actual named participant profiles had ATN plugin/tool visibility before the run;
- daemon/CLI event stream is authoritative and replayable;
- each non-opening speech in quality-required mode has valid relation evidence or justified `new_axis`;
- at least one relation targets a claim more than one turn earlier;
- at least two stance categories appear across the discussion, with one of them being `challenge`, `refine`, or `synthesize`;
- no runtime warning/noise appears as visible participant speech;
- transcript/export and visible plugin projection both show the relation graph;
- final reporting separates mechanical lifecycle pass from discussion-quality pass.

`ARGUE-LIVE-001` must not run until the control and plugin sides both pass their local gates and actual participant profile activation is separately verified.

## 13. Non-goals

This SOT does not:

- enable production/live readiness;
- authorize gateway, provider, token, profile, Discord, daemon runtime, or plugin activation mutation;
- require KAS to install or own ATN artifacts;
- force direct reply to the immediately previous turn;
- require automatic natural-language claim extraction in the first implementation slice;
- authorize hidden fallback from plugin to CLI or from visible surface to lifecycle state;
- make plugin-rendered output the source of lifecycle truth.

## 14. Open implementation decisions

These are later ARGUE task decisions, not blockers for this SOT:

- exact JSON schema nesting for selected participant response context;
- whether `atn_council_command` and `atn_selected_participant_response` share one ARGUE validator module or separate command-specific validators;
- exact renderer compactness controls for long multi-claim discussions;
- whether local fake fixtures live under plugin tests or a copied control conformance-fixture mirror until `control/ARGUE-002` lands;
- exact operator-guide examples for Korean/English mixed participant responses.
