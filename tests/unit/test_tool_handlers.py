from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, cast

from kkachi_agent_network_plugin.client import DaemonClient, StaticDaemonTransport
from kkachi_agent_network_plugin.client.daemon import OP_DIAGNOSTICS_READ, OP_STATUS_READ
from kkachi_agent_network_plugin.protocol import JsonObject
from kkachi_agent_network_plugin.tools import (
    handle_compatibility_diagnostics,
    handle_daemon_status,
)

BASE_STATUS: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "status": "fake-ready",
    "feature_groups": ["version_features", "command_envelope", "structured_error"],
    "live_readiness": False,
}
BASE_DIAGNOSTICS: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "live_readiness": False,
    "checks": [
        {
            "name": "structured_error",
            "ok": True,
            "details": {"gateway_token": "do-not-leak"},
        }
    ],
}


def factory_for(responses: dict[str, JsonObject]) -> Callable[[], DaemonClient]:
    typed_responses = cast(
        dict[str, JsonObject | Callable[[JsonObject | None], JsonObject]],
        responses,
    )
    return lambda: DaemonClient(StaticDaemonTransport(typed_responses))


def decode(payload: str) -> dict[str, Any]:
    decoded = json.loads(payload)
    assert isinstance(decoded, dict)
    return decoded


def test_daemon_status_handler_returns_json_success_from_explicit_fake_client() -> None:
    result = decode(
        handle_daemon_status({}, client_factory=factory_for({OP_STATUS_READ: BASE_STATUS}))
    )

    assert result == {
        "ok": True,
        "tool": "kan_daemon_status",
        "protocol_version": "kan-protocol-v1alpha0",
        "live_readiness": False,
        "data": {
            "daemon_version": "0.0.0-fake",
            "status": "fake-ready",
            "feature_groups": ["version_features", "command_envelope", "structured_error"],
        },
    }


def test_compatibility_diagnostics_handler_returns_redacted_json_success() -> None:
    result = decode(
        handle_compatibility_diagnostics(
            {"session_id": "sess-1"},
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )

    assert result == {
        "ok": True,
        "tool": "kan_compatibility_diagnostics",
        "protocol_version": "kan-protocol-v1alpha0",
        "live_readiness": False,
        "data": {
            "daemon_version": "0.0.0-fake",
            "checks": [
                {
                    "name": "structured_error",
                    "ok": True,
                    "message": None,
                    "details": {"gateway_token": "[REDACTED]"},
                    "error": None,
                }
            ],
        },
    }


def test_handlers_fail_closed_without_client_factory() -> None:
    status = decode(handle_daemon_status({}))
    diagnostics = decode(handle_compatibility_diagnostics({}))

    assert status["ok"] is False
    assert status["tool"] == "kan_daemon_status"
    assert status["error"]["category"] == "unavailable"
    assert "client factory" in status["error"]["message"]
    assert diagnostics["ok"] is False
    assert diagnostics["error"]["category"] == "unavailable"


def test_diagnostics_handler_rejects_invalid_session_id_before_transport() -> None:
    result = decode(
        handle_compatibility_diagnostics(
            {"session_id": ""},
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "session_id must be a non-empty string when present",
        "retryable": False,
    }


def test_handlers_reject_non_object_args_without_raising() -> None:
    status = decode(
        handle_daemon_status(
            [],
            client_factory=factory_for({OP_STATUS_READ: BASE_STATUS}),
        )
    )
    diagnostics = decode(
        handle_compatibility_diagnostics(
            [],
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )

    assert status["ok"] is False
    assert status["error"]["category"] == "validation"
    assert diagnostics["ok"] is False
    assert diagnostics["error"]["category"] == "validation"


def test_handlers_reject_unknown_args_before_transport() -> None:
    status = decode(
        handle_daemon_status(
            {"unexpected": "x"},
            client_factory=factory_for({OP_STATUS_READ: BASE_STATUS}),
        )
    )
    diagnostics = decode(
        handle_compatibility_diagnostics(
            {"unexpected": "x"},
            client_factory=factory_for({OP_DIAGNOSTICS_READ: BASE_DIAGNOSTICS}),
        )
    )

    assert status["ok"] is False
    assert status["error"] == {
        "category": "validation",
        "message": "unsupported tool args: unexpected",
        "retryable": False,
    }
    assert diagnostics["ok"] is False
    assert diagnostics["error"] == {
        "category": "validation",
        "message": "unsupported tool args: unexpected",
        "retryable": False,
    }


def test_handler_malformed_daemon_payload_fails_closed_as_protocol_error() -> None:
    result = decode(
        handle_daemon_status(
            {},
            client_factory=factory_for({OP_STATUS_READ: {"protocol_version": "wrong"}}),
        )
    )

    assert result["ok"] is False
    assert result["error"]["category"] == "compatibility"
    assert result["live_readiness"] is False
