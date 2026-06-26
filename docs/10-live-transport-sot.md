# LIVE-TRANSPORT Source of Truth

## Status

This document is the plugin-side implementation Source of Truth for the first live transport slice that connects the plugin, the public `atn-controld` daemon surface, and the public `atn-control` CLI surface into a usable council/discussion flow.

The control-side companion SOT is `../../agent-turn-network-control/docs/24-live-transport-control-sot.md`. This plugin SOT may describe daemon/CLI/member-runtime responsibilities for boundary clarity, but control-owned behavior is implemented and roadmapped in the control repository.

`plugin/LTRAN-001` is completed as a documentation, SOT, and mapping task only. It did not change backend/source/test code, implement live transport, open a daemon socket, mutate production/live systems, contact Discord, gateway, auth, token, or KAB surfaces, or add a hidden plugin-to-CLI fallback. `plugin/LTRAN-002` is completed as the first bounded implementation task for explicit Unix-socket `status.read` / `version.read` live smoke only.

This document does **not** authorize production activation, live Discord delivery, gateway/auth/token changes, KAB bridge readiness, or active profile mutation by itself. It defines the architecture, component responsibilities, command/data-plane boundaries, plugin implementation slices, cross-repo dependency gates, and verification evidence required before any later activation decision.

RUNFIX update: this SOT also records the plugin-owned side of `RUNFIX`, the cross-repo remediation epic created from the 2026-06-17 council dogfood issues report. `control/RUNFIX-001` and `plugin/RUNFIX-002` are accepted docs-only SOT locks after historical Red/Orange/Gray review, focused re-check, and Blue final synthesis; they do not install or activate live ATN discussion by themselves. RUNFIX3 update: this SOT also records the plugin-owned follow-up from the 2026-06-25 KLM live-thread postmortem; `RUNFIX3-001` is a docs-only SOT/roadmap lock and does not authorize live Discord rollout, profile/provider/gateway/auth/token/model mutation, daemon startup, push, or production readiness. NEXFIX update: this SOT records the plugin-owned guidance follow-up for the 2026-06-26 selected-runner prompt envelope defect; `plugin/NEWFIX-002` is implementation_complete/review_pending and depends on `control/NEWFIX-001`, which is also implementation_complete/review_pending pending focused Blue re-review.

## Scope

LIVE-TRANSPORT covers the local ATN runtime path needed for a main agent to control a discussion session while participant agents observe and respond through the daemon event stream.

In scope:

- explicit daemon connection from the plugin through the ATN protocol client/contract;
- control-plane use of the canonical CLI by a main agent or operator;
- participant-agent stream observation and typed event writes through plugin/protocol-client tools;
- council session creation, agenda, attendance, preparation, floor grants, speeches, interventions, voting, finalization, unresolved closure, cancellation, transcript, and recovery semantics as daemon-owned events;
- local disposable live transport pilots that prove CLI/plugin/daemon equivalence without production activation;
- documented failure handling for missing daemon, unsafe socket, cursor gaps, unknown schema versions, missing participant runtimes, and delivery failures.

Out of scope for this SOT unless a later task explicitly opens it:

- production Hermes profile enablement;
- live/default Discord sending from the plugin;
- Discord thread creation by the daemon;
- gateway, auth, token, credential, or provider mutation;
- localhost/TCP/gateway fallback;
- hidden `plugin -> CLI subprocess -> daemon` fallback;
- replacing real participant-agent profiles with simulated role prompts;
- treating Discord message order as lifecycle state;
- KAB bridge execution claims.

## Terms

| Term | Meaning |
|---|---|
| daemon | `atn-controld`, the state/event authority. |
| CLI | `atn-control`, the canonical operator/control and diagnostics surface. |
| plugin | `atn-plugin`, the Hermes agent-facing adapter. |
| main agent | The coordinating moderator runtime that receives user intent, controls sessions, grants floor, and returns outcomes. |
| participant agent | A real named member runtime/profile that observes session events and emits its own typed responses. |
| member runtime | The loop or supervisor that watches daemon stream frames for one participant identity and invokes/resumes the real participant-agent profile when action is required. |
| surface | A human-visible room or record pointer, such as a Discord thread. It is not lifecycle state authority. |
| control plane | Session creation, agenda, moderation, intervention, finalization, diagnostics, recovery. |
| agent plane | Participant observation, preparation, hand raising, speech, vote, and cursor acknowledgement. |
| delivery plane | Human-visible presentation of recorded daemon events, plus evidence pointers such as message IDs. |

## Cross-repo epic ownership and active-task handoff

LIVE-TRANSPORT work is split into repo-owned five-letter epics. For legacy repo-owned epics, a repo switch must happen only at an epic boundary: do not start a control task in the middle of a plugin-owned legacy epic, and do not start a plugin task in the middle of a control-owned legacy epic. If a missing sibling capability is discovered mid-epic, block the active epic with evidence, complete the required sibling epic, then resume. For an accepted cross-repo feature/remediation epic with one global task stream, such as RUNFIX, transfer happens at the recorded repo-qualified global task boundary instead of the legacy epic boundary.

Recommended execution order:

| Order | Repo | Epic | Purpose | Blocks |
|---:|---|---|---|---|
| 1 | control | `LTRAN` | control companion SOT, daemon/CLI compatibility reads, live-local fixture/equivalence support | plugin `LTRAN` |
| 2 | plugin | `LTRAN` | explicit plugin live daemon transport and plugin/CLI/daemon equivalence evidence | control `MEMBR` |
| 3 | control | `MEMBR` | real participant profile/wrapper invocation path for selected participants | plugin `PARTC` |
| 4 | plugin | `PARTC` | participant stream/write path and selected-participant response via plugin/protocol client | control `SURFD` |
| 5 | control | `SURFD` | event-to-visible-surface rendering and delivery evidence contract | plugin `SURFD` |
| 6 | plugin | `SURFD` | visible helper/rendering boundary using daemon event data and evidence pointers | release/live pilot decision |

Plugin roadmap entries live in `docs/06-implementation-epics-tasks.md`. Control roadmap entries live in `../../agent-turn-network-control/docs/roadmap.md`. When a task ID is referenced outside its repo-local roadmap or SOT table, use repo-qualified notation such as `plugin/LTRAN-001` or `control/LTRAN-001` to avoid ambiguity.

For a jointly developed remediation or feature epic, both repos use one epic ID and one globally sequential task stream. Repo-qualified notation is mandatory, and repo-local gaps are expected. RUNFIX follows this rule: `control/RUNFIX-001`, `plugin/RUNFIX-002`, `control/RUNFIX-003`, `control/RUNFIX-004`, `control/RUNFIX-005`, `plugin/RUNFIX-006`, `plugin/RUNFIX-007`, `plugin/RUNFIX-008`, `control/RUNFIX-009`, `plugin/RUNFIX-010`, `control/RUNFIX-011`, `plugin/RUNFIX-012`, `plugin/RUNFIX-013`, `control/RUNFIX-014`, `plugin/RUNFIX-015`, `control/RUNFIX-016`, `plugin/RUNFIX-017`, `control/RUNFIX-018`, `plugin/RUNFIX-019`.

## RUNFIX activation and evidence contract

RUNFIX separates package installation from ATN discussion activation:

1. **Plugin install/load** means the repository or package can be loaded by Hermes and its declared tools are visible in an approved profile. It does not prove daemon compatibility, participant runtime operation, visible Discord delivery, or live council readiness.
2. **Discussion activation planning** means an operator has a dry-run plan that names the explicit control daemon/socket/config, participant profiles, selected Discord parent channel, eligible/excluded profiles, loaded daemon registry membership for the selected moderator/participants, any planned registry reconcile, planned config or allow-list changes, rollback, verification commands, and approval gates for mutation/apply scope.
3. **Discussion activation apply** may occur only after explicit approval for the exact live-local mutation scope. It must not mutate provider/gateway/auth/token/profile/Discord state outside the approved plan. The RUNFIX3 live-thread start gate, output-mode handling, and second-approval policy are owned by `docs/09-skill-and-operator-guide.md` and `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md`; this SOT records only the boundary that the surface must already be approved/configured before apply begins.
4. **Live-local pilot acceptance** requires selected-speaker runner evidence, canonical `speech` linkage, visible-surface evidence, ARGUE quality diagnostics, and fallback disclosure. Lifecycle-only or manual profile fallback evidence is not enough. The visible surface is thread-preferred under the approved parent channel; if thread creation/posting is unsupported, the approved parent channel may be used directly only with an explicit `fallback_reason` in task brief, surface metadata, visible closeout, and final report.

