# Plugin Implementation Epics and Tasks

## Scope

This roadmap and task backlog is for `atn-plugin`. Control daemon/CLI roadmap lives in `../../agent-turn-network-control/docs/09-implementation-epics.md` and `../../agent-turn-network-control/docs/roadmap.md`; those sibling paths are current local compatibility paths for public `atn-control` references.

Task status values are limited to:

- `planned`: accepted into the backlog but not started.
- `in_progress`: currently under an active implementation or docs run.
- `implementation_complete/review_pending`: implementation and fixed minimum gates are complete, but official focused/color review and Blue acceptance are still pending. A task in this state must not be marked `completed` until review closeout is accepted.
- `completed`: completed with verification evidence and accepted review closeout.
- `blocked`: blocked by an external dependency, missing input, unavailable fixture, or approval gate.

## KAS/Codex task sizing policy

Tasks after the SCAFF epic are sized as KAH/KAS execution slices for enterprise-style software development. A task should produce one reviewable capability with durable evidence, not just one file or internal component.

Each task should normally include:

- a task contract and plan captured before implementation;
- one Codex app-server implementation lane or an explicitly recorded no-backend/docs-only rationale;
- focused unit and integration coverage, with fake daemon or conformance fixtures where live core behavior is not available;
- documentation and roadmap updates for changed operator behavior;
- Red/Orange/Gray review when code or operator behavior changes, or narrower role review when the task is docs-only and 주군 explicitly narrows the reviewer set;
- feedback handling, final verification, and one commit after 주군 approval.

Split a task only when the dependency, approval gate, failure domain, or reviewer specialty is materially different. Do not split schema from handler, handler from error behavior, or client implementation from conformance coverage when those pieces are required to prove the same operator-facing capability.

## Control dependency gates

The plugin may develop ahead of `agent-turn-network-control` only when a task can be completed against docs, local fakes, or control conformance fixtures. When a task requires a control daemon capability, command, feature flag, fixture, or delivery-evidence path that does not exist yet, keep or move that task to `blocked` instead of inventing plugin-side fallback behavior.

Historical completed plugin tasks before the post-Release live-local work preserve their original short task IDs such as `SCAFF-1`, `DAEMN-1`, and `SKILL-2` for audit continuity. New post-Release cross-repo live-local epics normally use five-letter uppercase epic IDs and three-digit task IDs. `ATN` is the current public rename epic for Agent Turn Network. Explicit user-approved exceptions include `RUNFIX2`, `RUNFIX3`, and the `NEXFIX` epic whose requested task id prefix is `NEWFIX-*`. When a capability spans control and plugin, both repositories use the same epic ID and one globally sequential task number stream; cite tasks with repo-qualified notation such as `control/RUNFIX-001` or `plugin/RUNFIX-002`. A repo-local roadmap may therefore skip numbers owned by the sibling repo.

Use `docs/07-core-compatibility.md` as the compatibility SOT. The short rule is:

- `SCAFF` can complete before control implementation because it is scaffold/docs/test harness work; its upstream scaffold gate is `BOOTS-001`.
- `DAEMN` can progress with fixtures and fake daemon responses; live/client completion waits for stable control protocol fixtures and daemon status/version surfaces from `DAEMN-002`.
- `HPLUG` can define and test read-only plugin surfaces ahead of control only when matching fake responses or conformance fixtures exist; live tool completion waits for matching daemon/session/status/stream contracts from `DAEMN-002`.
- `DELRV` waits for implemented control delegation/review commands and fixtures from `DELEG-001` before non-skeleton completion.
- `CNDIS` waits for implemented council paths from `COUNC-001` and delivery-evidence command paths from `DAEMN-002` before non-skeleton completion.
- `SKILL` can complete the local compatibility matrix and local isolated plugin-load smoke once `TRANS-001`/`RELIA-001` evidence is recorded, but still cannot claim production activation, KAB readiness, live plugin readiness, live Discord readiness, or live daemon discovery without separate isolated/live tasks.
- `REL-PILOT-FIX` may repair local packaging/import blockers discovered by disposable profile pilots, but those repairs remain local activation-smoke evidence only unless a separately approved live-readiness task runs against live Hermes/Discord/daemon resources.

## SCAFF: Scaffold

Epic ID: `SCAFF`

Exit: `make test` and `make check-core-contract` pass without live Hermes, Discord, daemon, or network resources. `make check-core-contract` intentionally requires the local companion control repository, `ATN_CONTROL_REPO`, so protocol drift is detected. This epic may claim scaffold readiness only; do not claim installed/working Hermes integration until an install/plugin-load smoke test exists in `SKILL`.

SCAFF intentionally used smaller tasks to validate KAH/KAS/Codex collaboration and review gates. Future epics use larger capability slices to reduce KAH overhead while preserving evidence, review, feedback, and approval gates.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| SCAFF-1 | Initialize Python package layout | completed | Created `pyproject.toml`, `src/` package layout, package metadata, and a minimal importable module with local-only scaffold tests and review evidence. |
| SCAFF-2 | Add plugin manifest and entrypoint | completed | Added `plugin.yaml` and a minimal no-op Hermes directory plugin entrypoint matching the documented plugin contract, with focused manifest/entrypoint tests and review evidence. |
| SCAFF-3 | Establish Makefile target contract | completed | Tightened Makefile target contract, added `check-make-contract` drift verification, preserved offline/isolated test defaults, and recorded review evidence. |
| SCAFF-4 | Add docs and contract guardrails | completed | Added import-safe docs/core contract guardrails, focused guardrail unit tests, all-doc stale sibling path scanning, and recorded review/verification evidence. |
| SCAFF-5 | Add bootstrap smoke tests | completed | Added `check-bootstrap-smoke`, bootstrap smoke unit coverage, Makefile contract drift checks for the target, and review/verification evidence. |

