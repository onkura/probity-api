# Probity v1 Protocol Invariants

## Purpose
Freeze protocol-level invariants required for independent verification across implementations.
This file is normative for `spec_version = probity-v1` and `encoding_id = probity-json:v1`.

If an implementation behavior is not consistent with this document, two independent implementations may diverge while both claiming compliance.

This document is normative. The keywords **MUST**, **SHOULD**, and **MAY** are used as defined in RFC 2119.

## Applicability
These invariants apply to:
- `encoding_id = probity-json:v1`
- verification and verifier output for Probity v1

---

## 1. Canonicalization identifiers
The canonicalization identifier is declared in:
- PRE `canonical_serialization_id`
- PRE `integrity.canonical_serialization_id` (MUST match the PRE field)

### Allowed values
For `probity-json:v1`, the allowed set is:

- `jcs:rfc8785`

Records claiming `encoding_id = probity-json:v1` **MUST** use:
- `canonical_serialization_id = jcs:rfc8785`

No other canonicalization identifiers are valid for `probity-json:v1`.

---

## 2. Canonicalization rules (JCS strict profile)
When `canonical_serialization_id = jcs:rfc8785`, implementations **MUST** canonicalize the Decision Snapshot using RFC 8785 (JSON Canonicalization Scheme).

Additional strictness requirements for Probity v1:
- JSON numbers **MUST** be finite (no NaN/Infinity).
- `-0` **MUST NOT** be used (use `0`).
- Objects **MUST NOT** contain duplicate keys. Duplicate keys are invalid input.

### Unicode / UTF-8 normalization rule
Probity v1 **MUST NOT** apply Unicode normalization (e.g., NFC/NFD) to JSON strings.
Implementations MUST treat JSON strings as defined by JSON parsing + JCS output rules.

- Input JSON MUST be valid UTF-8 (no BOM).
- Canonical output MUST be UTF-8 bytes produced by JCS.
- No additional character normalization is permitted.

Rationale: Unicode normalization changes meaning and creates invisible transformations in an evidence layer.

---

## 3. Allowed hash algorithms
Hash parameters are declared in the PRE `integrity` object.

### Allowed values
For `probity-json:v1`, allowed hash algorithms are:

- `sha256`

Records claiming `encoding_id = probity-json:v1` **MUST** use:
- `integrity.hash_algo = sha256`

---

## 4. Digest encodings
Digest encoding is declared in:
- `integrity.hash_encoding`

### Allowed values
For `probity-json:v1`, allowed encodings are:

- `hex`
- `base64url`

If `hash_encoding = hex`:
- digests MUST be lowercase hex.

If `hash_encoding = base64url`:
- digests MUST be URL-safe base64 without padding.

### v1 default
For published test vectors, the default digest encoding is:
- `hex`

---

## 5. Digest input and scope
The expected digest (PRE `integrity.digest`) **MUST** be computed over:
- the canonicalized Decision Snapshot bytes (UTF-8), and
- ONLY the snapshot bytes (not the PRE wrapper), unless a future encoding explicitly specifies otherwise.

---

## 6. Signature target values
If a PRE includes `signature`, the signature target is declared in:
- `signature.target`

### Allowed values
Allowed signature targets are:

- `snapshot_bytes`
- `snapshot_digest`

Target semantics:
- `snapshot_bytes`: signature over canonical snapshot bytes.
- `snapshot_digest`: signature over raw digest bytes corresponding to PRE `integrity.digest` (decoded per `integrity.hash_encoding`).

Records claiming `encoding_id = probity-json:v1` **MUST NOT** use any other signature target.

---

## 7. Verification status and reason token set
Verifier output status MUST be one of:

- `verified`
- `unverified`
- `invalid`
- `incomplete`

Verifier output reasons MUST come from the canonical token set below.

### Canonical reason tokens (minimum required)
Implementations MUST support emitting the following reason tokens:

- `invalid_json`
- `missing_envelope_fields`
- `snapshot_unresolvable`
- `snapshot_ref_hash_mismatch`
- `unknown_canonical_id`
- `unsupported_hash_algo`
- `unsupported_hash_encoding`
- `integrity_mismatch`
- `signature_key_unknown`
- `signature_invalid`
- `missing_snapshot_fields`

Implementations MAY emit additional reasons, but they MUST be namespaced (e.g., `com.example.reason`) to avoid collisions.

---

## 8. Backwards compatibility and versioning
Any breaking change to these invariants requires:
- a new `encoding_id` (e.g., `probity-json:v2`) and
- a new invariant freeze document.

Probity v1 invariants are frozen once test vectors are published.