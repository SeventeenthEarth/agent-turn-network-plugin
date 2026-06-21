# Hermes Unified Network Plugin Naming SOT

## Status

Task: `plugin/HUN-002`  
Status: completed/docs-only SOT lock after local Blue implementation and color-review synthesis.  
Scope: plugin repository naming, roadmap sequencing, public package/tool/skill naming, and clean-rename policy only.

This document is the plugin-side Source of Truth for the Hermes Unified Network rename. It locks the public plugin naming contract before Python package, Hermes tool, bundled skill, manifest, docs, and smoke-test rename tasks start.

This SOT does not rename source directories, publish a package, mutate live Hermes profiles, alter gateway/provider/auth/token state, contact Discord, start a daemon, or claim production readiness.

## Canonical public names

| Surface | Canonical name |
| --- | --- |
| Product | Hermes Unified Network |
| Short product label | HUN |
| Plugin repository | `hun-plugin` |
| Python distribution package | `hermes-unified-network-plugin` |
| Python import package | `hermes_unified_network_plugin` |
| Hermes plugin manifest id | `hermes-unified-network-plugin` |
| Hermes plugin display name | Hermes Unified Network Plugin |
| Hermes tool prefix | `hun_` |
| Main bundled operator skill | `hun-plugin` |
| Moderator/operator bundled skill | `hun-moderator` |
| Participant bundled skill | `hun-participant` |
| Companion control repository | `hun-control` |
| Companion CLI binary | `hun` |
| Companion daemon binary | `hund` |

The plugin package uses the longer `hermes_unified_network_plugin` import path for public discoverability. Short labels remain available in tool names and skill names through the `hun_` prefix and `hun-*` skill names.

The moderation hard-rules guidance currently remains part of the moderator/operator bundled guidance surface. HUN-009 must fold that guidance into `hun-moderator` unless a later explicitly approved task creates a separate fourth bundled skill. It must not silently introduce both `hun-moderator` and a duplicate moderation skill surface.

## Tool rename map

| Current tool surface class | HUN tool name |
| --- | --- |
| daemon status read | `hun_daemon_status` |
| compatibility diagnostics | `hun_compatibility_diagnostics` |
| stream tail/read | `hun_stream_tail` |
| stream cursor acknowledgement | `hun_stream_ack` |
| delegation creation | `hun_delegate_new` |
| delegation action/review/delivery commands | `hun_delegate_action` |
| council command submission | `hun_council_command` |
| selected participant response | `hun_selected_participant_response` |
| delivery evidence command | `hun_delivery_evidence` |
| visible/audit projection rendering | `hun_surface_render_projection` |
| discussion activation plan/doctor | `hun_discussion_activation_plan` |
| injected Discord send helper | `hun_discord_send_message` |

No old tool aliases are allowed in the public plugin repository. Tests and examples must use the HUN names only after the tool rename task lands.

## Compatibility and alias policy

The public plugin repository must not retain legacy product, project, tool, package, skill, path, manifest, or docs aliases. The rename is a clean public rename, not a transitional compatibility layer.

Required consequences:

- no old Python import package kept as a wrapper module;
- no old distribution package alias;
- no old Hermes tool aliases;
- no old bundled skill aliases;
- no old manifest id or display-name alias;
- no old config environment-variable alias;
- no examples, tests, or docs that preserve old public labels for compatibility.

Private migration notes may live outside the repository if needed. Public repository content must converge to HUN-only wording by the final guardrail tasks.

## Plugin-owned rename boundaries

The plugin repository owns these rename surfaces:

| Surface | Plugin target |
| --- | --- |
| Python source package | `src/hermes_unified_network_plugin/` |
| Root import bridge | public import path only, no legacy import bridge |
| `pyproject.toml` distribution metadata | `hermes-unified-network-plugin` |
| `plugin.yaml` id/display metadata | Hermes Unified Network Plugin |
| Hermes tool schemas and handlers | `hun_*` names only |
| Fake/injected daemon client tests | HUN labels and HUN tool names |
| Live Unix socket configuration docs | companion `hund` socket naming |
| Bundled operator guidance | `hun-plugin`, `hun-moderator`, `hun-participant` |
| Plugin load smoke | HUN manifest, HUN package, HUN tools, HUN skills |
| Core compatibility checker | `hun-control` companion expectations |

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

## Plugin task sequence

| Task | Repo | Status | Purpose |
| --- | --- | --- | --- |
| HUN-002 | plugin | completed/docs-only | Lock this plugin naming SOT and plugin roadmap entries. |
| HUN-004 | plugin | local implementation proof | Renamed Python distribution/import package, plugin manifest, entrypoint imports, package metadata/build/version/mypy paths, and package-load smoke under bounded local proof; HUN-006/HUN-009/HUN-010/HUN-013 remain deferred. |
| HUN-006 | plugin | planned | Rename Hermes tool schemas, handlers, tests, and contract docs to `hun_*`. |
| HUN-008 | plugin | planned | Reconfirm activation planner evidence fields under HUN names and vanilla Hermes profile/plugin visibility requirements. |
| HUN-009 | plugin | planned | Rename bundled skills to `hun-plugin`, `hun-moderator`, and `hun-participant`, fold moderation hard rules into `hun-moderator` unless separately approved, and rewrite packaged guidance as public-safe operator guidance. |
| HUN-010 | plugin | planned | Scrub plugin public docs, package metadata, examples, and operator docs for HUN-only wording and public release suitability. |
| HUN-013 | plugin | planned | Add plugin forbidden-term guardrails and HUN-only plugin-load smoke checks. |
| HUN-014 | cross-repo | planned | Final cross-repo HUN compatibility, stale-reference scan, and release-readiness sync. |

Control-owned tasks are recorded in the control roadmap. Cross-repo references must use repo-qualified task names when needed, for example `control/HUN-001` and `plugin/HUN-002`.

## Acceptance criteria for HUN-002

HUN-002 is accepted when:

- this SOT exists and defines canonical plugin/package/tool/skill names;
- the plugin roadmap records the HUN sequence;
- docs index and docs map point to this SOT;
- the policy forbids in-repo legacy aliases;
- plugin/control authority boundaries remain unchanged;
- Red, Orange, Gray, and Blue review agree that later rename implementation tasks have a clear, testable contract.

## Non-scope

HUN-002 does not perform implementation rename work. It does not update every existing old reference in the repository, because later HUN implementation and guardrail tasks own that full sweep. It also does not claim public release readiness or live plugin readiness.
