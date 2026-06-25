"""Injected-only Discord send_message helper boundary.

This module contains no environment reads and no live Discord/Hermes discovery.
Callers must provide both an explicit isolated target and an injected sender.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, Self

from .protocol import JsonObject

DEFAULT_TEST_LABEL = "[Kkachi CNDIS-2 isolated E2E]"

_ACTIVE_TARGET_MARKERS = (
    "active",
    "active-thread",
    "active_user",
    "current",
    "current-thread",
    "current_user",
    "hermes-current",
    "live-user",
    "user-thread",
)


class SendMessageFn(Protocol):
    """Callable supplied by tests or explicit non-default wiring only."""

    def __call__(self, *, target: DiscordMessageTarget, content: str) -> DiscordMessageResult: ...


@dataclass(frozen=True)
class DiscordMessageTarget:
    """Explicit Discord target metadata for isolated tests."""

    channel_id: str
    thread_id: str | None = None
    dedicated_test_target: bool = False
    label: str | None = None
    cleanup_hint: str | None = None
    live_opt_in: bool = False
    platform: str = "discord"

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> Self:
        unknown = sorted(
            str(key)
            for key in value
            if key
            not in {
                "platform",
                "channel_id",
                "thread_id",
                "dedicated_test_target",
                "label",
                "cleanup_hint",
                "live_opt_in",
            }
        )
        if unknown:
            raise ValueError(f"unsupported Discord target fields: {', '.join(unknown)}")
        return cls(
            platform=_optional_string(value.get("platform"), label="target.platform") or "discord",
            channel_id=_required_string(value.get("channel_id"), label="target.channel_id"),
            thread_id=_optional_string(value.get("thread_id"), label="target.thread_id"),
            dedicated_test_target=_required_bool(
                value.get("dedicated_test_target"), label="target.dedicated_test_target"
            ),
            label=_optional_string(value.get("label"), label="target.label"),
            cleanup_hint=_optional_string(value.get("cleanup_hint"), label="target.cleanup_hint"),
            live_opt_in=_optional_bool(value.get("live_opt_in"), label="target.live_opt_in"),
        )

    def validate(self) -> None:
        if self.platform != "discord":
            raise ValueError("target.platform must be 'discord'")
        if not self.dedicated_test_target:
            raise ValueError("target.dedicated_test_target must be true")
        _reject_active_target_marker(self.channel_id, label="target.channel_id")
        if self.thread_id is not None:
            _reject_active_target_marker(self.thread_id, label="target.thread_id")
        if self.label is not None:
            _reject_active_target_marker(self.label, label="target.label")
        if self.label is None:
            raise ValueError("target.label is required for Discord send evidence")
        if self.cleanup_hint is None:
            raise ValueError("target.cleanup_hint is required for Discord send evidence")

    def to_mapping(self) -> JsonObject:
        data: JsonObject = {
            "platform": self.platform,
            "channel_id": self.channel_id,
            "dedicated_test_target": self.dedicated_test_target,
            "live_opt_in": self.live_opt_in,
        }
        if self.thread_id is not None:
            data["thread_id"] = self.thread_id
        if self.label is not None:
            data["label"] = self.label
        if self.cleanup_hint is not None:
            data["cleanup_hint"] = self.cleanup_hint
        return data


@dataclass(frozen=True)
class DiscordMessageResult:
    """Evidence pointer returned by the injected sender."""

    message_id: str
    channel_id: str
    thread_id: str | None = None
    message_ref: str | None = None
    label: str | None = None
    cleanup_hint: str | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> Self:
        unknown = sorted(
            str(key)
            for key in value
            if key
            not in {
                "message_id",
                "channel_id",
                "thread_id",
                "message_ref",
                "label",
                "cleanup_hint",
            }
        )
        if unknown:
            raise ValueError(f"unsupported Discord result fields: {', '.join(unknown)}")
        return cls(
            message_id=_required_string(value.get("message_id"), label="result.message_id"),
            channel_id=_required_string(value.get("channel_id"), label="result.channel_id"),
            thread_id=_optional_string(value.get("thread_id"), label="result.thread_id"),
            message_ref=_optional_string(value.get("message_ref"), label="result.message_ref"),
            label=_optional_string(value.get("label"), label="result.label"),
            cleanup_hint=_optional_string(value.get("cleanup_hint"), label="result.cleanup_hint"),
        )

    def to_mapping(self) -> JsonObject:
        data: JsonObject = {"message_id": self.message_id, "channel_id": self.channel_id}
        if self.thread_id is not None:
            data["thread_id"] = self.thread_id
        if self.message_ref is not None:
            data["message_ref"] = self.message_ref
        if self.label is not None:
            data["label"] = self.label
        if self.cleanup_hint is not None:
            data["cleanup_hint"] = self.cleanup_hint
        return data


@dataclass(frozen=True)
class DiscordE2EConfig:
    """Parsed opt-in state from an explicitly supplied environment mapping."""

    enabled: bool
    reason: str
    target: DiscordMessageTarget | None = None


def send_discord_message(
    *,
    target: DiscordMessageTarget,
    content: str,
    sender: SendMessageFn | None,
) -> DiscordMessageResult:
    """Validate an isolated target and call the injected sender exactly once."""

    if sender is None:
        raise ValueError(
            "explicit Discord send_message sender is required; no live Discord fallback"
        )
    _required_string(content, label="content")
    target.validate()
    result = sender(target=target, content=content)
    if not isinstance(result, DiscordMessageResult):
        raise ValueError("sender must return DiscordMessageResult")
    if result.channel_id != target.channel_id:
        raise ValueError("result.channel_id must match target.channel_id")
    if result.thread_id != target.thread_id:
        raise ValueError("result.thread_id must match target.thread_id")
    return result


def e2e_config_from_env(env: Mapping[str, str]) -> DiscordE2EConfig:
    """Parse inert Discord E2E opt-in settings from a supplied mapping.

    The function never reads ``os.environ`` itself and never creates a sender.
    """

    if env.get("KAN_DISCORD_E2E") != "1":
        return DiscordE2EConfig(False, "KAN_DISCORD_E2E=1 is required for Discord E2E opt-in")
    raw_target = env.get("DISCORD_TEST_TARGET", "")
    if not raw_target:
        return DiscordE2EConfig(False, "DISCORD_TEST_TARGET is required for Discord E2E opt-in")
    target = DiscordMessageTarget(
        channel_id=raw_target,
        thread_id=env.get("DISCORD_TEST_THREAD") or None,
        dedicated_test_target=env.get("DISCORD_TEST_DEDICATED") == "1",
        label=env.get("DISCORD_TEST_LABEL") or DEFAULT_TEST_LABEL,
        cleanup_hint=env.get("DISCORD_TEST_CLEANUP_HINT") or None,
        live_opt_in=True,
    )
    try:
        target.validate()
    except ValueError as exc:
        return DiscordE2EConfig(False, str(exc))
    return DiscordE2EConfig(True, "Discord E2E target accepted", target)


def _required_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _optional_string(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, label=label)


def _required_bool(value: object, *, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean")
    return value


def _optional_bool(value: object, *, label: str) -> bool:
    if value is None:
        return False
    return _required_bool(value, label=label)


def _reject_active_target_marker(value: str, *, label: str) -> None:
    normalized = value.casefold().replace(" ", "-")
    marker = next((marker for marker in _ACTIVE_TARGET_MARKERS if marker in normalized), None)
    if marker is not None:
        raise ValueError(f"{label} must not reference current or active Discord targets")


__all__ = [
    "DEFAULT_TEST_LABEL",
    "DiscordE2EConfig",
    "DiscordMessageResult",
    "DiscordMessageTarget",
    "SendMessageFn",
    "e2e_config_from_env",
    "send_discord_message",
]
