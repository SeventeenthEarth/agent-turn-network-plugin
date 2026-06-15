from __future__ import annotations

import pytest

from kkachi_agent_network_plugin.surface_rendering import render_surface_projection


def test_surface_projection_renders_cursor_ordered_rows_and_evidence_statuses() -> None:
    projection = {
        "schema_version": 1,
        "session_id": "sess-surface",
        "events": [
            {
                "order": 3,
                "cursor": "cur_000000000003_evt_speech",
                "event": {
                    "event_id": "evt-speech",
                    "session_id": "sess-surface",
                    "type": "speech",
                    "from": "agent-1",
                    "payload": {"turn": 1, "speech": "I support the local projection."},
                },
            },
            {
                "order": 1,
                "cursor": "cur_000000000001_evt_session",
                "event": {
                    "event_id": "evt-session",
                    "session_id": "sess-surface",
                    "type": "session_created",
                    "payload": {
                        "surface": {"kind": "discord_thread", "thread_id": "thread-fixture"},
                        "linked_authority": {"kanban_card_id": "t_surface"},
                    },
                },
            },
            {
                "order": 4,
                "cursor": "cur_000000000004_evt_final",
                "event": {
                    "event_id": "evt-final",
                    "session_id": "sess-surface",
                    "type": "council_finalized",
                    "payload": {
                        "final_summary": "Consensus reached.",
                        "surface_evidence": {
                            "status": "posted",
                            "message_id": "msg-final",
                        },
                        "linked_authority_result": {
                            "status": "pending_followup",
                            "followup_card_id": "t_followup",
                        },
                    },
                },
            },
            {
                "order": 2,
                "cursor": "cur_000000000002_evt_grant",
                "event": {
                    "event_id": "evt-grant",
                    "session_id": "sess-surface",
                    "type": "speaker_selected",
                    "from": "agent-mod",
                    "to": ["agent-1"],
                    "payload": {
                        "turn": 1,
                        "member": "agent-1",
                        "selection_mode": "moderator_direct",
                    },
                },
            },
        ],
    }

    result = render_surface_projection(projection)

    assert result["live_readiness"] is False
    assert result["order_authority"] == "daemon_cursor"
    assert [row["event_id"] for row in result["rows"]] == [
        "evt-session",
        "evt-grant",
        "evt-speech",
        "evt-final",
        "evt-final",
    ]
    assert [row["status"] for row in result["rows"]] == [
        "created",
        "granted",
        "renderable",
        "posted",
        "pending_followup",
    ]
    speech_row = result["rows"][2]
    assert speech_row["target"] == "speech"
    assert speech_row["evidence"] == {
        "turn": 1,
        "selected": "agent-1",
        "speaker": "agent-1",
        "speaker_selected_event_id": "evt-grant",
        "speaker_selected_cursor": "cur_000000000002_evt_grant",
    }


@pytest.mark.parametrize(
    ("events", "message"),
    [
        (
            [
                {
                    "order": 1,
                    "cursor": "cur_000000000001_evt_speech",
                    "event": {
                        "event_id": "evt-speech",
                        "session_id": "sess-surface",
                        "type": "speech",
                        "from": "agent-1",
                        "payload": {"turn": 1, "speech": "too early"},
                    },
                }
            ],
            "floor_grant_missing_or_mismatched",
        ),
        (
            [
                {
                    "order": 1,
                    "cursor": "cur_000000000001_evt_speech",
                    "event": {
                        "event_id": "evt-speech",
                        "session_id": "sess-surface",
                        "type": "speech",
                        "from": "agent-1",
                        "payload": {"turn": 1, "speech": "too early"},
                    },
                },
                {
                    "order": 2,
                    "cursor": "cur_000000000002_evt_grant",
                    "event": {
                        "event_id": "evt-grant",
                        "session_id": "sess-surface",
                        "type": "speaker_selected",
                        "to": ["agent-1"],
                        "payload": {"turn": 1, "member": "agent-1"},
                    },
                },
            ],
            "floor_grant_missing_or_mismatched",
        ),
    ],
)
def test_surface_projection_fails_closed_when_speech_has_no_prior_matching_grant(
    events: list[dict[str, object]], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        render_surface_projection(
            {"schema_version": 1, "session_id": "sess-surface", "events": events}
        )


def test_surface_projection_fails_closed_for_proofless_delivery_evidence() -> None:
    with pytest.raises(ValueError, match="requires a reconstructable non-empty evidence pointer"):
        render_surface_projection(
            {
                "schema_version": 1,
                "session_id": "sess-surface",
                "events": [
                    {
                        "cursor": "cur_000000000001_evt_final",
                        "event": {
                            "event_id": "evt-final",
                            "session_id": "sess-surface",
                            "type": "council_finalized",
                            "payload": {"surface_evidence": {"status": "posted"}},
                        },
                    }
                ],
            }
        )


def test_surface_projection_fails_closed_for_unsupported_delivery_status() -> None:
    with pytest.raises(ValueError, match="unsupported delivery evidence status"):
        render_surface_projection(
            {
                "schema_version": 1,
                "session_id": "sess-surface",
                "events": [
                    {
                        "cursor": "cur_000000000001_evt_final",
                        "event": {
                            "event_id": "evt-final",
                            "session_id": "sess-surface",
                            "type": "council_unresolved",
                            "payload": {"surface_evidence": {"status": "complete"}},
                        },
                    }
                ],
            }
        )


def test_surface_projection_fails_closed_for_duplicate_cursor_authority() -> None:
    with pytest.raises(ValueError, match="duplicate daemon cursor"):
        render_surface_projection(
            {
                "schema_version": 1,
                "session_id": "sess-surface",
                "events": [
                    {
                        "order": 1,
                        "cursor": "cur_000000000001_evt_a",
                        "event": {
                            "event_id": "evt-a",
                            "session_id": "sess-surface",
                            "type": "session_created",
                            "payload": {},
                        },
                    },
                    {
                        "order": 2,
                        "cursor": "cur_000000000001_evt_a",
                        "event": {
                            "event_id": "evt-b",
                            "session_id": "sess-surface",
                            "type": "session_created",
                            "payload": {},
                        },
                    },
                ],
            }
        )
