
# Probity Recording Procedure Specification (Layer 3)

## Purpose
Define the step-by-step mechanical procedure an implementation SHOULD follow to produce a Probity-compliant record at the Decision Boundary. This prevents inconsistent timing, ordering, and incomplete captures across implementations.

This document is normative. The keywords **MUST**, **SHOULD**, and **MAY** are used as defined in RFC 2119.

## Overview
Implementations **MUST** follow a deterministic sequence when creating a record tied to an imminent external action. The sequence below describes the recommended atomic flow. Implementations are free to optimize but MUST preserve the observable semantics.

### Core Procedure (synchronous flow)
1. **Snapshot Capture** — gather Decision Snapshot components (perception, responsibility, intent, selection_basis, any references). This MUST be a stable, immutable object after capture.
2. **Canonicalize** — apply canonicalization (`canonical_serialization_id`) to the snapshot to produce the canonical byte sequence.
3. **Compute Integrity** — compute the expected digest over canonical snapshot bytes according to `hashing.spec`.
   Populate the PRE `integrity` object with:
   - `hash_algo`
   - `hash_encoding`
   - `digest` (expected)
   - `canonical_serialization_id`
4. **Assemble PRE** — create the Probity Record Envelope including `record_id`, `spec_version`, `encoding_id`, `schema_version`, `canonical_serialization_id`, and `integrity`
5. **Persist** — persist the PRE to durable storage in an append-only manner when possible. If persistence fails, follow Failure-State rules.
6. **Emit Reference** — emit the PRE reference into the runtime (e.g., attach to event, include in outgoing API headers, publish to audit stream). The emission MUST occur before or concurrent with the external instruction transmission (see Commitment Point Definition).
7. **Optional Sign** — if signatures are used, include a PRE `signature` object and sign either:
   - `snapshot_bytes`: the canonicalized snapshot bytes, or
   - `snapshot_digest`: the raw digest bytes corresponding to PRE `integrity.digest` (decoded per `integrity.hash_encoding`).
   
### Async / Queued Flow
- For queued or asynchronous actions, the PRE **MUST** be created at enqueue time (the decision boundary) and include enqueue metadata (queue_id, enqueue_time). Worker execution MAY attach execution metadata but MUST NOT replace the original PRE.

### Idempotency & Retries
- The implementation **MUST** ensure idempotency of PRE creation for a single logical decision. Retries caused by transient persistence failures SHOULD write the same PRE `record_id` and not create duplicate semantic records (use unique dedup tokens).

### Observability
- The system **MUST** emit operational signals describing PRE quality (see Failure States). These signals MUST be observable by operator tooling (logs/metrics/events).

## Atomicity Note
- Implementations **SHOULD** attempt to make PRE creation atomic relative to the external action. If atomicity cannot be achieved due to technical constraints, the PRE MUST be marked with an evidence quality state reflecting its temporal relation (e.g., `late`) and include `latency_ms` metadata.

