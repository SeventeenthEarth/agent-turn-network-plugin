"""Explicit-transport daemon client surfaces."""

from __future__ import annotations

from .daemon import DaemonClient
from .diagnostics import parse_daemon_diagnostics
from .live import configured_live_client_factory, live_client_factory_from_config
from .stream import parse_stream_frame, parse_stream_frames_ndjson, parse_stream_tail_response
from .transport import DaemonTransport, StaticDaemonTransport, UnixSocketDaemonTransport

__all__ = [
    "DaemonClient",
    "DaemonTransport",
    "StaticDaemonTransport",
    "UnixSocketDaemonTransport",
    "configured_live_client_factory",
    "live_client_factory_from_config",
    "parse_daemon_diagnostics",
    "parse_stream_frame",
    "parse_stream_frames_ndjson",
    "parse_stream_tail_response",
]
