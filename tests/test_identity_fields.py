from __future__ import annotations

import pytest

from dbl_vlog import (
    BehaviorV,
    DblEvent,
    DblEventKind,
    IdentityViolation,
    verify_identity_fields,
)


def test_intent_requires_boundary_identity_fields() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.INTENT,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    )
    with pytest.raises(IdentityViolation):
        verify_identity_fields(v)


def test_decision_requires_policy_identity_fields() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.DECISION,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    )
    with pytest.raises(IdentityViolation):
        verify_identity_fields(v)


def test_policy_digest_satisfies_identity_requirement() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.DECISION,
            deterministic_fields={"correlation_id": "c-1", "policy_digest": "sha256:" + "0" * 64},
            observational_fields={},
        )
    )
    verify_identity_fields(v)


def test_invalid_policy_digest_is_rejected() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.DECISION,
            deterministic_fields={"correlation_id": "c-1", "policy_digest": "banana"},
            observational_fields={},
        )
    )
    with pytest.raises(IdentityViolation):
        verify_identity_fields(v)


def test_intent_requires_input_or_intent_digest() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.INTENT,
            deterministic_fields={
                "correlation_id": "c-1",
                "boundary_version": 1,
                "boundary_config_hash": "sha256:" + "0" * 64,
            },
            observational_fields={},
        )
    )
    with pytest.raises(IdentityViolation):
        verify_identity_fields(v)


def test_intent_digest_must_be_sha256_label() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.INTENT,
            deterministic_fields={
                "correlation_id": "c-1",
                "boundary_version": 1,
                "boundary_config_hash": "sha256:" + "0" * 64,
                "intent_digest": "banana",
            },
            observational_fields={},
        )
    )
    with pytest.raises(IdentityViolation):
        verify_identity_fields(v)


def test_input_digest_satisfies_identity_requirement() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.INTENT,
            deterministic_fields={
                "correlation_id": "c-1",
                "boundary_version": 1,
                "boundary_config_hash": "sha256:" + "0" * 64,
                "input_digest": "sha256:" + "1" * 64,
            },
            observational_fields={},
        )
    )
    verify_identity_fields(v)
