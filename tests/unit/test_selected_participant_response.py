from __future__ import annotations

import copy
import json
from collections.abc import Callable
from typing import Any, cast

import pytest

from hermes_unified_network_plugin.client import DaemonClient, StaticDaemonTransport
from hermes_unified_network_plugin.client.daemon import (
    OP_COMMAND_SUBMIT,
    OP_STREAM_ACK,
    OP_VERSION_READ,
)
from hermes_unified_network_plugin.protocol import JsonObject
from hermes_unified_network_plugin.tools import handle_selected_participant_response

BASE_VERSION_WITH_PARTC: JsonObject = {
    "protocol_version": "kan-protocol-v1alpha0",
    "daemon_version": "0.0.0-fake",
    "feature_groups": [
        "version.read",
        "command_envelope",
        "structured_error",
        "council.lifecycle",
        "stream_frame",
        "stream.ack",
    ],
    "live_readiness": False,
}
BASE_COMMAND_SUCCESS: JsonObject = {
    "ok": True,
    "command_id": "cmd-speak-1",
    "event_id": "evt-speak-1",
    "session_id": "sess-partc",
    "request_id": "req-speak-1",
}
BASE_ACK_SUCCESS: JsonObject = {
    "ok": True,
    "command_id": "cmd-ack-1",
    "event_id": "evt-ack-1",
    "session_id": "sess-partc",
    "request_id": "plugin-live-stream-ack",
    "deduplicated": False,
}
SPEAKER_SELECTED_FRAME: JsonObject = {
    "cursor": "cur_000000000042_evt_selected",
    "is_replay": False,
    "sequence": 42,
    "schema_version": 1,
    "event": {
        "schema_version": 1,
        "event_id": "evt-selected",
        "command_id": "cmd-grant-1",
        "session_id": "sess-partc",
        "type": "speaker_selected",
        "from": "agent-mod",
        "to": ["kas"],
        "payload": {"turn": 3, "member": "kas"},
    },
}
PARTICIPANT_RESPONSE: JsonObject = {
    "source": "control_membr_evidence",
    "member": "kas",
    "message": "KAS bounded participant response from wrapper evidence.",
    "role_substitution": False,
    "runner": {
        "invocation_id": "run_cmd-grant-1_1",
        "started_event_id": "evt-run-started",
        "terminal_event_id": "evt-run-terminal",
        "terminal_event_type": "participant_response",
        "adapter_kind": "hermes-agent",
        "wrapper_binding_evidence": "redacted_wrapper_binding",
    },
}


def factory_for_transport(transport: StaticDaemonTransport) -> Callable[[], DaemonClient]:
    return lambda: DaemonClient(transport)


def decode(payload: str) -> dict[str, Any]:
    decoded = json.loads(payload)
    assert isinstance(decoded, dict)
    return decoded


def never_client_factory() -> DaemonClient:
    raise AssertionError("client factory must not be called")


def _args() -> JsonObject:
    return {
        "session_id": "sess-partc",
        "selected_member": "kas",
        "speaker_selected_frame": copy.deepcopy(SPEAKER_SELECTED_FRAME),
        "participant_response": copy.deepcopy(PARTICIPANT_RESPONSE),
        "command_id": "cmd-speak-1",
        "request_id": "req-speak-1",
        "idempotency_key": "idem-speak-1",
        "ack_command_id": "cmd-ack-1",
    }


