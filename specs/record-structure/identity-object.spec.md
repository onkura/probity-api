
# Identity Object — Specification (Layer 1)

## Purpose
Define the canonical representation of actors for use in Decision Snapshots and Record Envelopes.

## Identity Object (conceptual)
An Identity Object **MUST** represent one actor attribution and **MUST** be stable and resolvable within the deploying organization. The spec defines the minimal normative fields.

Required fields:
- `actor_id` (string) — opaque unique identifier for the actor
- `actor_type` (string) — one of `human|service|agent|delegated`
- `provenance` (object) — optional structured metadata describing origin (e.g., `org`, `role`, `versioned_credential_ref`)
- `revocation_state` (string, optional) — `active|revoked|unknown`

Notes:
- The spec intentionally avoids prescribing authentication mechanisms.
- Identity objects **MUST** include minimal provenance to permit later correlation by auditors.
