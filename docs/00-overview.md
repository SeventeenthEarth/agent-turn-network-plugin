# kkachi-agent-network-plugin Overview

## Purpose

`kkachi-agent-network-plugin` is the Python Hermes plugin adapter for KAN. It gives Hermes agents convenient tool/slash-command/skill surfaces for the Go daemon in `kkachi-agent-network`.

The plugin is not the source of truth. `kkachi-agent-networkd` owns state, event append, locks, replay, projections, and lifecycle decisions.

## Repository boundary

This repository owns:

- Hermes plugin manifest/entrypoint code;
- Python daemon client for KAN protocol;
- Hermes tool schemas and handlers;
- slash-command bindings where Hermes supports them;
- bundled KAN skill material;
- Discord visible-surface helpers through Hermes gateway/send_message;
- plugin tests and plugin docs.

It does not own:

- `channel.jsonl` append;
- SQLite projection mutation;
- daemon locks/cursors;
- protocol SOT;
- raw Discord bot tokens inside the daemon;
- Hermes core changes.

## Companion core repo

Core docs and protocol SOT live in `../../kkachi-agent-network/docs/`. The plugin should copy only the minimum compatibility summary needed for operators and should link back to the core docs for authority.
