# Probity Verification Algorithm Specification (Layer 4)

## Purpose
Define the deterministic algorithm an independent verifier uses to evaluate a Probity Record Envelope (PRE) and its Decision Snapshot.
This spec makes verification portable across implementations.

This document is normative. The keywords **MUST**, **SHOULD**, and **MAY** are used as defined in RFC 2119.

## Scope and non-goals
Verification in Probity means:
- reproduce canonical snapshot bytes (as declared),
- recompute hash digest (as declared),
- compare computed digest to the PRE’s expected digest,
- optionally verify a signature if present.

Verification does **not**:
- judge semantic correctness,
- judge authorization correctness,
- evaluate policy compliance,
- guarantee completeness of referenced artifacts.

## Inputs
A verifier MUST accept:
- the PRE JSON object
- any referenced artifacts required to resolve the snapshot when `snapshot_ref` is used
- any key material / trust roots required to verify a signature, if present (provisioning is out of scope)

## Preconditions
1. The PRE MUST declare hash verification metadata in `integrity`:
   - `hash_algo`
   - `hash_encoding`
   - `digest` (expected)
   - `canonical_serialization_id`

2. For `encoding_id = probity-json:v1`:
   - verifiers MUST treat `canonical_serialization_id` as `jcs:rfc8785`
   - verifiers MUST canonicalize the snapshot using RFC 8785 JCS
   - verifiers MUST compute the digest using `integrity.hash_algo` and compare to `integrity.digest`

## Status model
A verifier produces one of:
- `verified` — digest matches (and if signature present, signature is valid)
- `invalid` — digest mismatch, signature mismatch, or structurally inconsistent record
- `unverified` — verifier cannot complete verification due to missing/unsupported inputs
- `incomplete` — record is structurally present but missing required fields

Notes:
- `incomplete` indicates missing required fields (omitted fields), not semantic incompleteness.
- A record can be schema-valid but still `invalid` due to digest mismatch.

## Verification Steps (deterministic)

### Step 1 — Parse and minimally validate envelope
The verifier MUST parse the PRE as JSON and check presence of required envelope fields for the declared encoding.

For `probity-json:v1`, minimally required:
- `record_id`
- `spec_version`
- `encoding_id`
- `schema_version`
- `canonical_serialization_id`
- `created_at`
- `evidence_quality`
- `integrity` object with `hash_algo`, `hash_encoding`, `digest`, `canonical_serialization_id`
- exactly one of `snapshot` or `snapshot_ref`

If required fields are missing:
- return `incomplete`
- include reason `missing_envelope_fields`
- include `missing_fields` list

If the PRE is not valid JSON or contains duplicate keys:
- return `invalid` with reason `invalid_json`

### Step 2 — Resolve the Decision Snapshot
If PRE contains `snapshot`:
- use it directly as the snapshot object.

If PRE contains `snapshot_ref`:
- the verifier MUST attempt to retrieve the referenced snapshot artifact using `snapshot_ref.uri` (or equivalent resolution rules for the environment),
- MUST verify `snapshot_ref.content_hash` against the retrieved artifact bytes if present (recommended for verifiers; required if verifier claims it “resolved” the snapshot),
- MUST parse the snapshot artifact as JSON to obtain the snapshot object.

If the snapshot cannot be obtained or parsed:
- return `unverified` with reason `snapshot_unresolvable`

If `snapshot_ref.content_hash` is present and does not match retrieved bytes:
- return `invalid` with reason `snapshot_ref_hash_mismatch`

### Step 3 — Canonicalize the snapshot
The verifier MUST canonicalize the snapshot according to `canonical_serialization_id`.

If `canonical_serialization_id` is unknown or unsupported:
- return `unverified` with reason `unknown_canonical_id`

For `probity-json:v1`, the verifier MUST apply:
- `canonical_serialization_id = jcs:rfc8785`

The output of this step is:
- `canonical_snapshot_bytes` (UTF-8 byte sequence)

### Step 4 — Compute digest
The verifier MUST compute `computed_digest` over `canonical_snapshot_bytes` using:
- `integrity.hash_algo`

If the hash algorithm is unknown or unsupported:
- return `unverified` with reason `unsupported_hash_algo`

The verifier MUST encode `computed_digest` using:
- `integrity.hash_encoding`

If the digest encoding is unknown or unsupported:
- return `unverified` with reason `unsupported_hash_encoding`

### Step 5 — Compare digest
The verifier MUST compare:
- `computed_digest` (encoded) vs `integrity.digest` (expected)

If mismatch:
- return `invalid` with reason `integrity_mismatch`

If match:
- continue.

### Step 6 — Optional signature verification
If the PRE contains a `signature` object:
- the verifier MUST attempt signature verification using `signature.signature_algo` and the appropriate key material for `signature.signer_key_id`
- the verifier MUST respect `signature.target`:
  - `snapshot_bytes`: verify signature over `canonical_snapshot_bytes`
  - `snapshot_digest`: verify signature over the raw digest bytes corresponding to `integrity.digest` (decoded per `integrity.hash_encoding`)

If the verifier cannot obtain key material for `signer_key_id`:
- return `unverified` with reason `signature_key_unknown`

If signature verification fails:
- return `invalid` with reason `signature_invalid`

If signature verification succeeds:
- continue.

If no `signature` is present:
- verification MAY still return `verified` based on digest match alone.

### Step 7 — Snapshot field presence checks (structural completeness)
The verifier SHOULD validate required snapshot fields for the declared snapshot schema version (e.g., `decision-snapshot:v1`):
- If required snapshot fields are missing, return `incomplete` with reason `missing_snapshot_fields` and list missing fields.

This step is about structural completeness, not semantic correctness.

### Step 8 — Emit verification output
The verifier MUST emit a machine-readable verification report conforming to `verifier-output` for the encoding (see `schemas/verifier-output.schema.json`).

The output MUST include:
- `record_id`
- `verification_time`
- `status`
- `status_reasons`
- `canonical_serialization_id`
- integrity details including computed vs expected digest and match boolean
- signature result if signature was present

## Determinism & Idempotence
- The verification algorithm MUST be deterministic: given the same inputs (PRE + referenced artifacts + key material), it MUST produce the same output.
- Verifiers MUST NOT rely on non-deterministic external signals (e.g., current time) for core decisions; the current time MAY be recorded as `verification_time` metadata.

## Offline Verification
Verification MUST be possible offline if all referenced artifacts and required key material are available locally.

## Error handling & reporting
Verifiers MUST provide explicit, machine-readable failure reasons from a canonical set. At minimum, implementations MUST support:
- `invalid_json`
- `missing_envelope_fields`
- `snapshot_unresolvable`
- `snapshot_ref_hash_mismatch`
- `unknown_canonical_id`
- `unsupported_hash_algo`
- `unsupported_hash_encoding`
- `integrity_mismatch`
- `signature_key_unknown`
- `signature_invalid`
- `missing_snapshot_fields`

Reason tokens are frozen in `specs/protocol-invariants/probity-v1.invariants.spec.md`.
Implementations MAY add additional reasons only if namespaced (e.g., `com.example.reason`).

## Trust & key management note
Key provisioning is out-of-scope. Verifiers MUST accept key material and signer metadata via configurable trust roots, registries, or supplied key sets.