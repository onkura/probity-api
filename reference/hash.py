"""
Probity reference hashing (Phase B2).

Protocol invariant (Probity v1):
- integrity.hash_algo MUST be "sha256"
- integrity.hash_encoding MUST be "hex" (lowercase) or "base64url" (no padding)

This module hashes BYTES (already-canonicalized snapshot bytes).
It does not canonicalize JSON.
"""

from __future__ import annotations

import base64
import hashlib


class HashingError(Exception):
    pass


def _b64url_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def decode_digest(encoded: str, encoding: str) -> bytes:
    """Decode a digest string into raw bytes."""
    if encoding == "hex":
        try:
            return bytes.fromhex(encoded)
        except Exception as e:
            raise HashingError("invalid_digest_encoding") from e

    if encoding == "base64url":
        pad = "=" * ((4 - (len(encoded) % 4)) % 4)
        try:
            return base64.urlsafe_b64decode((encoded + pad).encode("ascii"))
        except Exception as e:
            raise HashingError("invalid_digest_encoding") from e

    raise HashingError("unsupported_hash_encoding")


def encode_digest(raw: bytes, encoding: str) -> str:
    """Encode raw digest bytes using declared encoding."""
    if encoding == "hex":
        return raw.hex()  # lowercase hex
    if encoding == "base64url":
        return _b64url_nopad(raw)
    raise HashingError("unsupported_hash_encoding")


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def compute_digest(data: bytes, hash_algo: str, hash_encoding: str) -> str:
    """Compute encoded digest for given data and parameters."""
    if hash_algo != "sha256":
        raise HashingError("unsupported_hash_algo")
    raw = sha256(data)
    return encode_digest(raw, hash_encoding)