## DAEMN: Python daemon client

Epic ID: `DAEMN`

Exit: the plugin has a fail-closed Python client foundation that can speak to the core daemon contract through fake daemon responses or conformance fixtures, with no live daemon required by default tests.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| DAEMN-1 | Implement control protocol client foundation | completed | Implemented status/version reads, command envelope serialization, structured daemon error decoding, idempotency-ready request metadata, and conformance/fake-daemon tests for the minimum safe daemon client. This is fake/injected transport only; live-client readiness remains blocked until stable control status/version fixtures and protocol declarations exist. |
| DAEMN-2 | Implement stream and diagnostics client surfaces | completed | Implemented stream frame parsing, malformed-frame protection, diagnostics response decoding, and fake-daemon coverage for tail/read-only diagnostic paths. Stream tail reads require positive `stream_frame` feature compatibility before `stream.tail` runs. Live stream claims remain blocked until the core stream/status contracts exist. |

## HPLUG: Hermes plugin surface

Epic ID: `HPLUG`

Exit: read-only Hermes plugin tools expose the daemon client safely through JSON-returning handlers with fail-closed errors, documented unsupported surfaces, and no hidden live-resource fallback.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| HPLUG-1 | Add read-only Hermes plugin tools | completed | Defined schemas and implemented fail-closed JSON-returning handlers for daemon status and compatibility diagnostics backed by DAEMN client fixtures. `atn_session_status` is deferred because core `session.status.read` fixture/protocol authority is not available. Closure review: Red `t_bd2965d2`, Orange `t_b18e05d5`, Gray `t_42ad6902` ACCEPT. |
| HPLUG-2 | Add session status and stream/tail plugin tools | completed | Implemented the fake/injected `atn_stream_tail` read-only plugin tool with stream-frame compatibility probing, malformed-frame protection, JSON-string fail-closed handler coverage, and operator docs. `atn_session_status` remains deferred because matching core `session.status.read` fixture/protocol authority is not available. Final closure reviews: Red `t_51358e60` ACCEPT, Orange `t_c6e67e69` ACCEPT, Gray `t_4fcec3cd` ACCEPT. |
| HPLUG-3 | Document unsupported slash-command bindings | completed | Historical row: recorded unsupported Hermes/ATN surfaces and future binding requirements while keeping `provides_commands: []` and avoiding live/install readiness claims. Closure reviews: Red `t_588e6985` ACCEPT, Orange `t_c66d72c8` ACCEPT, Gray `t_c2f2e318` ACCEPT after sidecar cleanup. |

## DELRV: Delegation and review tools

Epic ID: `DELRV`

Exit: delegation and review plugin tools map to implemented control commands with idempotency, structured errors, fake-daemon coverage, and no plugin-owned state authority.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| DELRV-1 | Add delegation and review command tools | completed | Implemented and locally verified fake/injected-only `atn_delegate_new` -> `delegate.new` and `atn_delegate_action` -> exact implemented `delegate.*` action/review/delivery command-envelope tools. The plugin requires caller-supplied `request_id`/`idempotency_key`, rejects `delegate.request`, top-level `review`, and non-enum commands before transport, preserves structured daemon errors, keeps `provides_commands: []`, and does not claim live daemon/plugin-load/release readiness. Completion evidence: KAH `run-20260605T182154Z-3fbf63b18b6e`, local `make test-prepare`, `make check-core-contract`, and `make test` pass after optimize, first color review, GLM Octo feedback handling, post-Octo re-review, final KAH gate pass, and 주군 commit approval. |
| DELRV-2 | Add delegation/review failure coverage | completed | Added fake-daemon integration tests for delegation/review success, duplicate/idempotency, permission/validation error, retryability preservation, and malformed response cases. Completed after kan-control `DELEG-002` conformance fixture matrix unblock, GLM Octo PASS, post-Octo Red/Orange/Gray re-review ACCEPT, and final verification evidence. |

## CNDIS: Council and Discord surface

Epic ID: `CNDIS`

Exit: council and delivery-evidence surfaces preserve core-owned state and evidence while providing safe Hermes/Discord operator UX in isolated test paths.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| CNDIS-1 | Add council and delivery-evidence plugin tools | completed | Expose implemented council command and delivery-evidence command surfaces through plugin tools while preserving daemon-owned logs, locks, cursors, and evidence transitions. Completed after kan-control `COUNC-001` council paths and `DAEMN-002` delivery-evidence command paths, local verification, first color review, official GLM Octo PASS, post-Octo feedback handling, and final Gray traceability follow-up acceptance. |
| CNDIS-2 | Add Discord helper and isolated E2E coverage | completed | Added the injected-only `atn_discord_send_message` helper and isolated no-live E2E coverage. It never defaults to live Discord or the current Hermes session; any real send path requires an injected sender, dedicated target metadata, visible labels, and cleanup guidance. Completed after local verification, first color review, official GLM Octo PASS, post-Octo feedback handling, and post-Octo Red/Orange/Gray re-review acceptance. |

## SKILL: Skill and distribution

Epic ID: `SKILL`

