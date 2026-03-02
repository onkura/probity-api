# Privacy & Redaction Guidance

## Purpose
Provide implementation guidance for storing decision evidence while minimizing exposure of sensitive data.

Probity records decision context, not raw business data.

---

## Reference-First Principle

Implementations SHOULD store stable references instead of raw content whenever possible.

Preferred forms:

- cryptographic hash of content
- object identifier
- document version reference
- provenance URI

Raw content capture SHOULD be avoided by default.

---

## Sensitive Data

Sensitive categories include (non-exhaustive):

- personal identifiers
- protected health information
- financial account data
- confidential business documents
- authentication secrets
- user free-text inputs

If such data influences a decision, implementations SHOULD store a reference that allows later retrieval under proper authorization rather than embedding the data in the record.

---

## Explicit Raw Capture

If raw capture is required:

- the record SHOULD include `raw_capture_policy: true`
- retention policies MUST be defined externally
- access controls MUST be enforced outside the Probity spec

Probity does not define access control.

---

## Redaction Stability

Redaction MUST preserve interpretability.

A reviewer should still be able to determine:

- what category of information was used
- whether changing it could alter the decision

Example:
Instead of storing a full document → store document hash + classification label.

---

## Legal Coordination

Organizations SHOULD align redaction practices with legal and compliance teams before enabling raw capture modes.

Probity provides evidence structure, not privacy policy.