RUNFIX evidence labels are mandatory in operator reports:

- `lifecycle_pass`: daemon event flow completed, but runner/visible/ARGUE quality may still be unproven;
- `fallback_profile_pass`: manual or fallback profile text was obtained; this is never full ATN runner success;
- `selected_runner_pass`: selected member runtime/runner was invoked from `speaker_selected` and submitted linked canonical speech. Durable runner failure is separate terminal-failure diagnostic evidence and blocks `selected_runner_pass`;
- `visible_surface_pass`: approved visible surface rendering/delivery evidence points back to daemon events;
- `discussion_quality_pass`: ARGUE relation evidence or justified `new_axis` is present and diagnostics do not fail the requested quality mode.

### RUNFIX cross-repo DAG

| Global Order | Repo | Task ID | Task Status | Purpose |
|---:|---|---|---|---|
| 1 | control | RUNFIX-001 | completed/docs-only | Control SOT/roadmap remediation contract, canonical readiness labels, and control-owned implementation boundaries accepted after RUNFIX-001/002 review and Blue synthesis. |
| 2 | plugin | RUNFIX-002 | completed/docs-only | Plugin activation/operator SOT, roadmap companion, install-vs-activation split, and bundled guidance boundary accepted after Red `t_612b4d58`, Orange `t_c673aed4`, Gray `t_ce1b0c31`, focused Orange `t_131ea8c9`, focused Gray `t_7cec278f`, and Blue synthesis `t_1bb67569`. |
| 3 | control | RUNFIX-003 | completed/local-control | Selected-speaker member runtime dispatch accepted in control repo commit `56a8991` with KAH run `run-20260617T064753Z-103e15ca05fa`, final gate pass, focused tests/docs guardrails/check-plugin-contract pass, and no plugin package mutation. |
| 4 | control | RUNFIX-004 | completed | Hermes adapter command contract and runner diagnostics completed in control commit `0138b59` with KAH run `run-20260617T101645Z-1757e05ffbcf`; this mirror now uses `completed` after later focused re-validation and does not widen the original local/control-only evidence scope. |
| 5 | control | RUNFIX-005 | completed/local-control | Control-local implementation under KAH run `run-20260618T020120Z-fe2144618fe6` adds the status projection/diagnostic surface for `discussion_quality`, hard warnings, and linked hand-raise `graph_need` counts. Control-local verification passed `git diff --check`, focused storage/protocol/daemon/command tests, `make docs-guardrails`, `make check-plugin-contract`, `make test-prepare`, and `make test`; Red `t_1d5692f1`, Orange `t_388bb347`, Gray `t_6fb40282`, and Blue synthesis `t_1eb87c6b` accepted bounded local-control closeout. This does not claim plugin implementation/readiness, live Discord delivery, production daemon activation, profile/provider/gateway/auth/token mutation, commit, push, or broad rollout. |
| 6 | plugin | RUNFIX-006 | local implementation proof | Discussion activation planner/doctor is implemented as pure/local `atn_discussion_activation_plan` from explicit caller-provided evidence only. It classifies eligible/excluded/blocked profiles, excludes bot-to-bot-enabled profiles by default, blocks missing tool visibility or unknown eligibility, requires explicit parent-channel allow-list inheritance proof or reports a Hermes/gateway blocker, keeps RUNFIX evidence labels separate, and always returns `live_readiness: false`. No apply/live-local pilot, live Discord delivery, daemon startup, profile/gateway/provider/auth/token/model mutation, production activation, commit, push, or broad rollout claim is made by this row. |
| 7 | plugin | RUNFIX-007 | local implementation proof | Existing pure/local activation planner now supports effective Discord eligibility evidence, eligible-only allow-list targets, profile remediation, parent-channel proof state, thread-only proof rejection, and fallback audit rejection while keeping `live_readiness: false` and making no live activation claim. |
| 8 | plugin | RUNFIX-008 | local implementation proof | Existing pure/local activation planner now accepts `plugin/RUNFIX-008` and exposes participant ARGUE response template fields, explicit operator evidence reporting, ARGUE counts, selected-runner evidence, canonical `speaker_selected -> speech` linkage, RUNFIX labels, and diagnostic-only fallback disclosure from caller-provided evidence only. Missing or ambiguous runner/ARGUE/canonical-link evidence remains `unproven`/`blocked`, `live_readiness` remains false, and this row makes no live Discord delivery, daemon startup/discovery, profile/provider/gateway/auth/token/model mutation, production activation, KAB readiness, commit, push, or broad rollout claim. |
| 9 | control | RUNFIX-009 | local implementation proof | Control KAH run `run-20260618T102752Z-7d8ccfa584e4` adds deterministic local smoke proof for runner invocation, canonical `speaker_selected -> speech` linkage, ARGUE diagnostics/hard warnings, and transcript/export/projection closeout evidence. This row is dependency evidence for the later plugin/RUNFIX-010 pilot only; it does not authorize live Discord delivery, daemon startup/discovery, profile/provider/gateway/auth/token/model mutation, production activation, KAB readiness, commit, push, or broad rollout. |
| 10 | plugin | RUNFIX-010 | completed/PASS_WITH_RISK | Approved live-local activation pilot and final operator package, now including Discord-origin live-visible default and artifact-only fail-closed guardrails. Bounded visible-local pilot evidence exists with parent-channel fallback disclosure and remaining risks; KAH run `run-20260618T112843Z-40b023a5d9c8` final gate passed. This is not production/live readiness, no-restart thread readiness, full ATN roster coverage, selected-speaker live runner readiness, or always-on participant runtime readiness. |
| 11 | control | RUNFIX-011 | local implementation proof | Control KAH run `run-20260618T162156Z-419f3769f2cc` implements derived participant runtime readiness from durable subscriber presence, cursor ack freshness, heartbeat freshness, attendance/preparation success or timeout/failure evidence, and selected-runner prerequisites. Control status/stream diagnostics now fail closed when those proofs are missing. This remains control-local evidence only and does not authorize live Discord delivery, production daemon activation, profile/gateway/provider/auth/token/model mutation, plugin/RUNFIX-012 consumption, or live readiness. |
| 12 | plugin | RUNFIX-012 | local implementation proof | Plugin activation planner/operator guardrails now consume explicit `control/RUNFIX-011` participant-runtime readiness evidence from caller input only. The planner reports control task/status/evidence ref, subscriber presence, cursor ack freshness, heartbeat freshness, attendance/preparation terminal evidence, selected-runner readiness/prerequisites, and visible-surface proof as separate evidence classes. Missing, stale, ambiguous, gateway-only, transcript/export-only, parent-channel-fallback-only, or manual/fallback-profile-only evidence blocks or diagnoses readiness and keeps `live_readiness=false`. This remains local plugin proof only and does not claim live Discord delivery, production/live readiness, profile/provider/gateway/auth/token/model mutation, commit, push, or broad rollout. |
| 13 | plugin | RUNFIX-013 | local implementation proof | Packaged skill/operator guidance now records ATN council moderation hard rules for lifecycle-first discussion, no predeclared complete live speaker order, per-turn poll/hand-raise evaluation, justified daemon `speaker_selected`, `relevance` as default with per-turn justified `targeted`, `random`, `moderator_direct`, and `role_order`, daemon `speech` event authority, moderator-opinion handling, and cancel/restart versus repair-forward guidance. This remains docs/bundled-skill/package proof only and does not claim live daemon/runtime activation, Discord delivery, production/live readiness, profile/provider/gateway/auth/token/model mutation, commit, push, or broad rollout. |
| 14 | control | RUNFIX-014 | local implementation proof dependency | Control KAH run `run-20260619T051710Z-8e1f6efb61ec` implements selected-runner terminal accounting and live-report guardrails. Plugin reports must consume control accounting labels and must not promote a run with `runner_invocation_failed` followed by fallback/manual canonical `speech` into `selected_runner_pass` or live readiness. |
| 15 | plugin | RUNFIX-015 | local implementation proof | Plugin KAH run `run-20260619T071526Z-7d2ba33b07d5` extends the pure/local `atn_discussion_activation_plan` with a pre-`council.new` visible author guard. The tool validates explicit caller-provided same-path author probes, expected author source (`registry_snapshot` or approved profile-author map), source-env/posting-path evidence, shared-default-then-profile-local env precedence proof, per-turn Discord message id/member/author/speech linkage, and separated final report fields. Missing/shared-default/unexpected author evidence fails closed without live Discord delivery or runtime/profile/provider/gateway/auth/token/model mutation. |
| 16 | control | RUNFIX-016 | local implementation proof control dependency | Control KAH run `run-20260619T083649Z-d10e1f5cc20b` final gate passed and local commit `9c15d22` is the bounded dependency for canonical summary/turn-accounting over `channel.jsonl` and export bundles, including export manifest `summary_turn_accounting`. Plugin visible runners should call or conform to the helper and must tolerate dict/list/missing evidence shapes instead of crashing after `council_finalized`. Unsupported evidence maps/lists remain fail-closed and do not prove visible delivery, live readiness, plugin readiness, production daemon activation, profile/provider/gateway/auth/token/model mutation, Discord delivery, commit, push, or broad rollout. |
| 17 | plugin | RUNFIX-017 | local implementation proof | ARGUE quality-required prompt and runner contract hardening is implemented locally under KAH run `run-20260619T101255Z-189d01ba8b8f`; official color review, Blue synthesis, and final KAH gate passed. Plugin/operator prompts provide compact prior claim graph targets, selected responses preserve ARGUE fields, non-opening quality-required speeches with sufficient local context require caller-target-valid `stance_links[]` or justified `new_axis`, explicit `discussion_quality` evidence is required for the quality gate, `discussion_quality_pass` fails on the first orphan non-opening speech in `quality_required`, and repeated-orphan counts remain diagnostics without synthetic relation inference. |
| 18 | control | RUNFIX-018 | local implementation proof control dependency | Control KAH run `run-20260619T214003Z-8a2afe33923f` implements daemon-owned registry reconciliation for explicit `council.new` rosters. If a selected moderator/participant principal is missing from the loaded registry but the principal id is valid, non-reserved, and same-named wrapper resolution is unambiguous, the daemon adds the member to persistent `registry.yaml`, reloads, snapshots, and reports `registry_reconcile`; ambiguous, invalid, unresolved, or disabled principals fail closed before session creation. |
| 19 | plugin | RUNFIX-019 | local implementation proof | Plugin KAH run `run-20260619T214004Z-4d1e54b7304a` extends `atn_discussion_activation_plan`, schema, operator guide, and bundled skills with explicit `daemon_registry_membership` evidence. Live-visible plans must show each eligible principal is loaded/enabled or has an unambiguous planned reconcile; ambiguous mapping, disabled principals, missing registry evidence, or unresolved wrappers block before `council.new` without downgrading to artifact-only or daemon CLI actor speech. |


