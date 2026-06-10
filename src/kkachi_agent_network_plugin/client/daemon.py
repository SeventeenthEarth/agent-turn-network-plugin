"""Import-safe daemon client foundation for explicit fake/injected transports."""

from __future__ import annotations

from collections.abc import Mapping

from ..errors import (
    DaemonCommandError,
    DaemonCompatibilityError,
    DaemonProtocolError,
    DaemonTransportError,
    decode_daemon_error,
)
from ..protocol import (
    REQUIRED_FEATURE_GROUPS,
    STREAM_REQUIRED_FEATURE_GROUPS,
    STREAM_TAIL_FRAME_LIMIT,
    SUPPORTED_PROTOCOL_VERSION,
    ClientMetadata,
    CommandEnvelope,
    CommandResult,
    DaemonDiagnostics,
    DaemonStatus,
    DaemonVersion,
    JsonObject,
    StreamTail,
)
from .diagnostics import parse_daemon_diagnostics
from .stream import parse_stream_tail_response
from .transport import DaemonTransport

OP_STATUS_READ = "status.read"
OP_VERSION_READ = "version.read"
OP_COMMAND_SUBMIT = "command.submit"
OP_STREAM_TAIL = "stream.tail"
OP_DIAGNOSTICS_READ = "diagnostics.read"


class DaemonClient:
    """Small daemon client that requires an explicit injected transport."""

    def __init__(self, transport: DaemonTransport | None = None) -> None:
        if transport is None:
            raise DaemonTransportError(
                "explicit daemon transport is required; "
                "no live localhost/CLI/Hermes/Discord fallback"
            )
        self._transport = transport

    def read_version(self) -> DaemonVersion:
        response = self._request(OP_VERSION_READ, _protocol_probe_body())
        return _parse_version(response)

    def require_feature_groups(self, required_feature_groups: tuple[str, ...]) -> DaemonVersion:
        """Probe injected `version.read` and fail closed unless features exist."""

        response = self._request(OP_VERSION_READ, _protocol_probe_body())
        return _parse_version(response, required_feature_groups=required_feature_groups)

    def read_status(self) -> DaemonStatus:
        response = self._request(OP_STATUS_READ, _protocol_probe_body())
        return _parse_status(response)

    def read_stream_tail(
        self,
        *,
        session_id: str,
        member: str,
        since_cursor: str | None = None,
        limit: int = 100,
    ) -> StreamTail:
        """Read stream tail frames through an explicit transport only.

        Stream reads require a positive `stream_frame` feature-group probe
        before the stream operation is attempted.
        """

        self.require_feature_groups(STREAM_REQUIRED_FEATURE_GROUPS)
        body: JsonObject = {
            "protocol_version": SUPPORTED_PROTOCOL_VERSION,
            "session_id": _require_string(session_id, label="session_id"),
            "member": _require_string(member, label="member"),
            "limit": _require_stream_limit(limit),
        }
        if since_cursor is not None:
            body["since_cursor"] = _require_string(since_cursor, label="since_cursor")
        response = self._request(OP_STREAM_TAIL, body)
        return parse_stream_tail_response(response)

    def read_diagnostics(self, *, session_id: str | None = None) -> DaemonDiagnostics:
        body: JsonObject = {"protocol_version": SUPPORTED_PROTOCOL_VERSION}
        if session_id is not None:
            body["session_id"] = _require_string(session_id, label="session_id")
        response = self._request(OP_DIAGNOSTICS_READ, body)
        return parse_daemon_diagnostics(response)

    def build_command_envelope(
        self,
        *,
        command: str,
        payload: Mapping[str, object],
        request_id: str,
        idempotency_key: str,
    ) -> CommandEnvelope:
        return CommandEnvelope(
            command=command,
            payload=payload,
            request_id=request_id,
            idempotency_key=idempotency_key,
            client_metadata=ClientMetadata(transport="injected"),
        )

    def submit_command(self, envelope: CommandEnvelope) -> CommandResult:
        response = self._request(OP_COMMAND_SUBMIT, envelope.to_mapping())
        return _parse_command_response(response)

    def _request(self, operation: str, body: JsonObject | None = None) -> JsonObject:
        try:
            response = self._transport.request(operation, body)
        except (DaemonProtocolError, DaemonTransportError):
            raise
        except Exception as exc:
            raise DaemonTransportError(f"injected daemon transport failed: {operation}") from exc
        if not isinstance(response, dict):
            raise DaemonProtocolError(f"daemon response must be an object: {operation}")
        return response


