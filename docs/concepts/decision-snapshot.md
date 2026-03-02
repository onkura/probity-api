
# Decision Snapshot Model
The snapshot reconstructs the decision environment.

Components:
- perception: information relied upon
- responsibility: actor attribution
- intent: committed action
- outcome reference: observed result
- integrity reference: tamper evidence

## Selection Basis

A record MUST include the basis on which the system selected the committed action over other viable actions.

This does not require reasoning text or chain-of-thought.
It represents the criteria or signals the system treated as decision-determining at the moment of commitment.

The selection basis exists so independent reviewers can determine why this action was taken instead of alternatives.

## Reference-First Principle (NORMS)

Implementations **SHOULD** prefer storing stable references (hashes, object IDs, or provenance URIs) to sensitive raw content.  
Raw payload capture (e.g., full user messages, full retrieved documents, or PHI) **MUST** be an explicit local policy decision, recorded in organizational governance, and visible in record metadata (e.g., `raw_capture_policy: true`).  

Rationale: reference-first reduces privacy, legal, and storage risk while preserving reconstructability.

Implementations SHOULD store references instead of raw data.

Goal:
Allow reviewers to understand conditions under which the action occurred.

## Schema & Spec Versioning

Every record **MUST** include the `spec_version` and a `schema_version` field. These enable future evolution while preserving interpretability of older records.