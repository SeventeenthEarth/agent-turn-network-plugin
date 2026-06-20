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
                            "references_event_id": "evt-final",
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


def test_surface_projection_renders_clean_visible_closeout_transcript_and_audit_log() -> None:
    projection = {
        "schema_version": 1,
        "session_id": "sess-visux",
        "require_terminal_closeout": True,
        "events": [
            {
                "order": 1,
                "cursor": "cur_000000000001_evt_session",
                "event": {
                    "event_id": "evt-session",
                    "session_id": "sess-visux",
                    "type": "session_created",
                    "from": "gongmyeong",
                    "payload": {
                        "surface": {"kind": "discord_thread", "thread_id": "thread-visux"},
                        "linked_authority": {"kanban_card_id": "t_visux"},
                    },
                },
            },
            {
                "order": 2,
                "cursor": "cur_000000000002_evt_grant",
                "event": {
                    "event_id": "evt-grant",
                    "session_id": "sess-visux",
                    "type": "speaker_selected",
                    "from": "gongmyeong",
                    "to": ["seohwang"],
                    "payload": {"turn": 1, "member": "seohwang"},
                },
            },
            {
                "order": 3,
                "cursor": "cur_000000000003_evt_speech",
                "event": {
                    "event_id": "evt-speech",
                    "session_id": "sess-visux",
                    "type": "speech",
                    "from": "seohwang",
                    "payload": {
                        "turn": 1,
                        "speech": "Fail closed on missing final proof.",
                        "visible_turn_index": 1,
                        "visible_turn_total": 3,
                        "runner_id": "runner-visible-hidden",
                        "speech_event_id": "evt-speech-hidden",
                    },
                },
            },
            {
                "order": 4,
                "cursor": "cur_000000000004_evt_draft",
                "event": {
                    "event_id": "evt-draft",
                    "session_id": "sess-visux",
                    "type": "draft_conclusion",
                    "from": "gongmyeong",
                    "payload": {
                        "draft_version": 1,
                        "draft": "Ship with posted proof only.",
                        "discussion_lifecycle": {
                            "visible_turn": {"index": 2, "total": 3},
                            "lifecycle_stage": "closeout",
                        },
                    },
                },
            },
            {
                "order": 5,
                "cursor": "cur_000000000005_evt_vote_request",
                "event": {
                    "event_id": "evt-vote-request",
                    "session_id": "sess-visux",
                    "type": "consensus_vote_requested",
                    "from": "gongmyeong",
                    "payload": {"draft_version": 1, "timeout_sec": 600},
                },
            },
            {
                "order": 6,
                "cursor": "cur_000000000006_evt_vote",
                "event": {
                    "event_id": "evt-vote",
                    "session_id": "sess-visux",
                    "type": "consensus_vote",
                    "from": "seohwang",
                    "payload": {"draft_version": 1, "vote": "approve", "reason": "Proof present."},
                },
            },
            {
                "order": 7,
                "cursor": "cur_000000000007_evt_final",
                "event": {
                    "event_id": "evt-final",
                    "session_id": "sess-visux",
                    "type": "council_finalized",
                    "from": "gongmyeong",
                    "payload": {
                        "final_summary": "Approved with visible proof.",
                        "consensus": "approve",
                        "visible_turn_index": 3,
                        "visible_turn_total": 3,
                        "surface_evidence": {
                            "status": "posted",
                            "final_message_id": "msg-final",
                            "references_event_id": "evt-final",
                        },
                        "linked_authority_result": {
                            "status": "posted",
                            "kanban_comment_id": "comment-final",
                        },
                    },
                },
            },
        ],
    }

    result = render_surface_projection(projection)

    visible_transcript = result["visible_transcript"]
    assert [row["kind"] for row in visible_transcript] == [
        "header",
        "floor_grant",
        "speech",
        "draft_closeout",
        "vote_request",
        "vote",
        "final_closeout",
    ]
    assert visible_transcript[2]["label"] == "[KAN | T1/3]"
    assert visible_transcript[1]["text"] == "[KAN]\nNext speaker: seohwang."
    assert (
        visible_transcript[2]["text"]
        == "[KAN | T1/3]\nseohwang: Fail closed on missing final proof."
    )
    assert visible_transcript[3]["label"] == "[KAN | T2/3]"
    assert visible_transcript[3]["text"] == (
        "[KAN | T2/3]\ngongmyeong proposed draft closeout v1: Ship with posted proof only."
    )
    assert visible_transcript[5]["text"] == (
        "[KAN]\nseohwang voted approve on draft v1. Reason: Proof present."
    )
    assert visible_transcript[-1] == {
        "kind": "final_closeout",
        "label": "[KAN | T3/3]",
        "outcome": "finalized",
        "text": "[KAN | T3/3]\ngongmyeong final closeout: Approved with visible proof.",
        "consensus": "approve",
    }
    forbidden_visible_keys = {
        "cursor",
        "event_id",
        "member",
        "speaker",
        "moderator",
        "evidence_pointer",
        "runner_id",
        "speech_event_id",
        "speaker_selected_event_id",
    }
    assert all(forbidden_visible_keys.isdisjoint(row) for row in visible_transcript)
    visible_text = "\n".join(str(row["text"]) for row in visible_transcript)
    assert "Next speaker: seohwang." in visible_text
    assert "seohwang: Fail closed on missing final proof." in visible_text
    assert "seohwang voted approve on draft v1." in visible_text
    assert "gongmyeong final closeout: Approved with visible proof." in visible_text
    for hidden_text in (
        "sess-visux",
        "evt-",
        "cur_",
        "msg-final",
        "comment-final",
        "runner-visible-hidden",
        "speech_event_id",
        "speaker_selected_event_id",
        "thread-visux",
    ):
        assert hidden_text not in visible_text
    assert result["audit_log"][0]["cursor"] == "cur_000000000001_evt_session"
    assert result["audit_log"][-1]["event_id"] == "evt-final"
    assert result["audit_log"][2]["evidence"]["speaker_selected_event_id"] == "evt-grant"
    assert result["audit_log"][-2]["evidence"]["final_message_id"] == "msg-final"
    assert result["source_event_count"] == 7