def _protocol_probe_body() -> JsonObject:
    return {"protocol_version": SUPPORTED_PROTOCOL_VERSION}


def _require_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise DaemonProtocolError(f"daemon {label} must be a non-empty string")
    return value


def _optional_string(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, label=label)


def _require_bool(value: object, *, label: str) -> bool:
    if not isinstance(value, bool):
        raise DaemonProtocolError(f"daemon {label} must be a boolean")
    return value


def _feature_groups(
    value: object,
    *,
    required_feature_groups: tuple[str, ...] = REQUIRED_FEATURE_GROUPS,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise DaemonProtocolError("daemon feature_groups must be a list")
    groups: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise DaemonProtocolError("daemon feature_groups entries must be non-empty strings")
        groups.append(item)
    missing = sorted(set(required_feature_groups).difference(groups))
    if missing:
        raise DaemonCompatibilityError(f"daemon missing required feature groups: {missing}")
    return tuple(groups)


def _require_supported_protocol(response: Mapping[str, object]) -> str:
    protocol_version = _require_string(response.get("protocol_version"), label="protocol_version")
    if protocol_version != SUPPORTED_PROTOCOL_VERSION:
        raise DaemonCompatibilityError(
            f"unsupported daemon protocol: {protocol_version} != {SUPPORTED_PROTOCOL_VERSION}"
        )
    return protocol_version


def _parse_version(
    response: Mapping[str, object],
    *,
    required_feature_groups: tuple[str, ...] = REQUIRED_FEATURE_GROUPS,
) -> DaemonVersion:
    protocol_version = _require_supported_protocol(response)
    return DaemonVersion(
        protocol_version=protocol_version,
        daemon_version=_require_string(response.get("daemon_version"), label="daemon_version"),
        feature_groups=_feature_groups(
            response.get("feature_groups"), required_feature_groups=required_feature_groups
        ),
        live_readiness=_live_readiness(response),
    )


def _parse_status(response: Mapping[str, object]) -> DaemonStatus:
    protocol_version = _require_supported_protocol(response)
    return DaemonStatus(
        protocol_version=protocol_version,
        daemon_version=_require_string(response.get("daemon_version"), label="daemon_version"),
        status=_status_label(response),
        feature_groups=_feature_groups(response.get("feature_groups")),
        live_readiness=_live_readiness(response),
    )


def _live_readiness(response: Mapping[str, object]) -> bool:
    value = response.get("live_readiness")
    if value is None:
        return False
    return _require_bool(value, label="live_readiness")


def _status_label(response: Mapping[str, object]) -> str:
    status = response.get("status")
    if status is not None:
        return _require_string(status, label="status")
    return _require_string(response.get("daemon"), label="daemon")


def _parse_command_response(response: Mapping[str, object]) -> CommandResult:
    ok = response.get("ok")
    if ok is False:
        error = response.get("error")
        if not isinstance(error, Mapping):
            raise DaemonProtocolError("daemon command failure missing structured error object")
        raise DaemonCommandError(decode_daemon_error(error))
    if ok is not True:
        raise DaemonProtocolError("daemon command response ok must be true or false")

    return CommandResult(
        command_id=_require_string(response.get("command_id"), label="command_id"),
        event_id=_optional_string(response.get("event_id"), label="event_id"),
        session_id=_optional_string(response.get("session_id"), label="session_id"),
        request_id=_optional_string(response.get("request_id"), label="request_id"),
    )


def _require_stream_limit(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DaemonProtocolError("stream tail limit must be an integer")
    if value < 1 or value > STREAM_TAIL_FRAME_LIMIT:
        raise DaemonProtocolError(
            f"stream tail limit must be between 1 and {STREAM_TAIL_FRAME_LIMIT}"
        )
    return value


__all__ = [
    "DaemonClient",
    "OP_COMMAND_SUBMIT",
    "OP_DIAGNOSTICS_READ",
    "OP_STATUS_READ",
    "OP_STREAM_TAIL",
    "OP_VERSION_READ",
]
