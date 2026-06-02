from __future__ import annotations

import pytest

from kkachi_agent_network_plugin.client import DaemonClient, StaticDaemonTransport
from kkachi_agent_network_plugin.client.daemon import OP_STATUS_READ, OP_VERSION_READ
from kkachi_agent_network_plugin.errors import (
    DaemonCompatibilityError,
    DaemonProtocolError,
    DaemonTransportError,
)

BASE_RESPONSE = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": ["version_features", "command_envelope", "structured_error"],
    "live_readiness": False,
}


def test_client_requires_explicit_transport_and_has_no_live_fallback() -> None:
    with pytest.raises(DaemonTransportError, match="explicit daemon transport is required"):
        DaemonClient()


def test_status_and_version_reads_use_injected_transport_only() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: dict(BASE_RESPONSE),
            OP_STATUS_READ: {**BASE_RESPONSE, "status": "fake-ready"},
        }
    )
    client = DaemonClient(transport)

    version = client.read_version()
    status = client.read_status()

    assert version.protocol_version == "kan-protocol-v1alpha0"
    assert version.live_readiness is False
    assert status.status == "fake-ready"
    assert status.live_readiness is False
    assert transport.requests == [
        (OP_VERSION_READ, {"protocol_version": "kan-protocol-v1alpha0"}),
        (OP_STATUS_READ, {"protocol_version": "kan-protocol-v1alpha0"}),
    ]


def test_unsupported_protocol_fails_closed() -> None:
    client = DaemonClient(
        StaticDaemonTransport({OP_VERSION_READ: {**BASE_RESPONSE, "protocol_version": "wrong"}})
    )

    with pytest.raises(DaemonCompatibilityError, match="unsupported daemon protocol"):
        client.read_version()


def test_missing_feature_group_fails_closed() -> None:
    client = DaemonClient(
        StaticDaemonTransport(
            {OP_VERSION_READ: {**BASE_RESPONSE, "feature_groups": ["version_features"]}}
        )
    )

    with pytest.raises(DaemonCompatibilityError, match="missing required feature groups"):
        client.read_version()


@pytest.mark.parametrize(
    "response",
    [
        {**BASE_RESPONSE, "daemon_version": ""},
        {**BASE_RESPONSE, "feature_groups": "not-list"},
        {**BASE_RESPONSE, "feature_groups": [""]},
        {**BASE_RESPONSE, "live_readiness": "false"},
    ],
)
def test_malformed_version_data_fails_closed(response: object) -> None:
    client = DaemonClient(StaticDaemonTransport({OP_VERSION_READ: response}))  # type: ignore[arg-type]

    with pytest.raises(DaemonProtocolError):
        client.read_version()


class NonObjectTransport:
    def request(self, operation: str, body: dict[str, object] | None = None) -> list[str]:
        _ = (operation, body)
        return ["not-object"]


def test_non_object_transport_response_fails_closed() -> None:
    client = DaemonClient(NonObjectTransport())  # type: ignore[arg-type]

    with pytest.raises(DaemonProtocolError):
        client.read_version()
