
# Probity Record Envelope — Specification (Layer 1)

## Purpose
Define the canonical outer container for all Probity records. The envelope provides versioning, provenance, canonicalization pointers, and integrity metadata required for independent verification.

This document is normative. The keywords **MUST**, **SHOULD**, **MAY**, and **MUST NOT** are used as defined in RFC 2119.

## Envelope Overview
A Probity Record Envelope (PRE) is an immutable container that wraps a Decision Snapshot and associated metadata.

This document defines the **conceptual** envelope fields and semantics.
For the **normative JSON field names and shapes**, see `specs/encodings/probity-json.v1.spec.md` (`encoding_id = probity-json:v1`).

A PRE **MUST** include the following conceptual fields:

- `record_id` (string) — globally unique identifier for the record (e.g., UUID or URN)
- `spec_version` (string) — Probity spec version the record conforms to (e.g., `probity-v1`)
- `encoding_id` (string) — identifies the concrete encoding (v1 normative JSON: `probity-json:v1`)
- `schema_version` (string) — schema version for the snapshot payload
- `canonical_serialization_id` (string) — identifier for the canonicalization rule applied to the snapshot
- `snapshot` (object) **or** `snapshot_ref` (object) — embedded snapshot or reference to one
- `integrity` (object) — machine-readable hash metadata + expected digest over canonicalized snapshot bytes
- `created_at` (timestamp) — record creation time (see Timestamp requirements)
- `evidence_quality` (string) — one of `verified|incomplete|late|unverified` (see failure-states.spec)
  Note: `absent` is not a PRE value (no PRE exists). It is reserved for operational signals where an expected PRE is missing.

Optional conceptual fields:
- `signature` (object) — signature metadata + value, if present
- `extensions` (object) — reserved container for implementer-specific data

## Envelope Rules
- `record_id`, `spec_version`, `schema_version`, `canonical_serialization_id`, `integrity`, and `created_at` **MUST** be present.
- The envelope **MUST** be immutable after creation; implementations **SHOULD** treat modification as a distinct new record (and not mutate the existing PRE).
- The envelope **MUST** allow extraction (or resolution) of the Decision Snapshot and reproduction of the canonicalized bytes used to compute `integrity.digest` without requiring the original runtime.

## Embedding vs Referencing
A PRE **MUST** carry the Decision Snapshot either embedded or by reference:

- Embedded form: `snapshot` contains the Decision Snapshot object.
- Referenced form: `snapshot_ref` contains a pointer **and** a binding hash of the referenced artifact bytes.

When referencing, the PRE **MUST** include sufficient metadata to verify the referenced payload:
- `snapshot_ref.uri` (string) — location of the snapshot artifact
- `snapshot_ref.content_hash` (object) — hash of the *exact bytes* stored at `uri`, including:
  - `hash_algo` (string)
  - `hash_encoding` (string)
  - `digest` (string)

Notes:
- `snapshot_ref.content_hash` binds the referenced artifact bytes.
- The PRE `integrity` binds the **canonicalized snapshot bytes** after parsing and canonicalization.
  These are distinct, and both may be necessary for reconstruction.

## Timestamps and Clocks
- `created_at` **MUST** be an RFC3339 timestamp in UTC with `Z` suffix (no offsets).
  - Fractional seconds are **OPTIONAL**.
  - If present, fractional seconds **MUST** be 1–9 digits.
- Implementations **MAY** include clock source metadata under `extensions` (e.g., NTP status, monotonic clock hints).
- Probity does not mandate clock synchronization protocols; implementations **SHOULD** document clock trust assumptions operationally.

## Backwards Compatibility
- Fields added in later spec versions **MUST** be optional for older records. `spec_version` **MUST** be used to interpret older records.

