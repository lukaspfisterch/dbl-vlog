from __future__ import annotations

from dbl_vlog import DblEvent, DblEventKind, event_digest, event_digest_hex


def test_same_event_same_digest() -> None:
    e1 = DblEvent(
        kind=DblEventKind.DECISION,
        deterministic_fields={"a": 1, "b": "x"},
        observational_fields={"t": "ignored"},
    )
    e2 = DblEvent(
        kind=DblEventKind.DECISION,
        deterministic_fields={"b": "x", "a": 1},
        observational_fields={"t": "different"},
    )
    assert event_digest(e1) == event_digest(e2)
    assert event_digest_hex(e1) == event_digest_hex(e2)


def test_unicode_normalization_is_deterministic() -> None:
    # "e" with acute can be composed or decomposed; NFC normalization should unify.
    composed = "é"
    decomposed = "e\u0301"

    e1 = DblEvent(
        kind=DblEventKind.INTENT,
        deterministic_fields={"s": composed},
        observational_fields={},
    )
    e2 = DblEvent(
        kind=DblEventKind.INTENT,
        deterministic_fields={"s": decomposed},
        observational_fields={},
    )
    assert event_digest(e1) == event_digest(e2)