def test_surface_projection_fails_closed_for_malformed_visible_progress() -> None:
    with pytest.raises(ValueError, match="visible_turn progress requires index and total"):
        render_surface_projection(
            {
                "schema_version": 1,
                "session_id": "sess-progress",
                "events": [
                    {
                        "cursor": "cur_000000000001_evt_session",
                        "event": {
                            "event_id": "evt-session",
                            "session_id": "sess-progress",
                            "type": "session_created",
                            "payload": {
                                "visible_turn_index": 1,
                            },
                        },
                    }
                ],
            }
        )


def test_surface_projection_fails_closed_for_ambiguous_nested_visible_progress() -> None:
    with pytest.raises(ValueError, match="discussion_lifecycle visible progress is ambiguous"):
        render_surface_projection(
            {
                "schema_version": 1,
                "session_id": "sess-progress",
                "events": [
                    {
                        "cursor": "cur_000000000001_evt_session",
                        "event": {
                            "event_id": "evt-session",
                            "session_id": "sess-progress",
                            "type": "session_created",
                            "payload": {
                                "discussion_lifecycle": {
                                    "visible_turn_index": 1,
                                    "visible_turn_total": 3,
                                    "visible_turn": {"index": 2, "total": 3},
                                }
                            },
                        },
                    }
                ],
            }
        )


def test_surface_projection_remains_local_and_exposes_no_live_fallback() -> None:
    result = render_surface_projection(
        {
            "schema_version": 1,
            "session_id": "sess-local",
            "events": [
                {
                    "cursor": "cur_000000000001_evt_session",
                    "event": {
                        "event_id": "evt-session",
                        "session_id": "sess-local",
                        "type": "session_created",
                        "payload": {"surface": {"kind": "discord_thread"}},
                    },
                }
            ],
        }
    )

    assert result["live_readiness"] is False
    assert result["order_authority"] == "daemon_cursor"
    assert result["visible_transcript"] == [
        {"kind": "header", "label": "[KAN]", "text": "[KAN]\nCouncil session opened."}
    ]
    assert "fallback" not in result
    assert "delivery" not in result


def test_surface_projection_closeout_mode_fails_closed_when_terminal_outcome_missing() -> None:
    with pytest.raises(ValueError, match="terminal_outcome_missing"):
        render_surface_projection(
            {
                "schema_version": 1,
                "session_id": "sess-visux",
                "require_terminal_closeout": True,
                "events": [
                    {
                        "cursor": "cur_000000000001_evt_draft",
                        "event": {
                            "event_id": "evt-draft",
                            "session_id": "sess-visux",
                            "type": "draft_conclusion",
                            "from": "gongmyeong",
                            "payload": {"draft_version": 1, "draft": "Not final."},
                        },
                    }
                ],
            }
        )