## RUNFIX2 discussion runtime usability hardening

RUNFIX2 records the 2026-06-20 KLM/주유 live discussion feedback as a new five-PR hardening epic. It is a continuation of RUNFIX, but it does not erase RUNFIX evidence semantics. Operators and plugin tools must distinguish configuration intent from proof:

- `visible_surface_enabled` / `visible_surface_required`, `participant_runtime_required`, and `selected_runner_required` may default to true in production/operator activation plans when the task scope approves them.
- `visible_surface_pass`, `participant_runtime_live_ready`, `selected_runner_pass`, and `discussion_quality_pass` are evidence-derived report labels. They must not be forced true by config defaults, final lifecycle success, transcript/export existence, manual profile text, or Discord messages alone.
- For finalized sessions, reports should separate current runtime freshness from grant/turn-time runtime readiness. A completed council naturally stops producing fresh heartbeat/ack evidence; stale post-final freshness is a diagnostic, not by itself proof that prerequisites were missing during the discussion.
- `selected_runner_pass` requires daemon-selected runner success and linked canonical `speech`. A runner terminal failure such as `malformed_or_missing_response` remains a blocker until a later selected-runner invocation succeeds through the fixed adapter path.
- Selected-runner participant/moderator wrapper stdout uses a compact JSONL semantic framing contract: exactly one JSON object per line for the canonical response, no markdown fence, and no surrounding prose. Pretty/multiline JSON is adapter compatibility input only and is not the producer contract; delivery/fallback-only JSON remains `adapter_command_mismatch`, and malformed JSON remains `malformed_or_missing_response`.
- Visible Discord messages should be short and audience-facing. Session ids, role/color labels, `speaker_selected_event_id`, `speech_event_id`, runner ids, and delivery/evidence details remain in audit/export/status surfaces.

RUNFIX2 cross-repo sequence and current local-proof status:

| Global Order | Repo | Task ID | Task Status | Purpose |
|---:|---|---|---|---|
| 1 | control | RUNFIX2-001 | completed/control-local | Evidence/config semantics and terminal readiness model: control local implementation separates status generation time from event-time readiness evaluation and keeps pass labels evidence-derived. Control KAH final gates, official review, and Blue acceptance passed; plugin-owned downstream consumption remains scoped to later RUNFIX2 tasks. |
| 2 | control | RUNFIX2-002 | completed/control-local | Selected-runner Hermes adapter fix: control local implementation changes default runner invocation from delivery-only `send <prompt>` to response-generation `chat -Q -q <prompt>`, requires `runner_invocation_succeeded` plus linked canonical `speech`, and keeps delivery/fallback output as terminal diagnostic evidence. Plugin consumption remains scoped to later RUNFIX2 rows. |
| 3 | control | RUNFIX2-003 | completed/control-local | Discussion lifecycle closeout: control local implementation exposes `discussion_lifecycle`, keeps `limits.max_discussion_turns` as participant discussion turns only, blocks `council.propose` until T0 moderator opening + T1..Tmax selected participant discussion + one selected closeout speech per participant, and leaves `council.unresolved` as the fail-closed terminal path. Expected visible turns are `max_discussion_turns + participant_count + 2`; plugin consumption remains scoped to RUNFIX2-004/005. |
| 4 | plugin | RUNFIX2-004 | local implementation proof | Clean visible transcript rendering is implemented locally in the pure renderer: visible rows use concise ATN labels, e.g. `[ATN | T15/15]`, while audit/export rows keep machine identifiers. This does not claim live Discord delivery or RUNFIX2-005 pilot proof. |
| 5 | plugin | RUNFIX2-005 | local implementation proof | Local plugin implementation now supports explicit-only `integrated_discussion_proof` for RUNFIX2-005, with separated lifecycle, selected-runner, runtime-at-turns, visible-surface, clean-transcript, visible-closeout, fallback, discussion-quality, and final-label axes. Selected-runner proof requires runner success plus canonical linked speech for the selected member; per-turn runtime readiness must be grant/turn-time evidence; visible count validates the RUNFIX2 formula. Manual/profile fallback remains diagnostic-only and cannot repair selected-runner failure. `live_readiness` remains false; actual live pilot, Discord/daemon/profile/provider/gateway/auth/token mutation, production readiness, push, and broad rollout remain separately approval-bound. |


## RUNFIX3 live-visible council contract hardening

RUNFIX3 records the 2026-06-25 KLM live Discord thread postmortem. The SOT is `17thHermes:40_outputs/team/macho/atn/2026-06-25-atn-live-visible-council-contract-hardening-sot.md`. The failed session `sess_klm_selected_runner_20260625T085557Z` is diagnostic-only evidence and must not be counted as a successful live-visible council.

Plugin-owned RUNFIX3 mirror tracks the ownership split and frozen contract only:
- normative live-thread procedure ownership now lives in `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md` and `docs/09-skill-and-operator-guide.md`;
- `atn-plugin` remains boundary/cross-link only for this topic;
- this SOT section remains traceability/status only and must not become another procedure owner.

Frozen contract reminder: `selected_runner_pass` remains an evidence-derived label, not a daemon `selection_mode`, selection policy, or feature toggle. Plugin guidance/schema work must consume the control-owned evidence contract rather than inventing control semantics. RUNFIX3-wide completion still requires the final closeout artifact `40_outputs/team/macho/atn/<date>-runfix3-final-live-visible-council-closeout.md` with bound-thread proof, per-turn daemon/runner/speech/delivery linkage, negative matrix results, Red/Orange/Gray review, 마초 Blue synthesis, and 주군 approval.

RUNFIX3 task order and current status:

