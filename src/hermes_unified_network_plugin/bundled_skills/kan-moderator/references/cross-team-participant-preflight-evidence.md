# Cross-team participant preflight evidence

Use this when 주군 asks non-KAN lane members, such as KLM 장수 profiles, to use KAN for discussion without becoming KAN developers.

## Core lesson

Do not equate these three states:

1. A profile can see `kan-plugin` / `kan-moderator` / `kan-participant` skills.
2. A profile has the `hermes-unified-network-plugin` installed and tool-visible.
3. A profile is ready for a live-visible KAN council in a specific Discord thread.

A live-visible KAN discussion preflight needs explicit evidence for all relevant layers. `hun_discussion_activation_plan` is pure/local and does not discover the environment by itself; if tool visibility, bot-to-bot state, allow-list inheritance, or visible author proof is not supplied as evidence, the correct planner result is `blocked` / `unknown`, even when the local operator has already verified those facts elsewhere.

Cross-team participants do not need full pilot-acceptance proof before the first discussion attempt. They need a minimal start gate: valid roster/registry or unambiguous reconcile, profile/plugin surface, bot-to-bot-safe Discord posture, and a target visible surface. Runtime readiness, selected-runner proof, visible author linkage, visible turn counts, and final acceptance labels are collected during and after the discussion unless one of them exposes a true `start_blocker`.

When 주군 or another user has already asked for the cross-team KAN discussion and the minimal start gate passes, do not ask for another approval; start the council. `ready_to_start` means the moderator should proceed to `council.new`; `ready_for_approval` is not the live-visible discussion start signal.

## Evidence to collect before rerunning the planner

For each participant profile, collect **and then copy these facts into the `hun_discussion_activation_plan` input**. Do not leave them as prose in the moderator's notes; the planner is pure/local and only evaluates caller-provided fields.

- `hermes --profile <profile> plugins list` shows `hermes-unified-network-plugin` enabled. Map this into `participant_profiles[].effective_discord.tools_visible: true` and include the command/session evidence in `proof_ref` or a sibling evidence field.
- Fresh profile smoke proves `hun_daemon_status ok=true` and current `live_readiness` value. Map this into the participant profile evidence, not just the final report.
- `hermes --profile <profile> chat -Q --max-turns 3 -s hermes-unified-network-plugin:kan-plugin -q '...'` or the corresponding `hermes-unified-network-plugin:kan-moderator` / `hermes-unified-network-plugin:kan-participant` load succeeds when role behavior depends on bundled guidance. Plugin-provided skills are read-only and plugin-qualified; do not require flat profile-local `kan-plugin` copies for the canonical path.
- `DISCORD_ALLOW_BOTS=none` or equivalent effective gateway proof is present unless 주군 explicitly approved bot-to-bot behavior for the pilot. Map this into `participant_profiles[].effective_discord.bot_to_bot_enabled: false`.
- The target Discord parent channel id, not only the thread id, is in `discord.allowed_channels` for every participant. If thread id is also known, include it too, but do not mistake a thread-only id for parent allow-list inheritance proof. Map this into `discord_parent_channel.parent_channel_id`, participant `allowed_channels`, and `discord_parent_channel.allow_list_inheritance_proven: true` only when parent-channel inheritance proof exists.
- Gateway was restarted after config/plugin changes, and logs show `Connected as <expected bot>` plus `✓ discord connected`.
- Visible author probe was sent through the same profile/send path into the target parent/thread, and the resulting message id is recorded per profile. Map this into `visible_surface_readiness.turn_posting_probe` / `real_profile_gateway_replies: true` and per-profile author proof fields.

### Minimal planner field mapping

A moderator who only reads this skill should not need a separate human instruction to avoid `tools_visibility_unknown` or `bot_to_bot_eligibility_unknown`. Before calling `hun_discussion_activation_plan`, make the evidence machine-readable in this shape or an equivalent richer shape:

```json
{
  "participant_profiles": [
    {
      "profile": "jangbi",
      "member": "jangbi",
      "effective_discord": {
        "tools_visible": true,
        "bot_to_bot_enabled": false,
        "allowed_channels": ["1516594793046605864"],
        "gateway_connected": true,
        "proof_ref": "profile smoke + config/gateway evidence pointer"
      }
    }
  ],
  "discord_parent_channel": {
    "channel_id": "1516594793046605864",
    "thread_id": "1517508235769413673",
    "allow_list_inheritance_proven": true,
    "proof_source": "parent channel is present in each participant discord.allowed_channels; same-path thread/parent probe recorded"
  },
  "visible_surface_readiness": {
    "surface_binding": {"thread_id": "1517508235769413673", "parent_channel_id": "1516594793046605864"},
    "turn_posting_probe": {"per_profile_author_proof": true},
    "visible_closeout_probe": {"ok": true},
    "real_profile_gateway_replies": true,
    "cli_actor_speech_only": false
  }
}
```

If these fields are unknown or absent, a `HAN_BLOCK`/blocked result is correct; it means the evidence was not materialized into the planner input, not necessarily that the environment is misconfigured.

## Config pitfall

When patching `config.yaml`, update the nested `discord.allowed_channels` entry, not another platform's `allowed_channels` such as `slack.allowed_channels`. Some profiles have multiple `allowed_channels` keys; locate the `discord:` block first, then patch within that block. Verify with a block-aware read or parser, not a plain first regex match.

## Practical probe pattern

After plugin install/enable and gateway restart, a minimal evidence package can be built with:

```bash
# Tool visibility / daemon smoke
hermes --profile <profile> chat -Q --max-turns 3 -s hermes-unified-network-plugin:kan-plugin -q \
  'Call hun_daemon_status exactly once. Then print only ok=<ok field> live_readiness=<live_readiness field if present> error=<error field if present>.'

# Visible author proof for Discord parent + thread
hermes --profile <profile> send \
  --to 'discord:<parent_channel_id>:<thread_id>' \
  --json \
  '[KAN preflight author probe] <korean-name> / <profile>: profile-send visible author probe.'
```

Record each returned Discord `message_id` as author proof. If the send succeeds but all messages appear as one shared/default bot or without clear per-speaker labels, block as `VISIBLE_SURFACE_IDENTITY_NOT_PROVEN` and redesign the surface before `council.new`.

## Reporting guidance

If a moderator reports `HAN_BLOCK` because these evidence classes were missing, treat it as a correct fail-closed preflight result, not as proof the plugin is unusable. Fix the missing evidence, restart affected gateways, rerun fresh smoke/probes, then tell the moderator to start a new session or `/reset` before rerunning preflight so the old blocked context does not anchor the next attempt.

Keep KAN development authority separate from KAN usage: cross-team KLM members may use KAN as discussion participants without becoming owners of `kkachi-agent-network-control` or `hermes-unified-network-plugin`.
