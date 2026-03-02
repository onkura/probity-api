
# Late Recording Specification (Layer 3)

## Purpose
Define normative rules and metadata when a PRE is created after the external effect has completed (a 'late' record).

## Definition
A record is considered **late** if the `created_at` timestamp is after the system's transmission of the external instruction or observable commitment event (commitment point).

## Requirements for Late Records
When a PRE is late, the PRE **MUST** include:
- `evidence_quality: "late"`
- `latency_ms` — integer milliseconds between commitment point and PRE creation
- `latency_reason` — short stable token indicating cause (e.g., `recorder_down`, `queue_backpressure`, `deferred_capture`)
- `originating_event_id` — identifier for the external action event if available

## Treatment of Late Records
- Late records remain valid evidence but have lower evidentiary confidence.
- Implementations **MUST** surface `late` records to monitoring and investigation tooling.

## Acceptable Thresholds
- The spec does not mandate exact latency thresholds but **RECOMMENDS** implementers document their SLAs for synchronous and async flows in operational docs.