def test_selected_participant_response_submits_speak_then_acks_selected_cursor() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS,
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )

    result = decode(
        handle_selected_participant_response(
            _args(),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result == {
        "ok": True,
        "tool": "kan_selected_participant_response",
        "live_readiness": False,
        "data": {
            "selected_member": "kas",
            "speaker_selected_event_id": "evt-selected",
            "speaker_selected_cursor": "cur_000000000042_evt_selected",
            "speak": {
                "command_id": "cmd-speak-1",
                "event_id": "evt-speak-1",
                "session_id": "sess-partc",
                "request_id": "req-speak-1",
            },
            "ack": {
                "command_id": "cmd-ack-1",
                "event_id": "evt-ack-1",
                "session_id": "sess-partc",
                "request_id": "plugin-live-stream-ack",
                "deduplicated": False,
            },
            "proof": {
                "source": "control_membr_evidence",
                "runner_invocation_id": "run_cmd-grant-1_1",
                "runner_terminal_event_id": "evt-run-terminal",
                "no_role_substitution": True,
                "real_profile_live_invocation": False,
            },
        },
    }
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
        OP_VERSION_READ,
        OP_STREAM_ACK,
    ]
    submitted = transport.requests[1][1]
    assert submitted is not None
    assert submitted["command"] == "council.speak"
    assert submitted["request_id"] == "req-speak-1"
    assert submitted["idempotency_key"] == "idem-speak-1"
    assert submitted["payload"] == {
        "session_id": "sess-partc",
        "actor": "kas",
        "command_id": "cmd-speak-1",
        "payload": {
            "speech": "KAS bounded participant response from wrapper evidence.",
            "turn": 3,
            "evidence": {
                "source": "control_membr_evidence",
                "speaker_selected_event_id": "evt-selected",
                "speaker_selected_cursor": "cur_000000000042_evt_selected",
                "runner_invocation_id": "run_cmd-grant-1_1",
                "runner_started_event_id": "evt-run-started",
                "runner_terminal_event_id": "evt-run-terminal",
                "runner_terminal_event_type": "participant_response",
                "adapter_kind": "hermes-agent",
                "wrapper_binding_evidence": "redacted_wrapper_binding",
                "no_role_substitution": True,
                "real_profile_live_invocation": False,
            },
        },
    }
    assert transport.requests[3] == (
        OP_STREAM_ACK,
        {
            "protocol_version": "kan-protocol-v1alpha0",
            "session_id": "sess-partc",
            "member": "kas",
            "cursor": "cur_000000000042_evt_selected",
            "command_id": "cmd-ack-1",
        },
    )


def test_selected_participant_response_passes_explicit_argue_fields_only_when_supplied() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS,
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )
    args = _args()
    response = cast(JsonObject, args["participant_response"])
    response.update(
        {
            "claims": [
                {
                    "claim_id": "T03.C1",
                    "summary": "Fixture publication is not runtime validation evidence.",
                    "kind": "risk",
                }
            ],
            "stance_links": [
                {
                    "target_event_id": "evt_argument_graph_support_prior_council",
                    "target_claim_id": "T02.C1",
                    "stance": "support",
                    "rationale": (
                        "Static fixtures are the right handoff before runtime enforcement."
                    ),
                }
            ],
            "contribution_type": "support",
            "new_axis_reason": None,
            "evidence": [],
            "responds_to_event_id": "evt_legacy_hint",
        }
    )

    result = decode(
        handle_selected_participant_response(args, client_factory=factory_for_transport(transport))
    )

    assert result["ok"] is True
    submitted = transport.requests[1][1]
    assert submitted is not None
    submitted_payload = cast(JsonObject, cast(JsonObject, submitted["payload"])["payload"])
    assert submitted_payload["claims"] == response["claims"]
    assert submitted_payload["stance_links"] == response["stance_links"]
    assert submitted_payload["contribution_type"] == "support"
    assert submitted_payload["new_axis_reason"] is None
    assert submitted_payload["evidence"] == []
    assert submitted_payload["responds_to_event_id"] == "evt_legacy_hint"
    assert "plugin_evidence" in submitted_payload
    assert (
        cast(JsonObject, submitted_payload["plugin_evidence"])["source"] == "control_membr_evidence"
    )


@pytest.mark.parametrize(
    "message",
    [
        "WARNING: max iterations reached before the participant produced a final answer.",
        'Traceback (most recent call last):\n  File "runner.py", line 1',
        "Tool run diagnostics: command exited before visible response.",
    ],
)
def test_selected_participant_response_rejects_runtime_noise_before_transport(
    message: str,
) -> None:
    args = _args()
    cast(JsonObject, args["participant_response"])["message"] = message

    result = decode(handle_selected_participant_response(args, client_factory=never_client_factory))

    assert result["ok"] is False
    assert result["tool"] == "kan_selected_participant_response"
    assert result["error"] == {
        "category": "validation",
        "message": "participant_response.message contains runtime/system noise",
        "retryable": False,
    }


def test_selected_participant_response_allows_normal_warning_word_in_speech() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS,
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )
    args = _args()
    cast(JsonObject, args["participant_response"])["message"] = (
        "I disagree with the warning that this rollout is too risky; the evidence is bounded."
    )

    result = decode(
        handle_selected_participant_response(args, client_factory=factory_for_transport(transport))
    )

    assert result["ok"] is True


