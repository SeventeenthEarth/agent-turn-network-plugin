---
name: atn-participant
description: "Use when acting as a selected ATN council participant: produce wrapper-proven visible speech, ARGUE claims/stance links, evidence fields, and fail-closed selected-member responses for canonical daemon speech submission."
version: 0.1.0
author: 17번째 지구 Kkachi
license: MIT
metadata:
  hermes:
    tags: [atn, Agent Turn Network, participant, council, selected-speaker, argue]
    related_skills: [atn-plugin]
---

# ATN Participant Skill

Use this skill when you are a selected ATN participant, selected-speaker runner, or participant profile asked to respond in a daemon-governed ATN council. Public docs and checked-in bundled skill resources now use the ATN skill names `atn-participant` and `atn-plugin`.

## Authority and boundary

- Canonical ATN discussion/operator source: `atn-plugin/src/atn_plugin/bundled_skills/atn-plugin/SKILL.md`.
- The daemon owns council lifecycle, selection, stream cursors, speech events, and validation.
- The participant must not simulate another member, substitute a role prompt, or turn wrapper/runtime logs into speech.
- A Discord/Hermes chat message alone is not council speech. It must be submitted as canonical daemon `speech` through the selected participant path.
- Fail closed on member mismatch, role substitution, missing selected frame/cursor, insufficient required local context, unknown prior claim targets, or missing runner evidence.

## Selected-speaker contract

When selected by a `speaker_selected` stream frame:

1. Confirm `speaker_selected_frame.event.type == "speaker_selected"`.
2. Confirm `selected_member` matches the frame target and your participant identity.
3. Confirm `participant_response.source == "control_membr_evidence"`.
4. Confirm `participant_response.member == selected_member`.
5. Confirm `participant_response.role_substitution == false`.
6. Preserve runner evidence: invocation id, started event id, terminal event id, terminal event type `participant_response`, adapter kind `hermes-agent`, and wrapper binding evidence.
7. Submit through `atn_selected_participant_response` only when all checks pass. The tool submits canonical `council.speak` and then acks the selected stream cursor after submit success.

Never acknowledge the selected cursor before canonical speech submit succeeds.

## Participant response shape

Keep visible text and structured evidence separate.

Required or expected fields:

```json
{
  "speech": "Visible participant answer only; no wrapper logs, runtime warnings, or role-substitution text.",
  "claims": [
    {
      "claim_id": "T03.C1",
      "summary": "A concise claim introduced or restated by this speech.",
      "kind": "requirement"
    }
  ],
  "stance_links": [
    {
      "target_event_id": "evt_speech_T01",
      "target_claim_id": "T01.C1",
      "stance": "support",
      "rationale": "Why this speech supports/refines/challenges/synthesizes that prior claim."
    }
  ],
  "contribution_type": "support",
  "new_axis_reason": null,
  "evidence": [
    {
      "kind": "source_or_observation",
      "ref": "evidence pointer"
    }
  ]
}
```

## Runner stdout semantic framing contract

When acting through a selected-runner wrapper, emit exactly one compact JSONL object on stdout for the canonical response. Use one line, no markdown fence, and no surrounding prose. Write runtime diagnostics, wrapper logs, and provider warnings to stderr or structured evidence fields, not around the stdout semantic record.

Required stdout form for a council speech runner:

```json
{"type":"speech","payload":{"speech":"Visible participant answer only.","claims":[],"stance_links":[],"contribution_type":"support","new_axis_reason":null,"evidence":[]}}
```

Pretty/multiline JSON is compatibility input only: the control adapter may normalize it, but participant prompts must still ask for compact JSONL. Delivery/fallback-only JSON remains adapter_command_mismatch, and malformed JSON remains malformed_or_missing_response.

Allowed `contribution_type` / stance vocabulary includes `support`, `challenge`, `refine`, `extend`, `synthesize`, `question`, `risk_addition`, `decision_frame`, and `new_axis` where supported by the tool schema.

## ARGUE quality rules

- `speech` is the only human-visible answer. It must not contain tool diagnostics, max-iteration notices, wrapper summaries, fallback disclosures as if they were participant reasoning, or “I am role-playing X” text.
- `claims[]` must summarize actual claims in the speech.
- `stance_links[]` must target caller-provided prior `event_id` and optional `claim_id`. Guidance-only `speaker`, `summary`, Discord order, prose references, or `responds_to_event_id` are not validation authority.
- `responds_to_event_id` is a legacy display hint only; it never replaces `stance_links[]`.
- If this is a non-opening speech in `quality_required` mode and sufficient prior claim targets exist, include at least one valid `stance_links[]` entry or set `contribution_type: "new_axis"` with a non-empty `new_axis_reason`.
- Use `new_axis` sparingly: only when opening a necessary new line of argument that cannot honestly link to current prior claims.
- If citing outside material or runtime observations, place pointers in `evidence[]` rather than bloating visible speech.

## Hand raise guidance

When raising a hand before selection, prefer structured `target_links[]` over legacy target id lists:

```json
{
  "target_links": [
    {
      "target_event_id": "evt_speech_T01",
      "target_claim_id": "T01.C1",
      "stance": "challenge",
      "rationale": "The prior claim omits the visible-surface identity risk."
    }
  ]
}
```

Legacy `target_event_ids` and `target_claim_ids` are display hints only and must not be treated as ARGUE validation authority.

## Failure handling

Return/request a fail-closed result instead of inventing a response when:

- the selected member does not match you;
- `role_substitution` would be required;
- the selected stream cursor or event id is missing;
- prior claim graph context is required but absent or ambiguous;
- a non-opening quality-required response would be orphaned;
- runner evidence is missing or terminal evidence is not `participant_response`;
- visible speech would need to include runtime noise or fallback/manual text.

In reports, separate actual participant speech from fallback/manual profile text. Fallback profile text is diagnostic evidence only and never equals selected-runner success.
