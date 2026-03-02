# Probity Test Vectors

This directory contains canonical truth cases for independent verifier implementations.

## Structure

- `canonicalization/` — canonicalization-only vectors (JCS RFC 8785 invariants)
- `01-.../` etc — end-to-end verification vectors

## Comparison rules

Verifier output MUST match `expected_verifier_output.json` exactly with one exception:

- `verification_time` MUST be present but is not compared (time-dependent). Harnesses MUST ignore it.

All other fields MUST match exactly:
- `status`
- `status_reasons` (order-sensitive)
- `canonical_serialization_id`
- `integrity.*` (including `computed_digest`, `expected_digest`, `match`)
- `missing_fields` (if present; order-sensitive)
- `signature.*` (if present)

## Offline resolution rule

Verification vectors using `snapshot_ref.uri` MUST be resolvable offline.
In this repository, such URIs are local file paths (e.g., `snapshot.json`).

## Vector layout (verification vectors)

Each vector directory MUST include:
- `pre.json`
- `snapshot.json` (optional; only if not embedded in `pre.json`)
- `canonical.txt` (canonical snapshot bytes, UTF-8, no trailing newline)
- `expected_digest.txt` (expected PRE `integrity.digest`)
- `hash_params.json` (hash + canonicalization parameters)
- `expected_verifier_output.json`
- `signature.json` (optional; signature materials metadata)
- `pubkey.ed25519.raw` (optional; for signature vectors)