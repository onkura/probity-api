
# Failure States & Evidence Quality Specification (Layer 3)

## Purpose
Define canonical evidence quality states and the required metadata for each state. These machine-readable states enable monitoring, automated responses, and consistent investigator interpretation.

## Evidence Quality States (enumeration)
A PRE **MUST** include an `evidence_quality` field with one of these values:
- `verified` — PRE exists and integrity verification succeeded
- `incomplete` — PRE persisted but one or more mandatory fields were missing (omitted)
- `late` — PRE created after commitment point (see late-recording.spec)
- `unverified` — integrity verification could not be performed due to missing or unusable verification metadata

`absent` is **not** a PRE value (no PRE exists). Systems **MUST** emit an operational event (log/metric)
when a decision that should produce a PRE has no corresponding PRE within configured SLA.

## Metadata Requirements
- `incomplete` PREs **MUST** include `missing_fields` (array of strings) describing the omitted mandatory fields.
- `unverified` PREs **MUST** include `verification_failure_reason` (short token) describing why verification failed (e.g., `missing_integrity_metadata`, `unknown_canonical_id`, `unsupported_hash_algo`)..

## Operational Signals
- Systems **MUST** export metrics/counters for each evidence quality state (e.g., `probity.pre.verified.count`, `probity.pre.late.count`).
- Systems **SHOULD** emit alerts when `absent` events exceed configured thresholds.

