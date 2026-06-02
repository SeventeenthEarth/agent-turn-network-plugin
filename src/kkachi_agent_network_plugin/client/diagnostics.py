"""Diagnostics response decoding for explicit DAEMN-2 transports."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import cast

from ..errors import DaemonProtocolError, decode_daemon_error, redact_sensitive
from ..protocol import (
    DIAGNOSTIC_CHECK_LIMIT,
    SUPPORTED_PROTOCOL_VERSION,
    DaemonDiagnostics,
    DiagnosticCheck,
    JsonObject,
    ProtocolValidationError,
    require_json_object,
)


def parse_daemon_diagnostics(value: Mapping[str, object] | str) -> DaemonDiagnostics:
    """Parse and redact a diagnostics response from a fake/injected transport."""

    response = _coerce_object(value, label="diagnostics response")
    protocol_version = _require_string(
        response.get("protocol_version"), label="diagnostics protocol_version"
    )
    if protocol_version != SUPPORTED_PROTOCOL_VERSION:
        raise DaemonProtocolError(
            f"unsupported diagnostics protocol: {protocol_version} != {SUPPORTED_PROTOCOL_VERSION}"
        )

    raw_checks = response.get("checks")
    if not isinstance(raw_checks, list):
        raise DaemonProtocolError("diagnostics checks must be a list")
    if len(raw_checks) > DIAGNOSTIC_CHECK_LIMIT:
        raise DaemonProtocolError(
            f"diagnostics checks exceeds limit: {len(raw_checks)} > {DIAGNOSTIC_CHECK_LIMIT}"
        )

    checks: list[DiagnosticCheck] = []
    for index, raw_check in enumerate(raw_checks):
        if not isinstance(raw_check, Mapping):
            raise DaemonProtocolError(f"diagnostics check {index} must be an object")
        checks.append(_parse_check(raw_check, index=index))

    return DaemonDiagnostics(
        protocol_version=protocol_version,
        daemon_version=_require_string(
            response.get("daemon_version"), label="diagnostics daemon_version"
        ),
        live_readiness=_require_bool(
            response.get("live_readiness"), label="diagnostics live_readiness"
        ),
        checks=tuple(checks),
    )


def _parse_check(value: Mapping[str, object], *, index: int) -> DiagnosticCheck:
    try:
        check = require_json_object(value, label=f"diagnostics check {index}")
    except ProtocolValidationError as exc:
        raise DaemonProtocolError(str(exc)) from exc

    details: JsonObject | None = None
    raw_details = check.get("details")
    if raw_details is not None:
        if not isinstance(raw_details, Mapping):
            raise DaemonProtocolError(
                f"diagnostics check {index} details must be an object when present"
            )
        try:
            details = require_json_object(raw_details, label=f"diagnostics check {index} details")
        except ProtocolValidationError as exc:
            raise DaemonProtocolError(str(exc)) from exc
        redacted = redact_sensitive(details)
        if not isinstance(redacted, dict):
            raise DaemonProtocolError(f"diagnostics check {index} details redaction failed")
        details = redacted

    error = None
    raw_error = check.get("error")
    if raw_error is not None:
        if not isinstance(raw_error, Mapping):
            raise DaemonProtocolError(
                f"diagnostics check {index} error must be an object when present"
            )
        error = decode_daemon_error(raw_error)

    return DiagnosticCheck(
        name=_require_string(check.get("name"), label=f"diagnostics check {index} name"),
        ok=_require_bool(check.get("ok"), label=f"diagnostics check {index} ok"),
        message=_optional_string(check.get("message"), label=f"diagnostics check {index} message"),
        details=details,
        error=error,
    )


def _coerce_object(value: Mapping[str, object] | str, *, label: str) -> JsonObject:
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as exc:
            raise DaemonProtocolError(f"{label} must be valid JSON") from exc
        if not isinstance(decoded, dict):
            raise DaemonProtocolError(f"{label} JSON root must be an object")
        value = cast(Mapping[str, object], decoded)
    if not isinstance(value, Mapping):
        raise DaemonProtocolError(f"{label} must be an object")
    try:
        return require_json_object(value, label=label)
    except ProtocolValidationError as exc:
        raise DaemonProtocolError(str(exc)) from exc


def _require_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise DaemonProtocolError(f"{label} must be a non-empty string")
    return value


def _optional_string(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, label=label)


def _require_bool(value: object, *, label: str) -> bool:
    if not isinstance(value, bool):
        raise DaemonProtocolError(f"{label} must be a boolean")
    return value


__all__ = ["parse_daemon_diagnostics"]
