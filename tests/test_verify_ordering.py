from __future__ import annotations

import pytest

from dbl_vlog import (
    BehaviorV,
    DblEvent,
    DblEventKind,
    OrderingViolation,
    verify_ordering,
)


def test_verify_ordering_rejects_execution_before_decision() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.EXECUTION,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    )
    with pytest.raises(OrderingViolation):
        verify_ordering(v)


def test_verify_ordering_allows_execution_after_decision_without_intent() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.DECISION,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    ).append(
        DblEvent(
            kind=DblEventKind.EXECUTION,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    )
    verify_ordering(v)


def test_verify_ordering_can_require_intent_before_decision() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.DECISION,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    )
    with pytest.raises(OrderingViolation):
        verify_ordering(v, require_intent_before_decision=True)


def test_verify_ordering_disallows_decision_after_execution() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.DECISION,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    ).append(
        DblEvent(
            kind=DblEventKind.EXECUTION,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    ).append(
        DblEvent(
            kind=DblEventKind.DECISION,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    )
    with pytest.raises(OrderingViolation):
        verify_ordering(v)


def test_verify_ordering_limits_decision_count() -> None:
    v = BehaviorV().append(
        DblEvent(
            kind=DblEventKind.DECISION,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    ).append(
        DblEvent(
            kind=DblEventKind.DECISION,
            deterministic_fields={"correlation_id": "c-1"},
            observational_fields={},
        )
    )
    with pytest.raises(OrderingViolation):
        verify_ordering(v)
