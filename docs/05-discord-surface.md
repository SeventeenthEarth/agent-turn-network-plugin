# Discord Surface

## Purpose

The plugin may provide a Discord visible surface for KAN council sessions by using Hermes gateway/send_message capability. Discord is for human-visible discussion/evidence, not canonical state.

## Rules

- Discord message IDs, channel IDs, and thread IDs are evidence pointers.
- `channel.jsonl` in the core daemon remains the SOT.
- The plugin records delivery success/failure by sending typed commands to `kkachi-agent-networkd`.
- The daemon must not require raw Discord tokens.
- Free-form Discord replies are never parsed as authoritative lifecycle transitions.
- KAN slash-command invocations are not supported in HPLUG-3. Native Discord slash commands may only become supported after a later task proves the Hermes command binding, KAN daemon command contract, delivery-evidence path, and isolated Discord test target.

## Testing

Unit and integration tests use fake gateway/send_message functions. E2E tests may post to Discord only when `DISCORD_TEST_TARGET` points to a dedicated test environment. Tests must never default to the active user thread.
