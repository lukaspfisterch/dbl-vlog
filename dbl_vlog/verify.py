from __future__ import annotations

from .exceptions import AppendOnlyViolation
from .v import BehaviorV


def verify_append_only(prev_v: BehaviorV, next_v: BehaviorV) -> None:
    """
    Verify that next_v extends prev_v by appending events only.

    This checks structural prefix equality of events, not only digests.
    """
    if len(next_v) < len(prev_v):
        raise AppendOnlyViolation("next_v is shorter than prev_v")

    prev_events = prev_v.events
    next_events = next_v.events[: len(prev_events)]
    if next_events != prev_events:
        raise AppendOnlyViolation("prefix mismatch: stream is not append-only")
