"""
Probity reference verifier (Phase B3) — strict, offline, fail-closed.

Capabilities:
- Load PRE JSON
- Locate snapshot (embedded or local snapshot_ref)
- Canonicalize snapshot using JCS (RFC 8785)
- Compute digest per PRE integrity params
- Compare digest against PRE integrity.digest
- Optionally verify ed25519 signatures if key provided
- Validate PRE and snapshot against JSON Schemas if schema directory provided
- Emit verifier-output JSON

Non-goals:
- No network fetching
- No storage/SDK integration
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import datetime
import hashlib
from typing import Any, Dict, Optional, Tuple, List

from jcs_rfc8785 import canonicalize as jcs_canonicalize, CanonicalizationError
from hash import compute_digest, decode_digest, HashingError

try:
    import jsonschema  # type: ignore
except Exception:
    jsonschema = None

# Optional accelerator; not required.
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # type: ignore
except Exception:
    Ed25519PublicKey = None  # type: ignore


# Minimum canonical reason tokens (Probity v1 invariants)
REASONS = {
    "invalid_json",
    "missing_envelope_fields",
    "snapshot_unresolvable",
    "snapshot_ref_hash_mismatch",
    "unknown_canonical_id",
    "unsupported_hash_algo",
    "unsupported_hash_encoding",
    "integrity_mismatch",
    "signature_key_unknown",
    "signature_invalid",
    "missing_snapshot_fields",
}


def utc_now_rfc3339() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def load_json_file(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise ValueError("invalid_json") from e


def _missing_fields_pre(pre: Dict[str, Any]) -> List[str]:
    required = [
        "record_id",
        "spec_version",
        "encoding_id",
        "schema_version",
        "canonical_serialization_id",
        "created_at",
        "evidence_quality",
        "integrity",
    ]
    missing = [k for k in required if k not in pre]

    # XOR: snapshot vs snapshot_ref
    if "snapshot" not in pre and "snapshot_ref" not in pre:
        missing.append("snapshot|snapshot_ref")
    if "snapshot" in pre and "snapshot_ref" in pre:
        missing.append("snapshot_xor_snapshot_ref")

    # integrity required subfields
    if isinstance(pre.get("integrity"), dict):
        for k in ["hash_algo", "hash_encoding", "digest", "canonical_serialization_id"]:
            if k not in pre["integrity"]:
                missing.append(f"integrity.{k}")
    else:
        if "integrity" in pre:
            missing.append("integrity.(object)")
    return missing


def resolve_snapshot(
    pre: Dict[str, Any], base_dir: str
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Optional[str]]:
    """Return (snapshot_obj, snapshot_ref_obj, error_reason)."""
    if "snapshot" in pre:
        snap = pre["snapshot"]
        if not isinstance(snap, dict):
            return None, None, "snapshot_unresolvable"
        return snap, None, None

    sref = pre.get("snapshot_ref")
    if not isinstance(sref, dict):
        return None, None, "snapshot_unresolvable"

    uri = sref.get("uri")
    if not isinstance(uri, str) or not uri:
        return None, sref, "snapshot_unresolvable"

    # Offline rule: only allow file paths or file: URIs.
    if uri.startswith("file:"):
        path = uri[len("file:") :]
    elif "://" in uri:
        return None, sref, "snapshot_unresolvable"
    else:
        path = uri

    if not os.path.isabs(path):
        path = os.path.normpath(os.path.join(base_dir, path))

    try:
        with open(path, "rb") as f:
            blob = f.read()
    except Exception:
        return None, sref, "snapshot_unresolvable"

    # If snapshot_ref.content_hash is present, verify it against artifact BYTES.
    ch = sref.get("content_hash")
    if isinstance(ch, dict) and "hash_algo" in ch and "hash_encoding" in ch and "digest" in ch:
        try:
            expected = ch["digest"]
            algo = ch["hash_algo"]
            enc = ch["hash_encoding"]
            computed = compute_digest(blob, algo, enc)
        except HashingError as e:
            reason = str(e)
            if reason == "unsupported_hash_algo":
                return None, sref, "unsupported_hash_algo"
            if reason == "unsupported_hash_encoding":
                return None, sref, "unsupported_hash_encoding"
            return None, sref, "snapshot_unresolvable"
        if computed != expected:
            return None, sref, "snapshot_ref_hash_mismatch"

    try:
        snap_obj = json.loads(blob.decode("utf-8"))
    except Exception:
        return None, sref, "snapshot_unresolvable"
    if not isinstance(snap_obj, dict):
        return None, sref, "snapshot_unresolvable"
    return snap_obj, sref, None


def canonicalize_snapshot(pre: Dict[str, Any], snapshot: Dict[str, Any]) -> Tuple[Optional[bytes], Optional[str]]:
    cid = pre.get("canonical_serialization_id")
    if cid != "jcs:rfc8785":
        return None, "unknown_canonical_id"
    try:
        text = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
        return jcs_canonicalize(text), None
    except CanonicalizationError:
        return None, "invalid_json"


def schema_validate(
    pre: Dict[str, Any],
    snapshot: Optional[Dict[str, Any]],
    schema_dir: Optional[str],
) -> Tuple[bool, List[str], Optional[str]]:
    """
    Return (ok, missing_fields, error_reason).

    If schema_dir is None, schema validation is skipped (digest verification still applies).
    If schema validation is enabled but unavailable, verifier fails closed with an unverified result.
    """
    if schema_dir is None:
        return True, [], None
    if jsonschema is None:
        return False, [], "com.probity.schema_validation_unavailable"

    def load_schema(rel: str) -> Dict[str, Any]:
        with open(os.path.join(schema_dir, rel), "r", encoding="utf-8") as f:
            return json.load(f)

    pre_schema = load_schema("pre-envelope.schema.json")
    snap_schema = load_schema("decision-snapshot.schema.json")

    store: Dict[str, Any] = {}
    for root, _, files in os.walk(schema_dir):
        for fn in files:
            if fn.endswith(".json"):
                p = os.path.join(root, fn)
                try:
                    s = json.load(open(p, "r", encoding="utf-8"))
                    sid = s.get("$id")
                    if isinstance(sid, str):
                        store[sid] = s
                except Exception:
                    pass

    resolver = jsonschema.RefResolver.from_schema(pre_schema, store=store)

    try:
        jsonschema.Draft202012Validator(pre_schema, resolver=resolver).validate(pre)
    except jsonschema.ValidationError as e:
        missing: List[str] = []

        # For "required", jsonschema's validator_value is the full required list,
        # not the missing key. The missing key is in the error message.
        # Example message: "'outcome' is a required property"
        if e.validator == "required" and isinstance(e.message, str):
            prefix = ".".join(str(p) for p in e.path)
            # Extract first quoted token
            if "'" in e.message:
                parts = e.message.split("'")
                if len(parts) >= 2 and parts[1]:
                    k = parts[1]
                    missing.append(f"{prefix}.{k}" if prefix else k)

        if missing:
            return False, missing, "missing_snapshot_fields"

        return False, [], "com.probity.schema_invalid_snapshot"
                
    if snapshot is not None:
        try:
            resolver2 = jsonschema.RefResolver.from_schema(snap_schema, store=store)
            jsonschema.Draft202012Validator(snap_schema, resolver=resolver2).validate(snapshot)
        except jsonschema.ValidationError as e:
            missing: List[str] = []
            if e.validator == "required" and isinstance(e.validator_value, list):
                prefix = ".".join(str(p) for p in e.path)
                for k in e.validator_value:
                    missing.append(f"{prefix}.{k}" if prefix else k)
            if missing:
                return False, missing, "missing_snapshot_fields"
            return False, [], "com.probity.schema_invalid_snapshot"

    return True, [], None


# ----------------------------
# Pure-Python Ed25519 verifier
# (RFC 8032) — dependency-free
# ----------------------------

# Field and group constants (ed25519)
_P = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = -121665 * pow(121666, _P - 2, _P) % _P

# sqrt(-1) mod p
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
    # double-and-add
    Q = (0, 1)  # neutral
    P = Pt
    while e > 0:
        if e & 1:
            Q = _edwards_add(Q, P)
        P = _edwards_add(P, P)
        e >>= 1
    return Q


# Base point
_B = (15112221349535400772501151409588531511454012693041857206046113283949847762202,
      46316835694926478169428394003475163141307993866256225615783033603165251855960)


def _decode_int_le(b: bytes) -> int:
    return int.from_bytes(b, "little")


def _encode_int_le(x: int, n: int) -> bytes:
    return x.to_bytes(n, "little")


def _decode_point(A: bytes):
    if len(A) != 32:
        raise ValueError("bad_point_length")
    y = _decode_int_le(A) & ((1 << 255) - 1)
    sign = (A[31] >> 7) & 1
    if y >= _P:
        raise ValueError("bad_point_y")
    x = _xrecover(y)
    if (x & 1) != sign:
        x = _P - x
    return (x, y)


def _is_on_curve(Pt) -> bool:
    x, y = Pt
    return (-x * x + y * y - 1 - _D * x * x * y * y) % _P == 0


def _sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def ed25519_verify(pubkey_raw: bytes, msg: bytes, sig_raw: bytes) -> bool:
    # Implements the RFC8032 verification equation:
    # [S]B = R + [k]A
    if len(pubkey_raw) != 32 or len(sig_raw) != 64:
        return False
    R_enc = sig_raw[:32]
    S = _decode_int_le(sig_raw[32:])
    if S >= _L:
        return False
    try:
        A = _decode_point(pubkey_raw)
        R = _decode_point(R_enc)
    except Exception:
        return False
    if not _is_on_curve(A) or not _is_on_curve(R):
        return False

    k = _decode_int_le(_sha512(R_enc + pubkey_raw + msg)) % _L

    SB = _scalarmult(_B, S)
    kA = _scalarmult(A, k)
    Rp = _edwards_add(R, kA)

    return SB == Rp


def verify_signature(
    pre: Dict[str, Any],
    canonical_bytes: bytes,
    computed_digest_encoded: str,
    pubkeys: Dict[str, bytes],
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    sig = pre.get("signature")
    if sig is None:
        return None, None
    if not isinstance(sig, dict):
        return None, "signature_invalid"

    signer_key_id = sig.get("signer_key_id")
    algo = sig.get("signature_algo")
    target = sig.get("target")
    sig_enc = sig.get("signature_encoding")
    sig_val = sig.get("signature")

    if not all(isinstance(x, str) and x for x in [signer_key_id, algo, target, sig_enc, sig_val]):
        return None, "signature_invalid"

    # Strict reference verifier: only implement ed25519 in v1 reference
    if algo != "ed25519":
        return None, "signature_invalid"

    pk = pubkeys.get(signer_key_id)
    if pk is None:
        return {
            "signature_algo": algo,
            "signer_key_id": signer_key_id,
            "target": target,
            "signature_valid": False,
        }, "signature_key_unknown"

    # decode signature bytes
    if sig_enc not in ("base64url", "hex"):
        return None, "signature_invalid"
    try:
        sig_bytes = decode_digest(sig_val, sig_enc)
    except Exception:
        return None, "signature_invalid"

    # determine message
    if target == "snapshot_bytes":
        msg = canonical_bytes
    elif target == "snapshot_digest":
        try:
            enc = pre["integrity"]["hash_encoding"]
            msg = decode_digest(computed_digest_encoded, enc)
        except Exception:
            return None, "signature_invalid"
    else:
        return {
            "signature_algo": algo,
            "signer_key_id": signer_key_id,
            "target": target,
            "signature_valid": False,
        }, "signature_invalid"

    # Verify (use cryptography if available, else pure python)
    try:
        if Ed25519PublicKey is not None:
            Ed25519PublicKey.from_public_bytes(pk).verify(sig_bytes, msg)
            ok = True
        else:
            ok = ed25519_verify(pk, msg, sig_bytes)
        if ok:
            return {
                "signature_algo": algo,
                "signer_key_id": signer_key_id,
                "target": target,
                "signature_valid": True,
            }, None
        return {
            "signature_algo": algo,
            "signer_key_id": signer_key_id,
            "target": target,
            "signature_valid": False,
        }, "signature_invalid"
    except Exception:
        return {
            "signature_algo": algo,
            "signer_key_id": signer_key_id,
            "target": target,
            "signature_valid": False,
        }, "signature_invalid"


def build_output(
    record_id: str,
    status: str,
    reasons: List[str],
    canonical_id: str,
    integrity_meta: Dict[str, Any],
    signature_meta: Optional[Dict[str, Any]],
    missing_fields: Optional[List[str]] = None,
    evidence_quality: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "record_id": record_id,
        "verification_time": utc_now_rfc3339(),
        "status": status,
        "status_reasons": reasons,
        "canonical_serialization_id": canonical_id,
        "integrity": integrity_meta,
    }
    if signature_meta is not None:
        out["signature"] = signature_meta
    if missing_fields:
        out["missing_fields"] = missing_fields
    if evidence_quality is not None:
        out["evidence_quality"] = evidence_quality
    if notes:
        out["notes"] = notes
    return out


def write_out(obj: Dict[str, Any], out_path: str) -> int:
    data = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    if out_path == "-":
        sys.stdout.write(data)
        return 0
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(data)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Probity strict offline verifier (reference).")
    ap.add_argument("--pre", required=True, help="Path to pre.json")
    ap.add_argument("--base-dir", default=".", help="Base directory for resolving snapshot_ref relative paths.")
    ap.add_argument("--schemas", default=None, help="Path to schemas/ directory (enables schema validation).")
    ap.add_argument(
        "--pubkey",
        action="append",
        default=[],
        help="Mapping signer_key_id=path_to_raw_ed25519_pubkey (32 bytes). Can be repeated.",
    )
    ap.add_argument("--out", default="-", help="Output path for verifier output JSON, or '-' for stdout.")
    args = ap.parse_args()

    # Load public keys (optional)
    pubkeys: Dict[str, bytes] = {}
    for mapping in args.pubkey:
        if "=" not in mapping:
            print("Invalid --pubkey mapping, expected signer_key_id=path", file=sys.stderr)
            return 2
        kid, p = mapping.split("=", 1)
        try:
            with open(p, "rb") as f:
                pubkeys[kid] = f.read()
        except Exception:
            pass

    # Parse PRE JSON
    try:
        pre = load_json_file(args.pre)
    except ValueError:
        out = build_output(
            record_id="(unknown)",
            status="invalid",
            reasons=["invalid_json"],
            canonical_id="(unknown)",
            integrity_meta={
                "hash_algo": "",
                "hash_encoding": "",
                "computed_digest": "",
                "expected_digest": "",
                "match": False,
            },
            signature_meta=None,
        )
        return write_out(out, args.out)

    if not isinstance(pre, dict):
        out = build_output(
            record_id="(unknown)",
            status="invalid",
            reasons=["invalid_json"],
            canonical_id="(unknown)",
            integrity_meta={
                "hash_algo": "",
                "hash_encoding": "",
                "computed_digest": "",
                "expected_digest": "",
                "match": False,
            },
            signature_meta=None,
        )
        return write_out(out, args.out)

    record_id = str(pre.get("record_id", "(unknown)"))
    evidence_quality = pre.get("evidence_quality") if isinstance(pre.get("evidence_quality"), str) else None
    canonical_id = str(pre.get("canonical_serialization_id", "(unknown)"))

    # Minimum envelope presence checks
    missing = _missing_fields_pre(pre)
    if missing:
        out = build_output(
            record_id=record_id,
            status="incomplete",
            reasons=["missing_envelope_fields"],
            canonical_id=canonical_id,
            integrity_meta={
                "hash_algo": "",
                "hash_encoding": "",
                "computed_digest": "",
                "expected_digest": "",
                "match": False,
            },
            signature_meta=None,
            missing_fields=missing,
            evidence_quality=evidence_quality,
        )
        return write_out(out, args.out)

    # Resolve snapshot (offline only)
    snapshot, _sref, err = resolve_snapshot(pre, args.base_dir)
    if err:
        status = "unverified" if err in {
            "snapshot_unresolvable",
            "unknown_canonical_id",
            "unsupported_hash_algo",
            "unsupported_hash_encoding",
        } else "invalid"
        out = build_output(
            record_id=record_id,
            status=status,
            reasons=[err],
            canonical_id=canonical_id,
            integrity_meta={
                "hash_algo": pre["integrity"].get("hash_algo", ""),
                "hash_encoding": pre["integrity"].get("hash_encoding", ""),
                "computed_digest": "",
                "expected_digest": pre["integrity"].get("digest", ""),
                "match": False,
            },
            signature_meta=None,
            evidence_quality=evidence_quality,
        )
        return write_out(out, args.out)

    # Canonicalize snapshot
    canonical_bytes, err = canonicalize_snapshot(pre, snapshot)  # type: ignore[arg-type]
    if err:
        out = build_output(
            record_id=record_id,
            status="unverified",
            reasons=[err],
            canonical_id=canonical_id,
            integrity_meta={
                "hash_algo": pre["integrity"].get("hash_algo", ""),
                "hash_encoding": pre["integrity"].get("hash_encoding", ""),
                "computed_digest": "",
                "expected_digest": pre["integrity"].get("digest", ""),
                "match": False,
            },
            signature_meta=None,
            evidence_quality=evidence_quality,
        )
        return write_out(out, args.out)

    # Compute digest
    algo = pre["integrity"]["hash_algo"]
    enc = pre["integrity"]["hash_encoding"]
    expected = pre["integrity"]["digest"]

    try:
        computed = compute_digest(canonical_bytes, algo, enc)
    except HashingError as e:
        reason = str(e)
        if reason not in REASONS:
            reason = "unsupported_hash_algo"
        out = build_output(
            record_id=record_id,
            status="unverified",
            reasons=[reason],
            canonical_id=canonical_id,
            integrity_meta={
                "hash_algo": algo,
                "hash_encoding": enc,
                "computed_digest": "",
                "expected_digest": expected,
                "match": False,
            },
            signature_meta=None,
            evidence_quality=evidence_quality,
        )
        return write_out(out, args.out)

    if computed != expected:
        out = build_output(
            record_id=record_id,
            status="invalid",
            reasons=["integrity_mismatch"],
            canonical_id=canonical_id,
            integrity_meta={
                "hash_algo": algo,
                "hash_encoding": enc,
                "computed_digest": computed,
                "expected_digest": expected,
                "match": False,
            },
            signature_meta=None,
            evidence_quality=evidence_quality,
        )
        return write_out(out, args.out)

    # Optional schema validation (enabled by --schemas)
    ok, missing_fields, schema_err = schema_validate(pre, snapshot, args.schemas)  # type: ignore[arg-type]
    if schema_err == "missing_snapshot_fields":
        out = build_output(
            record_id=record_id,
            status="incomplete",
            reasons=["missing_snapshot_fields"],
            canonical_id=canonical_id,
            integrity_meta={
                "hash_algo": algo,
                "hash_encoding": enc,
                "computed_digest": computed,
                "expected_digest": expected,
                "match": True,
            },
            signature_meta=None,
            missing_fields=missing_fields,
            evidence_quality=evidence_quality,
        )
        return write_out(out, args.out)
    if schema_err and not ok:
        out = build_output(
            record_id=record_id,
            status="unverified",
            reasons=[schema_err],  # namespaced reason
            canonical_id=canonical_id,
            integrity_meta={
                "hash_algo": algo,
                "hash_encoding": enc,
                "computed_digest": computed,
                "expected_digest": expected,
                "match": True,
            },
            signature_meta=None,
            evidence_quality=evidence_quality,
        )
        return write_out(out, args.out)

    # Optional signature verification (strict, offline)
    sig_meta, sig_err = verify_signature(pre, canonical_bytes, computed, pubkeys)
    if sig_err:
        status = "unverified" if sig_err == "signature_key_unknown" else "invalid"
        out = build_output(
            record_id=record_id,
            status=status,
            reasons=[sig_err],
            canonical_id=canonical_id,
            integrity_meta={
                "hash_algo": algo,
                "hash_encoding": enc,
                "computed_digest": computed,
                "expected_digest": expected,
                "match": True,
            },
            signature_meta=sig_meta,
            evidence_quality=evidence_quality,
        )
        return write_out(out, args.out)

    # Verified
    out = build_output(
        record_id=record_id,
        status="verified",
        reasons=[],
        canonical_id=canonical_id,
        integrity_meta={
            "hash_algo": algo,
            "hash_encoding": enc,
            "computed_digest": computed,
            "expected_digest": expected,
            "match": True,
        },
        signature_meta=sig_meta,
        evidence_quality=evidence_quality,
    )
    return write_out(out, args.out)


if __name__ == "__main__":
    raise SystemExit(main())