| Global Order | Repo | Task ID | Status | Plugin-owned acceptance |
|---:|---|---|---|---|
| 1 | cross-repo | RUNFIX3-001 | completed | Docs-only SOT and roadmap lock accepted after Red/Orange/Gray review and Blue synthesis. It records the KLM live-thread failure as diagnostic-only and defines the follow-up task split; no runtime mutation or live readiness claim. |
| 2 | plugin | RUNFIX3-002 | implementation_complete/review_pending | Mirror-only status row for the current RUNFIX3-002 implementation: normative live-thread procedure ownership stays in `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md` and `docs/09-skill-and-operator-guide.md`, while `atn-plugin` stays boundary/cross-link only and this SOT row stays traceability-only. Verification, tests/guardrails, and evidence remain bounded to plugin-owned guidance work without adding planner/schema/runtime fields or control enforcement semantics. Fixed minimum plugin gates have passed, and cross-repo status mirrors now align on implementation-complete / re-review-pending state pending focused reviewer acceptance. |
| 3 | plugin | RUNFIX3-003 | implementation_complete/review_pending | Plugin-owned planner/schema/operator-evidence support against the frozen control evidence contract is implemented and awaiting focused reviewer acceptance. Exact-origin proof now fails closed on mismatched observed targets, visible-turn accounting is grounded to `max_discussion_turns + participant_count + 2`, `start_status` stays separate from overall `status`, `runfix3_acceptance_status` exposes acceptance blocking explicitly, selected-runner proof is a named acceptance axis, daemon registry membership remains a live-visible start gate, and RUNFIX3 final-acceptance axes remain separate from start authority while remaining fail-closed in report output. Fixed minimum gates include plugin docs guardrails, core contract, test-prepare, and a completed `make test-unit` run as a deliberate tightening over the older waiver wording. Durable verification evidence: `docs/evidence/2026-06-26-runfix3-003-planner-proof-evidence.md`. |
| 4 | control | RUNFIX3-004 | implementation_complete/review_pending | Control-owned diagnostics/enforcement follow-up against the frozen evidence-label policy is implemented and under focused review. Plugin records dependency only and must not treat control diagnostics as plugin-owned readiness proof. |


## NEXFIX selected-runner prompt envelope remediation

NEXFIX records the 2026-06-26 selected-runner prompt envelope defect where a selected participant received a runner prompt without the locked agenda or prior context even though lifecycle/runtime readiness passed. The SOT lock is `17thHermes:40_outputs/team/macho/atn/2026-06-26-atn-selected-runner-prompt-envelope-nexfix-sot.md`. The epic label `NEXFIX` and task prefix `NEWFIX-*` are an explicit 주군-requested exception. NEXFIX does not authorize production activation, live Discord rollout, default Discord activation, gateway/auth/token/provider/profile/model mutation, daemon startup/discovery, package publication, push, or broad rollout; any live pilot remains separately approved and outside this completed local NEWFIX task.

Plugin-owned contract impact:

- Runtime readiness and content-plane readiness are separate operator gates. Subscriber/heartbeat/cursor/prepare/ready success does not prove selected-runner prompt adequacy.
- `atn-moderator` guidance must require `selected_runner_prompt_evidence` review before long or live-visible councils and must stop the run if a first speech says agenda/prior context is missing. Until a richer prompt-evidence event is approved, `selected_runner_prompt_evidence` is the named handoff from `control/NEWFIX-001`; acceptable evidence is a status/export field, deterministic fixture artifact, or equivalent non-secret prompt-capture proof with `session_id`, `speaker_selected_event_id`, `selected_member`, `turn`, agenda/prior-context source refs, `included_context[]`, `missing_required_context[]`, `prompt_context_sha256`, redacted prompt excerpt or fixture id, and `result`.
- For long or live-visible councils, absent or `blocked` `selected_runner_prompt_evidence` before start is a `start_blocker` in the existing preflight taxonomy. Per-turn selected-runner proof after start remains `runtime_evidence_pending`, and final prompt-quality proof remains `final_acceptance_unproven` until durable evidence is present.
- `atn-participant` guidance must not produce generic speech when required agenda context is absent; it should return a diagnostic/fail-closed response that still satisfies the current control selected-runner producer contract in `../../agent-turn-network-control/docs/13-operational-contracts.md#runner-stdout-semantic-framing` and canonical `speech` event shape in `../../agent-turn-network-control/docs/03-protocol-spec.md#surface-rendering-evidence-contract` until a richer diagnostic event type is approved. Minimal compatible shape: `{"type":"speech","payload":{"speech":"Cannot provide a substantive council turn because the selected-runner prompt omitted required agenda/context; moderator should intervene or cancel.","claims":[{"claim_id":"missing_context","summary":"Required agenda/context was absent from the selected-runner prompt.","kind":"open_question"}],"stance_links":[],"contribution_type":"question","new_axis_reason":null,"evidence":[{"kind":"diagnostic","code":"selected_runner_context_missing"}]}}`.
- Plugin guidance consumes daemon projection authority from `control/NEWFIX-001`; plugin-side hints are optional diagnostics only and cannot replace control projection.

NEXFIX task order and current status:

| Global Order | Repo | Task ID | Status | Plugin-owned acceptance |
|---:|---|---|---|---|
| 1 | control | NEWFIX-001 | completed | Control-owned projection-backed selected-runner prompt envelope and missing-context fail-closed diagnostics are accepted after focused color review and traceability repair. Verification passed: `git diff --check`, `go test ./internal/storage ./internal/daemon -run 'NEWFIX001|SelectedRunnerPrompt|SelectedSpeaker|RUNFIX009|RUNFIX011' -count=1`, and `make test`. Plugin records dependency only. |
| 2 | plugin | NEWFIX-002 | completed | Plugin-packaged moderator/participant guidance for `selected_runner_prompt_evidence` content-plane readiness preflight, start-blocker classification for missing/blocked evidence before long or live-visible councils, and selected-runner `speech`-contract-compatible missing-context diagnostics is accepted after focused color review and traceability repair. Verification passed: `git diff --check` and `make test`; focused color review and Blue synthesis are recorded in `/Users/draccoon/Workspace/SeventeenthEarth/agent-turn-network/feedback.md`. |


### Profile and Discord eligibility policy

ATN discussion channels are bot-to-bot-free by default. A profile whose effective Discord configuration allows bot-to-bot replies is excluded from the ATN discussion allow-list unless a later explicitly approved policy changes that rule. Activation planning must list candidate profiles as `eligible`, `excluded`, or `blocked/unknown`, with the reason for every exclusion. Eligible profiles only may be included in parent-channel allow-list dry-runs or applies.

A parent-channel allow-list is preferred so new discussion threads do not require per-thread reconfiguration or gateway restart. Visible pilots should use a dedicated thread under the approved parent channel first. If thread creation or thread posting is unsupported, 주군 approves direct parent-channel use as the fallback surface, but the fallback must be explicit in the task brief, ATN surface metadata, visible closeout, and final report. Parent-channel fallback must not be reported as no-restart thread readiness, selected-speaker runner success, or live readiness by itself.

Current RUNFIX3 live-thread operator procedure lives in `docs/09-skill-and-operator-guide.md` and `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md`. This SOT records only the mirrored boundary outcome: the surface must already be approved/configured, daemon registry membership remains separate from profile/Discord readiness, and final reports must still separate lifecycle success from visible UX (`ATN lifecycle finalized`, `Discord visible turns posted: N/expected`, `real profile/gateway replies`, `CLI actor speech only`). Transcript/export success alone is artifact evidence, not proof that the Discord thread saw the turn-by-turn discussion.

### Fallback disclosure policy

Fallback is allowed only as labeled diagnostic evidence. Reports must never collapse fallback/manual profile success into selected-speaker runner success or ATN discussion readiness. A fallback report must name the missing evidence, such as absent `runner_invocation_started`, adapter command failure, missing canonical `speech`, missing delivery evidence, zero ARGUE relation counts, or allow-list/gateway limitation.

## Architecture decision



The durable relationship is:

```text
user natural language
  -> main agent
  -> CLI control commands
  -> daemon event/state authority
  -> daemon stream/replay
  -> participant member runtimes
  -> participant agents
  -> plugin/protocol-client typed writes
  -> daemon event/state authority
  -> main agent or delivery helper renders visible surface
```

The plugin and CLI are not interchangeable in runtime responsibility:

- The CLI is the main agent/operator control plane.
- The plugin is the participant-agent ATN client surface.
- Both ultimately speak to the same daemon protocol and must remain equivalent at the daemon command/event level.
- The daemon remains the only state authority.

The plugin must not shell out to the CLI as its hidden data path. A main agent explicitly using the CLI as an operator is allowed and expected; plugin-internal CLI fallback is not.

## Component responsibilities

### Daemon

The daemon owns:

- `channel.jsonl` event append and ordering;
- session phase transitions and validation;
- registry snapshot and participant authority;
- command idempotency through `command_id`;
- active-session lock and recovery state;
- stream replay/follow frame production;
- cursor acknowledgement records;
- transcript and export rendering;
- structured errors and protocol/schema compatibility checks.

The daemon does not:

