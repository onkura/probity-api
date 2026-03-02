# Walkthrough: Tool Call (agent uses an external tool)

This walkthrough shows how to record a decision where an agent calls an external tool (API, retrieval system, database) before committing to an action.

Probity is not a tool tracer. We record only what is needed to reconstruct the decision basis.

## Scenario
An agent:
1) retrieves a runbook page from a knowledge base
2) decides to create a ticket using the runbook guidance

## Where the tool call appears
Tool interaction evidence belongs in `snapshot.perception`:
- Put tool outputs in `evidence_refs` as references (URI + content hash), not full payloads.
- Optionally include stable, non-sensitive metadata in `perception.env` (e.g., tool name, region).

This keeps the snapshot small while allowing independent verification of what was consulted.

## Recommended pattern for evidence refs
Represent a tool output as an evidence reference:
- `type`: a token (e.g., `tool_output`, `retrieved_doc`)
- `uri`: where the output is stored (optional but helpful)
- `content_hash`: hash binding the exact bytes of the referenced artifact

See `examples/basic-pre.json` for the shape.

## If the tool output is unavailable
If the referenced artifact cannot be retrieved later, you still emit a record, but you downgrade:
- `evidence_quality` in the PRE (e.g., `incomplete` or `unverified`)
Note: `absent` is not a PRE value; it is an operational signal used when no PRE exists for an expected decision.
- optionally provide a reason under `snapshot.extensions` or envelope `extensions`

This is still useful evidence: it records that an action was committed under incomplete reconstruction conditions.

## External snapshots
If the snapshot is too large to embed (e.g., sensitive data stored elsewhere), use `snapshot_ref` in the envelope and bind:
- `snapshot_ref.content_hash` for artifact bytes
- envelope `integrity.digest` for canonicalized snapshot bytes

See `examples/external-snapshot.json`.