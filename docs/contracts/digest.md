# Canonicalization and Digest Contract

Defines deterministic encoding rules and digest semantics.

## Canonicalization
- Reject floats and non-JSON-safe types.
- Normalize strings to NFC.
- Dict keys must be strings.
Object keys are sorted lexicographically during canonical JSON serialization.

## Forbidden keys guard
- Deterministic fields are checked against a case-insensitive forbidden list
  to prevent obvious observational data from entering the deterministic surface.
The forbidden keys list is implementation-defined and may expand; it is a safety rail,
not part of compatibility.

The `enforce_keys` flag may disable this guard for testing; it does not change
compatibility expectations.

## event_digest
- Hashes canonical JSON of deterministic payload only.
- Excludes observational fields.
- Excludes stream index t(e).

## event_canonical_bytes
- Returns canonical JSON bytes of the digest payload without hashing.
- Intended for test vectors and external validators.

## v_digest
- Commits to ordered pairs of (index, event_digest).

## Purpose
This contract is the determinism anchor; compatible implementations must
produce identical bytes and hashes.

## Compatibility scope
Compatible means:
- same `schema_version`
- same canonicalization rules
- same digest payload structure

Non-goal: compatibility across alternative encodings or canonicalizers.

## Versioning
`schema_version` is part of compatibility. Contract changes require a library minor
bump; breaking changes require a major bump.
