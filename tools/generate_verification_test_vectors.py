#!/usr/bin/env python3
"""
Generate Probity verification test vectors (01..09) with ZERO third-party deps.

These vectors are schema-valid for decision-snapshot.schema.json in this repo.
They are designed so an independent Rust verifier can pass them.

Writes under:
  test-vectors/01-basic-verified/
  ...
  test-vectors/09-signed-record-invalid/

Each vector contains:
- pre.json
- snapshot.json (optional)
- canonical.txt (UTF-8 bytes, NO trailing newline)
- expected_digest.txt
- hash_params.json
- expected_verifier_output.json
- signature.json (optional)
- pubkey.ed25519.raw (optional)
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple

# ---- Frozen identifiers (Probity v1) ----
SPEC_VERSION = "probity-v1"
ENCODING_ID = "probity-json:v1"
SCHEMA_VERSION = "decision-snapshot:v1"
CANON_ID = "jcs:rfc8785"
HASH_ALGO = "sha256"
HASH_ENCODING = "hex"

CREATED_AT = "2026-03-02T00:00:00Z"
VERIFICATION_TIME_PLACEHOLDER = "1970-01-01T00:00:00Z"

SIGNER_KEY_ID = "signer:demo"

# ---- Schema-valid snapshot object (minified JSON written to snapshot.json) ----
# Matches decision-snapshot.schema.json:
# - perception: allows inputs[]
# - responsibility.actor_type must be one of: human|service|agent|delegated
# - responsibility.authority_scope must be an object
# - intent requires action_type + action_params
# - selection_basis requires one of score_signals|policy_refs|heuristic_tags
# - outcome requires observed_result + result_refs + observed_at
SNAPSHOT_BASIC_OBJ: Dict[str, Any] = {
    "perception": {"inputs": [{"type": "user_text", "ref": "input:1"}]},
    "responsibility": {
        "actor_id": "agent:demo",
        "actor_type": "agent",
        "authority_scope": {"allow": ["purchase"]},
    },
    "intent": {"action_type": "purchase", "action_params": {"target": "item:123", "qty": 1}},
    "selection_basis": {"heuristic_tags": ["lowest_cost_within_policy"]},
    "outcome": {
        "observed_result": "succeeded",
        "result_refs": ["order:abc123"],
        "observed_at": "2026-03-02T00:00:01Z",
    },
}

SNAPSHOT_MISSING_FIELD_OBJ: Dict[str, Any] = {
    k: v for (k, v) in SNAPSHOT_BASIC_OBJ.items() if k != "outcome"
}

# ---- Canonical bytes (JCS RFC8785) for the above snapshots ----
# These are fixed truth bytes. Do NOT regenerate them from implementation code.
CANON_BASIC = (
    b'{"intent":{"action_params":{"qty":1,"target":"item:123"},"action_type":"purchase"},'
    b'"outcome":{"observed_at":"2026-03-02T00:00:01Z","observed_result":"succeeded","result_refs":["order:abc123"]},'
    b'"perception":{"inputs":[{"ref":"input:1","type":"user_text"}]},'
    b'"responsibility":{"actor_id":"agent:demo","actor_type":"agent","authority_scope":{"allow":["purchase"]}},'
    b'"selection_basis":{"heuristic_tags":["lowest_cost_within_policy"]}}'
)

CANON_MISSING_FIELD = (
    b'{"intent":{"action_params":{"qty":1,"target":"item:123"},"action_type":"purchase"},'
    b'"perception":{"inputs":[{"ref":"input:1","type":"user_text"}]},'
    b'"responsibility":{"actor_id":"agent:demo","actor_type":"agent","authority_scope":{"allow":["purchase"]}},'
    b'"selection_basis":{"heuristic_tags":["lowest_cost_within_policy"]}}'
)

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def b64url_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

def b64url_decode_nopad(s: str) -> bytes:
    pad = "=" * ((4 - (len(s) % 4)) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("ascii"))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

# ----------------------------
# Pure-Python Ed25519 signing
# (RFC 8032) — dependency-free
# ----------------------------
_P = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = -121665 * pow(121666, _P - 2, _P) % _P
_I = pow(2, (_P - 1) // 4, _P)

def _inv(x: int) -> int:
    return pow(x, _P - 2, _P)

def _xrecover(y: int) -> int:
    xx = (y * y - 1) * _inv(_D * y * y + 1) % _P
    x = pow(xx, (_P + 3) // 8, _P)
    if (x * x - xx) % _P != 0:
        x = (x * _I) % _P
    if x % 2 != 0:
        x = _P - x
    return x

def _edwards_add(P1, P2):
    (x1, y1) = P1
    (x2, y2) = P2
    x3 = (x1 * y2 + x2 * y1) * _inv(1 + _D * x1 * x2 * y1 * y2) % _P
    y3 = (y1 * y2 + x1 * x2) * _inv(1 - _D * x1 * x2 * y1 * y2) % _P
    return (x3, y3)

def _scalarmult(Pt, e: int):
    Q = (0, 1)
    P = Pt
    while e > 0:
        if e & 1:
            Q = _edwards_add(Q, P)
        P = _edwards_add(P, P)
        e >>= 1
    return Q

_B = (
    15112221349535400772501151409588531511454012693041857206046113283949847762202,
    46316835694926478169428394003475163141307993866256225615783033603165251855960,
)

def _decode_int_le(b: bytes) -> int:
    return int.from_bytes(b, "little")

def _encode_int_le(x: int, n: int) -> bytes:
    return x.to_bytes(n, "little")

def _encode_point(Pt) -> bytes:
    x, y = Pt
    bits = y | ((x & 1) << 255)
    return _encode_int_le(bits, 32)

def _sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()

def _clamp_scalar(h32: bytes) -> int:
    a = bytearray(h32)
    a[0] &= 248
    a[31] &= 63
    a[31] |= 64
    return _decode_int_le(bytes(a))

def ed25519_pubkey_from_seed(seed32: bytes) -> bytes:
    h = _sha512(seed32)
    a = _clamp_scalar(h[:32])
    A = _scalarmult(_B, a)
    return _encode_point(A)

def ed25519_sign(seed32: bytes, msg: bytes) -> bytes:
    h = _sha512(seed32)
    a = _clamp_scalar(h[:32])
    prefix = h[32:]
    r = _decode_int_le(_sha512(prefix + msg)) % _L
    R = _scalarmult(_B, r)
    Renc = _encode_point(R)
    pk = _encode_point(_scalarmult(_B, a))
    k = _decode_int_le(_sha512(Renc + pk + msg)) % _L
    S = (r + k * a) % _L
    return Renc + _encode_int_le(S, 32)

def base_pre(record_id: str, evidence_quality: str, canonical_id: str, digest: str) -> Dict[str, Any]:
    return {
        "record_id": record_id,
        "spec_version": SPEC_VERSION,
        "encoding_id": ENCODING_ID,
        "schema_version": SCHEMA_VERSION,
        "canonical_serialization_id": canonical_id,
        "created_at": CREATED_AT,
        "evidence_quality": evidence_quality,
        "integrity": {
            "hash_algo": HASH_ALGO,
            "hash_encoding": HASH_ENCODING,
            "digest": digest,
            "canonical_serialization_id": canonical_id,
        },
    }

def hash_params_obj(canonical_id: str) -> Dict[str, Any]:
    return {"canonical_serialization_id": canonical_id, "hash_algo": HASH_ALGO, "hash_encoding": HASH_ENCODING}

def expected_output(
    record_id: str,
    status: str,
    reasons: List[str],
    canonical_id: str,
    computed_digest: str,
    expected_digest: str,
    match: bool,
    evidence_quality: Optional[str] = None,
    missing_fields: Optional[List[str]] = None,
    signature_obj: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "record_id": record_id,
        "verification_time": VERIFICATION_TIME_PLACEHOLDER,
        "status": status,
        "status_reasons": reasons,
        "canonical_serialization_id": canonical_id,
        "integrity": {
            "hash_algo": HASH_ALGO,
            "hash_encoding": HASH_ENCODING,
            "computed_digest": computed_digest,
            "expected_digest": expected_digest,
            "match": match,
        },
    }
    if evidence_quality is not None:
        out["evidence_quality"] = evidence_quality
    if missing_fields:
        out["missing_fields"] = missing_fields
    if signature_obj is not None:
        out["signature"] = signature_obj
    return out

def main() -> None:
    tv = Path("test-vectors")

    # Snapshot artifact bytes are minified JSON with no trailing newline.
    snapshot_basic_bytes = json.dumps(SNAPSHOT_BASIC_OBJ, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    snapshot_missing_bytes = json.dumps(SNAPSHOT_MISSING_FIELD_OBJ, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    snapshot_basic_hash = sha256_hex(snapshot_basic_bytes)
    snapshot_missing_hash = sha256_hex(snapshot_missing_bytes)

    digest_basic = sha256_hex(CANON_BASIC)
    digest_missing = sha256_hex(CANON_MISSING_FIELD)

    # Deterministic test seed (NOT a production key)
    seed = bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")
    pub_raw = ed25519_pubkey_from_seed(seed)
    sig_valid = ed25519_sign(seed, CANON_BASIC)
    sig_valid_b64url = b64url_nopad(sig_valid)
    sig_invalid_b64url = sig_valid_b64url[:-1] + ("A" if sig_valid_b64url[-1] != "A" else "B")

    def write_vector(
        name: str,
        pre: Dict[str, Any],
        snapshot_bytes: Optional[bytes],
        canonical_bytes: bytes,
        expected_digest: str,
        expected_vo: Dict[str, Any],
        include_signature_files: bool = False,
        signature_json: Optional[Dict[str, Any]] = None,
        pubkey_raw: Optional[bytes] = None,
    ):
        d = tv / name
        write_json(d / "pre.json", pre)
        write_json(d / "hash_params.json", hash_params_obj(pre["canonical_serialization_id"]))
        write_bytes(d / "canonical.txt", canonical_bytes)  # NO newline
        write_text(d / "expected_digest.txt", expected_digest + "\n")
        write_json(d / "expected_verifier_output.json", expected_vo)

        if snapshot_bytes is not None:
            write_bytes(d / "snapshot.json", snapshot_bytes)

        if include_signature_files:
            if signature_json is not None:
                write_json(d / "signature.json", signature_json)
            if pubkey_raw is not None:
                write_bytes(d / "pubkey.ed25519.raw", pubkey_raw)

    # 01-basic-verified (external snapshot_ref + required content_hash)
    pre = base_pre("tv-01", "verified", CANON_ID, digest_basic)
    pre["snapshot_ref"] = {
        "uri": "snapshot.json",
        "content_hash": {"hash_algo": "sha256", "hash_encoding": "hex", "digest": snapshot_basic_hash},
    }
    write_vector(
        "01-basic-verified",
        pre,
        snapshot_basic_bytes,
        CANON_BASIC,
        digest_basic,
        expected_output("tv-01", "verified", [], CANON_ID, digest_basic, digest_basic, True, evidence_quality="verified"),
    )

    # 02-integrity-mismatch
    bad = "00" + digest_basic[2:]
    pre = base_pre("tv-02", "verified", CANON_ID, bad)
    pre["snapshot_ref"] = {
        "uri": "snapshot.json",
        "content_hash": {"hash_algo": "sha256", "hash_encoding": "hex", "digest": snapshot_basic_hash},
    }
    write_vector(
        "02-integrity-mismatch",
        pre,
        snapshot_basic_bytes,
        CANON_BASIC,
        bad,
        expected_output("tv-02", "invalid", ["integrity_mismatch"], CANON_ID, digest_basic, bad, False, evidence_quality="verified"),
    )

    # 03-embedded-snapshot
    pre = base_pre("tv-03", "verified", CANON_ID, digest_basic)
    pre["snapshot"] = SNAPSHOT_BASIC_OBJ
    write_vector(
        "03-embedded-snapshot",
        pre,
        None,
        CANON_BASIC,
        digest_basic,
        expected_output("tv-03", "verified", [], CANON_ID, digest_basic, digest_basic, True, evidence_quality="verified"),
    )

    # 04-external-snapshot (same as 01 but exists explicitly to test snapshot_ref resolution)
    pre = base_pre("tv-04", "verified", CANON_ID, digest_basic)
    pre["snapshot_ref"] = {
        "uri": "snapshot.json",
        "content_hash": {"hash_algo": "sha256", "hash_encoding": "hex", "digest": snapshot_basic_hash},
    }
    write_vector(
        "04-external-snapshot",
        pre,
        snapshot_basic_bytes,
        CANON_BASIC,
        digest_basic,
        expected_output("tv-04", "verified", [], CANON_ID, digest_basic, digest_basic, True, evidence_quality="verified"),
    )

    # 05-late-record (still verifies)
    pre = base_pre("tv-05", "late", CANON_ID, digest_basic)
    pre["snapshot_ref"] = {
        "uri": "snapshot.json",
        "content_hash": {"hash_algo": "sha256", "hash_encoding": "hex", "digest": snapshot_basic_hash},
    }
    write_vector(
        "05-late-record",
        pre,
        snapshot_basic_bytes,
        CANON_BASIC,
        digest_basic,
        expected_output("tv-05", "verified", [], CANON_ID, digest_basic, digest_basic, True, evidence_quality="late"),
    )

    # 06-missing-field (schema failure: missing top-level "outcome")
    pre = base_pre("tv-06", "incomplete", CANON_ID, digest_missing)
    pre["snapshot_ref"] = {
        "uri": "snapshot.json",
        "content_hash": {"hash_algo": "sha256", "hash_encoding": "hex", "digest": snapshot_missing_hash},
    }
    write_vector(
        "06-missing-field",
        pre,
        snapshot_missing_bytes,
        CANON_MISSING_FIELD,
        digest_missing,
        expected_output(
            "tv-06",
            "incomplete",
            ["missing_snapshot_fields"],
            CANON_ID,
            digest_missing,
            digest_missing,
            True,
            evidence_quality="incomplete",
            missing_fields=["outcome"],
        ),
    )

    # 07-unknown-canonical-id
    pre = base_pre("tv-07", "unverified", "jcs:unknown", digest_basic)
    pre["snapshot_ref"] = {
        "uri": "snapshot.json",
        "content_hash": {"hash_algo": "sha256", "hash_encoding": "hex", "digest": snapshot_basic_hash},
    }
    write_vector(
        "07-unknown-canonical-id",
        pre,
        snapshot_basic_bytes,
        CANON_BASIC,
        digest_basic,
        expected_output(
            "tv-07",
            "unverified",
            ["unknown_canonical_id"],
            "jcs:unknown",
            "",
            digest_basic,
            False,
            evidence_quality="unverified",
        ),
    )

    # 08-signed-record-valid (ed25519 over snapshot_bytes)
    pre = base_pre("tv-08", "verified", CANON_ID, digest_basic)
    pre["snapshot_ref"] = {
        "uri": "snapshot.json",
        "content_hash": {"hash_algo": "sha256", "hash_encoding": "hex", "digest": snapshot_basic_hash},
    }
    pre["signature"] = {
        "signature_algo": "ed25519",
        "signer_key_id": SIGNER_KEY_ID,
        "target": "snapshot_bytes",
        "signature_encoding": "base64url",
        "signature": sig_valid_b64url,
    }
    write_vector(
        "08-signed-record-valid",
        pre,
        snapshot_basic_bytes,
        CANON_BASIC,
        digest_basic,
        expected_output(
            "tv-08",
            "verified",
            [],
            CANON_ID,
            digest_basic,
            digest_basic,
            True,
            evidence_quality="verified",
            signature_obj={
                "signature_algo": "ed25519",
                "signer_key_id": SIGNER_KEY_ID,
                "target": "snapshot_bytes",
                "signature_valid": True,
            },
        ),
        include_signature_files=True,
        signature_json={"public_key_file": "pubkey.ed25519.raw", "public_key_format": "raw", "signer_key_id": SIGNER_KEY_ID},
        pubkey_raw=pub_raw,
    )

    # 09-signed-record-invalid
    pre = base_pre("tv-09", "verified", CANON_ID, digest_basic)
    pre["snapshot_ref"] = {
        "uri": "snapshot.json",
        "content_hash": {"hash_algo": "sha256", "hash_encoding": "hex", "digest": snapshot_basic_hash},
    }
    pre["signature"] = {
        "signature_algo": "ed25519",
        "signer_key_id": SIGNER_KEY_ID,
        "target": "snapshot_bytes",
        "signature_encoding": "base64url",
        "signature": sig_invalid_b64url,
    }
    write_vector(
        "09-signed-record-invalid",
        pre,
        snapshot_basic_bytes,
        CANON_BASIC,
        digest_basic,
        expected_output(
            "tv-09",
            "invalid",
            ["signature_invalid"],
            CANON_ID,
            digest_basic,
            digest_basic,
            True,
            evidence_quality="verified",
            signature_obj={
                "signature_algo": "ed25519",
                "signer_key_id": SIGNER_KEY_ID,
                "target": "snapshot_bytes",
                "signature_valid": False,
            },
        ),
        include_signature_files=True,
        signature_json={"public_key_file": "pubkey.ed25519.raw", "public_key_format": "raw", "signer_key_id": SIGNER_KEY_ID},
        pubkey_raw=pub_raw,
    )

    print("Wrote schema-valid verification test vectors 01..09 under test-vectors/")

if __name__ == "__main__":
    main()