# dbl-vlog 0.3.0
[![tests](https://github.com/lukaspfisterch/dbl-vlog/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/lukaspfisterch/dbl-vlog/actions/workflows/tests.yml)

**dbl-vlog** implements the append-only event stream **V** for *Deterministic Boundary Layers (DBL)*.

It provides a minimal, reference-grade substrate for recording events with deterministic
canonicalization and cryptographic digests, for applications requiring reproducible,
verifiable traces where determinism and strict non-interference between normative and
observational data are critical.

This library implements **only V** and its invariants.
"vlog" means V log (not "video log").

---

## Scope and guarantees

dbl-vlog provides the following guarantees by construction:

- **Append-only, immutable event stream (V)**
  Events are immutable at the event surface; nested values must not be mutated by callers.
  Stream extensions are prefix-only.

- **Ordering constraints verification**
  Explicit verification of per-request ordering (DECISION before EXECUTION/PROOF).

- **Deterministic canonicalization**
  Deterministic fields are transformed into stable, platform-independent bytes.

- **Cryptographic digests**
  - Content-based event digests (order-independent)
  - Stream digests committing to event order

- **Normative vs observational separation**
  - Deterministic fields participate in digests
  - Observational fields are explicitly excluded and cannot influence replay or projection

- **Deterministic identity fields**
  Required boundary and policy identity footprints can be verified in deterministic fields.

- **Normative projection**
  Deterministic extraction of DECISION-only streams (V_norm), yielding the normative
  behavior already committed in the stream.

---

## Contracts (normative)

The contracts in `docs/contracts/` are normative for compatibility. If code and contracts
diverge, contracts win (until a versioned contract update).

- `docs/contracts/index.md`
- `docs/contracts/trace.md`
- `docs/contracts/verify.md`
- `docs/contracts/digest.md`

---

## API surface (minimal)

Core functions:
- `verify_append_only(prev_v, next_v)`
- `verify_ordering(v, id_key="correlation_id", require_intent_before_decision=False, disallow_decision_after_execution=True, max_decisions_per_id=1)`
- `verify_identity_fields(v, id_key="correlation_id")`
- `verify_deterministic_is_canonicalizable(v)`
- `project_normative(v)`
- `event_canonical_bytes(event, enforce_keys=True)`

The canonical per-request key in deterministic fields is `correlation_id`.

---

## Explicit non-goals

dbl-vlog deliberately does **not** implement:

- boundaries or admission logic (L)
- governance or policy evaluation (G)
- execution, effectors, or LLM integration
- network services, persistence backends, or consensus
- adaptive or learning-based behavior

dbl-vlog is a substrate, not a system.
Verifier functions validate trace form only; they do not decide content or outcomes.

---

## Conceptual position in DBL

```text
Raw inputs
  |
  v
[ Boundaries (L) ]  (not implemented here)
  |
  v
[ Governance (G) ]  (not implemented here)
  |
  v
DECISION events
  |
  v
┌─────────────────────┐
│ dbl-vlog (V)         │  <- this library
│ append-only log      │
│ deterministic V      │
└─────────────────────┘
  |
  v
Execution / Observation  (out of scope)
```

---

## Installation (editable, development)

```bash
py -3.11 -m pip install -e .
```

## Tests

```bash
py -3.11 -m pytest -q
```

The test suite asserts DBL-critical invariants:

- determinism under reordering of fields
- observational non-interference
- append-only violations
- ordering constraints (DECISION before EXECUTION/PROOF)
- ordering sensitivity of V digests
- canonicalization rejection of ambiguous types
- deterministic identity field requirements (boundary/policy)

## Minimal example

```bash
py -3.11 examples/minimal_usage.py
```

Expected output demonstrates:

- stable event digests
- order-sensitive stream digest
- correct DECISION-only projection

---

## Design notes

- Event digests are content-based and exclude stream index t(e)
- Stream digests commit to (index, event_digest) pairs
- Canonicalization rejects floats, NaN/Inf, datetimes, and non-JSON-safe types
- Unicode strings are normalized to NFC

These choices are conservative by design to prevent semantic drift and
cross-platform ambiguity.

---

## Verifier contracts

`verify_ordering` enforces per-correlation structural constraints:
- EXECUTION/PROOF requires a prior DECISION for the same `correlation_id`.
- Optionally requires INTENT before DECISION.
- By default rejects DECISION after any EXECUTION/PROOF for the same `correlation_id`.
- By default limits DECISION count to `max_decisions_per_id=1` to prevent late normative overrides.

`verify_identity_fields` enforces deterministic trace identity footprints:
- INTENT requires `boundary_version`, `boundary_config_hash`, and `input_digest` or `intent_digest`.
- DECISION requires `policy_version` or `policy_digest`.
- Digest labels must be `sha256:<64 hex>`.

Append-only logs prevent mutation, but not late normative redefinition.
The default verifier settings make the stream suitable as a pre-execution commitment substrate.

---

## Why dbl-vlog is DBL-compliant

dbl-vlog is a reference implementation of the **event stream V** as defined in the
*Deterministic Boundary Layers (DBL)* model.  
It intentionally implements **only V** and enforces its invariants by construction.

This section explains how dbl-vlog aligns with the DBL definitions and axioms.

---

### Scope alignment

dbl-vlog implements:
- the append-only event stream **V**
- deterministic canonicalization and digests
- replay-safe normative projection

dbl-vlog does **not** implement:
- boundaries (L)
- governance (G)
- execution or effectors

This matches the DBL separation of concerns: V is an authoritative record of events,
not a decision engine or execution system.

---

### Append-only event stream (Axiom A1)

DBL requires V to be append-only and immutable.

dbl-vlog enforces this by:
- representing V as an immutable tuple of events
- allowing extension only via append operations
- providing explicit prefix verification (`verify_append_only`)

Once appended, events cannot be mutated or removed.

---

### Normative primacy of DECISION events (Axiom A2)

Under DBL, only DECISION events are normative.

dbl-vlog:
- represents event kinds explicitly (INTENT, DECISION, EXECUTION, PROOF)
- treats only DECISION events as normative
- provides deterministic projection of the DECISION-only stream (V_norm)

All other events are non-normative by construction.

---

### Observational non-interference (Axiom A3)

DBL requires that observational data does not influence governance or replay.

dbl-vlog enforces this structurally:
- deterministic fields participate in digests
- observational fields are explicitly excluded from digests and projections
- changes to observational fields do not affect event or stream digests

This guarantees observational non-interference at the event-substrate level.

---

### Deterministic representation and digests

DBL requires deterministic bytes and replayable auditability.

dbl-vlog provides:
- strict canonicalization of deterministic fields
- rejection of ambiguous types (floats, NaN/Inf, datetimes)
- stable Unicode normalization (NFC)
- cryptographic event digests independent of stream position
- stream digests committing to ordered (index, event_digest) pairs

These choices are conservative and prevent cross-platform or runtime ambiguity.

---

### Replay equivalence (Claim 3)

DBL defines replay as reconstruction of normative state from V alone.

dbl-vlog supports this by:
- preserving total order via stream position t(e)
- excluding observational data from normative projection
- allowing deterministic reconstruction of the DECISION sequence

Replay does not depend on execution behavior, timing, or infrastructure.

---

### No hidden normativity

dbl-vlog introduces no implicit decisions, policies, or side effects.

All normativity must be expressed explicitly as DECISION events produced
by external governance logic (G), which is out of scope for this library.

---

### Summary

dbl-vlog is DBL-compliant because it:
- faithfully implements V and its invariants
- enforces normative minimalism
- guarantees observational non-interference
- enables deterministic replay and auditability

It makes no claims beyond the DBL model and deliberately avoids implementing
components (L, G, execution) that belong to other layers.
For these reasons, dbl-vlog serves as a reliable, reference-grade substrate
for building DBL-compliant systems.

---

## Related repositories

For the full DBL axiom set and reference execution semantics, see:
- **[dbl-reference](https://github.com/lukaspfisterch/dbl-reference)**

For the shared conceptual core (events, phases, separation), see:
- **[dbl-core](https://github.com/lukaspfisterch/dbl-core)**

For the architectural overview and repository map, see:
- **[deterministic-boundary-layer](https://github.com/lukaspfisterch/deterministic-boundary-layer)**

dbl-vlog implements only the event substrate V and intentionally excludes boundary
admission, governance, and execution.
