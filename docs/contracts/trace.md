# Trace Contract

Public contract for DBL traces as represented in V.

## Event kinds
- INTENT
- DECISION
- EXECUTION
- PROOF

## Fields
- Deterministic fields participate in digests and replay semantics.
- Observational fields are excluded from digests and have no normative effect.
Events are immutable; field maps are read-only. Nested values can still be mutable
and must be treated as immutable by callers.

## Per-request key
- `correlation_id` is the canonical per-request key.
Other IDs (e.g., `request_id`) are allowed but non-canonical and ignored by verifiers.
`correlation_id` must be a non-empty string.

## Digest label format
- `sha256:<64hex>`

## Hash format requirements
`boundary_config_hash`, `input_digest`, and `intent_digest` must be `sha256:` labels.

## Minimal deterministic fields

INTENT requires:
- `boundary_version`
- `boundary_config_hash`
- `input_digest` or `intent_digest`

DECISION requires:
- `policy_version` or `policy_digest`

## Purpose
This is the schema-level truth that downstream consumers (enforcers, tools,
validators) rely on for trace validity.

## Versioning
Contract changes require a library minor bump; breaking changes require a major bump.
