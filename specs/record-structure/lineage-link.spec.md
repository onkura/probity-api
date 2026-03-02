
# Lineage Link — Specification (Layer 1)

## Purpose
Define how Decision Snapshots reference prior snapshots for lineage and causality.

## Link format
A lineage link **MUST** include:
- `parent_record_id` (string) — the `record_id` of the referenced parent PRE
- `relation_type` (string) — one of `influenced_by|derived_from|approved_by|forked_from`
- `context` (object, optional) — summary of why the parent is referenced (e.g., `policy_ref`, `signal_used`)
- `evidence_ref` (string, optional) — content-hash or artifact id if parent snapshot payload not embedded

## Semantics
- A child snapshot **MUST** include a lineage link when the parent snapshot's outcome was used as perception or selection input.
- Lineage links represent decision causality, not mere temporal ordering.
