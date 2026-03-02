
# Recorder Alerting & Operational Guidance (Layer 3)

## Purpose
Provide recommended machine-detectable signals and operational actions for common recorder states and failures.

## Recommended Signals (machine-readable)
- `probity.pre.persist.failure` — counter of persistence failures
- `probity.pre.late` — histogram of `latency_ms` for late PREs
- `probity.pre.incomplete` — counter of incomplete PREs
- `probity.pre.absent` — counter or event stream for expected missing PREs
- `probity.pre.unverified` — counter of PREs failing verification

## Suggested Alerting Rules
- Alert on `probity.pre.persist.failure` rate above configurable threshold for N minutes.
- Alert on `probity.pre.absent` events exceeding expected SLA: e.g., > 1% absent over 5 minutes.
- Alert on repeated `probity.pre.unverified` occurrences, indicating potential canonicalization/hash/signature mismatch issues.

## Operational Playbooks
Implementations **SHOULD** provide runbooks for:
- diagnosing persistence failures (check storage, dedup keys, space, permissions)
- investigating late PREs (check queue/backpressure, clock skew)
- handling unverified PREs (check canonicalization id, hashing params, signer key availability)

