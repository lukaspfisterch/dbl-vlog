from __future__ import annotations

from .canonical import canonicalize_value
from .exceptions import AppendOnlyViolation, CanonicalizationError, IdentityViolation, OrderingViolation
from .model import DblEvent, DblEventKind
from .v import BehaviorV


def verify_append_only(prev_v: BehaviorV, next_v: BehaviorV) -> None:
    """
    Verify that next_v extends prev_v by appending events only.

    This checks structural prefix equality of events, not only digests.
    """
    if len(next_v) < len(prev_v):
        raise AppendOnlyViolation("next_v is shorter than prev_v")

    prev_events = prev_v.events
    next_events = next_v.events[: len(prev_events)]
    if next_events != prev_events:
        raise AppendOnlyViolation("prefix mismatch: stream is not append-only")


def verify_ordering(
    v: BehaviorV,
    *,
    id_key: str = "correlation_id",
    require_intent_before_decision: bool = False,
    disallow_decision_after_execution: bool = True,
    max_decisions_per_id: int = 1,
) -> None:
    """
    Verify per-request ordering constraints in a stream.

    Rules:
    - If EXECUTION or PROOF appears, a prior DECISION must exist for the same id.
    - If require_intent_before_decision is set, DECISION must follow INTENT.
    """
    seen_intent: set[str] = set()
    seen_decision: dict[str, int] = {}
    seen_execution: set[str] = set()

    for idx, event in enumerate(v.events):
        corr = _require_id(event, id_key=id_key, index=idx)

        if event.kind == DblEventKind.INTENT:
            seen_intent.add(corr)
            continue

        if event.kind == DblEventKind.DECISION:
            if require_intent_before_decision and corr not in seen_intent:
                raise OrderingViolation(
                    f"DECISION observed before INTENT for {id_key}={corr}; index={idx}"
                )
            if disallow_decision_after_execution and corr in seen_execution:
                raise OrderingViolation(
                    f"DECISION observed after EXECUTION/PROOF for {id_key}={corr}; index={idx}"
                )
            count = seen_decision.get(corr, 0) + 1
            if max_decisions_per_id > 0 and count > max_decisions_per_id:
                raise OrderingViolation(
                    f"DECISION count exceeds {max_decisions_per_id} for {id_key}={corr}; index={idx}"
                )
            seen_decision[corr] = count
            continue

        if event.kind in (DblEventKind.EXECUTION, DblEventKind.PROOF):
            if corr not in seen_decision:
                raise OrderingViolation(
                    f"{event.kind.value} observed before DECISION for {id_key}={corr}; index={idx}"
                )
            seen_execution.add(corr)


def verify_identity_fields(
    v: BehaviorV,
    *,
    id_key: str = "correlation_id",
) -> None:
    """
    Verify required deterministic identity fields for DBL trace/policy identity.

    Rules:
    - INTENT requires boundary_version and boundary_config_hash.
    - DECISION requires policy_version or policy_digest.
    """
    for idx, event in enumerate(v.events):
        corr = event.deterministic_fields.get(id_key)
        if isinstance(corr, str):
            corr_label = canonicalize_value(corr)
        else:
            corr_label = "unknown"
        if event.kind == DblEventKind.INTENT:
            missing = [
                k for k in ("boundary_version", "boundary_config_hash")
                if k not in event.deterministic_fields
            ]
            if missing:
                raise IdentityViolation(
                    f"INTENT missing deterministic identity fields: {missing}; "
                    f"{id_key}={corr_label} index={idx}"
                )
            boundary_hash = event.deterministic_fields.get("boundary_config_hash")
            if not _is_sha256_label(boundary_hash):
                raise IdentityViolation(
                    f"INTENT has invalid boundary_config_hash; {id_key}={corr_label} index={idx}"
                )
            intent_digest = event.deterministic_fields.get("intent_digest")
            input_digest = event.deterministic_fields.get("input_digest")
            if intent_digest is not None and not _is_sha256_label(intent_digest):
                raise IdentityViolation(
                    f"INTENT has invalid intent_digest; {id_key}={corr_label} index={idx}"
                )
            if input_digest is not None and not _is_sha256_label(input_digest):
                raise IdentityViolation(
                    f"INTENT has invalid input_digest; {id_key}={corr_label} index={idx}"
                )
            if intent_digest is None and input_digest is None:
                raise IdentityViolation(
                    "INTENT missing input_digest or intent_digest; "
                    f"{id_key}={corr_label} index={idx}"
                )
        elif event.kind == DblEventKind.DECISION:
            policy_digest = event.deterministic_fields.get("policy_digest")
            if policy_digest is not None and not _is_sha256_label(policy_digest):
                raise IdentityViolation(
                    "DECISION has invalid policy_digest; "
                    f"{id_key}={corr_label} index={idx}"
                )
            if (
                "policy_version" not in event.deterministic_fields
                and policy_digest is None
            ):
                raise IdentityViolation(
                    "DECISION missing policy_version or policy_digest; "
                    f"{id_key}={corr_label} index={idx}"
                )


def _require_id(event: DblEvent, *, id_key: str, index: int) -> str:
    value = event.deterministic_fields.get(id_key)
    if not isinstance(value, str) or value == "":
        raise OrderingViolation(
            f"missing {id_key} in deterministic_fields; kind={event.kind.value} index={index}"
        )
    return str(canonicalize_value(value))


def _is_sha256_label(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if not value.startswith("sha256:"):
        return False
    hex_part = value[len("sha256:") :]
    if len(hex_part) != 64:
        return False
    for ch in hex_part:
        if ch.lower() not in "0123456789abcdef":
            return False
    return True


def verify_deterministic_is_canonicalizable(v: BehaviorV) -> None:
    """
    Verify that deterministic fields are canonicalizable.

    This is a fast-fail helper; canonicalization will also reject invalid values.
    """
    for idx, event in enumerate(v.events):
        try:
            canonicalize_value(event.deterministic_fields)
        except CanonicalizationError as exc:
            msg = str(exc)
            raise CanonicalizationError(
                f"deterministic_fields not canonicalizable; kind={event.kind.value} index={idx}"
            ) from exc
