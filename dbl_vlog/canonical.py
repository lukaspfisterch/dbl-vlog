from __future__ import annotations

import json
import unicodedata
from collections.abc import Mapping
from typing import Any, Iterable

from .exceptions import CanonicalizationError


DEFAULT_FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {
        "output",
        "outputs",
        "trace",
        "traces",
        "timing",
        "latency",
        "duration",
        "error",
        "errors",
        "exception",
        "stack",
        "metrics",
        "log",
        "logs",
    }
)


def _norm_str(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def enforce_forbidden_keys(
    deterministic_fields: Mapping[str, Any],
    forbidden_keys: Iterable[str] = DEFAULT_FORBIDDEN_KEYS,
) -> None:
    """
    Best-effort guard to prevent obvious observational keys from entering deterministic_fields.
    Comparison is case-insensitive, and checks only keys (not values).
    """
    deny = {k.casefold() for k in forbidden_keys}
    for k in deterministic_fields.keys():
        if k.casefold() in deny:
            raise CanonicalizationError(
                f"forbidden key in deterministic_fields: {k!r}"
            )


def canonicalize_value(v: Any) -> Any:
    """
    Convert a Python value into a strictly JSON-safe canonical form.

    Conservative rules:
    - Reject floats and non-JSON types to avoid cross-platform ambiguity.
    - Normalize all strings to Unicode NFC.
    - Dict keys must be strings.
    """
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        return _norm_str(v)

    if isinstance(v, float):
        raise CanonicalizationError("floats are forbidden in deterministic canonicalization")

    if isinstance(v, (bytes, bytearray)):
        raise CanonicalizationError("bytes are forbidden in deterministic canonicalization")

    if isinstance(v, (list, tuple)):
        return [canonicalize_value(x) for x in v]

    if isinstance(v, Mapping):
        out: dict[str, Any] = {}
        for k, val in v.items():
            if not isinstance(k, str):
                raise CanonicalizationError("dict keys must be strings")
            nk = _norm_str(k)
            out[nk] = canonicalize_value(val)
        return out

    raise CanonicalizationError(f"unsupported type for deterministic canonicalization: {type(v)!r}")


def canonical_json_bytes(obj: Any) -> bytes:
    """
    Deterministic JSON bytes for a canonicalized object.

    Notes:
    - sort_keys ensures stable ordering
    - separators remove whitespace variability
    - ensure_ascii=False preserves Unicode, combined with NFC normalization
    - allow_nan=False rejects NaN/Infinity
    """
    try:
        s = json.dumps(
            obj,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as e:
        raise CanonicalizationError(str(e)) from e
    return s.encode("utf-8")