def test_surface_projection_closeout_mode_fails_closed_for_mismatched_evidence() -> None:
    with pytest.raises(ValueError, match="visible_closeout_evidence_mismatch"):
        render_surface_projection(
            {
                "schema_version": 1,
                "session_id": "sess-visux",
                "require_terminal_closeout": True,
                "events": [
                    {
                        "cursor": "cur_000000000001_evt_final",
                        "event": {
                            "event_id": "evt-final",
                            "session_id": "sess-visux",
                            "type": "council_finalized",
                            "from": "gongmyeong",
                            "payload": {
                                "final_summary": "Approved.",
                                "surface_evidence": {
                                    "status": "posted",
                                    "final_message_id": "msg-final",
                                    "references_event_id": "evt-other",
                                },
                            },
                        },
                    }
                ],
            }
        )


def test_surface_projection_closeout_mode_fails_closed_for_missing_terminal_reference() -> None:
    with pytest.raises(ValueError, match="visible_closeout_evidence_reference_missing"):
        render_surface_projection(
            {
                "schema_version": 1,
                "session_id": "sess-visux",
                "require_terminal_closeout": True,
                "events": [
                    {
                        "cursor": "cur_000000000001_evt_final",
                        "event": {
                            "event_id": "evt-final",
                            "session_id": "sess-visux",
                            "type": "council_finalized",
                            "from": "gongmyeong",
                            "payload": {
                                "final_summary": "Approved.",
                                "surface_evidence": {
                                    "status": "posted",
                                    "final_message_id": "msg-final",
                                },
                            },
                        },
                    }
                ],
            }
        )


def test_surface_projection_renders_argument_graph_support_challenge_and_preserves_audit() -> None:
    support_claim = {
        "claim_id": "T02.C1",
        "summary": "Control projections already carry relation evidence.",
        "kind": "observation",
    }
    challenge_claim = {
        "claim_id": "T02.C2",
        "summary": "Visible output must stay compact enough for review.",
        "kind": "risk",
    }
    support_link = {
        "target_event_id": "evt-speech-1",
        "target_claim_id": "T01.C1",
        "target_speaker": "macho",
        "stance": "support",
        "rationale": "The renderer should preserve daemon-supplied audit fields.",
    }
    challenge_link = {
        "target_event_id": "evt-speech-1",
        "target_claim_id": "T01.C2",
        "target_speaker": "seohwang",
        "stance": "challenge",
        "rationale": "Audit preservation alone is not enough for human review.",
    }
    projection = _argument_projection(
        [
            _speech_event(
                order=3,
                event_id="evt-speech-1",
                turn=1,
                speaker="macho",
                speech="Renderer must preserve supplied relation fields.",
            ),
            _speech_event(
                order=5,
                event_id="evt-speech-2",
                turn=2,
                speaker="seohwang",
                speech="Preserve the graph and show compact relation lines.",
                extra_payload={
                    "claims": [support_claim, challenge_claim],
                    "stance_links": [support_link, challenge_link],
                    "contribution_type": "challenge",
                    "responds_to_event_id": "evt-speech-1",
                },
            ),
        ]
    )

    result = render_surface_projection(projection)

    speech_row = result["audit_log"][4]
    assert speech_row["speech"] == "Preserve the graph and show compact relation lines."
    assert speech_row["claims"] == [support_claim, challenge_claim]
    assert speech_row["stance_links"] == [support_link, challenge_link]
    assert speech_row["contribution_type"] == "challenge"
    assert speech_row["responds_to_event_id"] == "evt-speech-1"
    visible = result["visible_transcript"][4]
    assert visible["speech"] == "Preserve the graph and show compact relation lines."
    assert visible["relation_summary"] == [
        "support T01.C1 macho: The renderer should preserve daemon-supplied audit fields.",
        "challenge T01.C2 seohwang: Audit preservation alone is not enough for human review.",
    ]
    assert visible["claims_summary"] == [
        "Claim T02.C1: Control projections already carry relation evidence.",
        "Claim T02.C2: Visible output must stay compact enough for review.",
    ]
    assert "Preserve the graph and show compact relation lines." in visible["text"]
    assert "support T01.C1 macho" in visible["text"]


