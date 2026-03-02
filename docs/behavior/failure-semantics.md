
# Failure Semantics

## Purpose
Define how investigators interpret absent or incomplete records.

## Recorder Failure
If recording infrastructure fails, actions may still occur.
The absence of a record does not invalidate the action.

## Partial Records
A record missing components is incomplete evidence.
Incomplete records must remain distinguishable from valid records.

## Storage Failure
If a record cannot be persisted, the system SHOULD emit an operational alert.
Probity does not define alerting mechanisms.

## Tampering Suspicion
If integrity verification fails, the record becomes untrusted evidence.
Untrusted records remain historically relevant but unverifiable.

## Unknown State
Three states exist:
- verified record
- incomplete record
- no record

These states describe evidence quality, not system correctness.

## Out-of-Scope Actions

Systems may define actions outside recording scope.

Absence of a record can mean:
- recorder failure, or
- action not within recording scope

Probity records do not imply coverage completeness unless declared externally.