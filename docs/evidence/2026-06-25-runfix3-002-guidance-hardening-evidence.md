# RUNFIX3-002 guidance hardening evidence

## Scope
- Task: `plugin/RUNFIX3-002`
- Repo: `agent-turn-network-plugin`
- Date: 2026-06-25
- Objective: harden moderator/operator live-thread guidance against the frozen control evidence contract while keeping `atn-plugin` boundary-only and roadmap/SOT rows mirror-only.

## Ownership matrix
- Normative owners:
  - `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md`
  - `docs/09-skill-and-operator-guide.md`
- Boundary/cross-link only:
  - `src/atn_plugin/bundled_skills/atn-plugin/SKILL.md`
- Traceability/status mirrors only:
  - `docs/06-implementation-epics-tasks.md`
  - `docs/10-live-transport-sot.md`
- Verification hooks:
  - `tests/unit/test_bundled_skills.py`
  - `scripts/guardrails.py`
  - `tests/unit/test_guardrails.py`

## Changed files
- `agent-turn-network-plugin/docs/06-implementation-epics-tasks.md`
- `agent-turn-network-plugin/docs/spec/skill-and-operator-guide.md`
- `agent-turn-network-plugin/docs/spec/live-transport-sot.md`
- `agent-turn-network-plugin/scripts/guardrails.py`
- `agent-turn-network-plugin/src/atn_plugin/bundled_skills/atn-moderator/SKILL.md`
- `agent-turn-network-plugin/src/atn_plugin/bundled_skills/atn-plugin/SKILL.md`
- `agent-turn-network-plugin/tests/unit/test_bundled_skills.py`
- `agent-turn-network-plugin/tests/unit/test_guardrails.py`
- `agent-turn-network-control/docs/todo/implementation-decomposition.md`
- `agent-turn-network-control/docs/spec/live-transport-control-sot.md`
- `agent-turn-network-control/docs/roadmap.md`

## Hardened contract points
- Exact Discord origin binding uses `chat_id:thread_id`.
- Display-name, thread-title, and channel-label text do not satisfy origin proof.
- `selected_runner_pass` remains evidence-derived and is not repaired by fallback/manual/moderator reposting.
- Expected visible turns stay `max_discussion_turns + participant_count + 2`.
- Live-visible turns are participant-to-participant dialogue, not operator-report prose.
- Visible content and audit/control metadata stay separated.
- Recoverable drift repairs forward; unrecoverable drift closes unresolved.
- The two normative owners now ship a stable text-identical numbered RUNFIX3 hard-rule set.
- Guardrails and bundled-skill tests now parse the hard-rule section structurally, enforce full owner parity, recurse through nested `docs/**` markdown, and reject leaked rule ids outside the two owner surfaces.
- Canonical plugin/control RUNFIX3-002 status surfaces now align on `implementation_complete/review_pending` pending focused reviewer acceptance.
- `agent-turn-network-plugin/docs/06-implementation-epics-tasks.md` now defines `implementation_complete/review_pending` in the allowed task-status vocabulary so the mirrored RUNFIX3-002 rows no longer conflict with the plugin roadmap's own status rules.
- No live-readiness, production-readiness, or runtime-mutation overclaim is introduced.

## Verification
### Plugin repo
- `git diff --check` — pass
- `HOME=/Users/draccoon make docs-guardrails` — pass
- `HOME=/Users/draccoon make check-core-contract` — pass
- `HOME=/Users/draccoon make test-prepare` — pass
- `HOME=/Users/draccoon uv run python -m pytest tests/unit/test_bundled_skills.py tests/unit/test_guardrails.py tests/unit/test_plugin_load_smoke.py` — pass (`46 passed`)
- `HOME=/Users/draccoon make test` — pass (`446 unit + 64 integration + 13 e2e passed`)
- Adversarial guardrail checks:
  - missing owner marker rejection — pass
  - exact-origin overclaim rejection — pass
  - `selected_runner_pass` misuse rejection — pass
  - fallback/manual overclaim rejection — pass
  - `live_readiness` overclaim rejection — pass
  - RUNFIX3 owner parity drift rejection — pass
  - RUNFIX3 leaked rule-id rejection outside owner surfaces — pass
  - RUNFIX3 leaked rule-id rejection in nested `docs/evidence/` markdown — pass
  - plugin-load command overclaim / registration / env-inertness smoke — pass

### Control repo
- `git diff --check` — pass
- `HOME=/Users/draccoon make docs-guardrails` — pass
- `HOME=/Users/draccoon make check-plugin-contract` — pass
- `HOME=/Users/draccoon make test-prepare` — pass

## Cleanup sweep
- `agent://16-Runfix3CleanerFinal2`
- Result: `0` blocking findings, `4` advisory findings.

## Cross-repo status mirror refs
- `agent-turn-network-plugin/docs/06-implementation-epics-tasks.md` — `RUNFIX3-002 | implementation_complete/review_pending`
- `agent-turn-network-plugin/docs/spec/live-transport-sot.md` — `RUNFIX3-002 | implementation_complete/review_pending`
- `agent-turn-network-control/docs/todo/implementation-decomposition.md` — `RUNFIX3-002 | implementation_complete/review_pending`
- `agent-turn-network-control/docs/spec/live-transport-control-sot.md` — `RUNFIX3-002 | implementation_complete/review_pending`
- `agent-turn-network-control/docs/roadmap.md` — RUNFIX3 table now includes `RUNFIX3-002` as `implementation_complete/review_pending` and restores the four-task table shape.

## Non-goals preserved
- No planner/schema/report-field work reserved for `plugin/RUNFIX3-003`.
- No control diagnostics/enforcement work reserved for `control/RUNFIX3-004`.
- No live activation, production readiness, KAB readiness, daemon/profile/provider/gateway/auth/token mutation, or control-repo edits.
- No moderator reference markdown was promoted to canonical policy.

## Review refs
- Approved plan: `.gjc/_session-019efed9-bc64-7000-bad0-bb0b94879bca/plans/ralplan/019efed9-bc64-7000-bad0-bb0b94879bca/pending-approval.md`
- Cleanup sweep: `agent://16-Runfix3CleanerFinal2`
- QA lane (pre-artifact run): `agent://17-Runfix3Qa`
- Architect final review before G002: `agent://18-Runfix3ArchitectFinal`
- Focused G002 re-review: `agent://21-Runfix3G002Review` (`CLEAR/CLEAR/CLEAR`, `APPROVE`)
