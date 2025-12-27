from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class DblEventKind(str, Enum):
    INTENT = "INTENT"
    DECISION = "DECISION"
    EXECUTION = "EXECUTION"
    PROOF = "PROOF"


JsonMap = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class DblEvent:
    """
    DBL core event with strict field separation.

    - deterministic_fields participate in digests
    - observational_fields are excluded from digests and normative projections
    """
    kind: DblEventKind
    deterministic_fields: dict[str, Any] = field(default_factory=dict)
    observational_fields: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.deterministic_fields, dict):
            raise TypeError("deterministic_fields must be a dict[str, Any]")
        if not isinstance(self.observational_fields, dict):
            raise TypeError("observational_fields must be a dict[str, Any]")
