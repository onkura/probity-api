
# Event Chain Model

## Purpose
A single decision rarely explains an incident.
Probity records form a sequence describing how state evolved.

## Decision Lineage
A record MAY reference a prior record.

This indicates:
The later decision depended on the earlier decision outcome.

Lineage represents influence, not causation proof.

## Parent and Child Decisions
A decision is a child when its perception includes another decision’s outcome reference.

Multiple children may reference the same parent.

## Composite Actions
A workflow containing multiple commitments produces multiple records.
Probity records decisions, not workflows.

## Human Interaction
If a human reviews and confirms an action, the human action is a separate decision.

The system decision and the human decision are independent records.

## Overrides
A later decision may contradict an earlier decision.
Both records remain valid historical evidence.

## Absence of Lineage
If no reference exists, decisions are independent.
Implementations MUST NOT infer relationships from timing alone.

## Causality

Lineage represents decision causality, not chronological order.

A parent decision is one whose outcome was relied upon when committing the child decision.