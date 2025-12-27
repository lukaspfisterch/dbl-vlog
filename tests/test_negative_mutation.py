from __future__ import annotations

import pytest

from dbl_vlog import (
    AppendOnlyViolation,
    BehaviorV,
    CanonicalizationError,
    DblEvent,
    DblEventKind,
    verify_append_only,
)
from dbl_vlog.digest import event_digest


def test_event_is_frozen_and_cannot_be_mutated() -> None:
    e = DblEvent(kind=DblEventKind.INTENT, deterministic_fields={"a": 1}, observational_fields={})
    with pytest.raises(Exception):
        # dataclass is frozen
        e.kind = DblEventKind.DECISION  # type: ignore[misc]


def test_stream_is_immutable_tuple() -> None:
    v = BehaviorV()
    assert isinstance(v.events, tuple)
    with pytest.raises(Exception):
        # tuples do not support item assignment
        v.events[0] = DblEvent(kind=DblEventKind.INTENT, deterministic_fields={}, observational_fields={})  # type: ignore[index]


def test_verify_append_only_detects_prefix_mismatch() -> None:
    e0 = DblEvent(kind=DblEventKind.INTENT, deterministic_fields={"i": 0}, observational_fields={})
    e1 = DblEvent(kind=DblEventKind.INTENT, deterministic_fields={"i": 1}, observational_fields={})

    prev_v = BehaviorV().append(e0).append(e1)

    # Construct next_v that changes history by replacing e1
    e1_alt = DblEvent(kind=DblEventKind.INTENT, deterministic_fields={"i": 999}, observational_fields={})
    next_v = BehaviorV(events=(e0, e1_alt,))

    with pytest.raises(AppendOnlyViolation):
        verify_append_only(prev_v, next_v)


def test_float_in_deterministic_fields_is_rejected() -> None:
    e = DblEvent(
        kind=DblEventKind.INTENT,
        deterministic_fields={"x": 1.5},
        observational_fields={},
    )
    with pytest.raises(CanonicalizationError):
        event_digest(e)


def test_forbidden_key_in_deterministic_fields_is_rejected() -> None:
    e = DblEvent(
        kind=DblEventKind.INTENT,
        deterministic_fields={"output": "should not be here"},
        observational_fields={},
    )
    with pytest.raises(CanonicalizationError):
        event_digest(e)
