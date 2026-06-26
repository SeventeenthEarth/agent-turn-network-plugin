# RUNFIX3-003 planner proof evidence

## Scope
- Task: `plugin/RUNFIX3-003`
- Repo: `agent-turn-network-plugin`
- Date: 2026-06-26
- Objective: make RUNFIX3 planner output fail closed without conflating `ready_to_start` with accepted RUNFIX3 proof.

## Evidence summary
- Top-level planner output now separates `start_status` from overall `status`.
- The planner now exposes `runfix3_acceptance_status` so RUNFIX3 acceptance blocking is machine-readable.
- `runfix3_live_thread_proof_report` now includes an explicit `selected_runner_proof` axis.
- Discord-origin `live_visible_thread` planning remains start-gated by `start_status`; final RUNFIX3 acceptance stays fail-closed in top-level `status` when proof axes are blocked.

## Changed files
- `src/atn_plugin/activation_planner.py`
- `src/atn_plugin/tools.py`
- `src/atn_plugin/schemas.py`
- `docs/09-skill-and-operator-guide.md`
- `docs/10-live-transport-sot.md`
- `docs/06-implementation-epics-tasks.md`
- `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md`
- `src/atn_plugin/bundled_skills/atn-moderator/references/live-visible-preflight-and-council-new.md`
- `tests/unit/test_discussion_activation_planner.py`
- `tests/unit/test_tool_handlers.py`


## Verification
- `HOME=/Users/draccoon git diff --check` — pass
- `HOME=/Users/draccoon make docs-guardrails` — pass
- `HOME=/Users/draccoon make check-core-contract` — pass
- `HOME=/Users/draccoon make test-prepare` — pass
- `HOME=/Users/draccoon make test-unit` — pass (`472 passed`)
- `HOME=/Users/draccoon uv run python -m pytest tests/unit/test_discussion_activation_planner.py tests/unit/test_tool_handlers.py tests/unit/test_tool_schemas.py` — pass (`196 passed`)

## Acceptance notes
- This artifact records implementation and bounded verification only.
- Focused Red/Orange/Gray re-review, Blue synthesis, final closeout artifact, and 주군 approval remain required before any RUNFIX3-wide completion claim.