Exit: the plugin has operator-facing skill/docs, compatibility matrix, troubleshooting, and local isolated plugin-load smoke evidence. This exit is not a production activation, KAB readiness, live plugin readiness, or live Discord readiness claim.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| SKILL-1 | Add bundled ATN skill and operator docs | completed | Historical row: added the bundled `atn-plugin` skill surface, import-safe resource reader, install/enable/rollback documentation, troubleshooting guide, and docs/tests guardrails aligned with the plugin's actual fake/injected capabilities and unsupported surfaces. ATN-005 later replaced public packaged skill resources with `atn-plugin`, `atn-moderator`, and `atn-participant`. This does not claim installed-plugin or live readiness; SKILL-2 owns plugin-load smoke. Completed after KAH verification, Red/Orange/Gray review, Orange feedback handling and re-review, official GLM Octo PASS, final gate evidence, and 주군 commit approval. |
| SKILL-2 | Add compatibility matrix and plugin-load smoke | completed | Adds the compatibility matrix and `make check-plugin-load-smoke` local isolated plugin-load smoke gate after recording completed control `TRANS-001` and `RELIA-001` evidence as unblock sources. The smoke creates a temporary plugin home from repository files, loads `register(ctx)` with a fake Hermes context, asserts exact tool order, zero hooks, zero commands, fail-closed JSON handlers, live-looking environment inertness, negative command-overclaim fixtures, wheel package inclusion, and bundled skill compatibility. This is local isolated plugin-load smoke only; it does not claim production activation, KAB readiness, live plugin readiness, live daemon discovery, live/default Discord sending, or any change to `provides_commands: []`. Completed after verification, required reviews, final gates, and 주군 commit approval. |

## REL-PILOT-FIX: Release pilot activation repairs

Epic ID: `REL-PILOT-FIX`

Exit: disposable-profile activation blockers discovered by local pilots are captured as regression tests and local smoke coverage while preserving `provides_commands: []`, zero hooks, no live fallback, and no live Discord/Hermes/daemon readiness claim.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| REL-PILOT-FIX-001 | Repair root plugin activation blockers | completed | Repairs the root directory-plugin entrypoint so a cloned/staged repository can load its bundled `src/` package without external `PYTHONPATH`, replaces Python 3.12-only protocol type-alias syntax with Python 3.11-compatible aliases, lowers packaging/tooling metadata to Python `>=3.11`, and strengthens local smoke/unit coverage so production-style root entrypoint loading and Python 3.11 syntax compatibility fail fast. This remains local-only activation-smoke evidence and does not claim live Discord readiness, live daemon discovery, KAB readiness, or live Hermes production readiness. Completed after final gates, 주군 commit approval, and committed-HEAD disposable profile install verification. |
| REL-PILOT-FIX-002 | Load explicit plugin live config for profile-installed plugin | completed | Loads only adjacent plugin-local `config.yaml` with the approved `live_transport.unix_socket_path` shape when Hermes calls the root directory-plugin `register(ctx)` without explicit `config=` or `client_factory=`. Explicit overrides keep precedence; missing, malformed, unknown-key, unsafe, stale, or environment-looking config remains fail-closed through structured handler `ok=false` evidence without discovery crashes, CLI fallback, daemon auto-start, env/socket autodiscovery, localhost/TCP/URL transport, Discord/Hermes lifecycle inference, gateway/auth/token/provider/profile mutation, fake success, KAB readiness, production readiness, or live Discord readiness claims. Completed for bounded task verification only after targeted tests, plugin-load smoke, and repo gates in run `run-20260616T152624Z-4ae17d4704d8`. |

## LTRAN: Live daemon transport

Epic ID: `LTRAN`

Exit: the plugin has an explicit, locally verified live daemon transport that preserves daemon authority, keeps the CLI as the main-agent control plane, keeps the plugin as the participant-agent ATN client surface, and proves plugin reads/writes address the same daemon contract as the CLI. This exit is not production activation, live/default Discord delivery, gateway/auth/token mutation, or KAB bridge readiness.

SOT: `docs/10-live-transport-sot.md`. Control companion SOT: `../../agent-turn-network-control/docs/24-live-transport-control-sot.md`.

Dependency gate: complete the control `LTRAN` epic before starting the plugin `LTRAN` implementation epic. Do not switch from plugin `LTRAN` to control tasks mid-epic; if a missing control capability is discovered, block the plugin epic and open/complete the needed control epic before resuming plugin work.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| LTRAN-001 | Lock plugin live transport SOT and mapping | completed | Docs-only SOT/mapping closeout: `docs/10-live-transport-sot.md`, `docs/README.md`, `docs/kkachi-docs-map.yaml`, and `docs/07-core-compatibility.md` record the plugin-side daemon/plugin/CLI relationship, main-agent CLI control-plane policy, participant-agent plugin path, operation mapping, ID/idempotency rules, non-scope boundaries, and the control companion SOT dependency. No backend/source/test code changed, no live transport was implemented, and no live/production/Discord/gateway/auth/token/KAB/hidden CLI fallback readiness is claimed. Repo-qualified dependency evidence: control `docs/24-live-transport-control-sot.md` and control `docs/roadmap.md` mark `control/LTRAN-001`, `control/LTRAN-002`, and `control/LTRAN-003` completed; plugin implementation remains handed off to `plugin/LTRAN-002` as the first implementation task. |
| LTRAN-002 | Add explicit plugin live daemon transport | completed | Implemented explicit `live_transport.unix_socket_path` register-time Unix-socket client factory for `status.read` and `version.read` live smoke only. No-config still fails closed; empty, relative, `~`, URL/scheme, localhost/TCP, missing, regular-file, directory, symlink, permission, malformed-response, and unsupported-operation paths fail closed without CLI, localhost/TCP, Discord, Hermes, gateway, auth, token, KAB, provider/profile mutation, or production activation fallback. |
| LTRAN-003 | Prove plugin/CLI/daemon equivalence | completed | Implemented bounded explicit Unix-socket equivalence for `stream.tail` and `command.submit`: plugin `stream.tail` maps to daemon `stream.replay`, plugin `command.submit` unwraps to concrete daemon commands when public `idempotency_key` is representable as daemon `command_id`, and unrepresentable idempotency fails closed before socket connect. Evidence includes targeted integration coverage, full plugin gates, core contract check, and durable isolated real-daemon smoke at `docs/evidence/ltran-003-plugin-equivalence-evidence.json`. This remains local-only live-daemon equivalence and does not claim production activation, live/default Discord, gateway/auth/token/provider/profile mutation, KAB readiness, long-lived member runtime readiness, broad command coverage, or hidden CLI fallback. |

