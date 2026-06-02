"""Explicit-transport daemon client surfaces."""

from __future__ import annotations

from .daemon import DaemonClient
from .diagnostics import parse_daemon_diagnostics
from .stream import parse_stream_frame, parse_stream_frames_ndjson, parse_stream_tail_response
from .transport import DaemonTransport, StaticDaemonTransport

__all__ = [
    "DaemonClient",
    "DaemonTransport",
    "StaticDaemonTransport",
    "parse_daemon_diagnostics",
    "parse_stream_frame",
    "parse_stream_frames_ndjson",
    "parse_stream_tail_response",
]
