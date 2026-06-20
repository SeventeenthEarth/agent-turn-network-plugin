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
ARGUE_SPEECH_FIELDS: Final[tuple[str, ...]] = (
    "claims",
    "stance_links",
    "contribution_type",
    "new_axis_reason",
    "responds_to_event_id",
    "quality_diagnostics",
)
SUPPORTED_EVENT_TYPES: Final[frozenset[str]] = frozenset(
    {
        "session_created",
        "speaker_selected",
        "speech",
        "draft_conclusion",
        "consensus_vote_requested",
        "consensus_vote",
        "council_finalized",
        "council_unresolved",
        "session_cancelled",
    }
)
SUPPORTED_DELIVERY_STATUSES: Final[frozenset[str]] = frozenset(
    {"posted", "failed", "pending_followup", "missing", "unproven", "missing/unproven"}
)
CURSOR_ORDER_PATTERN: Final = re.compile(r"^cur_(\d+)(?:_|$)")
PROGRESS_FIELD_NAMES: Final[frozenset[str]] = frozenset(
    {"visible_turn_index", "visible_turn_total"}
)


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
    require_terminal_closeout = _optional_bool(
        source.get("require_terminal_closeout"), label="projection.require_terminal_closeout"
    )

    normalized_events = [_normalize_event(item, session_id=session_id) for item in events]
    ordered_events = sorted(normalized_events, key=lambda item: cast(int, item["order"]))
    _validate_cursor_authority(ordered_events)

    rows: list[JsonObject] = []
    visible_transcript: list[JsonObject] = []
    floor_grants: dict[tuple[JsonValue, str], JsonObject] = {}
    linked_authority_configured = False
    terminal_seen = False
    terminal_closeout_seen = False
    for item in ordered_events:
        event = cast(JsonObject, item["event"])
        event_type = cast(str, event["type"])
        payload = _mapping_or_empty(event.get("payload"), label=f"{event_type}.payload")
        visible_label = _visible_label(event=event, payload=payload)
        if event_type == "session_created":
            rows.append(_session_created_row(item=item, payload=payload))
            visible_transcript.append(
                _session_header_visible_row(event=event, payload=payload, label=visible_label)
            )
            linked_authority_configured = bool(
                _mapping_or_empty(
                    payload.get("linked_authority"),
                    label="session_created.payload.linked_authority",
                )
            )
            continue
        if event_type == "speaker_selected":
            grant = _speaker_grant_row(item=item, event=event, payload=payload)
            rows.append(grant)
            visible_transcript.append(_speaker_grant_visible_row(grant, label=visible_label))
            floor_grants[(grant["turn"], cast(str, grant["member"]))] = grant
            continue
        if event_type == "speech":
            speech = _speech_row(item=item, event=event, payload=payload, grants=floor_grants)
            rows.append(speech)
            visible_transcript.append(_speech_visible_row(speech, label=visible_label))
            continue
        if event_type == "draft_conclusion":
            draft = _draft_conclusion_row(item=item, event=event, payload=payload)
            rows.append(draft)
            visible_transcript.append(_draft_conclusion_visible_row(draft, label=visible_label))
            continue
        if event_type == "consensus_vote_requested":
            vote_request = _vote_request_row(item=item, event=event, payload=payload)
            rows.append(vote_request)
            visible_transcript.append(_vote_request_visible_row(vote_request, label=visible_label))
            continue
        if event_type == "consensus_vote":
            vote = _vote_row(item=item, event=event, payload=payload)
            rows.append(vote)
            visible_transcript.append(_vote_visible_row(vote, label=visible_label))
            continue
        if event_type in {"council_finalized", "council_unresolved", "session_cancelled"}:
            terminal_seen = True
            rows.extend(
                _terminal_rows(
                    item=item,
                    payload=payload,
                    linked_authority_configured=linked_authority_configured,
                )
            )
            closeout = _terminal_visible_row(
                item=item,
                event=event,
                payload=payload,
                require_closeout=require_terminal_closeout,
                label=visible_label,
            )
            if closeout is not None:
                terminal_closeout_seen = True
                visible_transcript.append(closeout)

    if require_terminal_closeout and not terminal_seen:
        raise ValueError("terminal_outcome_missing")
    if require_terminal_closeout and not terminal_closeout_seen:
        raise ValueError("visible_closeout_missing_or_unproven")

    rows_json: list[JsonValue] = list(rows)
    visible_json: list[JsonValue] = list(visible_transcript)
    return {
        "schema_version": SURFACE_PROJECTION_SCHEMA_VERSION,
        "session_id": session_id,
        "order_authority": "daemon_cursor",
        "source_event_count": len(ordered_events),
        "live_readiness": False,
        "rows": rows_json,
        "visible_transcript": visible_json,
        "audit_log": rows_json,
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
    row = _base_row(item=item, event_type="speech", target="speech", status="renderable") | {
        "turn": turn,
        "member": speaker,
        "speaker": speaker,
        "content": content,
        "speech": content,
        "evidence": {
            "turn": turn,
            "selected": speaker,
            "speaker": speaker,
            "speaker_selected_event_id": grant["event_id"],
            "speaker_selected_cursor": grant["cursor"],
        },
    }
    for key in ARGUE_SPEECH_FIELDS:
        if key in payload:
            row[key] = _speech_argument_field(payload.get(key), field_name=key)
    return row


def _draft_conclusion_row(
    *, item: JsonObject, event: Mapping[str, object], payload: Mapping[str, object]
) -> JsonObject:
    draft_version = _turn_value(
        payload.get("draft_version"), label="draft_conclusion.payload.draft_version"
    )
    draft = _required_string(payload.get("draft"), label="draft_conclusion.payload.draft")
    moderator = _required_string(event.get("from"), label="draft_conclusion.from")
    row = _base_row(
        item=item, event_type="draft_conclusion", target="draft_closeout", status="proposal"
    ) | {
        "moderator": moderator,
        "draft_version": draft_version,
        "content": draft,
    }
    revision_reason = payload.get("revision_reason")
    if revision_reason is not None:
        row["revision_reason"] = _required_string(
            revision_reason, label="draft_conclusion.payload.revision_reason"
        )
    return row


def _vote_request_row(
    *, item: JsonObject, event: Mapping[str, object], payload: Mapping[str, object]
) -> JsonObject:
    draft_version = _turn_value(
        payload.get("draft_version"), label="consensus_vote_requested.payload.draft_version"
    )
    moderator = _required_string(event.get("from"), label="consensus_vote_requested.from")
    row = _base_row(
        item=item,
        event_type="consensus_vote_requested",
        target="vote_request",
        status="requested",
    ) | {"moderator": moderator, "draft_version": draft_version}
    timeout_sec = payload.get("timeout_sec")
    if timeout_sec is not None:
        if isinstance(timeout_sec, bool) or not isinstance(timeout_sec, int) or timeout_sec < 0:
            raise ValueError(
                "consensus_vote_requested.payload.timeout_sec must be a non-negative integer"
            )
        row["timeout_sec"] = timeout_sec
    return row


def _vote_row(
    *, item: JsonObject, event: Mapping[str, object], payload: Mapping[str, object]
) -> JsonObject:
    draft_version = _turn_value(
        payload.get("draft_version"), label="consensus_vote.payload.draft_version"
    )
    voter = _required_string(event.get("from"), label="consensus_vote.from")
    vote = _required_string(payload.get("vote"), label="consensus_vote.payload.vote")
    row = _base_row(item=item, event_type="consensus_vote", target="vote", status="recorded") | {
        "member": voter,
        "draft_version": draft_version,
        "vote": vote,
    }
    reason = payload.get("reason")
    if reason is not None:
        row["reason"] = _required_string(reason, label="consensus_vote.payload.reason")
    required_change = payload.get("required_change")
    if required_change is not None:
        row["required_change"] = _required_string(
            required_change, label="consensus_vote.payload.required_change"
        )
    return row


def _terminal_rows(
    *, item: JsonObject, payload: Mapping[str, object], linked_authority_configured: bool
) -> list[JsonObject]:
    event = cast(Mapping[str, object], item["event"])
    event_type = cast(str, event["type"])
    rows: list[JsonObject] = []
    status, evidence = _delivery_status(payload.get("surface_evidence"), label="surface_evidence")
    rows.append(
        _base_row(item=item, event_type=event_type, target="visible_surface", status=status)
        | {"evidence": evidence}
    )
    if linked_authority_configured and "linked_authority_result" not in payload:
        raise ValueError("linked_authority_result_required")
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


def _session_header_visible_row(
    *, event: Mapping[str, object], payload: Mapping[str, object], label: str
) -> JsonObject:
    if event.get("from") is not None:
        _required_string(event.get("from"), label="session_created.from")
    surface = _mapping_or_empty(payload.get("surface"), label="session_created.payload.surface")
    surface_kind = surface.get("kind")
    if surface_kind is not None:
        _required_string(surface_kind, label="session_created.payload.surface.kind")
    text = "Council session opened."
    return {"kind": "header", "label": label, "text": _visible_text(label, text)}


def _speaker_grant_visible_row(row: Mapping[str, JsonValue], *, label: str) -> JsonObject:
    _turn_value(row.get("turn"), label="floor_grant.turn")
    member = _required_string(row.get("member"), label="floor_grant.member")
    text = f"Next speaker: {member}."
    return {
        "kind": "floor_grant",
        "label": label,
        "text": _visible_text(label, text),
    }


def _speech_visible_row(row: Mapping[str, JsonValue], *, label: str) -> JsonObject:
    _turn_value(row.get("turn"), label="speech.turn")
    member = _required_string(row.get("member"), label="speech.member")
    content = _required_string(row.get("content"), label="speech.content")
    visible: JsonObject = {
        "kind": "speech",
        "label": label,
        "speech": content,
    }
    contribution_type = row.get("contribution_type")
    if contribution_type is not None:
        _required_string(contribution_type, label="speech.contribution_type")
    relation_summary = _relation_summary(row.get("stance_links"))
    if relation_summary:
        visible["relation_summary"] = cast(list[JsonValue], relation_summary)
    claims_summary = _claims_summary(row.get("claims"))
    if claims_summary:
        visible["claims_summary"] = cast(list[JsonValue], claims_summary)
    quality_warnings = _quality_warnings(row.get("quality_diagnostics"))
    if quality_warnings:
        visible["quality_warnings"] = cast(list[JsonValue], quality_warnings)
    text_lines = [f"{member}: {content}"]
    text_lines.extend(relation_summary)
    text_lines.extend(claims_summary)
    text_lines.extend(f"Quality warning: {warning}" for warning in quality_warnings)
    visible["text"] = _visible_text(label, "\n".join(text_lines))
    return visible


def _draft_conclusion_visible_row(row: Mapping[str, JsonValue], *, label: str) -> JsonObject:
    draft_version = row["draft_version"]
    moderator = _required_string(row.get("moderator"), label="draft_closeout.moderator")
    content = _required_string(row.get("content"), label="draft_closeout.content")
    return {
        "kind": "draft_closeout",
        "label": label,
        "text": _visible_text(
            label, f"{moderator} proposed draft closeout v{draft_version}: {content}"
        ),
        "final": False,
    }


def _vote_request_visible_row(row: Mapping[str, JsonValue], *, label: str) -> JsonObject:
    draft_version = row["draft_version"]
    _required_string(row.get("moderator"), label="vote_request.moderator")
    return {
        "kind": "vote_request",
        "label": label,
        "text": _visible_text(label, f"Consensus vote requested for draft v{draft_version}."),
    }


def _vote_visible_row(row: Mapping[str, JsonValue], *, label: str) -> JsonObject:
    draft_version = row["draft_version"]
    member = _required_string(row.get("member"), label="vote.member")
    vote = _required_string(row.get("vote"), label="vote.vote")
    text = f"{member} voted {vote} on draft v{draft_version}."
    reason = row.get("reason")
    if reason is not None:
        text = f"{text} Reason: {_required_string(reason, label='vote.reason')}"
    return {
        "kind": "vote",
        "label": label,
        "vote": vote,
        "text": _visible_text(label, text),
    }


def _terminal_visible_row(
    *,
    item: JsonObject,
    event: Mapping[str, object],
    payload: Mapping[str, object],
    require_closeout: bool,
    label: str,
) -> JsonObject | None:
    status, evidence = _delivery_status(payload.get("surface_evidence"), label="surface_evidence")
    if status != "posted" or evidence is None:
        if require_closeout:
            raise ValueError("visible_closeout_missing_or_unproven")
        return None
    _validate_terminal_evidence_reference(
        evidence=evidence, terminal_event_id=cast(str, item["event_id"])
    )
    event_type = cast(str, event["type"])
    moderator = "moderator"
    if event.get("from") is not None:
        moderator = _required_string(event.get("from"), label=f"{event_type}.from")
    if event_type == "council_finalized":
        summary = _required_string(
            payload.get("final_summary"), label="council_finalized.payload.final_summary"
        )
        visible: JsonObject = {
            "kind": "final_closeout",
            "label": label,
            "outcome": "finalized",
            "text": _visible_text(label, f"{moderator} final closeout: {summary}"),
        }
        consensus = payload.get("consensus")
        if consensus is not None:
            visible["consensus"] = _required_string(
                consensus, label="council_finalized.payload.consensus"
            )
        return visible
    if event_type == "council_unresolved":
        reason = _required_string(
            payload.get("reason") or payload.get("final_summary"),
            label="council_unresolved.payload.reason",
        )
        return {
            "kind": "final_closeout",
            "label": label,
            "outcome": "unresolved",
            "text": _visible_text(label, f"{moderator} unresolved closeout: {reason}"),
        }
    reason = _required_string(payload.get("reason"), label="session_cancelled.payload.reason")
    return {
        "kind": "final_closeout",
        "label": label,
        "outcome": "cancelled",
        "text": _visible_text(label, f"{moderator} cancelled closeout: {reason}"),
    }


def _visible_label(*, event: Mapping[str, object], payload: Mapping[str, object]) -> str:
    direct = _visible_progress_from_fields(
        event,
        payload,
        labels=("event", f"{event.get('type', 'event')}.payload"),
    )
    if direct is not None:
        return direct
    nested = _visible_progress_from_nested(payload.get("discussion_lifecycle"))
    if nested is not None:
        return nested
    return "[KAN]"


def _visible_progress_from_fields(
    *objects: Mapping[str, object], labels: tuple[str, ...]
) -> str | None:
    fields_present = [any(field in item for field in PROGRESS_FIELD_NAMES) for item in objects]
    if not any(fields_present):
        return None
    progress_values: list[tuple[int, int]] = []
    for item, label in zip(objects, labels, strict=True):
        has_index = "visible_turn_index" in item
        has_total = "visible_turn_total" in item
        if not has_index and not has_total:
            continue
        if not has_index or not has_total:
            raise ValueError(f"{label}.visible_turn progress requires index and total")
        progress_values.append(
            _visible_progress_pair(
                index_value=item.get("visible_turn_index"),
                total_value=item.get("visible_turn_total"),
                label=label,
            )
        )
    first = progress_values[0]
    if any(value != first for value in progress_values[1:]):
        raise ValueError("visible_turn progress fields are ambiguous")
    return _format_visible_progress(*first)


def _visible_progress_from_nested(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("discussion_lifecycle must be a JSON object when present")
    lifecycle = require_json_object(value, label="discussion_lifecycle")
    candidates: list[tuple[int, int]] = []
    direct = _visible_progress_from_fields(
        lifecycle,
        labels=("discussion_lifecycle",),
    )
    if direct is not None:
        # Re-parse to keep ambiguity checks between supported nested shapes exact.
        candidates.append(
            _visible_progress_pair(
                index_value=lifecycle.get("visible_turn_index"),
                total_value=lifecycle.get("visible_turn_total"),
                label="discussion_lifecycle",
            )
        )
    visible_turn = lifecycle.get("visible_turn")
    if visible_turn is not None:
        if not isinstance(visible_turn, Mapping):
            raise ValueError("discussion_lifecycle.visible_turn must be a JSON object")
        visible_turn_payload = require_json_object(
            visible_turn, label="discussion_lifecycle.visible_turn"
        )
        has_index = "index" in visible_turn_payload
        has_total = "total" in visible_turn_payload
        if not has_index or not has_total:
            raise ValueError("discussion_lifecycle.visible_turn progress requires index and total")
        candidates.append(
            _visible_progress_pair(
                index_value=visible_turn_payload.get("index"),
                total_value=visible_turn_payload.get("total"),
                label="discussion_lifecycle.visible_turn",
            )
        )
    if not candidates:
        return None
    first = candidates[0]
    if any(candidate != first for candidate in candidates[1:]):
        raise ValueError("discussion_lifecycle visible progress is ambiguous")
    return _format_visible_progress(*first)


def _visible_progress_pair(
    *, index_value: object, total_value: object, label: str
) -> tuple[int, int]:
    if isinstance(index_value, bool) or not isinstance(index_value, int):
        raise ValueError(f"{label}.visible_turn_index must be a non-negative integer")
    if isinstance(total_value, bool) or not isinstance(total_value, int):
        raise ValueError(f"{label}.visible_turn_total must be a positive integer")
    if index_value < 0:
        raise ValueError(f"{label}.visible_turn_index must be a non-negative integer")
    if total_value <= 0:
        raise ValueError(f"{label}.visible_turn_total must be a positive integer")
    if index_value > total_value:
        raise ValueError("visible_turn_index must not exceed visible_turn_total")
    return index_value, total_value


def _format_visible_progress(index: int, total: int) -> str:
    return f"[KAN | T{index}/{total}]"


def _visible_text(label: str, body: str) -> str:
    return f"{label}\n{body}"


def _speech_argument_field(value: object, *, field_name: str) -> JsonValue:
    if field_name == "claims":
        return _argument_object_array(
            value,
            label="speech.payload.claims",
            required_strings=("claim_id", "summary"),
            optional_strings=("kind",),
        )
    if field_name == "stance_links":
        return _argument_object_array(
            value,
            label="speech.payload.stance_links",
            required_strings=("target_event_id", "stance"),
            optional_strings=("target_claim_id", "target_speaker", "speaker", "rationale"),
        )
    if field_name == "quality_diagnostics":
        return _quality_diagnostics(value, label="speech.payload.quality_diagnostics")
    if field_name in {"contribution_type", "responds_to_event_id"}:
        return _required_string(value, label=f"speech.payload.{field_name}")
    if field_name == "new_axis_reason":
        if value is None:
            return None
        return _required_string(value, label="speech.payload.new_axis_reason")
    return _json_value(value, label=f"speech.payload.{field_name}")


def _argument_object_array(
    value: object,
    *,
    label: str,
    required_strings: tuple[str, ...],
    optional_strings: tuple[str, ...],
) -> list[JsonValue]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array")
    rows: list[JsonValue] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError(f"{label}[] must be a JSON object")
        payload = require_json_object(item, label=f"{label}[]")
        for key in required_strings:
            _required_string(payload.get(key), label=f"{label}[].{key}")
        for key in optional_strings:
            if key in payload and payload.get(key) is not None:
                _required_string(payload.get(key), label=f"{label}[].{key}")
        rows.append(_json_value(payload, label=f"{label}[]"))
    return rows


def _quality_diagnostics(value: object, *, label: str) -> JsonValue:
    if isinstance(value, Mapping):
        return _json_value(require_json_object(value, label=label), label=label)
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON object or array")
    diagnostics: list[JsonValue] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError(f"{label}[] must be a JSON object")
        diagnostics.append(_json_value(require_json_object(item, label=f"{label}[]"), label=label))
    return diagnostics


def _relation_summary(value: JsonValue | None) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("speech.stance_links must be a JSON array")
    summaries: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("speech.stance_links[] must be a JSON object")
        stance = _required_string(item.get("stance"), label="speech.stance_links[].stance")
        target = item.get("target_claim_id")
        if target is None:
            _required_string(
                item.get("target_event_id"), label="speech.stance_links[].target_event_id"
            )
            target = "referenced speech"
        else:
            target = _required_string(target, label="speech.stance_links[].target_claim_id")
        speaker = item.get("target_speaker")
        if speaker is None:
            speaker = item.get("speaker")
        line = f"{stance} {target}"
        if speaker is not None:
            speaker_label = _required_string(speaker, label="speech.stance_links[].target_speaker")
            if target == "referenced speech":
                line = f"{line} by {speaker_label}"
            else:
                line = f"{line} {speaker_label}"
        rationale = item.get("rationale")
        if rationale is not None:
            line = f"{line}: {_required_string(rationale, label='speech.stance_links[].rationale')}"
        summaries.append(line)
    return summaries


def _claims_summary(value: JsonValue | None) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("speech.claims must be a JSON array")
    summaries: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("speech.claims[] must be a JSON object")
        claim_id = _required_string(item.get("claim_id"), label="speech.claims[].claim_id")
        summary = _required_string(item.get("summary"), label="speech.claims[].summary")
        summaries.append(f"Claim {claim_id}: {summary}")
    return summaries


def _quality_warnings(value: JsonValue | None) -> list[str]:
    if value is None:
        return []
    diagnostics: list[Mapping[str, JsonValue]]
    if isinstance(value, Mapping):
        diagnostics = [value]
    elif isinstance(value, list):
        diagnostics = []
        for item in value:
            if not isinstance(item, Mapping):
                raise ValueError("speech.quality_diagnostics[] must be a JSON object")
            diagnostics.append(item)
    else:
        raise ValueError("speech.quality_diagnostics must be a JSON object or array")
    warnings: list[str] = []
    for diagnostic in diagnostics:
        severity = diagnostic.get("severity") or diagnostic.get("level")
        if isinstance(severity, str) and severity.lower() not in {"warning", "warn"}:
            continue
        message = diagnostic.get("message") or diagnostic.get("summary")
        if message is None:
            continue
        message_text = _required_string(message, label="speech.quality_diagnostics[].message")
        code = diagnostic.get("code")
        if code is None:
            warnings.append(message_text)
            continue
        code_text = _required_string(code, label="speech.quality_diagnostics[].code")
        if severity is None:
            warnings.append(f"{code_text}: {message_text}")
            continue
        warnings.append(
            f"{_required_string(severity, label='speech.quality_diagnostics[].severity')} "
            f"{code_text}: {message_text}"
        )
    return warnings


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
    return _json_value(value, label="json")


def _json_value(value: object, *, label: str) -> JsonValue:
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be render-safe JSON") from exc
    decoded = json.loads(encoded)
    if not isinstance(decoded, str | int | float | bool | list | dict) and decoded is not None:
        raise ValueError(f"{label} must be render-safe JSON")
    return cast(JsonValue, decoded)


def _required_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _optional_bool(value: object, *, label: str) -> bool:
    if value is None:
        return False
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean when present")
    return value


def _validate_terminal_evidence_reference(
    *, evidence: Mapping[str, JsonValue], terminal_event_id: str
) -> None:
    reference_seen = False
    for key in ("references_event_id", "terminal_event_id", "event_id", "source_event_id"):
        value = evidence.get(key)
        if value is None:
            continue
        reference_seen = True
        if not isinstance(value, str) or value != terminal_event_id:
            raise ValueError("visible_closeout_evidence_mismatch")
    if not reference_seen:
        raise ValueError("visible_closeout_evidence_reference_missing")


__all__ = ["SURFACE_PROJECTION_SCHEMA_VERSION", "render_surface_projection"]
