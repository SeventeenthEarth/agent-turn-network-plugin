"""Hermes directory plugin entrypoint for kkachi-agent-network-plugin.

SCAFF-2 intentionally registers no tools or hooks. Real KAN tool schemas,
handlers, slash commands, and daemon client behavior are introduced by later
DAEMN/HPLUG tasks after their core contracts and tests exist.
"""

from __future__ import annotations


def register(ctx: object) -> None:
    """Register the scaffold-only plugin surface with Hermes.

    The context is accepted to match Hermes' directory-plugin contract, but the
    scaffold performs no registration yet so the manifest does not overclaim
    unavailable tools or hooks.
    """
    _ = ctx


__all__ = ["register"]
