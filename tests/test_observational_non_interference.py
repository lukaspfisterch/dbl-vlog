from __future__ import annotations

from dbl_vlog import DblEvent, DblEventKind, event_digest


def test_observational_changes_do_not_affect_digest() -> None:
    base = DblEvent(
        kind=DblEventKind.EXECUTION,
        deterministic_fields={"correlation_id": "r-1", "status": "ok"},
        observational_fields={"latency_ms": 10, "output": "hello"},
    )
    changed = DblEvent(
        kind=DblEventKind.EXECUTION,
        deterministic_fields={"correlation_id": "r-1", "status": "ok"},
        observational_fields={"latency_ms": 9999, "output": "different"},
    )
    assert event_digest(base) == event_digest(changed)