- create Discord threads;
- read Discord messages;
- send Discord messages;
- interpret user natural language;
- invoke participant LLMs as hidden role prompts;
- treat plugin, CLI, or Discord state as lifecycle authority.

### CLI

The CLI owns the canonical operator and main-agent control surface.

Primary control commands include:

```bash
atn-control council new ...
atn-control council request-attendance ...
atn-control council attend ...
atn-control council lock-agenda ...
atn-control council prepare ...
atn-control council poll ...
atn-control council grant ...
atn-control council intervene ...
atn-control council propose ...
atn-control council revise ...
atn-control council request-vote ...
atn-control council finalize ...
atn-control council unresolved ...
atn-control cancel ...
```

Primary diagnostics/recovery commands include:

```bash
atn-control daemon start
atn-control daemon status
atn-control daemon stop
atn-control doctor
atn-control registry validate
atn-control storage verify
atn-control storage rebuild-projection
atn-control status <session_id> --verbose
atn-control stream <session_id> --member <member> --since <cursor> --follow --format ndjson
atn-control stream ack <session_id> --member <member> --cursor <cursor>
atn-control transcript <session_id> --format md
atn-control export <session_id> --bundle
```

The CLI must be usable by the main agent through normal terminal execution and by a human operator during diagnostics or recovery.

### Plugin

The plugin owns the participant-agent Hermes tool surface. It provides typed access to daemon status, stream/tail frames, and write commands, but it does not own lifecycle state.

Current registered plugin tool inventory is the manifest-declared fake/injected Hermes tool set. One future non-tool placeholder is also listed separately for planning and must not be counted as a registered tool:

| Surface | Purpose | Plane | Notes |
|---|---|---|---|
| `atn_daemon_status` | read daemon status/readiness | agent/diagnostic | live only with explicit config; fail closed otherwise |
| `atn_compatibility_diagnostics` | read compatibility and redacted checks | agent/diagnostic | no hidden live discovery |
| `atn_stream_tail` | read retained frames | agent plane | minimum read path; implemented by `plugin/LTRAN-003`; preserve replay-before-live semantics |
| future non-tool `atn_stream_follow` | long poll or follow frames | agent plane | optional planning placeholder; not registered and not counted in the manifest-declared tool inventory; must preserve replay-before-live semantics if later scoped |
| `atn_stream_ack` | acknowledge processed cursor | agent plane | PARTC-001 candidate implementation; local/candidate proof only, not production/runtime approval |
| `atn_delegate_new` | submit `delegate.new` command envelope | agent plane | fake/injected command tool; no plugin-owned lifecycle state |
| `atn_delegate_action` | submit supported `delegate.*` action command envelopes | agent plane | fake/injected command tool; no plugin-owned lifecycle state |
| `atn_council_command` | typed participant writes | agent plane | participant commands such as `ready`, `hand_raise`, `speak`, `vote`; main-agent control use should prefer CLI |
| `atn_selected_participant_response` | convert selected participant response evidence into `council.speak` plus cursor ack | agent plane | PARTC-002 candidate/local bounded no-live proof only; consumes fake/injected control `MEMBR` evidence and does not invoke real profiles or grant runtime activation |
| `atn_delivery_evidence` | record evidence command where supported | delivery evidence | Discord IDs are evidence pointers only |
| `atn_surface_render_projection` | render visible-surface projection from daemon/control event data | visible surface evidence | local/candidate proof only; cursor order is authority, speech requires matching `speaker_selected` evidence, delivery pointers stay evidence-only, `live_readiness` remains false |
| `atn_discussion_activation_plan` | build dry-run discussion activation planner/doctor report | activation planning evidence | pure/local RUNFIX-006/008/010/012 planner only; explicit caller-provided evidence, effective Discord eligibility, bot-to-bot exclusion, eligible-only allow-list targets, parent-channel inheritance proof/blocker, participant ARGUE response template, runner/ARGUE/canonical speech-link evidence reporting, explicit control/RUNFIX-011 participant runtime readiness diagnostics, fallback audit/disclosure, separated RUNFIX labels, `live_readiness` remains false |
| `atn_discord_send_message` | injected-only visible send helper | delivery plane | no default/live sender; not daemon state |

The plugin must:

- require explicit live transport configuration before opening a daemon socket;
- fail closed when config is absent, unsafe, unavailable, or incompatible;
- use bounded timeouts;
- preserve daemon error categories and identifiers;
- keep `request_id` and `command_id` distinct;
- avoid plugin-owned session state, hidden dedupe, or lifecycle projection.

The plugin must not:

- auto-start the daemon;
- infer current Discord/Hermes thread as a target;
- use CLI subprocess fallback internally;
- create, finalize, or mutate sessions without an explicit typed command;
- substitute fake role-prompt output for a real participant-agent runtime.

### Main agent

The main agent is the user-facing moderator/operator runtime. It converts user natural language into explicit control actions and visible summaries.

The main agent:

- receives user intents such as “create a discussion room”, “change direction”, “grant this participant the floor”, “summarize”, “finish”, or “cancel”;
- creates or binds a visible surface such as a Discord thread when an external delivery layer permits it;
- uses the CLI for session creation, agenda lock, preparation, polling, floor grants, interventions, proposals, vote requests, finalization, unresolved closure, cancellation, diagnostics, and recovery;
- watches daemon stream/status to know when participant outputs arrive;
- posts or asks a delivery helper to post visible messages to the surface;
- records delivery evidence where required.

The main agent may use plugin tools for read-only diagnostics if explicitly configured, but the canonical main-agent control path for LIVE-TRANSPORT is CLI first.

### Participant agent and member runtime

A participant agent is not a simulated role prompt. It is a real profile/member runtime with its own identity, memory, skills, workspace, and session handle.

A member runtime:

1. validates its current registry identity before binding to a session;
2. validates identity against the active session's frozen `registry_snapshot.yaml` after binding;
3. subscribes to the daemon stream through the plugin/protocol client, or uses CLI stream as diagnostics/recovery fallback;
4. replays missed frames before live frames;
5. filters events by type, sender, recipient hints, phase, role, and local policy;
6. invokes or resumes the real participant-agent profile only when action is required;
7. emits typed ATN writes through plugin/protocol-client tools, or CLI fallback in recovery/manual mode;
8. acknowledges cursors only after successful local processing or durable failure handling.

A `speaker_selected` event is not a direct push message to an LLM. It is a durable floor-grant event. A member runtime observes it, decides that its participant identity must act, invokes/resumes the participant agent, and records the result as `council.speak`.

### Delivery layer

The delivery layer renders daemon events to a human-visible surface. It may be the main agent, a helper, or a dedicated integration.

Delivery responsibilities:

- announce session creation and state changes;
- show floor grants and participant speeches;
- show moderator interventions and final conclusions;
- record message IDs or equivalent evidence pointers when needed;
- report delivery failure without rewriting daemon state.

Delivery must not:

- become lifecycle state authority;
- create implicit state transitions from free-form visible messages;
- claim daemon delivery evidence without a daemon-owned evidence command;
- hide failed sends as successful discussion progress.

## Control-plane and agent-plane split

The preferred split is:

```text
control plane:
  user -> main agent -> CLI -> daemon

agent plane:
  daemon stream -> member runtime -> participant agent -> plugin/protocol client -> daemon

delivery plane:
  daemon event/projection -> main agent or helper -> visible surface -> evidence pointer
```

This keeps the user experience simple while preserving auditability:

- users issue natural-language commands only;
- the main agent performs explicit control actions;
- participant agents respond only when their real runtimes observe actionable daemon events;
- every state transition remains a typed daemon event;
- visible chat messages are presentation and evidence, not the source of truth.

## Canonical council scenario

### 1. Create or bind a room

User intent:

```text
Create a discussion room about <topic> with <participant list>.
```

Main agent actions:

1. Create a visible surface, or bind the current surface if already available.
2. Run CLI:

```bash
atn-control council new "<topic>" \
  --members <participant-1>,<participant-2>,<participant-3> \
  --moderator <main-agent-id> \
  --surface discord-thread \
  --thread-id <surface-thread-id> \
  --turn-mode relevance
```

3. Announce `session_id`, topic, participants, and control policy to the visible surface.

Daemon records `session_created`. The visible surface is metadata/evidence only.

### 2. Lock agenda and prepare

User intent:

```text
Discuss this in the direction of <decision criteria>.
```

Main agent actions:

```bash
atn-control council lock-agenda <session_id> \
  --decision-question "<decision question>" \
  --max-rounds <n>

atn-control council request-attendance <session_id> --timeout 5m
atn-control council prepare <session_id> --timeout 10m
```

