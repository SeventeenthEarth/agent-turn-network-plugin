# Discord Surface

## Purpose

The plugin may provide a Discord visible surface for KAN council sessions through an
injected Hermes gateway/send_message boundary. Discord is for human-visible
discussion/evidence, not canonical state.

## Rules

- Discord message IDs, channel IDs, and thread IDs are evidence pointers.
- `channel.jsonl` in the control daemon remains the SOT.
- `hun_discord_send_message` is an injected-only helper. It requires a caller-supplied
  `send_message` callable plus an explicit dedicated test target; without the injected
  sender it returns a fail-closed JSON error and does not post.
- The helper does not read environment variables, discover current Hermes sessions,
  inspect active Discord threads, open gateway/socket/CLI connections, or use tokens.
- The plugin records delivery success/failure only through fake/injected
  `hun_delivery_evidence` command submission. Discord message IDs, channel IDs, and
  thread IDs remain evidence pointers; they are not daemon state.
- The daemon must not require raw Discord tokens.
- Free-form Discord replies are never parsed as authoritative lifecycle transitions.
- KAN slash-command invocations are not supported in HPLUG-3/CNDIS-1. Native Discord slash commands may only become supported after a later task proves the Hermes command binding, KAN daemon command contract, delivery-evidence path, and isolated Discord test target.

CNDIS-1 supports council and delivery-evidence command tools through explicit fake/injected daemon clients only. It does not post to Discord, call Hermes gateway/send_message, or infer delivery evidence from live Discord state.

CNDIS-2 adds only the injected helper boundary. It still does not claim live Discord
readiness, active Hermes session delivery, gateway configuration, daemon-recorded evidence,
or KAN/KAB slash-command support.

## Testing

Unit and integration tests use fake gateway/send_message functions. E2E tests default to
`KAN_DISCORD_E2E=0` and no sender, so they cannot post. A live-post path must set all of
the following explicitly:

- `KAN_DISCORD_E2E=1`
- `DISCORD_TEST_TARGET=<dedicated test channel id>`
- `DISCORD_TEST_DEDICATED=1`
- `DISCORD_TEST_CLEANUP_HINT=<operator cleanup instruction>`
- optional `DISCORD_TEST_THREAD=<dedicated test thread id>`
- optional `DISCORD_TEST_LABEL=<visible test label>`; otherwise the helper uses
  `[Kkachi CNDIS-2 isolated E2E]`

Missing opt-in, current/active target labels, non-dedicated targets, missing cleanup
guidance, or missing injected sender all fail closed. Tests must never default to the
active user thread.
