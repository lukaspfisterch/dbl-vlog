from __future__ import annotations


class DblVlogError(Exception):
    """Base exception for dbl_vlog."""


class CanonicalizationError(DblVlogError):
    """Raised when a value cannot be deterministically canonicalized."""


class AppendOnlyViolation(DblVlogError):
    """Raised when a stream transition is not append-only."""