## PARTC: Participant client path

Epic ID: `PARTC`

Exit: participant agents can observe actionable daemon events and submit participant-originated council writes through the plugin/protocol-client path, with member runtime invocation evidence supplied by the completed control `MEMBR` epic. This exit does not claim always-on production runtimes or simulated role substitution.

SOT: `docs/10-live-transport-sot.md`. Control companion SOT: `../../agent-turn-network-control/docs/24-live-transport-control-sot.md`.

Dependency gate: complete the control `MEMBR` epic before starting plugin `PARTC`. Active task transfer between repos happens only at the epic boundary.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| PARTC-001 | Add participant stream and write coverage | candidate/local implementation proof | Candidate implementation evidence covers participant-focused `stream.tail` reuse from LTRAN-003, PARTC-001 `stream.ack`, and `council.attend`, `council.ready`, `council.prepared_partial`, `council.hand_raise`, `council.speak`, and `council.vote` submission through plugin/protocol-client tools with command-id/idempotency coverage. `stream.follow` remains deferred/not required for PARTC-001 unless separately scoped. Runtime/live approval remains false: no production activation, no live/default Discord delivery, no real participant profile response proof, no gateway/auth/token/provider/profile mutation, and no KAB bridge readiness claim. |
| PARTC-002 | Prove selected participant response path | candidate/local bounded no-live proof | Candidate implementation evidence covers the fake/injected `atn_selected_participant_response` tool consuming caller-supplied control `MEMBR` evidence, validating `speaker_selected` selection and participant-response provenance, submitting the resulting response as plugin/protocol-client `council.speak`, and acknowledging the selected cursor only after speak submission succeeds. Runtime/live approval remains false: this proof does not invoke real participant profiles or wrappers, does not prove production activation, does not enable live/default Discord delivery, and does not mutate gateway/auth/token/provider/profile state. A future real participant-profile runtime pilot remains separate and approval-gated. |

## SURFD: Surface delivery

Epic ID: `SURFD`

Exit: the plugin-side visible-surface helper/rendering boundary can present daemon event data and record evidence pointers without becoming lifecycle state authority or enabling live/default Discord from plugin registration.

SOT: `docs/10-live-transport-sot.md`. Control companion SOT: `../../agent-turn-network-control/docs/24-live-transport-control-sot.md`.

Dependency gate: complete the control `SURFD` epic before starting plugin `SURFD`. Active task transfer between repos happens only at the epic boundary.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| SURFD-001 | Render daemon events to visible discussion surface | candidate/local implementation proof | Candidate implementation evidence covers pure/local `atn_surface_render_projection` rendering from explicit daemon/control projection event JSON into visible rows and evidence pointers. Cursor/order authority is daemon-owned, `speech` requires a prior matching `speaker_selected` floor grant, terminal delivery statuses preserve `posted`, `failed`, `pending_followup`, and `missing/unproven`, and malformed/unsupported/proofless inputs fail closed. Runtime/live approval remains false: no production activation, no live/default Discord delivery, no daemon lifecycle reads/writes, no gateway/auth/token/provider/profile mutation, and no KAB readiness claim. |

## ARGUE: Council argument graph

Epic ID: `ARGUE`

Exit: the plugin can accept, validate where deterministically possible, submit, and render relation-aware council discussion evidence without becoming lifecycle authority. ARGUE completion means participant-agent tool schemas, selected participant response handling, visible projection rendering, and packaged operator guidance preserve `claims[]`, `stance_links[]`, `contribution_type`, `new_axis_reason`, and quality diagnostics supplied by control. This exit is not production activation, live/default Discord delivery, gateway/auth/token/provider/profile mutation, KAB bridge readiness, or a live-local pilot claim.

SOT: `docs/11-council-argument-graph-sot.md`. Control companion SOT: `../../agent-turn-network-control/docs/25-council-argument-graph-sot.md`.

Dependency gate: develop ARGUE sequentially through the control/plugin DAG. Control owns protocol/event/state/validation fixtures; plugin implementation starts only after the relevant control ARGUE fixture or gate exists, unless a task explicitly records local fake-fixture scope and keeps control compatibility completion blocked.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| ARGUE-001 | Add argument graph schemas and tool contract coverage | final/pre-commit complete | Extended plugin schemas/client validation for `claims[]`, `stance_links[]`, `contribution_type`, `new_axis_reason`, `evidence[]`, and `hand_raise.target_links[]` while preserving legacy `responds_to_event_id` as a display hint only. Consumes `control/ARGUE-002` fixtures for control-owned shapes. KAS/KAH run: `run-20260615T165619Z-8acdb4b9c817`; verification/color review/Octo/post-Octo review passed. Not committed/pushed, not live/runtime activated. |
| ARGUE-002 | Add selected participant relation-aware response handling | committed local complete | Stage 1 local implementation under KAS/KAH run `run-20260616T052232Z-4c31b627128b` updates `atn_selected_participant_response` framing and fail-closed handler behavior so participant output becomes structured relation-aware `council.speak` payloads, runtime warning/noise is rejected before visible speech, caller-provided validation context can fail closed on quality-required orphan/contradictory relation input when local context is sufficient, and selected cursor ack remains after successful submit only. Verification/color review/Octo/post-Octo review and KAH final gate passed; local commit recorded. This does not claim live/control compatibility, production activation, live/default Discord delivery, gateway/auth/token/provider/profile mutation, KAB readiness, visible relation rendering, or live pilot readiness. |
| ARGUE-003 | Render visible argument graph relations | committed local complete | Stage 1 local implementation under KAS/KAH run `run-20260616T105744Z-76231087220d` updates `atn_surface_render_projection` so visible rows render human-readable relation summaries while audit output preserves machine-readable relation fields and daemon quality diagnostics without rewriting speech or inferring state from Discord order. Verification/color review/Octo/post-Octo review and KAH final gate passed; local commit recorded. This does not claim live/control compatibility, production activation, live/default Discord delivery, gateway/auth/token/provider/profile mutation, KAB readiness, packaged operator guidance, or live pilot readiness. |
| ARGUE-004 | Update packaged operator guidance and pilot harness notes | committed local complete | Historical row: docs-only packaged guidance update under KAS/KAH run `run-20260616T141006Z-e4e234eae75c` updated the then-current bundled ATN operator skill and operator guide for ARGUE relation-aware response formatting, orphan/repeated-new-axis review signals, mechanical lifecycle pass versus discussion-quality pass separation, daemon/control authority boundaries, live-local pilot approval/evidence requirements, and the KAS non-ownership/non-install boundary. Current public packaged guidance lives under ATN skill names. Verification/color review and KAH final gate passed; local commit recorded. This does not claim live/runtime readiness, live/default Discord delivery, profile/plugin activation, provider/gateway/auth/token mutation, KAB readiness, KAS ownership/install/activation of ATN artifacts, production rollout, or live pilot readiness. |


