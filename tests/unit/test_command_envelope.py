from __future__ import annotations

import json
import math

import pytest

from atn_plugin.client import DaemonClient, StaticDaemonTransport
from atn_plugin.protocol import (
    COMMAND_ENVELOPE_VERSION,
    SUPPORTED_PROTOCOL_VERSION,
    CommandEnvelope,
    ProtocolValidationError,
)


def test_command_envelope_serialization_is_canonical_and_idempotency_ready() -> None:
    envelope = CommandEnvelope(
        command="session.note",
        payload={"z": 2, "a": {"nested": True}},
        request_id="req-001",
        idempotency_key="idem-001",
    )

    assert envelope.to_mapping() == {
        "protocol_version": SUPPORTED_PROTOCOL_VERSION,
        "envelope_version": COMMAND_ENVELOPE_VERSION,
        "command": "session.note",
        "payload": {"a": {"nested": True}, "z": 2},
        "request_id": "req-001",
        "idempotency_key": "idem-001",
        "client_metadata": {
            "name": "atn-plugin",
            "version": "0.1.0",
            "transport": "injected",
        },
    }
    assert envelope.canonical_json() == (
        '{"client_metadata":{"name":"atn-plugin","transport":"injected",'
        '"version":"0.1.0"},"command":"session.note",'
        '"envelope_version":"kan-command-envelope-v1alpha0","idempotency_key":"idem-001",'
        '"payload":{"a":{"nested":true},"z":2},'
        '"protocol_version":"atn-protocol-v1alpha0","request_id":"req-001"}'
    )
    assert json.loads(envelope.canonical_json())["payload"] == {"a": {"nested": True}, "z": 2}


def test_client_build_command_envelope_requires_explicit_ids() -> None:
    client = DaemonClient(StaticDaemonTransport({}))

    envelope = client.build_command_envelope(
        command="session.note",
        payload={},
        request_id="req-002",
        idempotency_key="idem-002",
    )

    assert envelope.request_id == "req-002"
    assert envelope.idempotency_key == "idem-002"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"command": "", "payload": {}, "request_id": "req", "idempotency_key": "idem"}, "command"),
        (
            {"command": "x", "payload": {}, "request_id": "", "idempotency_key": "idem"},
            "request id",
        ),
        (
            {"command": "x", "payload": {}, "request_id": "req", "idempotency_key": ""},
            "idempotency key",
        ),
        (
            {
                "command": "x",
                "payload": {"bad": object()},
                "request_id": "req",
                "idempotency_key": "idem",
            },
            "payload",
        ),
        (
            {
                "command": "x",
                "payload": {1: "coerces"},
                "request_id": "req",
                "idempotency_key": "idem",
            },
            "payload keys",
        ),
        (
            {
                "command": "x",
                "payload": {"bad": math.nan},
                "request_id": "req",
                "idempotency_key": "idem",
            },
            "payload floats",
        ),
    ],
)
def test_command_envelope_fails_closed_for_malformed_local_data(
    kwargs: dict[str, object], message: str
) -> None:
    envelope = CommandEnvelope(**kwargs)  # type: ignore[arg-type]

    with pytest.raises(ProtocolValidationError, match=message):
        envelope.to_mapping()
