
# Decision Snapshot Schema — Specification (Layer 1)

## Purpose
Provide a normative schema-level mapping for the conceptual Decision Snapshot defined in the docs. This spec defines required and optional fields and their semantics at the data level.

## Normative statement
This document defines the **conceptual** Decision Snapshot fields and semantics.

- Implementations claiming Probity v1 compliance **MUST** capture the required conceptual fields below.
- For the **normative JSON field names and shapes**, see `specs/encodings/probity-json.v1.spec.md` (`encoding_id = probity-json:v1`).

(Other encodings are permitted, but they MUST be losslessly renderable into `probity-json:v1` for independent verification.)

## Required Fields (conceptual -> schema)
- `perception` (object) — representation of the information the system relied upon. **MUST** be representable as references or inline minimal descriptors. Examples:
  - `inputs` (array of references) — references to user inputs, prompts, or triggers
  - `evidence_refs` (array) — references (hashes/URIs) to retrieved documents or tool outputs
  - `env` (object) — key-value map of relevant environmental observations (non-sensitive keys encouraged)

- `responsibility` (object) — attribution claim. **MUST** include:
  - `actor_id` (string) — identity reference for the actor the system associated with the decision
  - `actor_type` (string) — one of `human|service|agent|delegated`
  - `authority_scope` (object) — description of the permission scope the system believed applied (e.g., role, approval_tier, monetary_limit)

- `intent` (object) — the committed action. **MUST** include:
  - `action_type` (string) — short action verb (e.g., `refund`, `approve`, `deploy`)
  - `action_params` (object) — opaque map of parameters required to execute the action (may contain references)

- `selection_basis` (object) — the structured criteria used to select the committed action over alternatives. **MUST** include at least one of:
  - `score_signals` (object) — named signals or scores that influenced selection
  - `policy_refs` (array) — policy or rule references applied in decision
  - `heuristic_tags` (array) — short, stable tags indicating rationale (e.g., `high_risk`, `policy_override`)

- `outcome` (object) — observed result reference. **MUST** include:
  - `observed_result` (string) — short status (e.g., `succeeded`, `failed`, `unknown`)
  - `result_refs` (array) — references to downstream artifacts (transaction id, API response hash)
  - `observed_at` (timestamp) — when the system observed the outcome or its belief about it

- `integrity` (object) — **REMOVED in v1 snapshot payload**.

  Integrity metadata (hash algorithm, encoding, digest, canonical serialization id) is part of the **Record Envelope**.
  Embedding integrity pointers inside the snapshot creates ambiguity and encourages circular constructions.

  If an implementation needs to attach snapshot-local proof hints, it **MUST** place them under `extensions` and they
  will be covered by integrity like any other snapshot content.

## Optional Fields
- `human_approval` (object) — if a human intervened before or after commitment
- `lineage_refs` (array) — references to prior Decision Snapshots relied upon
- `raw_capture_policy` (boolean) — whether raw content was included
- `evidence_quality` (string) — mirrors envelope field when present

## Schema Evolution
- New optional fields **MAY** be added. Renaming or repurposing required fields **MUST NOT** occur without bumping `schema_version` and documenting migration guidance.