def test_selected_participant_response_rejects_invalid_argue_fields_before_transport() -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    args = _args()
    response = cast(JsonObject, args["participant_response"])
    response.update(
        {
            "claims": [
                {
                    "claim_id": "T04.C1",
                    "summary": "Synthesis needs more than one relation target.",
                    "kind": "decision_frame",
                }
            ],
            "stance_links": [
                {
                    "target_event_id": "evt_argument_graph_support_prior_council",
                    "target_claim_id": "T02.C1",
                    "stance": "synthesize",
                }
            ],
            "contribution_type": "synthesize",
        }
    )

    result = decode(handle_selected_participant_response(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["tool"] == "kan_selected_participant_response"
    assert result["error"] == {
        "category": "validation",
        "message": (
            "participant_response.stance_links must include at least two links for synthesize"
        ),
        "retryable": False,
    }
    assert client_factory_called is False


def test_selected_participant_response_rejects_role_substitution_before_transport() -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    args = _args()
    response = cast(JsonObject, args["participant_response"])
    args["participant_response"] = {**response, "role_substitution": True}

    result = decode(handle_selected_participant_response(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["tool"] == "kan_selected_participant_response"
    assert result["error"] == {
        "category": "validation",
        "message": "participant_response.role_substitution must be false",
        "retryable": False,
    }
    assert client_factory_called is False


def test_selected_participant_response_rejects_member_mismatch_before_transport() -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    args = _args()
    response = cast(JsonObject, args["participant_response"])
    args["participant_response"] = {**response, "member": "kah"}

    result = decode(handle_selected_participant_response(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "participant_response.member must match selected_member",
        "retryable": False,
    }
    assert client_factory_called is False


def test_selected_participant_response_rejects_caller_context_selected_event_mismatch() -> None:
    args = _args()
    args["caller_validation_context"] = {"selected_event_id": "evt-other"}

    result = decode(handle_selected_participant_response(args, client_factory=never_client_factory))

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": (
            "caller_validation_context.selected_event_id must match "
            "speaker_selected_frame.event.event_id"
        ),
        "retryable": False,
    }


@pytest.mark.parametrize(
    ("mutate_args", "message"),
    [
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["speaker_selected_frame"])["event"]
            ).__setitem__("type", "hand_raise_requested"),
            "speaker_selected_frame.event.type must be speaker_selected",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["speaker_selected_frame"])["event"]
            ).__setitem__("session_id", "sess-other"),
            "speaker_selected_frame.event.session_id must match session_id",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["speaker_selected_frame"])["event"]
            ).__setitem__("to", ["kah"]),
            "speaker_selected_frame.event.to must select exactly selected_member",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["speaker_selected_frame"])["event"]
            ).__setitem__("to", ["kas", "kah"]),
            "speaker_selected_frame.event.to must select exactly selected_member",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["speaker_selected_frame"])["event"]
            ).pop("to"),
            "speaker_selected_frame.event.to must select exactly selected_member",
        ),
        (
            lambda args: cast(JsonObject, args["participant_response"]).__setitem__(
                "source", "role_prompt"
            ),
            "participant_response.source must be control_membr_evidence",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["participant_response"])["runner"]
            ).__setitem__("adapter_kind", "role-prompt"),
            "participant_response.runner.adapter_kind must be hermes-agent",
        ),
        (
            lambda args: cast(
                JsonObject, cast(JsonObject, args["participant_response"])["runner"]
            ).__setitem__("terminal_event_type", "runner_invocation_failed"),
            "participant_response.runner.terminal_event_type must be participant_response",
        ),
    ],
)
def test_selected_participant_response_rejects_invalid_membr_evidence_before_transport(
    mutate_args: Callable[[JsonObject], object], message: str
) -> None:
    client_factory_called = False

    def client_factory() -> DaemonClient:
        nonlocal client_factory_called
        client_factory_called = True
        raise AssertionError("client factory must not be called")

    args = _args()
    mutate_args(args)

    result = decode(handle_selected_participant_response(args, client_factory=client_factory))

    assert result["ok"] is False
    assert result["tool"] == "kan_selected_participant_response"
    assert result["error"] == {
        "category": "validation",
        "message": message,
        "retryable": False,
    }
    assert client_factory_called is False