## RUNFIX: Council runner, activation, and discussion-quality remediation

Epic ID: `RUNFIX`

Exit: an approved live-local ATN discussion can be installed/activated only with explicit control dependency evidence, eligible real participant profiles, bot-to-bot-free Discord channel policy, selected-speaker runner evidence, visible-surface evidence, canonical speech linkage, fallback disclosure, and ARGUE discussion-quality diagnostics. This exit is not a production activation, arbitrary Discord deployment, KAB bridge readiness, or permission to mutate profiles/gateway/auth/token/provider state without separate approval.

SOT: `docs/10-live-transport-sot.md`. Control companion SOT: `../../agent-turn-network-control/docs/24-live-transport-control-sot.md`.

Dependency gate: RUNFIX uses one global cross-repo task sequence. `plugin/RUNFIX-002` follows `control/RUNFIX-001`; `plugin/RUNFIX-006` follows `control/RUNFIX-005`; `control/RUNFIX-009` follows `plugin/RUNFIX-008`; `plugin/RUNFIX-010` follows `control/RUNFIX-009`; `plugin/RUNFIX-012` follows `control/RUNFIX-011`; `plugin/RUNFIX-013` may proceed after the RUNFIX-013 plan records the moderation-skill evidence and control-policy references. `control/RUNFIX-014` precedes `plugin/RUNFIX-015` where reports consume selected-runner labels; `control/RUNFIX-016` provides the canonical summary helper that plugin visible runners should call or match; `plugin/RUNFIX-017` depends on control/RUNFIX-005 quality diagnostics and the post-pilot report labels; `plugin/RUNFIX-019` depends on `control/RUNFIX-018` daemon registry reconcile semantics.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| RUNFIX-002 | Plugin activation SOT and roadmap companion lock | completed | Historical row: accepted docs-only SOT lock for the plugin-side RUNFIX activation/operator contract, cross-repo DAG, control dependency, plugin install versus ATN discussion activation split, profile eligibility/bot-to-bot exclusion policy, fallback reporting boundaries, and docs-map/bundled guidance updates. Current public wording uses ATN for the discussion surface. Review evidence: Red `t_612b4d58`, Orange `t_c673aed4`, Gray `t_ce1b0c31`, focused Orange `t_131ea8c9`, focused Gray `t_7cec278f`, Blue synthesis `t_1bb67569`. This does not authorize RUNFIX-003..010 implementation or live readiness. |
| RUNFIX-006 | Discussion activation planner/doctor | local implementation proof | Historical row: added pure/local `atn_discussion_activation_plan` as the then-current approval-gated planner/doctor from explicit caller-provided evidence only. The current public tool naming is `atn_discussion_activation_plan`. It checks control/RUNFIX-005 evidence, plugin install/enabled/tool visibility, explicit daemon/config compatibility evidence, participant profile tool visibility and bot-to-bot eligibility, selected Discord parent-channel inheritance proof, planned changes, rollback, verification commands, approval gates, blockers, and separated RUNFIX evidence labels. Missing/unknown evidence fails closed as blocked/not_ready; live readiness always remains false. This does not authorize apply/live-local pilot, live Discord delivery, daemon startup, profile/gateway/provider/auth/token/model mutation, production activation, commit, push, or broad rollout. |
| RUNFIX-007 | Discord eligibility and bot-to-bot exclusion | local implementation proof | Extended the existing pure/local `atn_discussion_activation_plan` dry-run tool for effective Discord eligibility evidence while preserving legacy `tools_visible`/`bot_to_bot_enabled` compatibility. The report now exposes eligible-only `allow_list_targets`, excluded/blocked profile remediation, parent-channel inheritance proof state, and fallback audit rejection of hidden plugin-to-CLI subprocess fallback, current Hermes/Discord inference, manual profile replies as full ATN success, daemon startup/discovery, profile/gateway/provider/auth/token/model mutation, `codex exec`, generic OpenAI SDK, raw app-server transport, and KAB `native_codex`. Thread-only/current-channel/manual profile evidence is rejected as parent-channel inheritance proof unless explicit gateway proof covers parent inheritance. `live_readiness` remains false; no live Discord delivery, daemon startup/discovery, profile/gateway/provider/auth/token/model mutation, production activation, commit, push, or broad rollout is claimed. |
| RUNFIX-008 | Participant ARGUE response guidance and fallback reporting | local implementation proof | Extended the existing pure/local `atn_discussion_activation_plan` and packaged operator guidance so participant ARGUE response templates expose `speech`, `claims[]`, `stance_links[]`, `contribution_type`, `new_axis_reason`, and optional `evidence[]`; operator evidence reports expose ARGUE counts, selected-runner evidence, canonical `speaker_selected -> speech` linkage, RUNFIX labels, and diagnostic-only fallback disclosure from explicit caller-provided evidence only. Missing or ambiguous runner/ARGUE/canonical-link evidence remains `unproven`/`blocked`, `live_readiness` remains false, and no live Discord delivery, daemon startup/discovery, profile/gateway/provider/auth/token/model mutation, production activation, commit, push, or broad rollout is claimed. |
| RUNFIX-010 | Live-local activation pilot and final operator package | completed/PASS_WITH_RISK | With explicit approval, ran a bounded visible-local pilot using eligible available profiles and published the final operator package. Preferred visible surface is a dedicated thread under the approved parent channel; if thread creation/posting is unsupported, direct parent-channel use is allowed only as an explicit fallback with `fallback_reason`. The planner/operator guidance now defaults Discord-origin council requests to `live_visible_thread`, blocks silent artifact-only or daemon CLI actor speech downgrades without explicit confirmation, and requires final reports to separate lifecycle finalized, visible turns posted, real profile/gateway replies, and CLI actor speech only. Current bounded pilot evidence is PASS_WITH_RISK: parent-channel visible messages were verified and canonical daemon events finalized, but real selected-speaker runner invocation, always-on participant runtime readiness, and full ATN roster coverage remain unproven. KAH run `run-20260618T112843Z-40b023a5d9c8` final gate passed; this is not production/live readiness. |
| RUNFIX-012 | Activation planner consumes participant runtime readiness | local implementation proof | Extended the pure/local activation planner, schema, operator guide, bundled skill, and RUNFIX SOT wording so `plugin/RUNFIX-012` consumes explicit `control/RUNFIX-011` participant-runtime readiness evidence from caller input only. The report exposes control task/status/evidence ref, subscriber presence, cursor ack freshness, heartbeat freshness, attendance/preparation terminal evidence, selected-runner readiness/prerequisites, and visible-surface proof as separate evidence classes. Missing, stale, ambiguous, gateway-only, transcript/export-only, parent-channel-fallback-only, or manual/fallback-profile-only evidence blocks or diagnoses readiness and keeps `live_readiness=false`; `ready_for_approval` remains only a bounded planner/operator status. This is local plugin proof only and does not mutate live profiles, providers, gateways, auth, tokens, Discord state, or production daemons, and does not claim live/production readiness, commit, push, or broad rollout. |
| RUNFIX-013 | ATN council moderation skill hard rules | local implementation proof | Historical row: added packaged moderation hard rules to the bundled skill and operator guide from 주유's 2026-06-19 moderation-skill-gap report: no predeclared complete live speaker order; complete `council.new` -> `request_attendance` -> terminal attendance -> `lock_agenda` -> `prepare` -> `ready`/`prepared_partial` before turn discussion; each turn uses poll/hand-raise evaluation and a justified daemon `speaker_selected`; `relevance` is the default mode while `targeted`, `random`, `moderator_direct`, and `role_order` remain per-turn justified options; Discord/Hermes replies are not state without daemon `speech`; moderator substantive opinions use participant-style turns; mistaken fixed-order flows cancel/restart before speech or repair-forward after speech. This is docs/bundled-skill/package proof only and does not claim live daemon/runtime activation, Discord delivery, production/live readiness, profile/provider/gateway/auth/token/model mutation, commit, push, or broad rollout. |
| RUNFIX-015 | Visible author guard | local implementation proof | Plugin KAH run `run-20260619T071526Z-7d2ba33b07d5` implements local pre-`council.new` visible author guard proof in `atn_discussion_activation_plan`: explicit caller-provided same-path probes record `profile`, expected author source (`registry_snapshot` or approved profile-author map), observed bot/user, `source_env`, `posting_path`, shared/default negative proof, shared-default-then-profile-local env precedence, per-turn Discord message id/member/profile-author/speech linkage, and separated final result fields. Missing/shared-default/unexpected author evidence fails closed without live Discord delivery or runtime/profile/provider/gateway/auth/token/model mutation. |
| RUNFIX-017 | ARGUE quality-required prompt contract | local implementation proof | Local implementation under KAH run `run-20260619T101255Z-189d01ba8b8f` passed official color review, Blue synthesis, and final KAH gate; strengthens participant prompts and selected-response guidance for quality-required councils: compact prior claim graph targets distinguish validation-authority `event_id`/`claim_id` from guidance-only `speaker`/`summary`/`available_stances`, non-opening turns with sufficient local context must carry caller-target-valid `stance_links[]` or justified `new_axis`, ARGUE fields are preserved through `atn_selected_participant_response`, explicit `discussion_quality` evidence is required for the quality gate, `discussion_quality_pass` fails on the first orphan non-opening speech in `quality_required`, and lifecycle-vs-quality counts remain separate without synthetic relation inference. |
| RUNFIX-019 | Activation planner consumes daemon registry reconcile evidence | local implementation proof | Historical row: plugin KAH run `run-20260619T214004Z-4d1e54b7304a` extended the then-current `atn_discussion_activation_plan`, schema, operator guide, and bundled `atn-plugin`/`atn-moderator` skills so live-visible plans must provide explicit loaded daemon registry membership evidence for every selected moderator/participant principal. Current public surfaces use `atn_discussion_activation_plan`, `atn-plugin`, and `atn-moderator`; the old names remain provenance for this completed row. A principal is acceptable only when present/enabled in the loaded registry or when an unambiguous planned control-owned reconcile proves valid mapping and wrapper resolution. Ambiguous principal/profile mapping, disabled loaded principals, invalid/reserved ids, unresolved wrappers, or missing registry evidence block before `council.new`; no artifact-only or daemon CLI actor speech downgrade is implied. |