Participant runtime actions:

- observe `attendance_requested`, emit `council.attend`;
- observe `preparation_requested`, prepare or time out;
- emit `council.ready` or `council.prepared_partial` through plugin/protocol-client writes.

### 3. Poll and grant floor

Main agent actions:

```bash
atn-control council poll <session_id> --research-timeout 10m
```

Participant runtime actions:

- observe `hand_raise_requested`;
- research/fact-check if needed;
- emit `council.hand_raise` when it has relevant input.

Main agent grants floor:

```bash
atn-control council grant <session_id> \
  --to <participant-id> \
  --mode relevance \
  --reason "<why this participant should speak now>"
```

Daemon records `speaker_selected`.

### 4. Participant speaks

Member runtime for the selected participant observes `speaker_selected` and invokes/resumes the real participant-agent profile.

The participant agent emits:

```text
atn_council_command(command="council.speak", ...)
```

or the equivalent protocol-client write. The daemon records `speech`.

The delivery layer renders the speech to the visible surface and stores evidence if required.

### 5. Change discussion direction

For small steering changes, the main agent records an intervention:

```bash
atn-control council intervene <session_id> \
  --to <participant-id> \
  --reason "user_direction_change" \
  --message "<new direction or constraint>"
```

Participant runtimes observe `moderator_intervention` and adjust subsequent actions.

For material decision-question changes, the safe default is:

1. close the current session as `unresolved` or with a partial conclusion;
2. create a new council session with a new locked agenda;
3. link the old session as context/evidence.

A single council has one locked decision question. New topics become follow-up candidates, not silent expansion of the current session.

### 6. Finish, cancel, or mark unresolved

User intent may be natural language, such as:

- “finish and summarize”;
- “end without conclusion”;
- “cancel this discussion”.

Main agent maps the intent to explicit CLI commands.

Normal finalization:

```bash
atn-control council propose <session_id> --from-file draft.md
atn-control council request-vote <session_id> --draft-version <n> --timeout 10m
```

Participant runtimes observe `consensus_vote_requested` and emit `council.vote`.

Main agent finalizes:

```bash
atn-control council finalize <session_id> \
  --authority-return-status posted \
  --return-evidence <evidence-pointer>
```

Unresolved closure:

```bash
atn-control council unresolved <session_id> --reason "<reason>"
```

Cancellation:

```bash
atn-control cancel <session_id> --reason "<reason>"
```

## Live daemon transport contract for the plugin

The plugin live transport is implemented as an explicit local daemon client for
the first read-only smoke slice. The approved plugin config key is
`live_transport.unix_socket_path`; the value must be an absolute filesystem path
to an existing Unix socket.

Required behavior:

- require explicit config before creating a live `client_factory` during plugin registration;
- derive socket path only from explicit `live_transport.unix_socket_path`;
- reject empty, relative, `~`, URL/scheme, localhost/TCP, missing, regular-file, directory, symlink, and permission-denied paths fail-closed;
- avoid symlink traversal and unsafe ownership/mode conditions where practical;
- verify protocol/schema version before marking readiness true;
- use bounded request timeouts;
- return structured `unavailable`, `compatibility`, `protocol`, `validation`, or daemon-preserved command/stream errors;
- preserve `request_id` for wire correlation and `command_id` for daemon idempotency;
- never inspect or mutate daemon storage files directly.

Explicit config absent means tools may register but live dispatch remains unavailable/fail-closed.

Unsafe socket, stale socket, missing daemon, unsupported protocol, malformed response, and unknown schema all fail closed. They must not silently fall back to CLI, localhost, Discord, gateway, or fake success.

`plugin/LTRAN-002` implemented `status.read` and `version.read` over this
transport. `plugin/LTRAN-003` extends the explicit Unix-socket transport to the
bounded equivalence pilot: `stream.tail` maps to daemon `stream.replay`, and
`command.submit` unwraps to a concrete daemon command when `idempotency_key` can
be represented as the daemon `command_id` (`command_id` or `idem-{command_id}`).
Unsupported stream/write operations, unrepresentable idempotency, unsafe sockets,
or malformed daemon responses still fail closed. After LTRAN-003, `stream.ack`
and broader participant council writes are covered only by the PARTC-001
candidate/local implementation proof. `diagnostics.read`, `stream.follow`,
long-lived member runtime behavior, production activation, Discord/gateway
delivery, and KAB bridge readiness remain later explicitly scoped tasks.

## Operation mapping

Plugin operations and daemon command names are not always identical. LIVE-TRANSPORT must resolve the mapping explicitly.

| Plugin-side operation | Daemon command/path | Requirement |
|---|---|---|
| `version.read` | `version.read` | direct mapping |
| `status.read` | `status` or future `status.read` | response must identify protocol version, daemon version, feature groups, readiness |
| `diagnostics.read` | `health` or future `diagnostics.read` | normalize to plugin diagnostics without guessing |
| `stream.tail` | `stream.replay` / bounded tail command | implemented in `plugin/LTRAN-003` for bounded replay tail equivalence; preserve replay-before-live, cursor, member, limit semantics |
| future `stream.follow` | `stream.replay` with follow or daemon follow stream | bounded and resumable; no silent gaps |
| `stream.ack` | `stream.ack` | PARTC-001 candidate implementation; acknowledge only after processing and only within explicit live transport configuration |
| `command.submit` | concrete daemon command | implemented in `plugin/LTRAN-003` for commands that carry a daemon `command_id`; unwrap to `delegate.*`, `council.*`, delivery evidence commands; do not assume generic daemon alias unless implemented |

For LIVE-TRANSPORT, participant-agent writes through the plugin should focus on participant-originated events: `council.attend`, `council.ready`, `council.prepared_partial`, `council.hand_raise`, `council.speak`, and `council.vote`. Main-agent control commands should prefer CLI even if the plugin can technically submit the same command envelope.

## ID and idempotency rules

Keep correlation and idempotency distinct:

- `request_id`: one daemon request/response correlation handle;
- `command_id`: logical state-mutating command identity used by daemon dedupe;
- `event_id`: daemon-generated or validated event identity;
- `correlation_id`: logical thread across related commands/events, normally the session.

Current plugin schemas expose `idempotency_key` in some command tools. Keep that
public schema stable. For daemon-facing write work, document and implement
`idempotency_key` as the legacy/request-side value that maps internally to the
daemon `command_id`; do not rename public plugin fields without a separate
breaking-change task. The long-term daemon SOT term remains `command_id`.

Retries for the same logical command must reuse the same `command_id`. A participant runtime must not emit duplicate speeches, votes, or hand raises by generating a new command id after a transport retry unless policy explicitly creates a new logical action.

## Member runtime requirements

LIVE-TRANSPORT cannot rely on plugin tools alone to make participant agents answer. A member runtime is required.

Minimum member-runtime capabilities:

- one runtime identity per participant member;
- active-session discovery or explicit session binding;
- stream replay from last acknowledged cursor;
- event filtering for actionable events;
- wrapper/profile invocation for the real participant agent;
- prompt/context construction from agenda, recent transcript, selected event, and participant role;
- typed write submission through plugin/protocol client;
- cursor acknowledgement after processing;
- durable failure handling when wrapper invocation fails.

Action examples:

| Observed event | Participant action |
|---|---|
| `attendance_requested` addressed to participant | record `council.attend` |
| `preparation_requested` addressed to participant | prepare, then record `council.ready` or `council.prepared_partial` |
| `hand_raise_requested` | decide whether to record `council.hand_raise` |
| `speaker_selected` addressed to participant | invoke/resume participant agent and record `council.speak` |
| `moderator_intervention` addressed to participant | adjust next action/speech or withdraw/clarify |
| `consensus_vote_requested` | evaluate draft and record `council.vote` |
| terminal phase event | stop or detach from the session after acknowledgement |

Failure to invoke a participant should not be replaced with a simulated role response. Record or surface a participant runtime failure and let the main agent retry, mark partial, intervene, block, or close unresolved according to policy.

## MVP versus target implementation

### MVP: main-agent mediated participant invocation

The MVP may avoid always-on participant runtimes by letting the main agent or a local supervisor invoke the selected participant profile when floor is granted.

MVP flow:

1. main agent uses CLI to grant floor;
2. supervisor observes `speaker_selected` or main agent reads status/stream;
3. supervisor invokes/resumes the real participant-agent profile;
4. participant output is submitted as `council.speak` through plugin/protocol client or explicit CLI fallback;
5. delivery layer renders the speech.

MVP constraints:

