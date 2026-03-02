# Tamper Evidence Model

## Purpose
Define how a record demonstrates it has not been modified after creation.

## Guarantee
A valid record allows independent verification that its Decision Snapshot contents changed or did not change since recording.
Tamper evidence guarantees record integrity after creation.
It does not guarantee the correctness of the recorded information at creation time.

## Mechanism Requirements
Implementations MUST provide:
- stable canonicalization of the Decision Snapshot
- hash-based integrity metadata that enables independent digest recomputation
- optional signatures, if desired, without making hashing dependent on signatures

Implementations MAY use signing, chaining, or anchoring in external ledgers.
Probity defines the requirement for reconstructable evidence, not a governance layer.

## Minimal Verification Metadata (REQUIRED)
To enable independent verification, a PRE MUST include metadata sufficient for canonical verification, including:

- `record_id` — globally unique identifier for the record
- `spec_version` — version of the Probity spec the record conforms to
- `encoding_id` — identifies the concrete encoding (e.g., `probity-json:v1`)
- `schema_version` — snapshot schema identifier
- `canonical_serialization_id` — canonicalization algorithm used to produce snapshot bytes
- `created_at` — time of record creation (see threat model for clock trust assumptions)
- `integrity` — hash metadata and expected digest over canonical snapshot bytes:
  - `hash_algo`
  - `hash_encoding`
  - `digest`
  - `canonical_serialization_id`

Optional:
- `signature` — signature metadata + value if a signature is applied, including:
  - `signature_algo`, `signer_key_id`, `target`, `signature_encoding`, `signature`

## Verification Result
Verification produces one of four states:

- `verified` — digest matches (and if signature present, signature is valid)
- `unverified` — insufficient data or unsupported algorithms prevent verification
- `invalid` — evidence of modification (digest mismatch) or signature mismatch
- `incomplete` — required fields missing (omitted)

## Independence
Verification MUST be possible without the original runtime environment, given access to:
- the PRE
- the snapshot (embedded or resolvable)
- any referenced artifacts needed for resolution
- any required key material for signature verification

## Limitations
Tamper evidence does not prove:
- the record is complete (beyond field presence checks)
- the decision was correct
- the action was authorized

It only proves the snapshot bytes used for digest/signature verification have not been altered since recording (relative to the digest/signature carried by the PRE).