## RUNFIX2: Discussion runtime usability hardening

Epic ID: `RUNFIX2`

Exit: an approved live-local ATN discussion can run with production-friendly defaults and clean visible UX only when the daemon-selected runner path succeeds, participant runtime readiness is proven at grant/turn time, visible turns match the lifecycle formula, Discord messages hide audit identifiers, and final labels remain evidence-derived. RUNFIX2 does not authorize production activation, live/default Discord outside an approved pilot, gateway/auth/token/provider/profile mutation, KAB readiness, push, or broad rollout.

SOT: `docs/10-live-transport-sot.md`. Control companion SOT: `../../agent-turn-network-control/docs/24-live-transport-control-sot.md`.

Dependency gate: `control/RUNFIX2-001` locks evidence/config semantics before implementation claims. `control/RUNFIX2-002` is completed/control-local for selected-runner response generation, runner-success accounting, compact JSONL stdout framing, and pretty/multiline JSON compatibility before `plugin/RUNFIX2-005` can claim `selected_runner_pass`. `control/RUNFIX2-003` is completed/control-local for the lifecycle turn formula before `plugin/RUNFIX2-004` and `plugin/RUNFIX2-005` claim expected visible turn counts.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| RUNFIX2-004 | Clean visible Discord transcript UX | local implementation proof | Pure/local renderer cleanup is implemented with focused unit proof: visible transcript rows render concise ATN labels such as `[ATN | T15/15]`, omit session id, role/color labels, `speaker_selected_event_id`, `speech_event_id`, runner ids, raw cursors, raw delivery ids, and evidence machine identifiers from human-visible text/body, and keep those identifiers in audit/export/status rows. This is not live Discord delivery or RUNFIX2-005 pilot proof. |
| RUNFIX2-005 | Integrated live-local discussion proof | local implementation proof | Local plugin implementation now supports explicit-only `integrated_discussion_proof` for RUNFIX2-005, with separated lifecycle, selected-runner, runtime-at-turns, visible-surface, clean-transcript, visible-closeout, fallback, discussion-quality, and final-label axes. Selected-runner proof requires runner success plus canonical linked speech for the selected member; per-turn runtime readiness must be grant/turn-time evidence; visible count validates the RUNFIX2 formula. Manual/profile fallback remains diagnostic-only and cannot repair selected-runner failure. `live_readiness` remains false; actual live pilot, Discord/daemon/profile/provider/gateway/auth/token mutation, production readiness, push, and broad rollout remain separately approval-bound. |

