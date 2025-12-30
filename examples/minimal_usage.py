from __future__ import annotations

from dbl_vlog import (
    BehaviorV,
    DblEvent,
    DblEventKind,
    append_event,
    event_digest_hex,
    project_normative,
    verify_append_only,
)


def main() -> None:
    v0 = BehaviorV()

    e0 = DblEvent(
        kind=DblEventKind.INTENT,
        deterministic_fields={
            "correlation_id": "r-001",
            "actor": "user123",
            "boundary_version": 1,
            "boundary_config_hash": "sha256:" + "0" * 64,
            "input_digest": "sha256:" + "1" * 64,
        },
        observational_fields={"received_at": "2025-12-27T16:00:00+01:00"},
    )

    e1 = DblEvent(
        kind=DblEventKind.DECISION,
        deterministic_fields={"correlation_id": "r-001", "policy_version": 3, "outcome": "ALLOW"},
        observational_fields={"decided_at": "2025-12-27T16:00:01+01:00"},
    )

    v1 = append_event(v0, e0)
    v2 = append_event(v1, e1)

    verify_append_only(v1, v2)

    print("V digest:", v2.digest_hex())
    print("Event 1 digest:", event_digest_hex(e1))

    v_norm = project_normative(v2)
    print("V_norm length:", len(v_norm))


if __name__ == "__main__":
    main()
