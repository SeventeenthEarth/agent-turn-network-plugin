"""Explicit daemon transport boundary.

Only explicit fake/injected or configured Unix-socket transports are provided
here.  There is intentionally no localhost, subprocess, Hermes, Discord, auth,
token, or gateway fallback.
"""

from __future__ import annotations

import json
import os
import socket
import stat
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Final, Protocol, cast

from ..errors import DaemonProtocolError, DaemonTransportError
from ..protocol import SUPPORTED_PROTOCOL_VERSION, JsonObject

_LIVE_OPERATIONS: Final = frozenset(
    {"status.read", "version.read", "stream.tail", "stream.ack", "command.submit"}
)
_MAX_SOCKET_RESPONSE_BYTES: Final = 1024 * 1024
_COMMAND_SUBMIT_IDEMPOTENCY_GUIDANCE: Final = (
    "command.submit cannot be represented as daemon command_id; "
    "live Unix socket transport only supports idempotency_key equal to "
    "payload.command_id or idem-{payload.command_id}"
)


class DaemonTransport(Protocol):
    """Protocol implemented by explicit fake/injected daemon transports."""

    def request(self, operation: str, body: JsonObject | None = None) -> JsonObject:
        """Return a JSON object response for a daemon operation."""


class StaticDaemonTransport:
    """Deterministic fake transport for unit/integration tests.

    Responses may be static JSON objects or callables that inspect the request.
    The class records every request so tests can prove no hidden fallback was
    attempted.
    """

    def __init__(
        self,
        responses: dict[str, JsonObject | Callable[[JsonObject | None], JsonObject]],
        *,
        label: str = "fake-daemon",
    ) -> None:
        self.responses = dict(responses)
        self.label = label
        self.requests: list[tuple[str, JsonObject | None]] = []

    def request(self, operation: str, body: JsonObject | None = None) -> JsonObject:
        self.requests.append((operation, body))
        response = self.responses.get(operation)
        if response is None:
            raise DaemonTransportError(f"fake daemon has no response for operation: {operation}")
        if callable(response):
            return response(body)
        return deepcopy(response)


class UnixSocketDaemonTransport:
    """Explicit AF_UNIX transport for narrow live daemon mappings."""

    def __init__(self, socket_path: str, *, timeout: float = 2.0) -> None:
        self.socket_path = _validated_unix_socket_path(socket_path)
        self.timeout = _validated_timeout(timeout)

    def request(self, operation: str, body: JsonObject | None = None) -> JsonObject:
        if operation not in _LIVE_OPERATIONS:
            raise DaemonTransportError(
                "explicit Unix socket live transport supports status.read, version.read, "
                "stream.tail, stream.ack, and command.submit only"
            )
        payload = _live_request_payload(operation, body)
        wire = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(self.timeout)
                client.connect(self.socket_path)
                client.sendall(wire)
                response = _read_json_line(client, operation=operation)
        except DaemonProtocolError:
            raise
        except OSError as exc:
            raise DaemonTransportError(
                f"Unix socket daemon request failed for {operation}: {exc.strerror or exc}"
            ) from exc
        if not isinstance(response, dict):
            raise DaemonProtocolError(f"daemon response must be an object: {operation}")
        if response.get("ok") is not True:
            error = response.get("error")
            if operation == "command.submit" and isinstance(error, dict):
                return {"ok": False, "error": cast(JsonObject, error)}
            if isinstance(error, dict):
                message = error.get("message")
                code = error.get("code")
                if isinstance(message, str) and message:
                    raise DaemonTransportError(message)
                if isinstance(code, str) and code:
                    raise DaemonTransportError(code)
            raise DaemonProtocolError(f"daemon response was not ok: {operation}")
        result = response.get("result")
        if not isinstance(result, dict):
            raise DaemonProtocolError(f"daemon response result must be an object: {operation}")
        return _normalize_live_result(operation, body, cast(JsonObject, result))


