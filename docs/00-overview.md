# kkachi-agent-network-plugin Overview

## Purpose

`kkachi-agent-network-plugin` is the Python Hermes plugin adapter for KAN. In the current HPLUG-2 state it provides fake/injected read-only Hermes tool surfaces for daemon status, compatibility diagnostics, and stream tail reads, backed by the DAEMN client foundation. `kan_session_status`, write tools, slash commands, skills, live daemon discovery, and live Hermes/Discord integration are not exposed yet.

The plugin is not the source of truth. `kkachi-agent-networkd` owns state, event append, locks, replay, projections, and lifecycle decisions.

## Repository boundary

This repository owns:

- Hermes plugin manifest/entrypoint code;
- Python daemon client foundation for KAN protocol using explicit fake/injected transports;
- HPLUG-2 read-only Hermes tool schemas and JSON-string handlers for `kan_daemon_status`, `kan_compatibility_diagnostics`, and `kan_stream_tail`;
- future slash-command bindings where Hermes supports them;
- bundled KAN skill material when that task lands;
- future Discord visible-surface helpers through Hermes gateway/send_message after delivery-evidence contracts exist;
- plugin tests and plugin docs.

It does not own:

- `channel.jsonl` append;
- SQLite projection mutation;
- daemon locks/cursors;
- protocol SOT;
- raw Discord bot tokens inside the daemon;
- live daemon/Hermes/Discord/KAB/auth/token/gateway fallback behavior;
- Hermes core changes.

## Companion core repo

Core docs and protocol SOT live in `../../kkachi-agent-network/docs/`. The plugin should copy only the minimum compatibility summary needed for operators and should link back to the core docs for authority.