def test_surface_projection_renders_synthesis_with_multiple_claims_and_links() -> None:
    claims = [
        {
            "claim_id": "T03.C1",
            "summary": "Use daemon cursor order as the only rendering authority.",
            "kind": "requirement",
        },
        {
            "claim_id": "T03.C2",
            "summary": "Keep live readiness false for this local projection.",
            "kind": "requirement",
        },
    ]
    stance_links = [
        {
            "target_event_id": "evt-speech-1",
            "target_claim_id": "T01.C1",
            "target_speaker": "macho",
            "stance": "synthesize",
            "rationale": "Cursor authority anchors the audit trail.",
        },
        {
            "target_event_id": "evt-speech-2",
            "target_claim_id": "T02.C1",
            "target_speaker": "jonghoe",
            "stance": "synthesize",
            "rationale": "Local projection must not imply live Discord readiness.",
        },
    ]
    projection = _argument_projection(
        [
            _speech_event(
                order=3,
                event_id="evt-speech-1",
                turn=1,
                speaker="macho",
                speech="Cursor authority is the renderer boundary.",
            ),
            _speech_event(
                order=5,
                event_id="evt-speech-2",
                turn=2,
                speaker="jonghoe",
                speech="Live readiness remains out of scope.",
            ),
            _speech_event(
                order=7,
                event_id="evt-speech-3",
                turn=3,
                speaker="manchong",
                speech="Synthesize cursor authority with local-only projection.",
                extra_payload={
                    "claims": claims,
                    "stance_links": stance_links,
                    "contribution_type": "synthesize",
                },
            ),
        ]
    )

    result = render_surface_projection(projection)

    speech_row = result["audit_log"][6]
    assert speech_row["claims"] == claims
    assert speech_row["stance_links"] == stance_links
    assert speech_row["contribution_type"] == "synthesize"
    visible = result["visible_transcript"][6]
    assert visible["relation_summary"] == [
        "synthesize T01.C1 macho: Cursor authority anchors the audit trail.",
        "synthesize T02.C1 jonghoe: Local projection must not imply live Discord readiness.",
    ]
    assert visible["claims_summary"] == [
        "Claim T03.C1: Use daemon cursor order as the only rendering authority.",
        "Claim T03.C2: Keep live readiness false for this local projection.",
    ]


def test_surface_projection_hides_raw_relation_event_ids_from_visible_summary() -> None:
    raw_link = {
        "target_event_id": "evt-speech-1",
        "target_speaker": "macho",
        "stance": "support",
        "rationale": "Uses the prior event.",
    }
    projection = _argument_projection(
        [
            _speech_event(
                order=3,
                event_id="evt-speech-1",
                turn=1,
                speaker="macho",
                speech="First speech by cursor order.",
            ),
            _speech_event(
                order=5,
                event_id="evt-speech-2",
                turn=2,
                speaker="seohwang",
                speech="Support the previous speech without leaking its event id.",
                extra_payload={
                    "stance_links": [raw_link],
                    "contribution_type": "support",
                },
            ),
        ]
    )

    result = render_surface_projection(projection)

    speech_row = result["audit_log"][4]
    assert speech_row["stance_links"] == [raw_link]
    visible = result["visible_transcript"][4]
    assert visible["relation_summary"] == [
        "support referenced speech by macho: Uses the prior event."
    ]
    visible_text = visible["text"]
    assert "support referenced speech by macho: Uses the prior event." in visible_text
    for hidden_text in ("evt-speech-1", "evt-", "cur_", "runner", "message_id"):
        assert hidden_text not in visible_text


def test_surface_projection_renders_quality_warning_without_rewriting_speech() -> None:
    diagnostics = {
        "severity": "warning",
        "code": "orphan_speech",
        "message": "Accepted in warn mode but missing relation links.",
    }
    projection = _argument_projection(
        [
            _speech_event(
                order=3,
                event_id="evt-speech-1",
                turn=1,
                speaker="macho",
                speech="The original speech text must remain exact.",
                extra_payload={
                    "quality_diagnostics": diagnostics,
                    "contribution_type": "support",
                },
            )
        ]
    )

    result = render_surface_projection(projection)

    speech_row = result["audit_log"][2]
    visible = result["visible_transcript"][2]
    assert speech_row["quality_diagnostics"] == diagnostics
    assert speech_row["speech"] == "The original speech text must remain exact."
    assert visible["speech"] == "The original speech text must remain exact."
    assert visible["quality_warnings"] == [
        "warning orphan_speech: Accepted in warn mode but missing relation links."
    ]
    assert visible["text"].startswith("[KAN]\nmacho: The original speech text must remain exact.")


def test_surface_projection_renders_quality_warning_with_code_and_no_severity() -> None:
    diagnostics = {
        "code": "orphan_speech",
        "summary": "Accepted in warn mode but missing relation links.",
    }
    projection = _argument_projection(
        [
            _speech_event(
                order=3,
                event_id="evt-speech-1",
                turn=1,
                speaker="macho",
                speech="The daemon supplied warning details without severity.",
                extra_payload={"quality_diagnostics": diagnostics},
            )
        ]
    )

    result = render_surface_projection(projection)

    speech_row = result["audit_log"][2]
    visible = result["visible_transcript"][2]
    assert speech_row["quality_diagnostics"] == diagnostics
    assert visible["quality_warnings"] == [
        "orphan_speech: Accepted in warn mode but missing relation links."
    ]