def test_selected_participant_response_rejects_quality_required_orphan() -> None:
    args = _args()
    args["caller_validation_context"] = {
        "quality_mode": "quality_required",
        "local_context_sufficient": True,
        "is_opening_speech": False,
        "prior_claims": [{"event_id": "evt-prior", "claim_id": "T02.C1"}],
    }

    result = decode(handle_selected_participant_response(args, client_factory=never_client_factory))

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": (
            "participant_response is orphan speech in quality_required caller_validation_context"
        ),
        "retryable": False,
    }


def test_selected_participant_response_preserves_daemon_authority_when_context_ambiguous() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS,
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )
    args = _args()
    args["caller_validation_context"] = {"quality_mode": "quality_required"}

    result = decode(
        handle_selected_participant_response(args, client_factory=factory_for_transport(transport))
    )

    assert result["ok"] is True
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
        OP_VERSION_READ,
        OP_STREAM_ACK,
    ]


def test_selected_participant_response_quality_required_valid_prior_target_link_passes() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS,
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )
    args = _args()
    cast(JsonObject, args["participant_response"]).update(
        {
            "claims": [{"claim_id": "T03.C1", "summary": "Relation evidence stays local."}],
            "stance_links": [
                {
                    "target_event_id": "evt-prior",
                    "target_claim_id": "T02.C1",
                    "stance": "support",
                    "rationale": "The prior claim is the accepted target.",
                }
            ],
            "contribution_type": "support",
        }
    )
    args["caller_validation_context"] = {
        "quality_mode": "quality_required",
        "local_context_sufficient": True,
        "is_opening_speech": False,
        "prior_claims": [{"event_id": "evt-prior", "claim_id": "T02.C1"}],
    }

    result = decode(
        handle_selected_participant_response(args, client_factory=factory_for_transport(transport))
    )

    assert result["ok"] is True
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
        OP_VERSION_READ,
        OP_STREAM_ACK,
    ]


def test_selected_participant_response_quality_required_unknown_target_event_fails() -> None:
    args = _args()
    cast(JsonObject, args["participant_response"]).update(
        {
            "claims": [{"claim_id": "T03.C1", "summary": "Relation evidence stays local."}],
            "stance_links": [
                {
                    "target_event_id": "evt-unknown",
                    "target_claim_id": "T02.C1",
                    "stance": "support",
                    "rationale": "The event is not caller-provided.",
                }
            ],
            "contribution_type": "support",
        }
    )
    args["caller_validation_context"] = {
        "quality_mode": "quality_required",
        "local_context_sufficient": True,
        "is_opening_speech": False,
        "prior_claims": [{"event_id": "evt-prior", "claim_id": "T02.C1"}],
    }

    result = decode(handle_selected_participant_response(args, client_factory=never_client_factory))

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": (
            "participant_response.stance_links[0].target_event_id is not in "
            "caller_validation_context.prior_claims"
        ),
        "retryable": False,
    }


def test_selected_participant_response_rejects_stance_target_contradicting_context() -> None:
    args = _args()
    cast(JsonObject, args["participant_response"]).update(
        {
            "claims": [{"claim_id": "T03.C1", "summary": "Relation evidence stays local."}],
            "stance_links": [
                {
                    "target_event_id": "evt-prior",
                    "target_claim_id": "T99.C1",
                    "stance": "support",
                    "rationale": "This should fail because the claim is not in local context.",
                }
            ],
            "contribution_type": "support",
        }
    )
    args["caller_validation_context"] = {
        "quality_mode": "quality_required",
        "local_context_sufficient": True,
        "is_opening_speech": False,
        "prior_claims": [{"event_id": "evt-prior", "claim_id": "T02.C1"}],
    }

    result = decode(handle_selected_participant_response(args, client_factory=never_client_factory))

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": (
            "participant_response.stance_links[0].target_claim_id is not in "
            "caller_validation_context.prior_claims"
        ),
        "retryable": False,
    }


def test_selected_participant_response_quality_required_new_axis_with_reason_passes() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS,
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )
    args = _args()
    cast(JsonObject, args["participant_response"]).update(
        {
            "claims": [{"claim_id": "T03.C1", "summary": "A new acceptance axis is needed."}],
            "contribution_type": "new_axis",
            "new_axis_reason": "The prior graph has no claim about prompt target guidance.",
        }
    )
    args["caller_validation_context"] = {
        "quality_mode": "quality_required",
        "local_context_sufficient": True,
        "is_opening_speech": False,
        "prior_claims": [{"event_id": "evt-prior", "claim_id": "T02.C1"}],
    }

    result = decode(
        handle_selected_participant_response(args, client_factory=factory_for_transport(transport))
    )

    assert result["ok"] is True


