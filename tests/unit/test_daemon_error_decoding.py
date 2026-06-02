from __future__ import annotations

import pytest

from kkachi_agent_network_plugin.errors import (
    DaemonProtocolError,
    decode_daemon_error,
    redact_sensitive,
)


def test_daemon_error_decoding_preserves_ids_and_redacts_sensitive_values() -> None:
    details = decode_daemon_error(
        {
            "category": "validation",
            "message": "bad request with Bearer abc.def",
            "command_id": "cmd-1",
            "event_id": "evt-1",
            "session_id": "sess-1",
            "request_id": "req-1",
            "retryable": False,
            "diagnostics": {
                "safe": "kept",
                "auth_token": "secret-token",
                "nested": {"gatewaySecret": "do-not-show"},
                "line": "Hermes token=abc123 appeared",
            },
        }
    )

    assert details.category == "validation"
    assert details.command_id == "cmd-1"
    assert details.event_id == "evt-1"
    assert details.session_id == "sess-1"
    assert details.request_id == "req-1"
    assert "abc.def" not in details.message
    assert details.diagnostics == {
        "safe": "kept",
        "auth_token": "[REDACTED]",
        "nested": {"gatewaySecret": "[REDACTED]"},
        "line": "[REDACTED] appeared",
    }


@pytest.mark.parametrize(
    "error",
    [
        {"message": "missing category"},
        {"category": "new-category", "message": "unknown"},
        {"category": "validation"},
        {"category": "validation", "message": "bad", "retryable": "yes"},
        {"category": "validation", "message": "bad", "diagnostics": ["not-object"]},
        {"category": "validation", "message": "bad", "command_id": ""},
    ],
)
def test_malformed_daemon_errors_fail_closed(error: dict[str, object]) -> None:
    with pytest.raises(DaemonProtocolError):
        decode_daemon_error(error)


def test_redact_sensitive_recurses_without_changing_safe_values() -> None:
    assert redact_sensitive({"ok": [1, "safe"], "password": "pw", "text": "Bearer raw-token"}) == {
        "ok": [1, "safe"],
        "password": "[REDACTED]",
        "text": "[REDACTED]",
    }
