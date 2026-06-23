# Hermes Unified Network Plugin Overview

## Purpose

`hermes-unified-network-plugin` is the Python Hermes plugin adapter for Hermes Unified Network (HUN). In the current SKILL-2 state it provides fake/injected Hermes tool surfaces for daemon status, compatibility diagnostics, stream tail reads, delegation/review command-envelope submission, council lifecycle command submission, delivery-evidence command submission, an injected-only Discord helper backed by the DAEMN client foundation, packaged HUN operator skills, a compatibility matrix, and local isolated plugin-load smoke. Hermes provides a plugin slash-command host API, but `hun_session_status`, HUN slash commands, live daemon discovery, live/default Discord helper posting, production activation, KAB readiness, live plugin readiness, and live Hermes/Discord integration are not exposed.

The plugin is not the source of truth. `kkachi-agent-networkd` owns state, event append, locks, replay, projections, and lifecycle decisions.

## Repository boundary

This repository owns:

- Hermes plugin manifest/entrypoint code;
- Python daemon client foundation for the HUN protocol using explicit fake/injected transports;
- HPLUG-2 read-only Hermes tool schemas and JSON-string handlers for `hun_daemon_status`, `hun_compatibility_diagnostics`, and `hun_stream_tail`;
- DELRV-1 fake/injected command-envelope tool schemas and JSON-string handlers for `hun_delegate_new` and `hun_delegate_action`;
- CNDIS-1 fake/injected command-envelope tool schemas and JSON-string handlers for `hun_council_command` and `hun_delivery_evidence`;
- CNDIS-2 injected-only Discord helper schema, target validation, and JSON-string handler for `hun_discord_send_message`;
- future HUN slash-command bindings after concrete daemon command contracts, fixtures, manifest declarations, and isolated tests exist;
- bundled HUN skill material;
- future live Discord visible-surface wiring through Hermes gateway/send_message after explicit isolated live-target tests exist;
- plugin tests and plugin docs.

It does not own:

- `channel.jsonl` append;
- SQLite projection mutation;
- daemon locks/cursors;
- protocol SOT;
- raw Discord bot tokens inside the daemon;
- live daemon/Hermes/Discord/KAB/auth/token/gateway fallback behavior;
- Hermes core changes.

## Companion control repo

Control docs and protocol SOT live in `../../kkachi-agent-network-control/docs/`. The plugin should copy only the minimum compatibility summary needed for operators and should link back to the control docs for authority.
