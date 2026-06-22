from __future__ import annotations

import json
from copy import deepcopy
from typing import cast

import pytest

from hermes_unified_network_plugin.client.diagnostics import parse_daemon_diagnostics
from hermes_unified_network_plugin.errors import DaemonErrorDetails, DaemonProtocolError
from hermes_unified_network_plugin.protocol import DIAGNOSTIC_CHECK_LIMIT, JsonObject


def valid_diagnostics() -> JsonObject:
    return {
        "protocol_version": "hun-protocol-v1alpha0",
        "daemon_version": "0.0.0-fake",
        "live_readiness": False,
        "checks": [
            {
                "name": "stream_frame",
                "ok": True,
                "message": "fake fixture supports stream_frame",
                "details": {
                    "feature_groups": [
                        "version.read",
                        "command_envelope",
                        "stream_frame",
                        "structured_error",
                    ],
                    "discord_token": "do-not-leak",
                },
            },
            {
                "name": "cursor_gap",
                "ok": False,
                "error": {
                    "category": "unavailable",
                    "message": "Bearer secret-value",
                    "event_id": "evt-gap",
                    "session_id": "sess_1",
                    "retryable": True,
                    "diagnostics": {"gateway_secret": "do-not-leak"},
                },
            },
        ],
    }


def test_diagnostics_response_decodes_checks_and_redacts_details() -> None:
    diagnostics = parse_daemon_diagnostics(valid_diagnostics())

    assert diagnostics.protocol_version == "hun-protocol-v1alpha0"
    assert diagnostics.daemon_version == "0.0.0-fake"
    assert diagnostics.live_readiness is False
    assert len(diagnostics.checks) == 2
    assert diagnostics.checks[0].name == "stream_frame"
    assert diagnostics.checks[0].ok is True
    assert diagnostics.checks[0].details == {
        "feature_groups": [
            "version.read",
            "command_envelope",
            "stream_frame",
            "structured_error",
        ],
        "discord_token": "[REDACTED]",
    }

    error = diagnostics.checks[1].error
    assert isinstance(error, DaemonErrorDetails)
    assert error.category == "unavailable"
    assert error.message == "[REDACTED]"
    assert error.event_id == "evt-gap"
    assert error.diagnostics == {"gateway_secret": "[REDACTED]"}


def test_diagnostics_response_decodes_json_string() -> None:
    diagnostics = parse_daemon_diagnostics(json.dumps(valid_diagnostics()))

    assert diagnostics.checks[0].name == "stream_frame"


@pytest.mark.parametrize(
    "response",
    [
        "{not-json",
        [],
        {
            "protocol_version": "wrong",
            "daemon_version": "0.0.0",
            "live_readiness": False,
            "checks": [],
        },
        {"daemon_version": "0.0.0", "live_readiness": False, "checks": []},
        {"protocol_version": "hun-protocol-v1alpha0", "live_readiness": False, "checks": []},
        {
            "protocol_version": "hun-protocol-v1alpha0",
            "daemon_version": "0.0.0",
            "live_readiness": "false",
            "checks": [],
        },
        {
            "protocol_version": "hun-protocol-v1alpha0",
            "daemon_version": "0.0.0",
            "live_readiness": False,
        },
        {
            "protocol_version": "hun-protocol-v1alpha0",
            "daemon_version": "0.0.0",
            "live_readiness": False,
            "checks": "not-list",
        },
        {
            "protocol_version": "hun-protocol-v1alpha0",
            "daemon_version": "0.0.0",
            "live_readiness": False,
            "checks": ["not-object"],
        },
    ],
)
def test_malformed_diagnostics_roots_fail_closed(response: object) -> None:
    with pytest.raises(DaemonProtocolError):
        parse_daemon_diagnostics(response)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "check",
    [
        {"ok": True},
        {"name": "", "ok": True},
        {"name": "stream_frame", "ok": "yes"},
        {"name": "stream_frame", "ok": True, "message": ""},
        {"name": "stream_frame", "ok": True, "details": ["not-object"]},
        {"name": "stream_frame", "ok": False, "error": ["not-object"]},
        {
            "name": "stream_frame",
            "ok": False,
            "error": {"category": "unknown", "message": "bad"},
        },
    ],
)
def test_malformed_diagnostics_checks_fail_closed(check: JsonObject) -> None:
    response = cast(dict[str, object], valid_diagnostics())
    response["checks"] = [check]

    with pytest.raises(DaemonProtocolError):
        parse_daemon_diagnostics(response)


def test_oversized_diagnostics_checks_array_fails_closed() -> None:
    check: JsonObject = {"name": "stream_frame", "ok": True}
    response = cast(dict[str, object], valid_diagnostics())
    response["checks"] = [deepcopy(check) for _ in range(DIAGNOSTIC_CHECK_LIMIT + 1)]

    with pytest.raises(DaemonProtocolError, match="exceeds limit"):
        parse_daemon_diagnostics(response)
