
# Recording Semantics

## Purpose
Define when and how records must be emitted during execution.

## Timing
A record MUST be created at the decision boundary before the external effect is committed when possible.

If atomic emission is impossible, the record MUST be created as close as practically possible to the commitment.

## Idempotency
Retries of the same commitment MUST NOT create new records unless the decision changes.

## Parallel Decisions
Simultaneous decisions are independent unless lineage is explicitly recorded.

## Partial Execution
If execution fails after commitment, the record remains valid.
Outcome reference reflects failure.

## Late Recording
A record created after an action completes MUST be marked as late.
Late records remain evidence but are lower reliability.

## Evidence quality in PRE vs operational evidence state

### PRE evidence_quality (normative)
The PRE `evidence_quality` field is a small, machine-readable indicator of evidence completeness for a record that exists.

Valid PRE values:
- `verified`
- `incomplete`
- `late`
- `unverified`

(See `specs/recorder-behavior/failure-states.spec.md` and the JSON Schema in `schemas/enums/evidence-quality.json`.)

### Operational evidence state (non-PRE)
`absent` is not a PRE value (no PRE exists). It is an operational signal used when a decision that should have produced a PRE has no corresponding PRE within an SLA.

Operational guidance:
- On storage/persistence failure: emit an operational alert (log/metric/event) and emit an `absent` signal for the expected record.
- On late emission: include latency and reason in operational metrics/logs and/or in PRE `extensions` (if captured).
- Audits and investigations SHOULD treat `absent` and `incomplete` situations as lower confidence evidence.

## Recording Requirement Modes

Implementations may operate in one of three recording modes:

- Evidence-Best-Effort: action may proceed if recording fails
- Evidence-Required: system retries recording before action proceeds
- Evidence-Blocking: action MUST NOT occur without a record

The chosen mode MUST be externally observable to system operators.
Probity itself does not mandate which mode is used.

## Commitment Point Definition

The commitment point is the moment the system irreversibly issues an instruction that can cause an external state change.

For purposes of Probity, commitment occurs when:
- a request is transmitted to an external system, or
- a durable write is issued to a persistence layer outside the model runtime.

Commitment does not require confirmation or success of the external effect.