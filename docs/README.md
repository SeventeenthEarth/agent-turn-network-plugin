# atn-plugin Documentation

This directory is the source of truth for the Python Hermes plugin adapter for Agent Turn Network (ATN). The plugin is not the control source of truth; in guardrail terms, plugin is not the source of truth. It adapts Hermes-facing tools and packaged skills to the daemon protocol owned by `atn-control`.

`roadmap.md` is the SSOT for plugin epic/task status, sequencing, and evidence pointers. Other docs describe stable architecture, contracts, compatibility, or operator procedure and should reference the roadmap instead of duplicating current task state.

## Structure

1. `roadmap.md` - plugin epic/task status, sequencing, and evidence-pointer SSOT
2. `spec/overview.md` - plugin purpose, repo boundary, and non-goals
3. `spec/architecture.md` - plugin architecture, tool contract, and Discord helper surface
4. `spec/compatibility-and-operations.md` - control compatibility, testing policy, tooling, and unsupported surfaces
5. `spec/skill-and-operator-guide.md` - bundled ATN skill install, enable, rollback, troubleshooting, and local isolated plugin-load smoke boundary
6. `spec/live-transport-sot.md` - plugin-side live transport SOT
7. `spec/council-argument-graph-sot.md` - plugin-side council argument graph SOT
8. `spec/agent-turn-network-plugin-naming-sot.md` - plugin-side ATN naming SOT

## Required Makefile Targets

```bash
make test-prepare
make check-plugin-load-smoke
make test-unit
make test-int
make test-e2e
make test
make check-core-contract
```

Slash commands, live daemon discovery, production activation, KAB bridge behavior, long-lived member runtime readiness, broad command coverage, and live/default Discord visible-surface wiring remain unsupported.
