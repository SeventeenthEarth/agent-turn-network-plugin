# Agent Turn Network Plugin Naming SOT

## Status

Task: `cross-repo/ATN-001`  
Status: completed/docs-only SOT lock after Red/Orange/Gray review and Blue synthesis consensus.  
Scope: plugin repository naming, public package/tool/skill naming, cross-repo task sequencing, and clean no-alias policy only.

This document is the plugin-side Source of Truth for the **Agent Turn Network** public rename. It locks the public plugin naming contract before Python package, Hermes tool, bundled skill, manifest, docs, and smoke-test rename tasks start.

This SOT does not rename source directories, publish a package, mutate live Hermes profiles, alter gateway/provider/auth/token state, contact Discord, start a daemon, push commits, or claim production readiness.

## Canonical public names

| Surface | Canonical name |
| --- | --- |
| Product | Agent Turn Network |
| Short product label | ATN |
| Plugin repository | `atn-plugin` |
| Python distribution package | `atn-plugin` |
| Python import package | `atn_plugin` |
| Hermes plugin manifest id | `atn-plugin` |
| Hermes plugin display name | Agent Turn Network Plugin |
| Hermes tool prefix | `atn_` |
| Main bundled operator skill | `atn-plugin` |
| Moderator/operator bundled skill | `atn-moderator` |
| Participant bundled skill | `atn-participant` |
| Companion control repository | `atn-control` |
| Companion CLI binary | `atn-control` |
| Companion daemon binary | `atn-controld` |

The plugin package uses the short `atn_plugin` import path and `atn-plugin` distribution/manifest identity because 주군 chose ATN as the fixed product label and requested `atn-plugin` / `atn-control` as the public repo names.

The moderation hard-rules guidance remains part of the moderator/operator bundled guidance surface. ATN-005 must fold that guidance into `atn-moderator` unless a later explicitly approved task creates a separate fourth bundled skill. It must not silently introduce both `atn-moderator` and a duplicate moderation skill surface.

## Tool rename map

| Current tool surface class | ATN tool name |
| --- | --- |
| daemon status read | `atn_daemon_status` |
| compatibility diagnostics | `atn_compatibility_diagnostics` |
| stream tail/read | `atn_stream_tail` |
| stream cursor acknowledgement | `atn_stream_ack` |
| delegation creation | `atn_delegate_new` |
| delegation action/review/delivery commands | `atn_delegate_action` |
| council command submission | `atn_council_command` |
| selected participant response | `atn_selected_participant_response` |
| delivery evidence command | `atn_delivery_evidence` |
| visible/audit projection rendering | `atn_surface_render_projection` |
| discussion activation plan/doctor | `atn_discussion_activation_plan` |
| injected Discord send helper | `atn_discord_send_message` |

No old tool aliases are allowed in the public plugin repository. Tests and examples must use the ATN names only after the tool rename task lands.

## Compatibility and alias policy

The public plugin repository must not retain prior product, project, tool, package, skill, path, manifest, config, or docs aliases. The rename is a clean public rename, not a transitional compatibility layer.

Required consequences:

- no prior Python import package kept as a wrapper module;
- no prior distribution package alias;
- no prior Hermes tool aliases;
- no prior bundled skill aliases;
- no prior manifest id or display-name alias;
- no prior config environment-variable alias;
- no examples, tests, or docs that preserve earlier public labels for compatibility.

Private migration notes may live outside the repository if needed. Public repository content must converge to ATN-only wording by the final guardrail task.

## Plugin-owned rename boundaries

The plugin repository owns these rename surfaces:

| Surface | Plugin target |
| --- | --- |
| Python source package | `src/atn_plugin/` |
| Root import bridge | public import path only, no legacy import bridge |
| `pyproject.toml` distribution metadata | `atn-plugin` |
| `plugin.yaml` id/display metadata | Agent Turn Network Plugin |
| Hermes tool schemas and handlers | `atn_*` names only |
| Fake/injected daemon client tests | ATN labels and ATN tool names |
| Live Unix socket configuration docs | companion `atn-controld` socket naming |
| Bundled operator guidance | `atn-plugin`, `atn-moderator`, `atn-participant` |
| Plugin load smoke | ATN manifest, ATN package, ATN tools, ATN skills |
| Core compatibility checker | `atn-control` companion expectations |

The plugin repository does not own daemon lifecycle, event/state authority, protocol schema authority, registry reconciliation, storage, transcript/export authority, or CLI implementation. Those remain control repository responsibilities.

## Runtime authority model retained by the rename

The rename must not change runtime authority:

1. The plugin is the participant-agent Hermes tool surface.
2. The control CLI remains the main-agent/operator control plane.
3. The daemon remains the only event/state authority.
4. Plugin tools submit typed protocol commands or render explicit caller-provided projection evidence; they do not own lifecycle state.
5. The plugin must not discover live daemons, start daemons, infer current Hermes/Discord state, or shell out to the CLI as hidden fallback.
6. Visible helper delivery remains injected/explicit only and never defaults to current Discord or the current Hermes session.
7. Live readiness, production activation, Discord delivery, profile/provider/gateway/auth/token mutation, package publication, and hosted repository rename remain separately approved scopes.

## ATN task sequence

ATN uses one five-task cross-repo sequence. The owning repository is part of the task citation when the task is executed.

| Task | Repo | Initial status | Purpose |
| --- | --- | --- | --- |
| ATN-001 | cross-repo | completed/docs-only | Lock control and plugin ATN naming SOT documents, roadmap entries, and clean no-alias policy. Review consensus: Red `t_d43402f0`, Orange `t_6d6bb8e8`, Gray `t_7ebc9e1e`, Blue synthesis `t_8e348f72`. |
| ATN-002 | control | planned | Rewrite control public docs, roadmap/index/map surfaces, protocol wording, examples, and operator-facing text to ATN-only wording without binary/code rename. |
| ATN-003 | plugin | planned | Rewrite plugin public docs, package/docs metadata, operator guide, and bundled skill documentation to ATN-only wording without tool/package code rename. |
| ATN-004 | control | planned | Rename control code, Go module, CLI binary, daemon binary, data-home/env/socket/protocol markers, fixtures, tests, and Makefile surfaces to ATN names with no aliases. |
| ATN-005 | plugin | planned | Rename plugin package/import/manifest/tools/bundled skills to ATN names, add/update final no-alias guardrails, and close cross-repo compatibility proof. |

## Acceptance criteria for ATN-001

ATN-001 is accepted when:

- control and plugin SOT documents define canonical ATN names;
- control and plugin roadmaps record ATN-001 through ATN-005;
- docs index and docs map surfaces point to the ATN SOTs;
- the policy forbids in-repository legacy aliases;
- plugin/control authority boundaries remain unchanged;
- Red, Orange, Gray, and Blue review agree that later rename implementation tasks have a clear, testable contract.

## Non-scope

ATN-001 does not perform implementation rename work. It does not update every existing stale reference in either repository, because later ATN implementation and guardrail tasks own that full sweep. It also does not claim public release readiness, live plugin readiness, package publication, hosted repository rename, push, or production rollout.
