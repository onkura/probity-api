# Retention & Lifecycle Guidance

## Purpose
Define how Probity records may be stored and managed over time without affecting evidentiary meaning.

Probity specifies record interpretation, not retention duration.

---

## Retention Categories

Organizations typically maintain three storage phases:

1. Active — recent records available for immediate investigation
2. Archived — immutable storage for long-term audit
3. Extracted — metadata retained after content deletion

Probity remains valid across all phases if integrity evidence is preserved.

---

## Deletion

If underlying referenced data is deleted:

The record remains valid historical evidence.

Investigators interpret it as:

"information existed but is no longer available"

Deletion MUST NOT modify the original record.

---

## Expiration

Retention duration is determined by organizational policy.

The spec does not require permanent storage.

---

## Legal Holds

When legal hold applies:

Organizations SHOULD preserve both records and referenced artifacts where permitted by policy.

Probity does not manage legal holds.

---

## Migration

Records MAY be migrated across storage systems if:

- canonical serialization is preserved
- integrity verification remains possible

Migration must not alter the record content.