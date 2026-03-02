# Recorder Alerting Guidance

## Purpose
Provide operational practices for detecting recording failures.

Probity defines evidence states; organizations monitor them.

---

## Recommended Signals

Implementations SHOULD emit operational signals for:

- persistence failure
- late recording
- incomplete record creation
- integrity verification failure

Signals may be logs, metrics, or monitoring events.

---

## Suggested Evidence States

Systems SHOULD surface:

- verified
- incomplete
- late
- absent
- unverified

---

## Operational Response

Typical responses:

| State | Example Action |
|------|------|
absent | investigate recorder availability |
late | inspect queue or service latency |
incomplete | check instrumentation |
unverified | investigate potential tampering |

Probity does not define alert thresholds.