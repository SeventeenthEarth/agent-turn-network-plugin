# atn-plugin

`atn-plugin` is the Python Hermes plugin adapter for Agent Turn Network (ATN).
It exposes Hermes-facing ATN tools and bundled operator skills that talk to the
`atn-control` daemon protocol. It does **not** own ATN lifecycle or state.

Current public names:

- Product/network: **Agent Turn Network (ATN)**
- Plugin repo: `agent-turn-network-plugin`
- Plugin package/import: `atn_plugin`
- Plugin manifest name: `atn-plugin`
- Hermes tool labels: `atn_*`
- Bundled skills: `atn-plugin`, `atn-moderator`, `atn-participant`
- Current plugin version: `0.1.0`
- Required companion control module: `github.com/SeventeenthEarth/agent-turn-network-control`, public name `atn-control`

## What this repository does

`atn-plugin` provides the Hermes-side tool surface for ATN participants,
moderators, and local operators. The checked-in plugin includes:

- plugin manifest and root Hermes entrypoint;
- Python package metadata and protocol/client types;
- fake/injected and explicit live daemon client transport boundaries;
- read-only daemon status, compatibility diagnostics, and stream-tail tools;
- stream ack, delegation, council, selected-participant response, and delivery
  evidence command-envelope tools;
- pure/local visible-surface transcript rendering from explicit projections;
- pure/local discussion activation planner/doctor from explicit evidence;
- injected-only Discord test-message helper;
- bundled ATN operator skills for plugin, moderator, and participant roles;
- local tests and compatibility gates against the control repo.

The plugin is not the source of truth. It preserves caller-supplied IDs,
validates tool payloads, probes daemon compatibility when required, and submits
structured daemon requests. It owns no daemon lifecycle, event log, cursor,
consensus, lock, idempotency, dedupe, or delivery-evidence state.

## Required companion binaries: atn-control

Install and verify the released `atn-control` / `atn-controld` binaries before
treating plugin tools as usable for real ATN workflows. Ordinary plugin/profile
installation does not require cloning or reading the control repository; use Go's
remote module install path. A sibling control checkout is only needed for local
development and cross-repo compatibility checks. The control module provides:

- Go CLI `atn-control` and daemon `atn-controld`;
- local data home and `registry.yaml` authority;
- `channel.jsonl` event SOT and SQLite projection;
- command-envelope validation and state transitions;
- stream replay/follow/ack/status;
- council/delegation lifecycle authority;
- transcript/export/tail rendering;
- protocol version, feature groups, conformance fixtures, and compatibility docs.

Typical local control setup, from any directory:

```bash
go install github.com/SeventeenthEarth/agent-turn-network-control/cmd/atn-control@v0.1.0
go install github.com/SeventeenthEarth/agent-turn-network-control/cmd/atn-controld@v0.1.0
hash -r
command -v atn-control
command -v atn-controld

export ATN_HOME=/path/to/local/data-home
atn-control init
atn-control daemon start
atn-control daemon status
atn-control version
atn-controld version
atn-control version --features --format json
```

Expected version output for the companion release line:

```text
atn-control version=v0.1.0 protocol_version=atn-protocol-v1alpha0 schema_version=1
atn-controld version=v0.1.0 protocol_version=atn-protocol-v1alpha0 schema_version=1
```

The plugin should be configured with an explicit Unix socket/config reference to
that daemon. It must not auto-discover daemon sockets, auto-start daemons, fall
back to CLI subprocesses, infer Discord targets, or mutate live Hermes profiles,
gateway/auth/token/provider settings, or production state without explicit
approval and evidence.

## Repository boundary

- This repo owns: Python plugin code, `plugin.yaml`, Hermes tool schemas/handlers,
  daemon client adapters, bundled skills, fake/injected tests, and plugin-side
  operator guidance.
- The control repo owns: daemon/CLI, protocol SOT, event/state/storage authority,
  lifecycle/recovery/security rules, conformance fixtures, and compatibility
  version/feature responses.
- Discord/Hermes visible messages are evidence pointers only. Lifecycle state
  remains in the control daemon.
- ATN slash commands remain unsupported; `provides_commands: []` is intentional.

## Python runtime compatibility

This plugin targets the Python version used by Hermes runtime. Current runtime
compatibility is Python 3.11.

The repository declares `requires-python = ">=3.11"` in `pyproject.toml`, targets
`py311` for Ruff, type-checks as Python 3.11 with mypy, and includes a Python
3.11 syntax guard so Python 3.12-only syntax does not enter the runtime package.

Use `uv`, `pyproject.toml`, and `uv.lock` as the dependency source of truth. A
separate `requirements.txt` is intentionally not maintained while runtime
dependencies are empty; add one only if a pip-only install path becomes an
approved operator surface.

## Local development and smoke checks

```bash
uv run python - <<'PY'
import atn_plugin
print(atn_plugin.package_metadata())
PY

make test-prepare
make check-plugin-load-smoke
make check-core-contract
```

`check-core-contract` is a local development gate. It expects a sibling control
checkout at `../agent-turn-network-control` unless `ATN_CONTROL_REPO` is set; it
is not part of ordinary profile/plugin installation.

