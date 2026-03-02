
# Recorder Modes Specification (Layer 3)

## Purpose
Define the recording modes implementations may adopt and the observable semantics they imply.

## Modes
Implementations **MAY** operate in one of the following declared modes. The chosen mode MUST be externally declared in operational configuration and audit logs.

1. **evidence_best_effort** — PRE creation is attempted but action may proceed if recording fails.
   - Operational implication: higher throughput, lower evidence guarantees.
2. **evidence_required** — system retries PRE creation; the system may delay action until PRE is persisted or retries exhausted.
   - Operational implication: moderate assurance, potential increased latency.
3. **evidence_blocking** — action MUST NOT be transmitted without a persisted PRE; failure to persist prevents action.
   - Operational implication: highest assurance, may require transactional integration with downstream systems.

## Declaration
Implementations **MUST** declare the recorder mode in operational metadata and include it in monitoring dashboards (not necessarily in PRE itself).

