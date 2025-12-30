from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any


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
    deterministic_fields: Mapping[str, Any] = field(default_factory=dict)
    observational_fields: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.deterministic_fields, Mapping):
            raise TypeError("deterministic_fields must be a mapping[str, Any]")
        if not isinstance(self.observational_fields, Mapping):
            raise TypeError("observational_fields must be a mapping[str, Any]")
        object.__setattr__(
            self,
            "deterministic_fields",
            MappingProxyType(dict(self.deterministic_fields)),
        )
        object.__setattr__(
            self,
            "observational_fields",
            MappingProxyType(dict(self.observational_fields)),
        )