def test_selected_participant_response_quality_required_new_axis_without_reason_fails() -> None:
    args = _args()
    cast(JsonObject, args["participant_response"]).update(
        {
            "claims": [{"claim_id": "T03.C1", "summary": "A new acceptance axis is needed."}],
            "contribution_type": "new_axis",
        }
    )
    args["caller_validation_context"] = {
        "quality_mode": "quality_required",
        "local_context_sufficient": True,
        "is_opening_speech": False,
        "prior_claims": [{"event_id": "evt-prior", "claim_id": "T02.C1"}],
    }

    result = decode(handle_selected_participant_response(args, client_factory=never_client_factory))

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": "participant_response.new_axis_reason must be a non-empty string",
        "retryable": False,
    }


def test_selected_participant_response_quality_warn_orphan_passes() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS,
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )
    args = _args()
    args["caller_validation_context"] = {
        "quality_mode": "quality_warn",
        "local_context_sufficient": True,
        "is_opening_speech": False,
        "prior_claims": [{"event_id": "evt-prior", "claim_id": "T02.C1"}],
    }

    result = decode(
        handle_selected_participant_response(args, client_factory=factory_for_transport(transport))
    )

    assert result["ok"] is True


def test_selected_participant_response_quality_warn_unknown_target_is_warning_only() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: BASE_COMMAND_SUCCESS,
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )
    args = _args()
    cast(JsonObject, args["participant_response"]).update(
        {
            "claims": [{"claim_id": "T03.C1", "summary": "Warning-only invalid target."}],
            "stance_links": [
                {
                    "target_event_id": "evt-unknown",
                    "target_claim_id": "T99.C1",
                    "stance": "support",
                    "rationale": "Quality warn must not block transport.",
                }
            ],
            "contribution_type": "support",
        }
    )
    args["caller_validation_context"] = {
        "quality_mode": "quality_warn",
        "local_context_sufficient": True,
        "is_opening_speech": False,
        "prior_claims": [{"event_id": "evt-prior", "claim_id": "T02.C1"}],
    }

    result = decode(
        handle_selected_participant_response(args, client_factory=factory_for_transport(transport))
    )

    assert result["ok"] is True


def test_selected_participant_response_responds_to_event_id_does_not_satisfy_relation() -> None:
    args = _args()
    cast(JsonObject, args["participant_response"]).update(
        {
            "claims": [{"claim_id": "T03.C1", "summary": "Legacy hints are display-only."}],
            "contribution_type": "support",
            "responds_to_event_id": "evt-prior",
        }
    )
    args["caller_validation_context"] = {
        "quality_mode": "quality_required",
        "local_context_sufficient": True,
        "is_opening_speech": False,
        "prior_claims": [{"event_id": "evt-prior", "claim_id": "T02.C1"}],
    }

    result = decode(handle_selected_participant_response(args, client_factory=never_client_factory))

    assert result["ok"] is False
    assert result["error"] == {
        "category": "validation",
        "message": (
            "participant_response is orphan speech in quality_required caller_validation_context"
        ),
        "retryable": False,
    }


def test_selected_participant_response_does_not_ack_when_speak_submit_fails() -> None:
    transport = StaticDaemonTransport(
        {
            OP_VERSION_READ: BASE_VERSION_WITH_PARTC,
            OP_COMMAND_SUBMIT: {
                "ok": False,
                "error": {
                    "category": "conflict",
                    "message": "speaker grant is missing",
                    "retryable": False,
                    "session_id": "sess-partc",
                    "request_id": "req-speak-1",
                },
            },
            OP_STREAM_ACK: BASE_ACK_SUCCESS,
        }
    )

    result = decode(
        handle_selected_participant_response(
            _args(),
            client_factory=factory_for_transport(transport),
        )
    )

    assert result["ok"] is False
    assert result["tool"] == "kan_selected_participant_response"
    assert result["error"]["category"] == "conflict"
    assert [operation for operation, _body in transport.requests] == [
        OP_VERSION_READ,
        OP_COMMAND_SUBMIT,
    ]