@pytest.mark.parametrize(
    ("extra_payload", "message"),
    [
        ({"claims": {"claim_id": "T01.C1"}}, "speech.payload.claims must be a JSON array"),
        ({"claims": ["T01.C1"]}, "speech.payload.claims\\[\\] must be a JSON object"),
        (
            {"stance_links": {"target_event_id": "evt-speech-1"}},
            "speech.payload.stance_links must be a JSON array",
        ),
        (
            {"quality_diagnostics": "orphan"},
            "speech.payload.quality_diagnostics must be a JSON object or array",
        ),
        (
            {"quality_diagnostics": ["orphan"]},
            "speech.payload.quality_diagnostics\\[\\] must be a JSON object",
        ),
    ],
)
def test_surface_projection_fails_closed_for_malformed_relation_and_diagnostic_shapes(
    extra_payload: dict[str, object], message: str
) -> None:
    projection = _argument_projection(
        [
            _speech_event(
                order=3,
                event_id="evt-speech-1",
                turn=1,
                speaker="macho",
                speech="Malformed relation data must not render.",
                extra_payload=extra_payload,
            )
        ]
    )

    with pytest.raises(ValueError, match=message):
        render_surface_projection(projection)


def test_surface_projection_argument_graph_respects_daemon_cursor_order() -> None:
    projection = _argument_projection(
        [
            _speech_event(
                order=5,
                event_id="evt-speech-2",
                turn=2,
                speaker="seohwang",
                speech="Second speech by cursor order.",
                extra_payload={
                    "claims": [{"claim_id": "T02.C1", "summary": "Second claim."}],
                    "stance_links": [
                        {
                            "target_event_id": "evt-speech-1",
                            "target_claim_id": "T01.C1",
                            "stance": "support",
                        }
                    ],
                    "contribution_type": "support",
                },
            ),
            _speech_event(
                order=3,
                event_id="evt-speech-1",
                turn=1,
                speaker="macho",
                speech="First speech by cursor order.",
                extra_payload={"claims": [{"claim_id": "T01.C1", "summary": "First claim."}]},
            ),
        ]
    )

    result = render_surface_projection(projection)

    speech_rows = [row for row in result["audit_log"] if row["type"] == "speech"]
    assert [row["event_id"] for row in speech_rows] == ["evt-speech-1", "evt-speech-2"]
    visible_speech = [row for row in result["visible_transcript"] if row["kind"] == "speech"]
    assert [row["speech"] for row in visible_speech] == [
        "First speech by cursor order.",
        "Second speech by cursor order.",
    ]
    assert all("speaker" not in row for row in visible_speech)


def _argument_projection(speech_events: list[dict[str, object]]) -> dict[str, object]:
    events: list[dict[str, object]] = [
        {
            "order": 1,
            "cursor": "cur_000000000001_evt_session",
            "event": {
                "event_id": "evt-session",
                "session_id": "sess-argue",
                "type": "session_created",
                "payload": {"surface": {"kind": "local_fixture"}},
            },
        }
    ]
    for speech_event in speech_events:
        order = speech_event["order"]
        assert isinstance(order, int)
        turn = speech_event["event"]["payload"]["turn"]  # type: ignore[index]
        speaker = speech_event["event"]["from"]  # type: ignore[index]
        events.append(
            {
                "order": order - 1,
                "cursor": f"cur_{order - 1:012d}_evt_grant_{turn}",
                "event": {
                    "event_id": f"evt-grant-{turn}",
                    "session_id": "sess-argue",
                    "type": "speaker_selected",
                    "to": [speaker],
                    "payload": {"turn": turn, "member": speaker},
                },
            }
        )
        events.append(speech_event)
    return {"schema_version": 1, "session_id": "sess-argue", "events": events}


def _speech_event(
    *,
    order: int,
    event_id: str,
    turn: int,
    speaker: str,
    speech: str,
    extra_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {"turn": turn, "speech": speech}
    if extra_payload:
        payload.update(extra_payload)
    return {
        "order": order,
        "cursor": f"cur_{order:012d}_{event_id}",
        "event": {
            "event_id": event_id,
            "session_id": "sess-argue",
            "type": "speech",
            "from": speaker,
            "payload": payload,
        },
    }
