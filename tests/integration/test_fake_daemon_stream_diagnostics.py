from __future__ import annotations

import pytest

from hermes_unified_network_plugin.client import DaemonClient, StaticDaemonTransport
from hermes_unified_network_plugin.client.daemon import (
    OP_DIAGNOSTICS_READ,
    OP_STREAM_TAIL,
    OP_VERSION_READ,
)
from hermes_unified_network_plugin.errors import DaemonCompatibilityError, DaemonProtocolError
from hermes_unified_network_plugin.protocol import JsonObject

BASE_VERSION_WITH_STREAM: JsonObject = {
    "protocol_version": "hun-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": [
        "version.read",
        "command_envelope",
        "stream_frame",
        "structured_error",
    ],
    "live_readiness": False,
}


def frame(cursor: str, *, is_replay: bool = False) -> JsonObject:
    return {
        "cursor": cursor,
        "is_replay": is_replay,
        "event": {
            "schema_version": 1,
            "event_id": f"evt_{cursor[-1]}",
            "session_id": "sess-int-2",
            "type": "task_assigned",
            "from": "agent-mod",
            "to": ["agent-1"],
            "payload": {"task": "fixture-only"},
        },
    }


def test_fake_daemon_stream_tail_requires_positive_stream_frame_feature_and_parses() -> None:
    def stream_tail(body: JsonObject | None) -> JsonObject:
        assert body == {
            "protocol_version": "hun-protocol-v1alpha0",
            "session_id": "sess-int-2",
            "member": "agent-1",
            "limit": 2,
            "since_cursor": "cur_0",
        }
        return {
            "protocol_version": "hun-protocol-v1alpha0",
            "frames": [frame("cur_1", is_replay=True), frame("cur_2")],
            "next_cursor": "cur_2",
        }

    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_STREAM,
            OP_STREAM_TAIL: stream_tail,
        }
    )
    client = DaemonClient(transport)

    tail = client.read_stream_tail(
        session_id="sess-int-2", member="agent-1", since_cursor="cur_0", limit=2
    )

    assert [stream_frame.cursor for stream_frame in tail.frames] == ["cur_1", "cur_2"]
    assert tail.frames[0].is_replay is True
    assert tail.frames[1].event.payload == {"task": "fixture-only"}
    assert tail.next_cursor == "cur_2"
    assert transport.requests == [
        (OP_VERSION_READ, {"protocol_version": "hun-protocol-v1alpha0"}),
        (
            OP_STREAM_TAIL,
            {
                "protocol_version": "hun-protocol-v1alpha0",
                "session_id": "sess-int-2",
                "member": "agent-1",
                "limit": 2,
                "since_cursor": "cur_0",
            },
        ),
    ]


def test_fake_daemon_stream_tail_missing_stream_frame_feature_fails_before_stream_read() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: {
                **BASE_VERSION_WITH_STREAM,
                "feature_groups": ["version.read", "command_envelope", "structured_error"],
            },
            OP_STREAM_TAIL: {"protocol_version": "hun-protocol-v1alpha0", "frames": []},
        }
    )
    client = DaemonClient(transport)

    with pytest.raises(DaemonCompatibilityError, match="stream_frame"):
        client.read_stream_tail(session_id="sess-int-2", member="agent-1")

    assert transport.requests == [(OP_VERSION_READ, {"protocol_version": "hun-protocol-v1alpha0"})]


def test_fake_daemon_malformed_stream_tail_response_fails_closed() -> None:
    client = DaemonClient(
        StaticDaemonTransport(
            {
                OP_VERSION_READ: BASE_VERSION_WITH_STREAM,
                OP_STREAM_TAIL: {
                    "protocol_version": "hun-protocol-v1alpha0",
                    "frames": [{"cursor": "cur_bad", "is_replay": False}],
                },
            }
        )
    )

    with pytest.raises(DaemonProtocolError):
        client.read_stream_tail(session_id="sess-int-2", member="agent-1")


def test_fake_daemon_diagnostics_decodes_and_redacts() -> None:
    def diagnostics(body: JsonObject | None) -> JsonObject:
        assert body == {"protocol_version": "hun-protocol-v1alpha0", "session_id": "sess-int-2"}
        return {
            "protocol_version": "hun-protocol-v1alpha0",
            "daemon_version": "0.0.0-fake",
            "live_readiness": False,
            "checks": [
                {
                    "name": "stream_frame",
                    "ok": True,
                    "details": {
                        "feature_groups": [
                            "version.read",
                            "command_envelope",
                            "stream_frame",
                            "structured_error",
                        ],
                        "auth_token": "do-not-leak",
                    },
                }
            ],
        }

    transport = StaticDaemonTransport({OP_DIAGNOSTICS_READ: diagnostics})
    client = DaemonClient(transport)

    result = client.read_diagnostics(session_id="sess-int-2")

    assert result.checks[0].name == "stream_frame"
    assert result.checks[0].details == {
        "feature_groups": [
            "version.read",
            "command_envelope",
            "stream_frame",
            "structured_error",
        ],
        "auth_token": "[REDACTED]",
    }
    assert transport.requests == [
        (
            OP_DIAGNOSTICS_READ,
            {"protocol_version": "hun-protocol-v1alpha0", "session_id": "sess-int-2"},
        )
    ]


def test_fake_daemon_malformed_diagnostics_response_fails_closed() -> None:
    client = DaemonClient(
        StaticDaemonTransport(
            {
                OP_DIAGNOSTICS_READ: {
                    "protocol_version": "hun-protocol-v1alpha0",
                    "daemon_version": "0.0.0-fake",
                    "live_readiness": False,
                    "checks": [{"name": "stream_frame", "ok": "yes"}],
                }
            }
        )
    )

    with pytest.raises(DaemonProtocolError):
        client.read_diagnostics()
