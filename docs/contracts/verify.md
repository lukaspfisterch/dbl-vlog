# Verifier Semantics Contract

Defines what the verifier functions guarantee and what they do not.

## verify_append_only
- Checks prefix equality between streams.
- Verifies structural equality of events, not just digest equality.

## verify_deterministic_is_canonicalizable
- Ensures deterministic fields are canonicalizable under the contract rules.

## verify_ordering (defaults)
- All events require `correlation_id`.
- DECISION must exist before EXECUTION/PROOF for the same `correlation_id`.
- DECISION after EXECUTION/PROOF is rejected by default.
- `max_decisions_per_id=1` by default.
- `require_intent_before_decision` is optional and off by default.

Defaults are recommended safety rails. Callers may relax them.
Relaxing them changes trace admissibility for pre-execution commitment use.

## Non-goals
- Verifiers do not perform governance.
- Verifiers do not decide ALLOW/DENY or evaluate policy content.

## Purpose
These checks ensure the stream is DBL-semantically usable and prevent late
normative overrides while keeping governance external.

## Versioning
Contract changes require a library minor bump; breaking changes require a major bump.
