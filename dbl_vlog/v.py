from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Tuple

from .digest import event_digest, v_digest
from .model import DblEvent


@dataclass(frozen=True, slots=True)
class BehaviorV:
    """
    Immutable append-only event stream V.

    Total order is tuple order. Index t(e) is the position in this tuple.
    """
    events: Tuple[DblEvent, ...] = ()

    def __len__(self) -> int:
        return len(self.events)

    def __iter__(self) -> Iterator[DblEvent]:
        return iter(self.events)

    def __repr__(self) -> str:
        if not self.events:
            return "BehaviorV(len=0)"
        digest_prefix = self.digest_hex()[:8]
        return f"BehaviorV(len={len(self)}, digest={digest_prefix}...)"

    def at(self, index: int) -> DblEvent:
        return self.events[index]

    def append(self, event: DblEvent) -> "BehaviorV":
        return BehaviorV(events=self.events + (event,))

    def event_digests(self) -> list[bytes]:
        return [event_digest(e) for e in self.events]

    def digest(self) -> bytes:
        return v_digest(self.event_digests())

    def digest_hex(self) -> str:
        return self.digest().hex()


def append_event(v: BehaviorV, event: DblEvent) -> BehaviorV:
    return v.append(event)