- must invoke a real participant profile/wrapper, not a role prompt;
- must record durable events in daemon before visible completion claims;
- must preserve `command_id` and runner/session evidence;
- must not claim long-lived stream-driven runtime readiness.

### Target: long-lived member runtime

Target flow:

1. each participant runtime continuously follows the daemon stream;
2. runtimes maintain durable cursor ack state;
3. runtimes autonomously invoke/resume participant agents when addressed by actionable events;
4. participants submit typed writes through plugin/protocol-client tools;
5. main agent only moderates, observes, and controls the session.

Target constraints:

- stream gaps, unknown schema, registry mismatch, stale heartbeat, and unsafe runtime state fail closed;
- cursor acknowledgement happens only after processing;
- one participant identity cannot be silently substituted for another;
- wrapper failures are recorded and surfaced.

## Visibility and delivery evidence

The visible room is not the source of truth.

Rules:

- `channel.jsonl` is canonical for ordering and lifecycle;
- Discord or other room messages are presentation/evidence;
- free-form visible replies do not become state unless the main agent or participant runtime emits a typed daemon command;
- every visible speech should correspond to a daemon `speech` event;
- every final visible result should correspond to `council_finalized`, `council_unresolved`, or `session_cancelled`;
- delivery failures are not rewritten as successful discussion progress;
- delivery evidence, when required, records message ids or report paths as evidence pointers.

## Security and safety boundaries

LIVE-TRANSPORT must preserve these boundaries:

- no credential, token, auth, or gateway mutation without explicit approval;
- no live Discord default from plugin registration;
- no current-thread or active-session inference inside plugin helpers;
- no daemon storage writes outside daemon commands;
- no participant identity substitution;
- no hidden CLI fallback inside plugin code;
- no TCP/localhost fallback unless separately approved and tested;
- no production activation claim from disposable local pilots;
- no KAB bridge execution claim from direct CLI/plugin pilots.

## Verification requirements

A LIVE-TRANSPORT implementation is not complete without evidence for all applicable layers.

### Local plugin checks

```bash
make test-prepare
make check-core-contract
make test
```

Required plugin-specific assertions:

- no-config plugin load still registers tools and fails closed;
- explicit config with missing daemon returns structured `unavailable`;
- unsafe data home/socket fails closed;
- malformed daemon response returns structured `protocol` failure;
- unsupported protocol/feature returns `compatibility` failure;
- live disposable daemon status/version path passes;
- participant write command reaches daemon with preserved `request_id` and `command_id`;
- duplicate `command_id` proves daemon dedupe behavior;
- no plugin-internal CLI shell-out occurs.

### CLI/daemon equivalence checks

Disposable data-home pilot should prove:

- CLI `daemon status` and plugin `atn_daemon_status` address the same daemon/data home;
- CLI `version --features --format json` and plugin compatibility diagnostics agree on required feature groups;
- CLI council command and plugin participant write produce equivalent daemon events;
- CLI stream/tail and plugin stream/tail return compatible frames/cursors;
- transcript/export reflects daemon events, not visible surface guesses.

### Member runtime checks

MVP checks:

- real participant profile/wrapper is invoked when selected;
- generated speech is recorded as `council.speak` before visible success is reported;
- wrapper failure is reported without fake replacement;
- cursor/replay evidence or explicit MVP limitation is recorded.

Target checks:

- participant runtime replays from last cursor;
- actionable event filtering works;
- selected participant speaks exactly once per logical floor grant unless retried with same `command_id`;
- `stream ack` happens after processing;
- registry mismatch and unknown schema fail closed;
- stale participant handling is visible to the main agent.

### Delivery checks

- visible message rendering uses daemon event data;
- delivery evidence is recorded as evidence pointer only;
- delivery failure does not mark the council finalized/posted unless an explicit failed/pending evidence status is recorded.

## Plugin implementation slices

### LTRAN-001: plugin SOT and cross-repo mapping

Status: completed docs-only. This closeout locked the plugin-side source of truth and mapping without changing source code, tests, backend behavior, daemon state, plugin registration, live transport, production activation, Discord delivery, gateway/auth/token behavior, KAB behavior, or any hidden CLI fallback. Follow-on `plugin/LTRAN-002` is now completed as the first bounded implementation task for explicit Unix-socket status/version smoke.

Deliverables:

- this plugin SOT and cross-links in docs map/index;
- cross-link to the control companion SOT;
- explicit repo-owned epic/task split;
- no-scope list for production activation, live Discord, gateway/auth/token, KAB, and hidden CLI fallback.

Repo-qualified dependency evidence:

- `control/LTRAN-001` is completed in `../../agent-turn-network-control/docs/24-live-transport-control-sot.md` and `../../agent-turn-network-control/docs/roadmap.md` as the control-side SOT/mapping task.
- `control/LTRAN-002` is completed with explicit daemon compatibility-read evidence for `version.read`, `status.read`, `diagnostics.read`, bounded stream replay/follow/status/ack, and command-path feature evidence.
- `control/LTRAN-003` is completed with disposable live-local CLI/daemon evidence and no production activation or plugin mutation claim.
- These control completions were dependency evidence for `plugin/LTRAN-002`; plugin live transport is implemented only within the bounded explicit status/version smoke slice recorded below. They still do not authorize live/production/Discord/gateway/auth/token/KAB/hidden CLI fallback behavior in this repository.

### LTRAN-002: plugin live daemon transport

Status: completed for the bounded read-only smoke slice. The plugin now exposes
an explicit register-time live client factory from `live_transport.unix_socket_path`
and a Unix-socket JSON request transport for `status.read` and `version.read`
only. The implementation preserves no-config fail-closed behavior and rejects
unsafe or unavailable paths without CLI, localhost/TCP, Hermes, Discord,
gateway, auth, token, KAB, profile/provider mutation, or production activation
claims.

Deliverables:

- explicit Unix socket client transport: completed;
- config loader and register-time `client_factory` injection: completed;
- no-config fail-closed preservation: completed;
- unsafe/missing/malformed/unsupported daemon tests: completed;
- local status/version transport smoke: completed with a socket-boundary test double;
- disposable real-daemon live status/version smoke: completed against a temporary `/tmp` data-home and sibling control daemon binary, with no production activation claim.

### LTRAN-003: plugin/CLI/daemon equivalence pilot

Status: completed for the bounded live-local equivalence slice. The plugin now
maps `stream.tail` to the daemon `stream.replay` command and maps
`command.submit` to concrete daemon commands when the public `idempotency_key` is
representable as the daemon `command_id`. Unrepresentable idempotency fails
closed before socket connect. Structured daemon command errors are preserved as
daemon command errors. This completion does not claim production activation,
live/default Discord delivery, gateway/auth/token/provider/profile mutation, KAB
bridge readiness, long-lived member runtime readiness, broad command coverage, or
hidden CLI fallback.

Deliverables:

- disposable data home: completed with `/tmp/kanl3-*` short-path data home;
- daemon started through CLI: completed with temporary control CLI and daemon binaries;
- plugin configured explicitly against that data home: completed through
  `live_transport.unix_socket_path` targeting the disposable daemon socket;
- CLI and plugin stream/write equivalence evidence: completed;
- no production activation claim: preserved;
- stream/write support, command-id/idempotency equivalence, and daemon dedupe
  proof: completed for the bounded `stream.tail` and `command.submit` slice.

Evidence:

- targeted integration: `UV_CACHE_DIR=/tmp/kkachi-plugin-uv-cache uv run pytest tests/integration/test_live_unix_socket_transport.py -q` → 8 passed;
- full plugin gates: `make test-prepare && make test && make check-core-contract` → unit 227 passed, integration 59 passed, e2e 13 passed, core contract OK;
- durable real-daemon smoke evidence:
  `docs/evidence/ltran-003-plugin-equivalence-evidence.json`;
- the smoke confirms CLI stream and plugin `stream.tail` event IDs match before
  and after plugin writes, plugin `delegate.ack` + `delegate.submit` append
  durable daemon events, duplicate `command_id` returns the same event, a
  conflicting duplicate fails with daemon `command_id` conflict, and the daemon
  stops cleanly.

### PARTC-001: participant-agent plugin path

Deliverables:

- participant-focused stream support: `stream.tail` already exists from `plugin/LTRAN-003`; `stream.ack` is implemented in the PARTC-001 candidate;
- `stream.follow` is intentionally deferred/not required for PARTC-001 unless a separate task scopes it;
- participant-originated council writes through plugin/protocol client;
- command-id/idempotency coverage;
- tests for `ready`, `hand_raise`, `speak`, and `vote` write paths.

