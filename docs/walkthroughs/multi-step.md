# Walkthrough: Multi-step execution (chain of records)

This walkthrough shows how to represent a multi-step workflow as multiple Probity records, rather than one oversized record.

Probity is a minimal evidence layer. For multi-step behavior, prefer multiple PREs with explicit lineage.

## Scenario
An agent:
1) gathers evidence (retrieval)
2) proposes a plan
3) commits an external action (ticket creation)

Each step emits its own PRE at the moment it commits to an externally meaningful action.

## Why multiple records
One monolithic record encourages ambiguity:
- unclear which evidence applied to which commit
- unclear what changed between steps
- harder to verify or partially reconstruct

Multiple records preserve:
- smaller, more auditable decision snapshots
- explicit lineage relationships

## Lineage pattern
When step 3 is derived from step 1/2:
- include `snapshot.lineage_refs` in the new snapshot
- each lineage link references a parent `record_id` and a `relation_type`

Example link:
- `relation_type = derived_from` for “this decision was derived from earlier evidence”
- `relation_type = influenced_by` for “this decision was influenced by earlier state”

(If you also store artifacts elsewhere, you can include `evidence_ref` and hashes.)

## Late capture and reconstruction
If a step’s record is created after the action completed (recorder outage, async reconstruction), mark:
- envelope `evidence_quality = late`

See `examples/late-record.json`.

## Detecting tamper-evidence failures
A schema-valid record can still fail verification if integrity doesn’t match the snapshot bytes.
This is a core property: “valid JSON shape” is not “valid evidence”.

See `examples/integrity-mismatch.json`.