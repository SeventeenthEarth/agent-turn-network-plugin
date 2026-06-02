"""Minimal package scaffold for kkachi-agent-network-plugin."""

from __future__ import annotations

__version__ = "0.1.0"


def package_metadata() -> dict[str, str]:
    """Return stable package metadata without importing runtime integrations."""
    return {
        "name": "kkachi-agent-network-plugin",
        "module": "kkachi_agent_network_plugin",
        "version": __version__,
    }


__all__ = ["__version__", "package_metadata"]