def _live_request_payload(operation: str, body: JsonObject | None) -> JsonObject:
    if operation == "stream.tail":
        params = _stream_replay_params(_require_body(body, operation=operation))
        return {
            "schema_version": 1,
            "request_id": "plugin-live-stream-tail",
            "command": "stream.replay",
            "params": params,
        }
    if operation == "stream.ack":
        return {
            "schema_version": 1,
            "request_id": "plugin-live-stream-ack",
            "command": "stream.ack",
            "params": _stream_ack_params(_require_body(body, operation=operation)),
        }
    if operation == "command.submit":
        envelope = _require_body(body, operation=operation)
        command = _require_string(envelope.get("command"), label="command")
        request_id = _require_string(envelope.get("request_id"), label="request_id")
        payload = _require_mapping(envelope.get("payload"), label="payload")
        command_id = _command_id_for_daemon(payload)
        idempotency_key = _require_string(envelope.get("idempotency_key"), label="idempotency_key")
        if idempotency_key not in {command_id, f"idem-{command_id}"}:
            raise DaemonTransportError(_COMMAND_SUBMIT_IDEMPOTENCY_GUIDANCE)
        return {
            "schema_version": 1,
            "request_id": request_id,
            "command": command,
            "params": payload,
        }

    request_payload: JsonObject = {
        "schema_version": 1,
        "request_id": f"plugin-live-{operation.replace('.', '-')}",
        "command": operation,
    }
    if body:
        request_payload["params"] = body
    return request_payload


def _stream_replay_params(body: JsonObject) -> JsonObject:
    params: JsonObject = {
        "session_id": _require_string(body.get("session_id"), label="session_id"),
        "member": _require_string(body.get("member"), label="member"),
    }
    since_cursor = body.get("since_cursor")
    if since_cursor is not None:
        params["since"] = _require_string(since_cursor, label="since_cursor")
    else:
        params["from_start"] = True
    return params


def _stream_ack_params(body: JsonObject) -> JsonObject:
    return {
        "session_id": _require_string(body.get("session_id"), label="session_id"),
        "member": _require_string(body.get("member"), label="member"),
        "cursor": _require_string(body.get("cursor"), label="cursor"),
        "command_id": _require_string(body.get("command_id"), label="command_id"),
    }


def _normalize_live_result(
    operation: str, body: JsonObject | None, result: JsonObject
) -> JsonObject:
    if operation == "stream.tail":
        return _normalize_stream_tail_result(_require_body(body, operation=operation), result)
    if operation == "stream.ack":
        return _normalize_stream_ack_result(_require_body(body, operation=operation), result)
    if operation == "command.submit":
        return _normalize_command_submit_result(_require_body(body, operation=operation), result)
    return result


def _normalize_stream_tail_result(body: JsonObject, result: JsonObject) -> JsonObject:
    raw_frames = result.get("frames")
    if not isinstance(raw_frames, list):
        raise DaemonProtocolError("daemon stream.replay result frames must be a list")
    limit = _require_int(body.get("limit"), label="stream tail limit")
    frames = raw_frames[-limit:]
    normalized = dict(result)
    normalized["protocol_version"] = SUPPORTED_PROTOCOL_VERSION
    normalized["frames"] = frames
    if "next_cursor" not in normalized:
        next_cursor = _last_frame_cursor(frames)
        if next_cursor is not None:
            normalized["next_cursor"] = next_cursor
    return normalized


def _normalize_command_submit_result(envelope: JsonObject, result: JsonObject) -> JsonObject:
    if result.get("ok") is False:
        return result
    payload = _require_mapping(envelope.get("payload"), label="payload")
    command_id = _command_id_for_daemon(payload)
    return {
        "ok": True,
        "command_id": command_id,
        "event_id": _optional_string(result.get("event_id")),
        "session_id": _optional_string(result.get("session_id"))
        or _optional_string(payload.get("session_id")),
        "request_id": _optional_string(result.get("request_id"))
        or _require_string(envelope.get("request_id"), label="request_id"),
    }


def _normalize_stream_ack_result(body: JsonObject, result: JsonObject) -> JsonObject:
    normalized: JsonObject = {
        "ok": True,
        "command_id": _optional_string(result.get("command_id"))
        or _require_string(body.get("command_id"), label="command_id"),
        "event_id": _optional_string(result.get("event_id")),
        "session_id": _optional_string(result.get("session_id"))
        or _require_string(body.get("session_id"), label="session_id"),
        "request_id": _optional_string(result.get("request_id")) or "plugin-live-stream-ack",
    }
    deduplicated = result.get("deduplicated")
    if deduplicated is not None:
        if not isinstance(deduplicated, bool):
            raise DaemonProtocolError("daemon stream.ack result deduplicated must be a boolean")
        normalized["deduplicated"] = deduplicated
    return normalized


