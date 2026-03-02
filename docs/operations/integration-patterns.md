
# Integration Patterns

## Purpose
Illustrate typical deployment contexts for Probity recording.

## Synchronous Agent
Record created immediately before external action.

## Asynchronous Job
Record created when work is queued.

## Human-in-the-Loop
Human approval generates a separate record.

## Tool Orchestration
Each tool action crossing a decision boundary creates its own record.

## Batch Automation
Each committed external effect produces a record.

## Operational Guidance: SLAs & Alerts

To be operationally useful, implementers should define expected emission SLAs and monitoring:

- **Synchronous actions**: aim for record emission within X ms of the decision (example default: 500ms).
- **Asynchronous/queued actions**: record enqueue time and processing latency; include `latency_ms`.
- **Persistence failure**: emit an operational alert; mark evidence state `absent`.
- **Corrupted verification**: emit an alert and mark evidence state `unverified`.

These are implementation-level choices; the spec requires that the evidence state be observable and machine-readable.