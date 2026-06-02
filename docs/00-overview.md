# kkachi-agent-network-plugin Overview

## Purpose

`kkachi-agent-network-plugin` is the Python Hermes plugin adapter for KAN. In the current DAEMN-2 state it provides an import-safe Python daemon-client foundation for fake/injected transports, including fake-only status/version, command envelope, stream tail parsing, and diagnostics decoding. Hermes tool/slash-command/skill surfaces for the Go daemon in `kkachi-agent-network` are planned but not exposed by the manifest or entrypoint yet.

The plugin is not the source of truth. `kkachi-agent-networkd` owns state, event append, locks, replay, projections, and lifecycle decisions.

## Repository boundary

This repository owns:

- Hermes plugin manifest/entrypoint code;
- Python daemon client foundation for KAN protocol using explicit fake/injected transports;
- future Hermes tool schemas and handlers;
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