def _last_frame_cursor(frames: Sequence[object]) -> str | None:
    if not frames:
        return None
    frame = frames[-1]
    if isinstance(frame, str):
        try:
            decoded = json.loads(frame)
        except json.JSONDecodeError:
            return None
        frame = decoded
    if not isinstance(frame, Mapping):
        return None
    cursor = frame.get("cursor")
    if isinstance(cursor, str) and cursor:
        return cursor
    return None


def _require_body(body: JsonObject | None, *, operation: str) -> JsonObject:
    if not isinstance(body, dict):
        raise DaemonProtocolError(f"daemon request body must be an object: {operation}")
    return body


def _require_mapping(value: object, *, label: str) -> JsonObject:
    if not isinstance(value, dict):
        raise DaemonProtocolError(f"daemon {label} must be an object")
    return cast(JsonObject, value)


def _require_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise DaemonProtocolError(f"daemon {label} must be a non-empty string")
    return value


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and value:
        return value
    return None


def _require_int(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DaemonProtocolError(f"daemon {label} must be an integer")
    return value


def _command_id_for_daemon(payload: JsonObject) -> str:
    try:
        return _require_string(payload.get("command_id"), label="payload command_id")
    except DaemonProtocolError as exc:
        raise DaemonTransportError(_COMMAND_SUBMIT_IDEMPOTENCY_GUIDANCE) from exc


def _validated_unix_socket_path(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise DaemonTransportError(
            "live_transport.unix_socket_path must be a non-empty absolute Unix socket path"
        )
    lowered = value.lower()
    if value.startswith("~"):
        raise DaemonTransportError("live_transport.unix_socket_path must not use ~ expansion")
    if (
        "://" in value
        or lowered.startswith(("http:", "https:", "tcp:", "unix:", "ws:", "wss:"))
        or lowered.startswith(("localhost:", "127.0.0.1:", "[::1]:", "::1:"))
    ):
        raise DaemonTransportError(
            "live_transport.unix_socket_path must be an absolute Unix socket path, "
            "not a URL/TCP endpoint"
        )
    if not Path(value).is_absolute():
        raise DaemonTransportError("live_transport.unix_socket_path must be absolute")
    try:
        mode = os.lstat(value).st_mode
    except FileNotFoundError as exc:
        raise DaemonTransportError(
            f"live_transport.unix_socket_path does not exist: {value}"
        ) from exc
    except PermissionError as exc:
        raise DaemonTransportError(
            f"live_transport.unix_socket_path permission denied: {value}"
        ) from exc
    if stat.S_ISLNK(mode):
        raise DaemonTransportError(
            f"live_transport.unix_socket_path must not be a symlink: {value}"
        )
    if not stat.S_ISSOCK(mode):
        raise DaemonTransportError(f"live_transport.unix_socket_path is not a Unix socket: {value}")
    return value


def _validated_timeout(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise DaemonTransportError("Unix socket timeout must be numeric")
    timeout = float(value)
    if timeout <= 0 or timeout > 30:
        raise DaemonTransportError("Unix socket timeout must be greater than 0 and at most 30")
    return timeout


def _read_json_line(client: socket.socket, *, operation: str) -> object:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = client.recv(4096)
        if chunk == b"":
            break
        newline_index = chunk.find(b"\n")
        if newline_index >= 0:
            chunks.append(chunk[:newline_index])
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > _MAX_SOCKET_RESPONSE_BYTES:
            raise DaemonProtocolError(f"daemon response exceeded size limit: {operation}")
    raw = b"".join(chunks)
    if not raw:
        raise DaemonProtocolError(f"daemon response was empty: {operation}")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DaemonProtocolError(f"daemon response was not valid JSON: {operation}") from exc


__all__ = ["DaemonTransport", "StaticDaemonTransport", "UnixSocketDaemonTransport"]
