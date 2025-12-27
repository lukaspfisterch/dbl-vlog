# dbl-vlog

**dbl-vlog** implements the append-only event stream **V** for *Deterministic Boundary Layers (DBL)*.

It provides a minimal, reference-grade substrate for recording events with deterministic
canonicalization and cryptographic digests, enabling auditability, replay, and strict
separation of normative and observational data.

This library implements **only V** and its invariants.

---

## Scope and guarantees

dbl-vlog provides the following guarantees by construction:

- **Append-only, immutable event stream (V)**
  Events are immutable once appended. Stream extensions are prefix-only.

- **Deterministic canonicalization**
  Deterministic fields are transformed into stable, platform-independent bytes.

- **Cryptographic digests**
  - Content-based event digests (order-independent)
  - Stream digests committing to event order

- **Normative vs observational separation**
  - Deterministic fields participate in digests
  - Observational fields are explicitly excluded and cannot influence replay or projection

- **Normative projection**
  Deterministic extraction of DECISION-only streams (V_norm).

---

## Explicit non-goals

dbl-vlog deliberately does **not** implement:

- boundaries or admission logic (L)
- governance or policy evaluation (G)
- execution, effectors, or LLM integration
- network services, persistence backends, or consensus
- adaptive or learning-based behavior

dbl-vlog is a substrate, not a system.

---

## Conceptual position in DBL

Raw inputs
│
▼
[ Boundaries (L) ]  (not implemented here)
│
▼
[ Governance (G) ]  (not implemented here)
│
▼
DECISION events
│
▼
┌─────────────────────┐
│ dbl-vlog (V)         │  ← this library
│ append-only log      │
│ deterministic V      │
└─────────────────────┘
│
▼
Execution / Observation  (out of scope)

dbl-vlog is authoritative **only** for the structure and integrity of **V**.

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
- ordering sensitivity of V digests
- canonicalization rejection of ambiguous types

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

---

## License

MIT