Control-owned RUNFIX2 tasks are listed in the control roadmap: `control/RUNFIX2-001`, `control/RUNFIX2-002`, and `control/RUNFIX2-003`. Plugin rows here record only plugin-owned implementation/proof work and cross-repo dependency boundaries.


## RUNFIX3: Live-visible council contract hardening

Epic ID: `RUNFIX3`

RUNFIX3 is the 2026-06-25 follow-up from 주유's KLM live Discord thread postmortem and 마초 Blue triage. It preserves the RUNFIX lineage as an explicit epic-id exception like RUNFIX2 because the work directly hardens the same live-council readiness lane. The SOT is `17thHermes:40_outputs/team/macho/atn/2026-06-25-atn-live-visible-council-contract-hardening-sot.md`.

Exit: an approved live-visible ATN discussion can enforce exact origin Discord thread binding, the `max_discussion_turns + participant_count + 2` visible-turn formula, selected-runner proof versus manual/profile fallback, content/audit prompt separation, participant-to-participant dialogue mode, and drift repair or unresolved closeout while keeping all pass labels evidence-derived. RUNFIX3 does not authorize production activation, live/default Discord outside an approved pilot, gateway/auth/token/provider/profile mutation, KAB readiness, push, or broad rollout.

Post-feedback plan amendment: RUNFIX3 now freezes `selected_runner_pass` as an evidence-derived label, not a daemon `selection_mode`, selection policy, or feature toggle. Plugin guidance/schema tasks consume the frozen control evidence contract and must not invent control semantics. RUNFIX3-wide completion requires the final cross-repo closeout artifact `40_outputs/team/macho/atn/<date>-runfix3-final-live-visible-council-closeout.md` with exact scenario, bound-thread evidence, per-turn daemon/runner/speech/delivery linkage, negative fail-closed matrix results, Red/Orange/Gray review, 마초 Blue synthesis, and 주군 approval.

Dependency gate: `RUNFIX3-001` locks the cross-repo SOT and roadmaps before implementation and now includes the post-feedback execution-plan amendment. `plugin/RUNFIX3-002` hardens moderator/operator guidance against the frozen contract. `plugin/RUNFIX3-003` adds planner/schema/operator-evidence support against the same frozen contract. `control/RUNFIX3-004` then implements diagnostics/enforcement for control lifecycle/selected-runner/delivery evidence and finalization behavior.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| RUNFIX3-001 | Live-visible council contract SOT and roadmap lock | completed | Docs-only cross-repo SOT lock in `17thHermes:40_outputs` records `sess_klm_selected_runner_20260625T085557Z` as failed live-visible council contract evidence, fixes the expected T0/T1..TN/TN+1..TN+P/TN+P+1 lifecycle, and defines the four-PR sequence. Review evidence is recorded in the SOT color review log. |
| RUNFIX3-002 | Moderator/operator live-thread contract hardening | implementation_complete/review_pending | Mirror-only status row for the current RUNFIX3-002 implementation: normative live-thread procedure ownership stays in `src/atn_plugin/bundled_skills/atn-moderator/SKILL.md` and `docs/09-skill-and-operator-guide.md`, while `atn-plugin` stays boundary/cross-link only and this roadmap row stays traceability-only. Verification, tests/guardrails, and evidence remain bounded to plugin-owned guidance work; planner/schema/runtime fields stay deferred to `plugin/RUNFIX3-003` and control diagnostics/enforcement stay deferred to `control/RUNFIX3-004`. Fixed minimum plugin gates have passed, and cross-repo status mirrors now align on implementation-complete / re-review-pending state pending focused reviewer acceptance. |
| RUNFIX3-003 | Planner and evidence schema for live-thread proof axes | implementation_complete/review_pending | Plugin-owned planner/schema/operator-evidence support against the frozen control evidence contract is implemented and awaiting focused reviewer acceptance. The planner/report surface now adds `plugin/RUNFIX3-003` task support, exact-origin fail-closed proof, formula-grounded visible-turn accounting, separate `start_status` versus overall `status`, explicit `runfix3_acceptance_status`, a dedicated selected-runner proof-chain acceptance axis, start-gated daemon registry membership, and RUNFIX3-specific closeout/synthesis/delivery-target/prompt-envelope/dialogue/drift/fail-closed reports without promoting live readiness. Fixed minimum gates have passed, with `make test-unit` run as a deliberate tightening over the older waiver wording. Durable verification evidence: `docs/evidence/2026-06-26-runfix3-003-planner-proof-evidence.md`. |

