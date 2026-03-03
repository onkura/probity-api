from __future__ import annotations

from typing import Any, Dict, Tuple

from .constants import CANONICAL_SERIALIZATION_ID, DEFAULT_HASH_ALGO, DEFAULT_HASH_ENCODING
from .jcs_rfc8785 import canonicalize as jcs_canonicalize
from .hashing import compute_digest


def canonicalize_snapshot(snapshot: Dict[str, Any], canonical_serialization_id: str = CANONICAL_SERIALIZATION_ID) -> bytes:
    if canonical_serialization_id != CANONICAL_SERIALIZATION_ID:
        raise ValueError("unknown_canonical_id")
    return jcs_canonicalize(snapshot)


def compute_integrity(
    snapshot: Dict[str, Any],
    *,
    canonical_serialization_id: str = CANONICAL_SERIALIZATION_ID,
    hash_algo: str = DEFAULT_HASH_ALGO,
    hash_encoding: str = DEFAULT_HASH_ENCODING,
) -> Tuple[bytes, Dict[str, Any]]:
    canonical_bytes = canonicalize_snapshot(snapshot, canonical_serialization_id=canonical_serialization_id)
    digest = compute_digest(canonical_bytes, algo=hash_algo, encoding=hash_encoding)  # type: ignore[arg-type]
    integrity = {
        "hash_algo": hash_algo,
        "hash_encoding": hash_encoding,
        "digest": digest,
        "canonical_serialization_id": canonical_serialization_id,
    }
    return canonical_bytes, integrity