## Hermes profile installation

For a complete Hermes profile install, first install the companion control
binaries with Go's remote module install path, then install `atn-plugin` the same
way as a normal Hermes plugin. This path does not require a local
`agent-turn-network-control` checkout.

```bash
go install github.com/SeventeenthEarth/agent-turn-network-control/cmd/atn-control@v0.1.0
go install github.com/SeventeenthEarth/agent-turn-network-control/cmd/atn-controld@v0.1.0
hash -r
atn-control version
atn-controld version
```

Then use the Hermes plugin manager for each target profile and verify
plugin/tool visibility from that profile. Use the approved Git URL or
`owner/repo` identifier for the plugin source:

```bash
hermes --profile <profile> plugins install <atn-plugin-git-url-or-owner/repo> --enable
hermes --profile <profile> plugins list --enabled --json
hermes --profile <profile> tools list
```

If the plugin is intentionally installed disabled first, enable it explicitly:

```bash
hermes --profile <profile> plugins enable atn-plugin
```

When an approved live-local daemon connection is in scope, configure the
profile-local plugin install with an adjacent `config.yaml` containing only the
explicit Unix socket path:

```yaml
live_transport:
  unix_socket_path: /absolute/path/to/atn-control.sock
```

The plugin must not discover this path from the environment, call the CLI as a
fallback, or auto-start a daemon. Verify the axes separately:

1. `atn-control` binary/daemon works and `atn-control version --features --format json`
   reports the expected protocol and feature groups.
2. The target profile has `atn-plugin` installed and enabled.
3. The target profile can see the expected `atn_*` tools.
4. The target profile has the bundled ATN skills it needs, usually
   `atn-plugin`, `atn-moderator`, and/or `atn-participant`.
5. The plugin config points to the explicit daemon socket/config; no discovery or
   fallback path is accepted as proof.
6. Any live Discord/gateway/profile restart claim has separate approval and fresh
   evidence.

Installing only the plugin is not sufficient for ATN operation. Installing only
control is not sufficient for Hermes participant-agent tools. Keep both repos in
sync and run the cross-repo checks after protocol/tool changes:

```bash
# From this repo
make check-core-contract

# From the sibling control repo
cd ../agent-turn-network-control && make check-plugin-contract
```

## Tool surface summary

- `atn_daemon_status`: read daemon status through an explicit daemon client.
- `atn_compatibility_diagnostics`: read redacted compatibility diagnostics.
- `atn_stream_tail`: read retained stream frames after compatibility probing.
- `atn_stream_ack`: acknowledge a stream cursor with caller-supplied IDs.
- `atn_delegate_new` / `atn_delegate_action`: submit exact implemented delegation
  command envelopes.
- `atn_council_command`: submit exact implemented council lifecycle commands.
- `atn_selected_participant_response`: map a selected participant response to
  canonical `council.speak`, then ack the selected cursor after successful submit.
- `atn_delivery_evidence`: submit explicit delivery-evidence command envelopes.
- `atn_surface_render_projection`: render explicit daemon/control projection JSON
  into clean visible transcript rows and audit rows without reading live state.
- `atn_discussion_activation_plan`: produce deterministic activation-planning
  diagnostics from explicit evidence only.
- `atn_discord_send_message`: send only through an injected Discord sender to a
  dedicated test target; it does not record daemon delivery evidence by itself.

## Documentation

Start at [`docs/README.md`](docs/README.md).

Key docs:

- [`docs/spec/overview.md`](docs/spec/overview.md) — plugin purpose and non-goals
- [`docs/spec/architecture.md`](docs/spec/architecture.md) — plugin architecture
- [`docs/spec/compatibility-and-operations.md`](docs/spec/compatibility-and-operations.md) — control compatibility, testing, tooling, and unsupported surfaces
- [`docs/spec/skill-and-operator-guide.md`](docs/spec/skill-and-operator-guide.md) — bundled skill install, enable, rollback, troubleshooting, and local isolated plugin-load smoke boundary
- [`docs/spec/live-transport-sot.md`](docs/spec/live-transport-sot.md) — plugin-side live transport SOT
- [`docs/spec/council-argument-graph-sot.md`](docs/spec/council-argument-graph-sot.md) — plugin-side ARGUE council argument graph SOT

## Test targets

```bash
make test-prepare             # ruff/mypy/docs guardrails; no live external resources
make check-plugin-load-smoke  # local isolated plugin-load smoke; no live resources
make test-unit                # unit tests
make test-int                 # fake daemon/Hermes/Discord integration; no external resources
make test-e2e                 # isolated Hermes/Discord test environment only
make test                     # sequential all targets
make check-core-contract      # verify companion control milestone/contract readiness
```

`make test-e2e` must never target the currently running Hermes or active Discord
thread by default.

## Fail-close posture

The plugin fails closed without explicit daemon client/transport injection or an
approved explicit live socket configuration. It performs no live daemon discovery,
Hermes/Discord state discovery, gateway/profile/provider/auth/token mutation,
daemon startup, slash-command registration, or production activation by itself.

No live Hermes, live Discord, gateway, credential, token, provider, KAB,
production install, commit, push, or broad rollout readiness is implied by this
README.