Control-owned RUNFIX3 follow-up `control/RUNFIX3-004` is now implementation_complete/review_pending in the control roadmap; plugin mirrors it as a dependency/status trace only.


## NEXFIX: Selected-runner prompt envelope remediation

Epic ID: `NEXFIX`

NEXFIX is the 2026-06-26 follow-up from 주유's selected-runner prompt envelope defect report. The SOT lock is `17thHermes:40_outputs/team/macho/atn/2026-06-26-atn-selected-runner-prompt-envelope-nexfix-sot.md`. This is an explicit naming exception: the epic label is `NEXFIX`, while 주군 requested task ids `NEWFIX-001` and `NEWFIX-002`.

Exit: long or live-visible selected-runner councils have both runtime readiness and content-plane readiness gates. Control owns the projection-backed prompt envelope in `control/NEWFIX-001`; plugin owns packaged moderator/participant guidance in `plugin/NEWFIX-002`. NEXFIX does not authorize production activation, live Discord rollout, default Discord activation, gateway/auth/token/provider/profile/model mutation, KAB readiness, push, package publication, or broad rollout; any live pilot remains separately approved and outside this docs-only task.

Dependency gate: `plugin/NEWFIX-002` should consume the `control/NEWFIX-001` contract once accepted, or phrase guidance against the planned control contract without inventing daemon authority. The named handoff target is `selected_runner_prompt_evidence`: a control status/export field, deterministic fixture artifact, or equivalent non-secret prompt-capture proof that records selected member, turn, causation, agenda/prior-context source refs, included/missing context keys, prompt hash or redacted excerpt, and `result`. The plugin must not treat `council.grant` hints, visible messages, or operator prose as authoritative replacement for daemon projection.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| NEWFIX-002 | Moderator and participant content-plane readiness guidance | planned | Plugin-owned guidance hardening: `atn-moderator` separates runtime readiness from content-plane readiness, classifies missing/blocked `selected_runner_prompt_evidence` as a `start_blocker` for long or live-visible councils, and intervenes/cancels if a first speech reports missing agenda/prior context. `atn-participant` guidance must fail closed or return a current-control `speech`-contract-compatible diagnostic payload when agenda context is missing rather than producing generic speech; until a richer diagnostic event type is approved, the producer stdout remains `type: "speech"` with `payload.speech`, optional diagnostic `claims[]`, empty or valid `stance_links[]`, `contribution_type`, `new_axis_reason`, and optional `evidence[]`. |

Control-owned `control/NEWFIX-001` is listed in the control roadmap. Plugin mirrors it as the blocking content-plane prompt contract dependency and does not claim control implementation authority.


## ATN: Agent Turn Network public rename

Epic ID: `ATN`

Exit: both repositories converge to Agent Turn Network public naming with `atn-control`, `atn-plugin`, `atn_` tools, ATN bundled skills, no public legacy aliases, and final cross-repo guardrail proof. Live readiness, production activation, Discord delivery, package publication, hosted repository rename, push, and profile/provider/gateway/auth/token mutation remain separately approved scopes.

| Task ID | Task Title | Task Status | Task Description |
|---|---|---|---|
| ATN-001 | ATN naming SOT and roadmap lock | completed/docs-only | Added control and plugin ATN naming SOT documents, recorded ATN-001 through ATN-005 in the roadmaps/docs maps, and locked the no-alias policy. Review consensus: Red `t_d43402f0`, Orange `t_6d6bb8e8`, Gray `t_7ebc9e1e`, Blue synthesis `t_8e348f72`. This does not rename code, binaries, packages, tools, live profiles, hosted repositories, or public release artifacts. |
| ATN-002 | Control public docs rename | completed/local-docs-proof | Control-owned task rewrote control public docs, docs index/map surfaces, protocol wording, examples, operator-facing text, and roadmap status wording to ATN-only naming without changing binaries or code behavior. |
| ATN-003 | Plugin public docs rename | completed/local-docs-proof | Rewrote plugin public docs, package/docs metadata, operator guide, and bundled skill documentation to ATN-only naming ahead of ATN-005, updated sibling workspace path references to the current `agent-turn-network-control` checkout, and removed superseded prior-rename references from the checked-in docs set. |
| ATN-004 | Control code and binary rename | completed/local-proof | Control-owned task renamed the control Go module, CLI binary, daemon binary, data-home/env/socket/protocol markers, fixtures, tests, Makefile surfaces, and command examples to ATN names with no aliases. |
| ATN-005 | Plugin package, tools, skills, and final guardrails | completed/local-proof | Renamed the plugin distribution/import package, manifest, Hermes tools, bundled skills, schemas/handlers/tests/scripts, docs examples, and no-alias guardrails to ATN names; completed the final local ATN control/plugin compatibility proof with no aliases. |

Control-owned ATN rows are also listed in the control roadmap. Use repo-qualified task names when needed, for example `control/ATN-002` or `plugin/ATN-005`.
