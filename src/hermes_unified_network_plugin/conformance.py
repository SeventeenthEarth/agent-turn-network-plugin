"""Conformance manifest guard for draft fake-daemon development."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .errors import DaemonCompatibilityError
from .protocol import REQUIRED_FEATURE_GROUPS, SUPPORTED_PROTOCOL_VERSION

DRAFT_STABILITY_MARKERS = ("draft", "scaffold")


@dataclass(frozen=True)
class ConformanceManifest:
    manifest_version: int | None
    protocol_version: str
    stability: str
    fixtures: tuple[str, ...]
    required_feature_groups: tuple[str, ...]
    live_readiness: bool


def _tuple_of_strings(value: object, *, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise DaemonCompatibilityError(f"conformance manifest {label} must be a list")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise DaemonCompatibilityError(
                f"conformance manifest {label} entries must be non-empty strings"
            )
        result.append(item)
    return tuple(result)


def _is_draft_stability(stability: str) -> bool:
    lowered = stability.lower()
    return any(marker in lowered for marker in DRAFT_STABILITY_MARKERS)


def parse_conformance_manifest(value: Mapping[str, object]) -> ConformanceManifest:
    protocol_version = value.get("protocol_version")
    if protocol_version != SUPPORTED_PROTOCOL_VERSION:
        raise DaemonCompatibilityError(
            f"conformance manifest protocol mismatch: {protocol_version!r} != "
            f"{SUPPORTED_PROTOCOL_VERSION!r}"
        )

    manifest_version_value = value.get("manifest_version")
    if manifest_version_value is not None and (
        isinstance(manifest_version_value, bool) or not isinstance(manifest_version_value, int)
    ):
        raise DaemonCompatibilityError("conformance manifest manifest_version must be an integer")

    stability = value.get("stability", "")
    if not isinstance(stability, str) or not stability:
        raise DaemonCompatibilityError("conformance manifest stability must be a non-empty string")

    fixtures = _tuple_of_strings(value.get("fixtures", []), label="fixtures")
    required_feature_groups = _tuple_of_strings(
        value.get("required_feature_groups", []), label="required_feature_groups"
    )

    missing = sorted(set(REQUIRED_FEATURE_GROUPS).difference(required_feature_groups))
    if missing:
        raise DaemonCompatibilityError(
            f"conformance manifest missing required feature groups: {missing}"
        )

    draft_stability = _is_draft_stability(stability)
    if not fixtures and not draft_stability:
        raise DaemonCompatibilityError(
            "conformance manifest fixtures=[] is allowed only for draft/scaffold stability"
        )

    explicit_live_readiness = value.get("live_readiness")
    if explicit_live_readiness is not None and not isinstance(explicit_live_readiness, bool):
        raise DaemonCompatibilityError("conformance manifest live_readiness must be boolean")

    live_readiness = bool(explicit_live_readiness) if explicit_live_readiness is not None else True
    if draft_stability or not fixtures:
        live_readiness = False

    return ConformanceManifest(
        manifest_version=manifest_version_value,
        protocol_version=protocol_version,
        stability=stability,
        fixtures=fixtures,
        required_feature_groups=required_feature_groups,
        live_readiness=live_readiness,
    )


def load_conformance_manifest(path: Path) -> ConformanceManifest:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DaemonCompatibilityError(f"cannot load conformance manifest: {path}") from exc
    if not isinstance(raw, dict):
        raise DaemonCompatibilityError("conformance manifest must be a JSON object")
    return parse_conformance_manifest(raw)


__all__ = ["ConformanceManifest", "load_conformance_manifest", "parse_conformance_manifest"]
