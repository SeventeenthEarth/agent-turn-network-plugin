from __future__ import annotations

from kkachi_agent_network_plugin import schemas


def test_hplug1_schemas_expose_only_authorized_readonly_tools() -> None:
    assert schemas.tool_names() == ("kan_daemon_status", "kan_compatibility_diagnostics")
    assert [schema["name"] for schema in schemas.KAN_TOOL_SCHEMAS] == list(schemas.tool_names())


def test_daemon_status_schema_has_no_arguments_and_no_write_claims() -> None:
    schema = schemas.KAN_DAEMON_STATUS

    assert schema["name"] == "kan_daemon_status"
    assert "read-only" in str(schema["description"]).lower()
    assert "command.submit" not in str(schema["description"]).lower()
    assert schema["parameters"] == {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }


def test_compatibility_diagnostics_schema_accepts_optional_session_id_only() -> None:
    schema = schemas.KAN_COMPATIBILITY_DIAGNOSTICS

    assert schema["name"] == "kan_compatibility_diagnostics"
    assert "diagnostics" in str(schema["description"]).lower()
    assert schema["parameters"] == {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "minLength": 1,
                "description": "Optional KAN session identifier for scoped diagnostics.",
            }
        },
        "additionalProperties": False,
    }


def test_hplug1_does_not_expose_deferred_session_status_schema() -> None:
    assert "kan_session_status" not in schemas.tool_names()
