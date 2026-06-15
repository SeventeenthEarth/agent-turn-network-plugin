"""Pure visible-surface projection rendering for daemon event data.

This module performs no daemon, Discord, Hermes, environment, network, or CLI
access. It accepts caller-supplied daemon/control projection JSON and returns a
local render projection with evidence pointers preserved as display data only.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Final, cast

from .protocol import JsonObject, JsonValue, require_json_object

SURFACE_PROJECTION_SCHEMA_VERSION: Final = 1
SUPPORTED_EVENT_TYPES: Final[frozenset[str]] = frozenset(
    {
        "session_created",
        "speaker_selected",
        "speech",
        "council_finalized",
        "council_unresolved",
        "session_cancelled",
    }
)
SUPPORTED_DELIVERY_STATUSES: Final[frozenset[str]] = frozenset(
    {"posted", "failed", "pending_followup", "missing", "unproven", "missing/unproven"}
)
CURSOR_ORDER_PATTERN: Final = re.compile(r"^cur_(\d+)(?:_|$)")


def render_surface_projection(projection: Mapping[str, object]) -> JsonObject:
    """Render explicit daemon/control projection data into local surface rows."""

    source = require_json_object(projection, label="projection")
    schema_version = source.get("schema_version")
    if schema_version != SURFACE_PROJECTION_SCHEMA_VERSION:
        raise ValueError("projection.schema_version must be 1")
    session_id = _required_string(source.get("session_id"), label="projection.session_id")
    events = source.get("events")
    if not isinstance(events, list):
        raise ValueError("projection.events must be a JSON array")

    normalized_events = [_normalize_event(item, session_id=session_id) for item in events]
    ordered_events = sorted(normalized_events, key=lambda item: cast(int, item["order"]))
    _validate_cursor_authority(ordered_events)

    rows: list[JsonObject] = []
    floor_grants: dict[tuple[JsonValue, str], JsonObject] = {}
    for item in ordered_events:
        event = cast(JsonObject, item["event"])
        event_type = cast(str, event["type"])
        payload = _mapping_or_empty(event.get("payload"), label=f"{event_type}.payload")
        if event_type == "session_created":
            rows.append(_session_created_row(item=item, payload=payload))
            continue
        if event_type == "speaker_selected":
            grant = _speaker_grant_row(item=item, event=event, payload=payload)
            rows.append(grant)
            floor_grants[(grant["turn"], cast(str, grant["member"]))] = grant
            continue
        if event_type == "speech":
            rows.append(_speech_row(item=item, event=event, payload=payload, grants=floor_grants))
            continue
        if event_type in {"council_finalized", "council_unresolved", "session_cancelled"}:
            rows.extend(_terminal_rows(item=item, payload=payload))

    rows_json: list[JsonValue] = list(rows)
    return {
        "schema_version": SURFACE_PROJECTION_SCHEMA_VERSION,
        "session_id": session_id,
        "order_authority": "daemon_cursor",
        "source_event_count": len(ordered_events),
        "live_readiness": False,
        "rows": rows_json,
    }


def _normalize_event(item: object, *, session_id: str) -> JsonObject:
    if not isinstance(item, Mapping):
        raise ValueError("projection.events items must be JSON objects")
    frame = require_json_object(item, label="projection.events[]")
    event_value = frame.get("event")
    event = _mapping_or_none(event_value, label="projection.events[].event")
    if event is None:
        event = frame
    cursor = _required_string(frame.get("cursor") or event.get("cursor"), label="event.cursor")
    order = _event_order(frame.get("order") if "order" in frame else event.get("order"), cursor)
    event_type = _required_string(event.get("type"), label="event.type")
    if event_type not in SUPPORTED_EVENT_TYPES:
        raise ValueError(f"unsupported event type: {event_type}")
    event_session_id = _required_string(event.get("session_id"), label="event.session_id")
    if event_session_id != session_id:
        raise ValueError("event.session_id must match projection.session_id")
    event_id = _required_string(event.get("event_id"), label="event.event_id")
    return {
        "cursor": cursor,
        "order": order,
        "event_id": event_id,
        "event": event,
    }


def _validate_cursor_authority(events: list[JsonObject]) -> None:
    seen_cursors: set[str] = set()
    seen_orders: set[int] = set()
    previous_order: int | None = None
    for item in events:
        cursor = cast(str, item["cursor"])
        order = cast(int, item["order"])
        if cursor in seen_cursors:
            raise ValueError(f"duplicate daemon cursor: {cursor}")
        if order in seen_orders:
            raise ValueError(f"duplicate daemon cursor order: {order}")
        if previous_order is not None and order <= previous_order:
            raise ValueError("daemon cursor order must be strictly monotonic")
        seen_cursors.add(cursor)
        seen_orders.add(order)
        previous_order = order


def _session_created_row(*, item: JsonObject, payload: Mapping[str, object]) -> JsonObject:
    return _base_row(
        item=item, event_type="session_created", target="session", status="created"
    ) | {
        "evidence": {
            "surface": _json_or_none(payload.get("surface")),
            "linked_authority": _json_or_none(payload.get("linked_authority")),
        }
    }


def _speaker_grant_row(
    *, item: JsonObject, event: Mapping[str, object], payload: Mapping[str, object]
) -> JsonObject:
    turn = _turn_value(payload.get("turn"), label="speaker_selected.payload.turn")
    member = _selected_member(event=event, payload=payload)
    return _base_row(
        item=item, event_type="speaker_selected", target="floor_grant", status="granted"
    ) | {
        "turn": turn,
        "member": member,
        "evidence": {
            "turn": turn,
            "member": member,
            "selection_mode": _json_or_none(payload.get("selection_mode")),
        },
    }


def _speech_row(
    *,
    item: JsonObject,
    event: Mapping[str, object],
    payload: Mapping[str, object],
    grants: Mapping[tuple[JsonValue, str], JsonObject],
) -> JsonObject:
    turn = _turn_value(payload.get("turn"), label="speech.payload.turn")
    speaker = _required_string(event.get("from"), label="speech.from")
    grant = grants.get((turn, speaker))
    if grant is None:
        raise ValueError("floor_grant_missing_or_mismatched")
    speech = payload.get("speech")
    if speech is None:
        speech = payload.get("message")
    content = _required_string(speech, label="speech.payload.speech")
    return _base_row(item=item, event_type="speech", target="speech", status="renderable") | {
        "turn": turn,
        "member": speaker,
        "content": content,
        "evidence": {
            "turn": turn,
            "selected": speaker,
            "speaker": speaker,
            "speaker_selected_event_id": grant["event_id"],
            "speaker_selected_cursor": grant["cursor"],
        },
    }


def _terminal_rows(*, item: JsonObject, payload: Mapping[str, object]) -> list[JsonObject]:
    event = cast(Mapping[str, object], item["event"])
    event_type = cast(str, event["type"])
    rows: list[JsonObject] = []
    status, evidence = _delivery_status(payload.get("surface_evidence"), label="surface_evidence")
    rows.append(
        _base_row(item=item, event_type=event_type, target="visible_surface", status=status)
        | {"evidence": evidence}
    )
    if "linked_authority_result" in payload:
        linked_status, linked_evidence = _delivery_status(
            payload.get("linked_authority_result"), label="linked_authority_result"
        )
        rows.append(
            _base_row(
                item=item,
                event_type=event_type,
                target="linked_authority",
                status=linked_status,
            )
            | {"evidence": linked_evidence}
        )
    return rows


def _delivery_status(value: object, *, label: str) -> tuple[str, JsonObject | None]:
    if value is None:
        return "missing/unproven", None
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object when present")
    payload = require_json_object(value, label=label)
    if not payload:
        raise ValueError(f"{label} must not be an empty proofless object")
    raw_status = _required_string(payload.get("status"), label=f"{label}.status")
    if raw_status not in SUPPORTED_DELIVERY_STATUSES:
        raise ValueError(f"unsupported delivery evidence status: {raw_status}")
    if raw_status in {"missing", "unproven", "missing/unproven"}:
        return "missing/unproven", payload
    _require_pointer_for_status(status=raw_status, payload=payload, label=label)
    return raw_status, payload


def _require_pointer_for_status(
    *, status: str, payload: Mapping[str, JsonValue], label: str
) -> None:
    keys: tuple[str, ...]
    if status == "posted":
        keys = (
            "final_message_id",
            "message_id",
            "message_ref",
            "kanban_comment_id",
            "vault_decision_note",
            "evidence",
        )
    elif status == "failed":
        keys = ("failure_reason", "reason")
    elif status == "pending_followup":
        keys = ("followup_card_id", "pending_review", "handoff", "reason")
    else:  # defensive; caller validates enum first.
        keys = ()
    for key in keys:
        if _is_non_empty_pointer(payload.get(key)):
            return
    raise ValueError(f"{label}.{status} requires a reconstructable non-empty evidence pointer")


def _is_non_empty_pointer(value: JsonValue) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return any(_is_non_empty_pointer(item) for item in value.values())
    if isinstance(value, list):
        return any(_is_non_empty_pointer(item) for item in value)
    return False


def _base_row(*, item: JsonObject, event_type: str, target: str, status: str) -> JsonObject:
    return {
        "cursor": cast(str, item["cursor"]),
        "order": cast(int, item["order"]),
        "event_id": cast(str, item["event_id"]),
        "type": event_type,
        "target": target,
        "status": status,
    }


def _event_order(value: object, cursor: str) -> int:
    if value is not None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("event.order must be a non-negative integer when present")
        return value
    match = CURSOR_ORDER_PATTERN.match(cursor)
    if match is None:
        raise ValueError("event.cursor must be parseable daemon cursor or event.order is required")
    return int(match.group(1))


def _selected_member(*, event: Mapping[str, object], payload: Mapping[str, object]) -> str:
    member = payload.get("member")
    if member is not None:
        return _required_string(member, label="speaker_selected.payload.member")
    recipients = event.get("to")
    if not isinstance(recipients, list) or len(recipients) != 1:
        raise ValueError("speaker_selected.to must select exactly one member")
    return _required_string(recipients[0], label="speaker_selected.to[0]")


def _turn_value(value: object, *, label: str) -> JsonValue:
    if isinstance(value, bool) or not isinstance(value, int | str):
        raise ValueError(f"{label} must be an integer or string")
    if isinstance(value, str) and not value:
        raise ValueError(f"{label} must be non-empty when string")
    return value


def _mapping_or_none(value: object, *, label: str) -> JsonObject | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object")
    return require_json_object(value, label=label)


def _mapping_or_empty(value: object, *, label: str) -> JsonObject:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object when present")
    return require_json_object(value, label=label)


def _json_or_none(value: object) -> JsonValue:
    if value is None:
        return None
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
    return cast(JsonValue, json.loads(encoded))


def _required_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


__all__ = ["SURFACE_PROJECTION_SCHEMA_VERSION", "render_surface_projection"]
