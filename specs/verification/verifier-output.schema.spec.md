
# Verifier Output Schema — Specification (Layer 4)

## Purpose
Define the machine-readable output a Probity verifier must produce. This output is used by downstream tooling (forensics, dashboards, alerts).

## Top-level fields
A verifier **MUST** produce the following JSON object as output:

- `record_id` (string) — the PRE record id being verified
- `verification_time` (string) — RFC3339 timestamp in UTC with `Z` suffix (fractional seconds optional, 1–9 digits)
- `status` (string) — one of `verified|unverified|invalid|incomplete`
- `status_reasons` (array) — list of short tokens explaining status (e.g., `integrity_mismatch`)
- `integrity` (object) — `{ hash_algo, hash_encoding, computed_digest, expected_digest, match: true|false }`
- `signature` (object, optional) — if a signature was present:
  `{ signer_key_id, signature_algo, target, signature_valid: true|false }`
- `missing_fields` (array, optional) — list of missing required fields if `incomplete`
- `evidence_quality` (string, optional) — pass-through of PRE's declared evidence quality if present
- `canonical_serialization_id` (string) — identity of applied canonicalization
- `notes` (string, optional) — human-friendly note for investigation

## Example Output (verified)
```json
{
  "record_id": "urn:probity:1234",
  "verification_time": "2026-03-01T12:00:00Z",
  "status": "verified",
  "status_reasons": [],
  "signature": { "signer_key_id": "kms:abc", "signature_algo": "ed25519", "signature_valid": true },
  "integrity": { "algorithm": "sha256-hex", "computed_digest": "abcd...", "expected_digest": "abcd...", "match": true },
  "canonical_serialization_id": "canonical-json:v1"
}
```

