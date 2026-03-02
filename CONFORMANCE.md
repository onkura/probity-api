# Probity Conformance Checklist

This file defines the minimal mechanical tests an implementation SHOULD pass to be described as "Probity-conformant".

Conformance is about:
- producing records with the correct structure,
- producing deterministic canonical bytes,
- computing/verifying digests and optional signatures consistently,
- emitting verifier output consistently.

Conformance does NOT imply:
- correctness of decisions,
- authorization correctness,
- policy compliance.

## Minimal conformance tests

### Layer 1 (Record Structure)
- [ ] Produce a valid PRE envelope for `probity-json:v1` with required fields:
  - `record_id`, `spec_version`, `encoding_id`, `schema_version`, `canonical_serialization_id`, `created_at`, `evidence_quality`, `integrity`
  - Exactly one of `snapshot` or `snapshot_ref`
- [ ] Produce a Decision Snapshot that contains the required conceptual fields:
  - `perception`, `responsibility` (with `actor_id`, `actor_type`, `authority_scope`), `intent`, `selection_basis`, `outcome`
- [ ] Ensure `extensions` is the only permitted location for unknown vendor-specific top-level fields.

### Layer 2 (Canonicalization & Hashing)
- [ ] Support `canonical_serialization_id = jcs:rfc8785` for `encoding_id = probity-json:v1`
- [ ] Canonicalize the Decision Snapshot into canonical bytes deterministically
- [ ] Compute PRE `integrity.digest` over canonical snapshot bytes using PRE `integrity.hash_algo`
- [ ] Ensure two independent implementations produce byte-identical canonical bytes and identical digests for the same snapshot

### Layer 2 (Signatures) — optional
- [ ] If signatures are used, include PRE `signature` object with:
  - `signature_algo`, `signer_key_id`, `target`, `signature_encoding`, `signature`
- [ ] Verify signatures over the declared target (`snapshot_bytes` or `snapshot_digest`)

### Layer 3 (Recorder Behavior)
- [ ] Follow the recording procedure: capture → canonicalize → compute digest → assemble PRE → persist → emit record id/reference
- [ ] Support evidence quality states in PRE: `verified|incomplete|late|unverified`
  - `absent` is reserved for operational signals where no PRE exists
- [ ] Declare recorder mode (`evidence_best_effort|evidence_required|evidence_blocking`) in ops docs and/or coverage declaration docs

### Layer 4 (Verification)
- [ ] Run the official test vectors (see `test-vectors/`) and produce verifier output for each vector
- [ ] For the "Basic Verified Record" vector, verifier `status` MUST be `verified`
- [ ] For the "Integrity Mismatch" vector, verifier `status` MUST be `invalid` with reason `integrity_mismatch`

## Test vector layout (expected)
Each vector directory MUST include:
- `pre.json` — the PRE JSON
- `snapshot.json` — the snapshot JSON (only if not embedded in `pre.json`)
- `canonical.txt` — canonical snapshot bytes (UTF-8). MUST NOT include a trailing newline byte.
- `expected_digest.txt` — expected value of PRE `integrity.digest`
- `hash_params.json` — includes `hash_algo`, `hash_encoding`, `canonical_serialization_id`
- `signature.json` (optional) — includes signature inputs/material for signature vectors

## Passing
An implementation is considered "basic conformant" if it passes all Layer 1–3 tests and the Layer 4 basic verified / integrity mismatch vectors.