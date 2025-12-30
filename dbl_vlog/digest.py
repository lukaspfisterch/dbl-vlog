from __future__ import annotations

import hashlib
from typing import Any

from .canonical import canonical_json_bytes, canonicalize_value, enforce_forbidden_keys
from .model import DblEvent


SCHEMA_VERSION = 1


def event_digest_payload(event: DblEvent, *, enforce_keys: bool = True) -> dict[str, Any]:
    """
    Build the deterministic payload that participates in the event digest.

    Excludes:
    - observational_fields
    - stream index t(e)
    """
    if enforce_keys:
        enforce_forbidden_keys(event.deterministic_fields)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": event.kind.value,
        "deterministic_fields": canonicalize_value(event.deterministic_fields),
    }
    return payload


def event_digest(event: DblEvent, *, enforce_keys: bool = True) -> bytes:
    """
    SHA-256 over canonical JSON bytes of the digest payload.
    """
    payload = event_digest_payload(event, enforce_keys=enforce_keys)
    b = canonical_json_bytes(payload)
    return hashlib.sha256(b).digest()


def event_digest_hex(event: DblEvent, *, enforce_keys: bool = True) -> str:
    return event_digest(event, enforce_keys=enforce_keys).hex()


def event_canonical_bytes(event: DblEvent, *, enforce_keys: bool = True) -> bytes:
    """
    Canonical JSON bytes of the digest payload, without hashing.
    """
    payload = event_digest_payload(event, enforce_keys=enforce_keys)
    return canonical_json_bytes(payload)


def v_digest(event_digests: list[bytes]) -> bytes:
    """
    Digest of V over ordered event digests.

    The caller is responsible for order. This function commits to order by hashing:
      H( (i || d_i) for i=0..n-1 )

    Where:
    - i is uint64 big-endian index
    - d_i is 32-byte event digest
    """
    h = hashlib.sha256()
    for idx, d in enumerate(event_digests):
        if len(d) != 32:
            raise ValueError("event digest must be 32 bytes (sha256)")
        h.update(idx.to_bytes(8, byteorder="big", signed=False))
        h.update(d)
    return h.digest()


def v_digest_hex(event_digests: list[bytes]) -> str:
    return v_digest(event_digests).hex()
