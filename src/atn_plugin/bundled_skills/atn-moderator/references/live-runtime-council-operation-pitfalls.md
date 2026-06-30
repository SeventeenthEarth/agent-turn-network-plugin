# Live runtime council operation pitfalls

Use these notes when moderating or reporting on long live-visible selected-runner councils.

## Roster scope

If a user names a project/team plus color lanes or roles, resolve the actual project roster and role mapping from the authoritative registry, Kanban, or project SOT before `council.new`. Do not infer persona-style participants from culturally loaded terms or similar names. Ambiguous or missing principals are `start_blocker` evidence, not a reason to open a best-effort council.

## Parameterized visible-turn accounting

Never hard-code T20 as the final synthesis. For `max_discussion_turns = n` and `participant_count = p`, the live-visible shape is:

- T0: moderator opening
- T1..Tn: selected participant discussion turns
- T(n+1)..T(n+p): selected participant closeouts, one per participant
- T(n+p+1): moderator synthesis / terminal closeout

Expected visible turns are `n + p + 2`.

Examples:

- 15 discussion turns and 4 participants: final synthesis is T20, expected visible turns = 21.
- 5 discussion turns and 2 participants: final synthesis is T8, expected visible turns = 9.

If only T1..Tn discussion turns are complete, report `discussion_turns_complete; closeouts_and_synthesis_pending` and keep the session open unless the user explicitly stops it.

## Runtime freshness

Before each selected-runner grant, prefer fresh daemon status evidence for subscriber presence, cursor ack, heartbeat, selected-runner prerequisites, and visible-surface readiness. A stale post-final heartbeat must not retroactively disprove turn-time readiness, but missing turn-time readiness evidence must not be promoted to success.

## CLI/schema and timeout handling

Use canonical daemon/CLI field names. When a command times out at the transport layer, do not treat the timeout as definitive runner failure or success. Query bounded status evidence for command acceptance, runner started, runner succeeded/failed, canonical speech linkage, and visible delivery evidence before reporting the turn outcome.

## Terminal reporting

Do not claim `finalized` unless the daemon terminal phase and required visible closeout proof support it. If finalization is blocked after the moderator synthesis because visible proof is missing, use the supported unresolved terminal path with exact blocker evidence and report `terminal_unresolved` separately from lifecycle turn-count completion.
