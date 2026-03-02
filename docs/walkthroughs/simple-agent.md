# Walkthrough: Simple Agent (single-step action)

This walkthrough shows a basic agent performing one externally meaningful action and emitting a Probity Record Envelope (PRE) with an embedded Decision Snapshot.

Probity does not judge correctness or block the action. It records the decision state under which the agent committed.

## Scenario
An ops agent observes an alert and creates a ticket.

## Evidence captured
The snapshot’s `perception` carries:
- `inputs`: a reference to the triggering user message or alert payload
- `evidence_refs`: hashes/URIs for any retrieved documents used in the decision

Example: see `examples/basic-pre.json`.

## Authority captured
The snapshot’s `responsibility` carries:
- `actor_id`: the agent identifier
- `authority_scope`: the permissions the system believed it had (role + allowed action class)

This is a claim of *authority context*, not proof of authorization.

## Selection captured
The snapshot’s `selection_basis` carries:
- `policy_refs` (optional): policy documents or config versions referenced
- `heuristic_tags` / `score_signals` (optional): decision basis hints without implying correctness

## Commit captured
The snapshot’s `intent` describes the intended externally meaningful action (e.g., `create_ticket`).
The snapshot’s `outcome` binds what was observed about the result (ticket id, transaction id, etc.).

## Integrity and optional signatures
The PRE carries:
- `integrity`: hash algorithm + encoding + digest over canonicalized snapshot bytes
- `signature` (optional): if present, a signature over either snapshot bytes or snapshot digest

The example uses `target = snapshot_digest`.

## Minimal vs typical
- For a minimal schema-valid record, see `examples/minimal-pre.json`.
- For a richer record with inputs/evidence/signature, see `examples/basic-pre.json`.