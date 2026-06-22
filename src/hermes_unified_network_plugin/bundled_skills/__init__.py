"""Bundled operator skill resources for hermes-unified-network-plugin.

The helpers in this module are import-safe: they expose packaged text resources
only and never install files into a Hermes profile or discover live runtime
state.
"""

from __future__ import annotations

from importlib import resources
from importlib.resources.abc import Traversable

BUNDLED_SKILL_NAME = "hun-plugin"
BUNDLED_SKILL_NAMES = ("hun-plugin", "hun-moderator", "hun-participant")


def bundled_skill_names() -> tuple[str, ...]:
    """Return the bundled skill names shipped with this package."""

    return BUNDLED_SKILL_NAMES


def bundled_skill_resource(name: str = BUNDLED_SKILL_NAME) -> Traversable:
    """Return the packaged `SKILL.md` resource for a bundled skill.

    The helper deliberately accepts only known bundled names so future installers
    cannot use it as a profile/filesystem path traversal primitive.
    """

    if name not in bundled_skill_names():
        raise ValueError(f"unknown bundled skill: {name}")
    return resources.files(__package__).joinpath(name, "SKILL.md")


def read_bundled_skill_text(name: str = BUNDLED_SKILL_NAME) -> str:
    """Read a bundled skill as UTF-8 text without installing it."""

    return bundled_skill_resource(name).read_text(encoding="utf-8")


__all__ = [
    "BUNDLED_SKILL_NAME",
    "BUNDLED_SKILL_NAMES",
    "bundled_skill_names",
    "bundled_skill_resource",
    "read_bundled_skill_text",
]
