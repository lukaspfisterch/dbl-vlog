from __future__ import annotations

from .model import DblEventKind
from .v import BehaviorV


def project_normative(v: BehaviorV) -> BehaviorV:
    """
    Normative projection V_norm: DECISION-only stream, order preserved.
    """
    dec = tuple(e for e in v.events if e.kind == DblEventKind.DECISION)
    return BehaviorV(events=dec)
