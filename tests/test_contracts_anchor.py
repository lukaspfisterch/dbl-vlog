from __future__ import annotations

from dbl_vlog.canonical import DEFAULT_FORBIDDEN_KEYS
from dbl_vlog.digest import SCHEMA_VERSION
from dbl_vlog.model import DblEventKind


def test_schema_version_is_stable() -> None:
    assert SCHEMA_VERSION == 1


def test_forbidden_keys_cover_core_observational_terms() -> None:
    expected = {"output", "error", "latency", "trace"}
    assert expected.issubset({k.casefold() for k in DEFAULT_FORBIDDEN_KEYS})


def test_event_kinds_are_fixed() -> None:
    assert {k.value for k in DblEventKind} == {"INTENT", "DECISION", "EXECUTION", "PROOF"}
