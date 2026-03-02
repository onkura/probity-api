
# Verification Test Vectors — Guidance (Layer 4)

## Purpose
Provide guidance for creating a minimal set of test vectors that any verifier implementation should use to validate correctness and interoperability.

## Recommended Test Vector Set
At minimum, provide the following vectors (each vector includes PRE, snapshot, canonical bytes, expected digest, and optional signature material):

1. **Basic Verified Record** — small snapshot, canonicalized, hashed with SHA-256, digest matches (PRE `integrity.digest`). No signature.
2. **Embedded Snapshot** — snapshot embedded in PRE; verify resolution and hash match.
3. **External Snapshot Reference** — snapshot referenced via URI with content-hash; verifier must resolve and compute correct hash.
4. **Signature Valid** — signed snapshot with a known test key; verifier must validate signature.
5. **Integrity Mismatch** — tampered canonical bytes where computed digest differs — verifier must return `invalid` with `integrity_mismatch`.
6. **Unknown Canonical ID** — PRE whose `canonical_serialization_id` is not supported — verifier returns `unverified` with `unknown_canonical_id`.
7. **Incomplete Snapshot** — missing required field — verifier returns `incomplete` with `missing_fields` listing required fields.
8. **Late Record Metadata** — PRE with `evidence_quality: "late"` and `latency_ms` present; verifier ensures these fields are passed through in output.

## Format & Distribution
- Test vectors **MUST** be canonicalized and include both the original logical snapshot and the canonical bytes.
- Distribute test vectors in a public test suite (e.g., a `/test-vectors` directory) and include reference verifier code or scripts demonstrating verification steps.

