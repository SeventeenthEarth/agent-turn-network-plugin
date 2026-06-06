from __future__ import annotations

import pytest

from kkachi_agent_network_plugin.discord_surface import (
    DEFAULT_TEST_LABEL,
    DiscordMessageResult,
    DiscordMessageTarget,
    e2e_config_from_env,
    send_discord_message,
)


def valid_target(**overrides: object) -> DiscordMessageTarget:
    values: dict[str, object] = {
        "channel_id": "discord-test-channel-123",
        "thread_id": "discord-test-thread-456",
        "dedicated_test_target": True,
        "label": "[Kkachi CNDIS-2 isolated E2E]",
        "cleanup_hint": "Delete messages after CNDIS-2 verification.",
        "live_opt_in": False,
    }
    values.update(overrides)
    return DiscordMessageTarget(
        channel_id=values["channel_id"],
        thread_id=values["thread_id"],
        dedicated_test_target=values["dedicated_test_target"],
        label=values["label"],
        cleanup_hint=values["cleanup_hint"],
        live_opt_in=values["live_opt_in"],
    )


def test_discord_send_fails_closed_without_injected_sender() -> None:
    with pytest.raises(ValueError, match="explicit Discord send_message sender is required"):
        send_discord_message(target=valid_target(), content="hello", sender=None)


def test_discord_target_from_mapping_requires_dedicated_target_marker() -> None:
    target = DiscordMessageTarget.from_mapping(
        {"channel_id": "discord-test-channel-123", "dedicated_test_target": False}
    )

    with pytest.raises(ValueError, match="dedicated_test_target must be true"):
        target.validate()


def test_discord_target_rejects_current_or_active_labels() -> None:
    target = valid_target(label="current active user thread")

    with pytest.raises(ValueError, match="current or active Discord targets"):
        target.validate()


def test_discord_target_rejects_current_thread_pointer() -> None:
    target = valid_target(thread_id="current-thread")

    with pytest.raises(ValueError, match="current or active Discord targets"):
        target.validate()


def test_discord_send_requires_visible_label_and_cleanup_hint() -> None:
    missing_label = valid_target(label=None)
    missing_cleanup = valid_target(cleanup_hint=None)

    with pytest.raises(ValueError, match="target.label is required for Discord send evidence"):
        missing_label.validate()
    with pytest.raises(
        ValueError, match="target.cleanup_hint is required for Discord send evidence"
    ):
        missing_cleanup.validate()


def test_discord_target_mapping_rejects_unknown_fields() -> None:
    with pytest.raises(ValueError, match="unsupported Discord target fields: token"):
        DiscordMessageTarget.from_mapping(
            {"channel_id": "discord-test-channel-123", "dedicated_test_target": True, "token": "x"}
        )


def test_fake_sender_called_exactly_once_for_valid_isolated_target() -> None:
    calls: list[tuple[DiscordMessageTarget, str]] = []

    def fake_sender(*, target: DiscordMessageTarget, content: str) -> DiscordMessageResult:
        calls.append((target, content))
        return DiscordMessageResult(
            message_id="msg-123",
            channel_id=target.channel_id,
            thread_id=target.thread_id,
            message_ref="discord://discord-test-channel-123/discord-test-thread-456/msg-123",
            label=target.label,
            cleanup_hint=target.cleanup_hint,
        )

    result = send_discord_message(target=valid_target(), content="hello", sender=fake_sender)

    assert result.message_id == "msg-123"
    assert (
        result.message_ref == "discord://discord-test-channel-123/discord-test-thread-456/msg-123"
    )
    assert len(calls) == 1
    assert calls[0][1] == "hello"


def test_sender_result_must_match_target_evidence_pointers() -> None:
    def fake_sender(*, target: DiscordMessageTarget, content: str) -> DiscordMessageResult:
        _ = (target, content)
        return DiscordMessageResult(message_id="msg-123", channel_id="other-channel")

    with pytest.raises(ValueError, match="result.channel_id must match"):
        send_discord_message(target=valid_target(), content="hello", sender=fake_sender)


def test_e2e_config_is_inert_by_default_even_with_live_looking_env_names() -> None:
    config = e2e_config_from_env(
        {
            "DISCORD_TOKEN": "fake-token",
            "DISCORD_TEST_TARGET": "current-thread",
            "HERMES_HOME": "/tmp/current-hermes",
        }
    )

    assert config.enabled is False
    assert "KAN_DISCORD_E2E=1" in config.reason
    assert config.target is None


def test_e2e_config_rejects_invalid_opt_in_target_without_sender_or_post() -> None:
    config = e2e_config_from_env(
        {
            "KAN_DISCORD_E2E": "1",
            "DISCORD_TEST_TARGET": "current-thread",
            "DISCORD_TEST_DEDICATED": "1",
            "DISCORD_TEST_CLEANUP_HINT": "Delete test messages.",
        }
    )

    assert config.enabled is False
    assert "current or active Discord targets" in config.reason
    assert config.target is None


def test_e2e_config_accepts_valid_dedicated_target_with_label_and_cleanup_hint() -> None:
    config = e2e_config_from_env(
        {
            "KAN_DISCORD_E2E": "1",
            "DISCORD_TEST_TARGET": "discord-test-channel-123",
            "DISCORD_TEST_THREAD": "discord-test-thread-456",
            "DISCORD_TEST_DEDICATED": "1",
            "DISCORD_TEST_CLEANUP_HINT": "Delete the CNDIS-2 E2E test message.",
        }
    )

    assert config.enabled is True
    assert config.target is not None
    assert config.target.label == DEFAULT_TEST_LABEL
    assert config.target.cleanup_hint == "Delete the CNDIS-2 E2E test message."
    assert config.target.live_opt_in is True
