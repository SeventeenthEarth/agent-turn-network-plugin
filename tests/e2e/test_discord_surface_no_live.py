from __future__ import annotations

import json
import os

import pytest

from kkachi_agent_network_plugin.discord_surface import DEFAULT_TEST_LABEL, e2e_config_from_env
from kkachi_agent_network_plugin.tools import handle_discord_send_message


def test_e2e_discord_helper_default_no_live_with_live_looking_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert os.environ.get("KAN_E2E") == "1"
    monkeypatch.setenv("KAN_DISCORD_E2E", "0")
    monkeypatch.setenv("DISCORD_TOKEN", "fake-token")
    monkeypatch.setenv("DISCORD_TEST_TARGET", "current-thread")
    monkeypatch.setenv("HERMES_HOME", os.environ.get("HERMES_HOME", "/tmp/fake-hermes-home"))

    config = e2e_config_from_env(os.environ)
    result = json.loads(
        handle_discord_send_message(
            {
                "content": "must not post",
                "target": {
                    "channel_id": "discord-test-channel",
                    "dedicated_test_target": True,
                },
            }
        )
    )

    assert config.enabled is False
    assert "KAN_DISCORD_E2E=1" in config.reason
    assert result["ok"] is False
    assert result["error"]["category"] == "validation"
    assert "no live Discord fallback" in result["error"]["message"]


def test_e2e_discord_opt_in_absent_reports_skip_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    assert os.environ.get("KAN_E2E") == "1"
    monkeypatch.delenv("KAN_DISCORD_E2E", raising=False)
    monkeypatch.setenv("DISCORD_TEST_TARGET", "discord-test-channel")

    config = e2e_config_from_env(os.environ)

    assert config.enabled is False
    assert config.target is None
    assert config.reason == "KAN_DISCORD_E2E=1 is required for Discord E2E opt-in"


def test_e2e_discord_opt_in_invalid_target_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    assert os.environ.get("KAN_E2E") == "1"
    monkeypatch.setenv("KAN_DISCORD_E2E", "1")
    monkeypatch.setenv("DISCORD_TEST_TARGET", "active-user-thread")
    monkeypatch.setenv("DISCORD_TEST_DEDICATED", "1")
    monkeypatch.setenv("DISCORD_TEST_CLEANUP_HINT", "Delete test messages.")

    config = e2e_config_from_env(os.environ)

    assert config.enabled is False
    assert config.target is None
    assert "current or active Discord targets" in config.reason


def test_e2e_discord_valid_opt_in_target_requires_label_cleanup_but_no_live_send(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert os.environ.get("KAN_E2E") == "1"
    monkeypatch.setenv("KAN_DISCORD_E2E", "1")
    monkeypatch.setenv("DISCORD_TEST_TARGET", "discord-test-channel")
    monkeypatch.setenv("DISCORD_TEST_THREAD", "discord-test-thread")
    monkeypatch.setenv("DISCORD_TEST_DEDICATED", "1")
    monkeypatch.setenv("DISCORD_TEST_CLEANUP_HINT", "Delete CNDIS-2 isolated E2E message.")

    config = e2e_config_from_env(os.environ)
    result = json.loads(
        handle_discord_send_message(
            {
                "content": "would post only with injected sender",
                "target": config.target.to_mapping() if config.target is not None else {},
            }
        )
    )

    assert config.enabled is True
    assert config.target is not None
    assert config.target.label == DEFAULT_TEST_LABEL
    assert config.target.cleanup_hint == "Delete CNDIS-2 isolated E2E message."
    assert result["ok"] is False
    assert "no live Discord fallback" in result["error"]["message"]
