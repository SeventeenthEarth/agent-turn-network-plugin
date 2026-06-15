# kkachi-agent-network-plugin

`kkachi-agent-network-plugin` is the Python Hermes plugin adapter for KAN. In the current local stage it exposes fake/injected Hermes plugin tools only: read-only `kan_daemon_status`, `kan_compatibility_diagnostics`, `kan_stream_tail`, `kan_stream_ack`, command-envelope `kan_delegate_new` and `kan_delegate_action`, `kan_council_command`, `kan_selected_participant_response`, `kan_delivery_evidence`, pure local `kan_surface_render_projection`, plus the injected-only `kan_discord_send_message` helper. It also packages a `kan-plugin` operator skill and has a local isolated plugin-load smoke gate for the repository entrypoint. Hermes has a plugin slash-command host API, but this plugin still has no KAN slash-command bindings, live daemon discovery, live/default Discord gateway wiring, session-status tool, production activation claim, KAB bridge claim, or live plugin readiness claim.

The plugin is not the source of truth. `kkachi-agent-networkd` owns `channel.jsonl`, SQLite projections, locks, replay, cursors, and state transitions.

## Repository boundary

- This repo: Python plugin code, fake/injected-transport daemon client foundation, Hermes tool schemas/handlers, future KAN-facing surfaces as separate tasks land, fake-daemon integration tests, isolated plugin E2E tests.
- Control repo: `../kkachi-agent-network-control`, Go daemon/CLI, protocol SOT, event/state/storage/security/recovery docs.
- Discord helper behavior is injected-only by default. If delivery evidence is needed, it
  must be recorded separately through typed daemon commands, and raw Discord tokens must
  not move into the daemon.

## Python runtime compatibility

This plugin must remain compatible with the Python version used by the target
Hermes runtime. Current Hermes runtime compatibility is Python 3.11.

The repository declares `requires-python = ">=3.11"` in `pyproject.toml`, targets
`py311` for Ruff, type-checks as Python 3.11 with mypy, and includes a Python
3.11 syntax guard so Python 3.12-only syntax does not re-enter the runtime
package.

Use `uv`, `pyproject.toml`, and `uv.lock` as the dependency source of truth. A
separate `requirements.txt` is intentionally not maintained while runtime
dependencies are empty; add one only if a pip-only install path becomes an
approved operator surface.

## Documentation

Start at [`docs/README.md`](docs/README.md).

Key docs:

- [`docs/00-overview.md`](docs/00-overview.md) — plugin purpose and non-goals
- [`docs/01-architecture.md`](docs/01-architecture.md) — plugin architecture
- [`docs/02-plugin-contract.md`](docs/02-plugin-contract.md) — compatibility and fail closed behavior
- [`docs/03-testing-strategy.md`](docs/03-testing-strategy.md) — fake-only integration and isolated E2E policy
- [`docs/04-tooling.md`](docs/04-tooling.md) — Python tooling and Makefile contract
- [`docs/09-skill-and-operator-guide.md`](docs/09-skill-and-operator-guide.md) — bundled skill install, enable, rollback, troubleshooting, and local isolated plugin-load smoke boundary
- [`docs/08-unsupported-surfaces.md`](docs/08-unsupported-surfaces.md) — unsupported surfaces and future binding requirements
- [`docs/11-council-argument-graph-sot.md`](docs/11-council-argument-graph-sot.md) — plugin-side ARGUE council argument graph SOT and implementation DAG

## Current state

Local fake/injected plugin stage. The package layout, plugin manifest, root Hermes directory entrypoint, status/diagnostics/stream-tail tools, delegation/review command-envelope tools, council/delivery-evidence command tools, pure visible-surface projection renderer, injected-only Discord helper, bundled `kan-plugin` operator skill, compatibility matrix, and local isolated plugin-load smoke gate are in place. Handlers return JSON strings, preserve fail-closed error categories, redact sensitive diagnostics/stream payloads, and require explicit fake/injected `DaemonClient` factories or explicit injected Discord senders for daemon/Discord surfaces.

`kan_stream_tail` probes `version.read` for `stream_frame` compatibility before `stream.tail`. `kan_delegate_new` submits `delegate.new`; `kan_delegate_action` accepts only the exact implemented `delegate.*` action/review/delivery enum, rejects `delegate.request` and top-level `review`, requires caller-supplied `request_id`/`idempotency_key`, and owns no lifecycle/idempotency state.

`kan_council_command` accepts only the exact implemented `council.*` lifecycle enum and probes `version.read` for `council.lifecycle` before `command.submit`. `kan_selected_participant_response` submits a wrapper-proven `council.speak` payload for the selected member, then acks the selected cursor only after submit succeeds. `kan_delivery_evidence` accepts only `delegate.escalation_delivered` and `delegate.escalation_delivery_failed` and probes for `delivery_evidence` first. These tools preserve caller-supplied IDs and own no logs, locks, cursors, consensus/lifecycle state, idempotency/dedupe, or delivery evidence transitions.

`kan_surface_render_projection` is pure/local: it accepts explicit daemon/control
projection JSON, sorts by daemon cursor/order authority, renders a clean
`visible_transcript` for operator-facing discussion text, keeps raw cursors/event
ids in `audit_log`/`rows`, and returns `live_readiness: false`. In closeout mode
(`require_terminal_closeout: true`) it fails closed unless a terminal outcome has
posted visible evidence with an explicit reference back to that terminal event.
Missing or mismatched terminal-event references are not accepted as visible
closeout proof. It performs no daemon
reads, Discord reads or sends, environment reads, lifecycle transitions, or CLI
fallback.

`kan_discord_send_message` validates an explicit dedicated Discord test target with a
visible label and cleanup hint, then calls only an injected `send_message` callable. It
fails closed without sender injection, does not read environment variables or current
Hermes/Discord state, and treats Discord IDs only as evidence pointers.

`kan_session_status` remains deferred until the control repo provides fixture/protocol authority for `session.status.read`. KAN slash commands remain unsupported and `provides_commands: []` remains unchanged. SKILL-2 does not install into the user's Hermes profile and does not prove live daemon support, live Discord sending, production activation, KAB bridge behavior, or live Hermes integration.

## Test targets

```bash
make test-prepare  # ruff/mypy/docs guardrails; no live external resources
make check-plugin-load-smoke  # local isolated plugin-load smoke; no live resources
make test-unit     # unit tests for Python package scaffold and later plugin code
make test-int      # fake daemon/Hermes/Discord integration; no external resources
make test-e2e      # isolated Hermes/Discord test environment only
make test          # sequential all targets
make check-core-contract  # verify companion control milestone/contract readiness
```

`make test-e2e` must never target the currently running Hermes or active Discord thread by default.
