from __future__ import annotations

from dbl_vlog import BehaviorV, DblEvent, DblEventKind


def test_append_preserves_order_and_changes_v_digest() -> None:
    v0 = BehaviorV()
    e0 = DblEvent(kind=DblEventKind.INTENT, deterministic_fields={"i": 0}, observational_fields={})
    e1 = DblEvent(kind=DblEventKind.DECISION, deterministic_fields={"i": 1}, observational_fields={})

    v1 = v0.append(e0)
    v2 = v1.append(e1)

    assert len(v1) == 1
    assert len(v2) == 2
    assert v2.at(0) == e0
    assert v2.at(1) == e1
    assert v1.digest() != v2.digest()


def test_same_events_different_order_different_v_digest() -> None:
    e0 = DblEvent(kind=DblEventKind.INTENT, deterministic_fields={"i": 0}, observational_fields={})
    e1 = DblEvent(kind=DblEventKind.DECISION, deterministic_fields={"i": 1}, observational_fields={})

    v_a = BehaviorV().append(e0).append(e1)
    v_b = BehaviorV().append(e1).append(e0)

    assert v_a.digest() != v_b.digest()
