# Schema & Compatibility

## Purpose
Ensure records remain interpretable across versions of the specification.

---

## Version Fields

Every record MUST include:

- `spec_version`
- `schema_version`

These allow future interpretation of historical records.

---

## Backward Compatibility

New versions SHOULD NOT change the meaning of existing fields.

If a concept changes meaning, a new field SHOULD be introduced instead of redefining an existing one.

---

## Deprecation

Fields MAY be deprecated but MUST remain interpretable.

Deprecated fields SHOULD be documented but not removed from historical records.

---

## Forward Compatibility

Parsers SHOULD ignore unknown fields.

Unknown data MUST NOT invalidate the record.

---

## Compatibility Principle

Two systems are compatible if a reviewer interprets their records the same way, even if their internal implementations differ.