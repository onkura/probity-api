# Probity JSON Schemas (probity-json:v1)

These JSON Schemas validate the **normative wire encoding** `encoding_id = probity-json:v1`.

They are intended to support:
- structural validation at record boundaries (producer, storage, verifier)
- deterministic parsing (no unknown top-level keys outside `extensions`)
- interoperability across independent implementations

## What these schemas are (and are not)
These schemas are:
- a **shape contract** for `probity-json:v1`
- compatible with JSON Schema **Draft 2020-12**
- designed to prevent ambiguous encodings (e.g., `null` vs omitted, unknown top-level keys)

These schemas are **not**:
- a policy engine
- an evaluation of correctness
- a guarantee that a record is meaningful
- a substitute for canonicalization + hashing + signature verification

## Key invariants enforced
- `spec_version` is fixed to `probity-v1`
- `encoding_id` is fixed to `probity-json:v1`
- timestamps are RFC3339 UTC with `Z` suffix (fractional seconds optional, 1–9 digits)
- `snapshot` XOR `snapshot_ref` in the PRE
- extension data must be under `extensions` and uses namespaced keys
- `null` is not allowed anywhere in v1

## Canonical enumerations
Enumerations used across schemas are centralized under `schemas/enums/`.
Schemas MAY reference them via `$ref` if you prefer (recommended), but some schemas inline enums for ease of consumption.

## Referencing and $id
Schemas include `$id` fields (example: `https://probity.dev/schemas/...`) that SHOULD be replaced with your canonical schema base URL.
Keep `$id` stable once published to preserve long-term verifiability.

## Versioning guidance
- Schema files are versionless by filename for v1; changes MUST be backwards compatible.
- Any breaking change requires a new encoding id (e.g., `probity-json:v2`) and a new schema set.