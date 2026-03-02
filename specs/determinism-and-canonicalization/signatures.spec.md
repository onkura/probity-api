# Probity Signatures Specification (Layer 2)

## Purpose
Define how signatures provide attestation over canonicalized snapshots and envelope integrity.

This document is normative. The keywords **MUST**, **SHOULD**, and **MAY** are used as defined in RFC 2119.

## Overview
Signatures are optional but recommended for scenarios requiring non-repudiation or attestation. A PRE **MAY** include a signature; when present, it provides an additional integrity and attestation layer beyond raw hashing.

## Signature Envelope
When an implementation applies a signature, the PRE **MUST** include a `signature` object containing at minimum:
- `signature_algo` (string) — identifier for the signature algorithm (e.g., `rsa-pss-sha256`, `ecdsa-secp256r1-sha256`, `ed25519`)
- `signer_key_id` (string) — opaque identifier for the signing key (e.g., KMS key ARN, key fingerprint)
- `signature` (string) — the signature value (encoded bytes)
- `signature_encoding` (string) — e.g., `base64url`, `hex`

Compatibility note (non-normative):
- Older drafts used `signature_meta`. Implementations may choose to accept legacy inputs for migration,
  but records claiming `encoding_id = probity-json:v1` MUST use `signature`.

## Signature Target
Implementations **MUST** declare what the signature covers. The choice **MUST** be indicated in `signature.target`.

Allowed targets:
- `snapshot_bytes` (recommended) — signature over the canonicalized snapshot bytes
- `snapshot_digest` — signature over the raw digest bytes corresponding to PRE `integrity.digest`
- `envelope` (discouraged) — signature over a canonical form of the envelope (envelope signing complicates independent verification)

Records claiming `encoding_id = probity-json:v1` **SHOULD** use `snapshot_bytes` or `snapshot_digest`.

## Key Management & Trust
- Probity does not mandate key management solutions; implementers **MUST** document key provenance and trust assumptions in operational documentation.
- Signer key rotation **MUST** be supported by including `signer_key_id` metadata and publishing historical key material references if required for long-term verification.

## Signature Verification
A verifier MUST:
1. Resolve the canonicalized snapshot bytes according to `canonical_serialization_id`.
2. Recompute the digest over canonical snapshot bytes using PRE `integrity.hash_algo` and compare against PRE `integrity.digest`.
3. If a PRE `signature` is present, validate it using `signature.signature_algo` and key material for `signature.signer_key_id`, respecting `signature.target`:
   - `snapshot_bytes`: verify over canonical snapshot bytes
   - `snapshot_digest`: verify over the raw digest bytes corresponding to PRE `integrity.digest` (decoded per `integrity.hash_encoding`)
4. Report validity and signer identity metadata in verifier output.

## Signature Formats
- Implementations **MAY** use JWS or other standardized signature containers. If JWS is used, the PRE **MUST** include `signature_format: jws` and provide `signature` accordingly.