PARTC-001 remains candidate/local implementation proof only. It does not claim PARTC-002 selected real participant profile response proof, production activation, live/default Discord delivery, gateway/auth/token/provider/profile mutation, or KAB bridge readiness.

### PARTC-002: selected participant response through plugin path

Deliverables:

- candidate/local bounded no-live proof for `atn_selected_participant_response` using fake/injected control `MEMBR` evidence only;
- validate `speaker_selected` recipient/member evidence and participant response provenance without simulated role substitution;
- submit the resulting participant response through plugin/protocol-client `council.speak`;
- acknowledge the selected stream cursor only after the `council.speak` submit succeeds;
- preserve separate evidence for speak, ack, and proof records, with `live_readiness` false.

Evidence:

- implementation and bounded proof manifest:
  `docs/evidence/partc-002-selected-participant-response-evidence.json`;
- targeted unit proof:
  `uv run pytest tests/unit/test_selected_participant_response.py -q` → 12 passed;
- targeted schema/entrypoint/bootstrap/load smoke:
  `uv run pytest tests/unit/test_selected_participant_response.py tests/unit/test_tool_schemas.py tests/unit/test_plugin_entrypoint.py tests/unit/test_bootstrap_smoke.py -q && make check-plugin-load-smoke` → 36 passed and plugin-load smoke OK;
- full local gate recorded by Blue:
  `make check-core-contract && make test-prepare && make test && git diff --check` → check-core-contract OK, test-prepare OK, unit 252 passed, integration 60 passed, e2e 13 passed, `git diff --check` exit 0.

Boundaries:

- this proof does not consume or invoke a real participant profile/wrapper at runtime;
- it does not claim production activation, live/default Discord delivery, gateway/auth/token/provider/profile mutation, KAB readiness, or long-lived member runtime readiness;
- the future real participant-profile pilot remains approval-gated and must provide separate runtime evidence before PARTC-002 can be treated as real-profile/runtime approved.

### SURFD-001: visible room helper/rendering boundary

SURFD-001 candidate/local implementation proof is in place through
`atn_surface_render_projection`. The tool renders explicit daemon/control
projection event JSON into separated `visible_transcript` and `audit_log`/`rows`:
operator-facing transcript entries include session header, compact floor grant,
selected participant speech, draft closeout proposals, vote progress, and final
moderator closeout, while raw cursors/event ids remain in audit rows and evidence
artifacts. The tool does this without reading daemon state, reading or sending
Discord messages, reading environment variables, starting or stopping daemons,
shelling out to CLI fallbacks, mutating gateway/auth/token/provider/profile
state, or claiming production/live readiness.

Deliverables:

- main-agent or helper rendering from daemon events;
- speech/final result posting to visible surface where authorized;
- delivery evidence pointer handling;
- failure and pending-follow-up behavior.

Local proof boundaries:

- cursor/order authority stays with daemon/control projection input;
- `speech` renders only after a prior matching `speaker_selected` floor grant
  for the same turn/member;
- `draft_conclusion`, `consensus_vote_requested`, and `consensus_vote` render as
  process/draft/vote transcript entries, not final closeout;
- when `require_terminal_closeout: true`, the renderer fails closed unless a
  terminal `council_finalized`, `council_unresolved`, or `session_cancelled`
  event has posted visible evidence with an explicit reference back to that
  terminal event; missing or mismatched terminal-event references are not
  accepted as visible closeout proof;
- terminal visible/linked-authority status preserves `posted`, `failed`,
  `pending_followup`, and `missing/unproven`;
- unsupported event types, unsupported schema versions, duplicate cursor
  authority, floor-grant mismatches, and proofless delivery evidence fail closed;
- `atn_discord_send_message` remains injected-only and non-default.


### RUNFIX-015: visible author guard (local implementation proof)

`plugin/RUNFIX-015` local implementation proof is recorded under plugin KAH run `run-20260619T071526Z-7d2ba33b07d5`. The pure/local `atn_discussion_activation_plan` now exposes a pre-`council.new` `visible_author_guard_report` from explicit caller-provided evidence only. It does not read profiles, gateway config, Discord state, environment, sockets, or live messages, and it does not claim runtime enforcement unless a caller/operator path consumes blockers before session creation.

Implemented acceptance:

- probe each selected participant's outbound Discord identity through the same posting path used for turns before `council.new`;
- record `profile`, expected author source (`registry_snapshot` or explicit approved profile-author map), `bot_id`, `username`, `source_env`, and `posting_path` as evidence;
- test env merge precedence as shared defaults first and profile-local env second;
- fail closed before session creation if any selected participant resolves to a shared/default or unexpected author;
- attach per-turn Discord message id, selected member, profile author id, posting path, and `speech_event_id` to visible evidence;
- final reports separate lifecycle, visible turns, real profile/gateway replies, and shared/default author fallback status.

This is a plugin/operator-harness planning entry only; it does not authorize live Discord delivery, profile/gateway/auth/token/provider mutation, production activation, or live readiness.

### RUNFIX-017: ARGUE quality-required prompt contract (local implementation proof)

`plugin/RUNFIX-017` hardens quality-required council prompts and selected participant response guidance so machine-auditable ARGUE graphs do not depend on human-readable prose alone. This is local implementation-candidate evidence until official color review, Blue synthesis, and final KAH closeout pass.

Implementation-candidate acceptance:

- selected-participant prompts include a compact prior claim graph with `event_id`, optional `claim_id`, and prompt-guidance-only `speaker`, `summary`, and `available_stances`;
- non-opening quality-required turns with sufficient local context include at least one `stance_links[]` target that validates against caller-provided `event_id`/`claim_id` targets, or declare `contribution_type: "new_axis"` with non-empty `new_axis_reason`;
- `atn_selected_participant_response` and operator guidance preserve `claims[]`, `stance_links[]`, `contribution_type`, `new_axis_reason`, and optional `evidence[]` without synthetic inference;
- `atn_discussion_activation_plan` requires explicit `discussion_quality` evidence for the quality gate rather than substituting participant-response summaries;
- in `quality_required`, the first orphan non-opening speech blocks `discussion_quality_pass`; repeated orphan counts remain diagnostic evidence, and warning-only behavior is reserved for `quality_warn`;
- final reports split `lifecycle_pass`, `discussion_quality_pass`, `orphan_speech_count`, `linked_speech_count`, `stance_link_count`, and `new_axis_count`.

Only caller-provided `event_id` and `claim_id` are local relation-validation authority. `responds_to_event_id`, visible prose, keywords, Discord order, Hermes messages, `speaker`, `summary`, and `available_stances` remain prompt/display guidance only. Control/RUNFIX-005 remains the quality diagnostics authority, and no production/live readiness or profile/provider/gateway/auth/token mutation is authorized.

## Remaining decisions for post-LTRAN-003 slices

Resolved for `plugin/LTRAN-002`:

- The approved explicit plugin config key is `live_transport.unix_socket_path`; it is supplied at register/config time and must be an absolute path to an existing Unix socket.
- The bounded LTRAN-002 live transport slice supports only `status.read` and `version.read` over the explicit Unix socket. Control's current daemon status response may be normalized safely for this read-only smoke slice, while missing or malformed protocol fields fail closed.
- Existing public schemas keep `idempotency_key` for compatibility; live transport bridges daemon `command_id` only where an explicitly scoped command/write slice requires it.

Resolved for `plugin/LTRAN-003`:

- The first stream/write equivalence pilot is bounded to explicit Unix-socket
  `stream.tail` and `command.submit` against a disposable daemon/data home.
- `stream.tail` uses daemon `stream.replay`; the plugin applies tail limiting to
  the final N replayed frames and preserves cursor evidence in the normalized
  stream result.
- `command.submit` bridges public `idempotency_key` to daemon `command_id` only
  when the values are equivalent (`command_id` or `idem-{command_id}`); otherwise
  it fails closed before socket connect.
- Real-daemon smoke evidence is recorded at
  `docs/evidence/ltran-003-plugin-equivalence-evidence.json`.

Still open for later `PARTC`, `SURFD`, or future LTRAN hardening tasks:

1. Does the first participant pilot use MVP participant invocation or long-lived member runtimes?
2. Which delivery layer owns visible surface posting in the first pilot?
3. What is the minimum acceptable evidence that a participant answer came from the real participant-agent profile?
4. Whether production-grade stream tail needs a server-side limit/bounded replay command instead of client-side tail slicing.

Later implementation may proceed only on slices that do not depend on an unresolved future decision, or must record the selected default in the task contract before coding.
