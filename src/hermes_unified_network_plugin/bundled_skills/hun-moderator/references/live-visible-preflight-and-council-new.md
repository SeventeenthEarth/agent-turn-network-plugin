# Live-visible preflight and `council.new` pitfalls

This reference captures a reusable HUN moderator pattern from a Discord-origin request: “run live HUN preflight first, and only execute the discussion if it passes.”

## Correct operator sequence

1. Load `hun-moderator` and `hun-plugin` guidance before acting.
2. Confirm the requested output mode. Discord-origin “discuss / council” requests default to `live_visible_thread` unless the user explicitly approves `artifact_only` or `daemon_cli_actor_speech` before session creation. If the user already asked for the HUN discussion and the live-visible start gate passes, do not ask for another approval; start the council.
3. Run daemon/tool health checks, but do not treat `hun_daemon_status ok=true` as sufficient live-discussion readiness. It proves daemon/protocol visibility only.
4. Run `hun_discussion_activation_plan` with the relevant RUNFIX planning mode:
   - `plugin/RUNFIX-010` for live visible surface readiness: surface binding, turn-posting probe, visible closeout probe, real profile/gateway replies, and `cli_actor_speech_only=false`.
   - `plugin/RUNFIX-015` for visible author guard: same-path per-profile author probes, shared/default author negative proof, env precedence proof, and per-turn `selected_member/profile_author_id/speech_event_id` linkage.
   - `plugin/RUNFIX-017` when ARGUE quality-required discussion evidence must be evaluated.
5. If the planner returns `status: blocked`, do not automatically stop before `council.new`. Classify each blocker first:
   - `start_blocker`: stop before `council.new`;
   - `runtime_evidence_pending`: proceed when the start gate passes, then collect during lifecycle/turn execution;
   - `final_acceptance_unproven`: proceed when the start gate passes, then report as a separated closeout label.
6. Only `start_blocker` findings block `council.new`. A pure/local planner may report missing evidence because it cannot discover the environment. That is a probe or field-mapping task unless the missing evidence proves an unsafe or impossible start condition.
7. Do not treat `hun_discussion_activation_plan.live_readiness=false` as a start blocker by itself; the planner never proves live readiness.
8. `ready_to_start` means the moderator should proceed to `council.new`. `ready_for_approval` is not the live-visible discussion start signal; it applies only to apply/mutation or activation-planning scopes.

## Participant profile evidence that is not enough

Discord config snippets such as `allowed_channels`, `free_response_channels`, `auto_thread`, and `history_backfill` can support “the profile is Discord-enabled for that channel,” but they do not by themselves prove:

- HUN plugin/tool visibility in that profile;
- bot-to-bot disabled eligibility;
- selected-runner readiness;
- same-path visible author identity;
- live profile/gateway turn posting;
- parent-channel allow-list inheritance into newly created threads.

Treat these as partial diagnostic evidence only.

## `council.new` schema reminders

When `hun_council_command(command="council.new")` is eventually allowed, the payload validator expects these top-level fields inside the command payload:

- `command_id`
- `moderator`
- `members` as a JSON array
- `title`
- `surface` as a JSON object
- `event_id`

Do not put `moderator`, `members`, or `surface` only inside nested `payload`. The tool-level `session_id` should be daemon-compatible; observed stream tooling rejects IDs that do not start with `sess_`.

## Fail-closed report shape

When blocked, include:

- lifecycle not started / no `council.new` created;
- visible turns posted: `0/expected`;
- real profile/gateway replies: false or unproven;
- selected-runner pass: false/unproven;
- discussion quality: unproven, not failed by content;
- exact missing evidence classes;
- explicit statement that artifact-only substitution was not performed.
