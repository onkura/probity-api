
# Probity Canonicalization Specification (Layer 2)

## Purpose
Define a language- and implementation-independent canonicalization process for Decision Snapshot payloads prior to integrity computation. Canonicalization ensures that independently-produced serializations of the same logical snapshot produce identical canonical byte sequences for hashing/signing.

This document is normative. The keywords **MUST**, **SHOULD**, and **MAY** are used as defined in RFC 2119.

## Scope
Applies to the Decision Snapshot payload (the snapshot object referenced by the PRE `snapshot_ref`) and any embedded objects that contribute to the snapshot's integrity.

## High-Level Requirements
1. The canonicalization process **MUST** produce a deterministic byte sequence for logically equivalent snapshot data.
2. The process **MUST** be deterministic across languages and environments if the same canonicalization algorithm and parameters are applied.
3. The canonicalization **MUST** be fully specified so that independent implementations can reproduce the same byte sequence.

## Canonicalization Algorithm

### Canonicalization identifiers
A PRE **MUST** declare the canonicalization algorithm via `canonical_serialization_id`.

For the normative v1 JSON encoding (`encoding_id = probity-json:v1`), the canonicalization identifier:
- **MUST** be `jcs:rfc8785`

Other encodings **MAY** use other identifiers, but they **MUST** be fully specified and independently implementable.

### `jcs:rfc8785`
When `canonical_serialization_id` is `jcs:rfc8785`, the Decision Snapshot payload is canonicalized using
RFC 8785 JSON Canonicalization Scheme (JCS) to produce canonical UTF-8 bytes.

Additional v1 constraints:
- JSON numbers **MUST** be finite (no NaN/Infinity).
- `-0` **MUST NOT** be used (use `0`).

### Arrays
Canonicalization **MUST NOT** reorder arrays. Array order is always preserved.

## Canonicalization Identifier
- Implementations **MUST** set `canonical_serialization_id` in the PRE to a string identifying the canonicalization algorithm and parameters used (e.g., `canonical-json:v1`).
- Verification requires knowledge of which canonicalization id was used.

## Handling Optional Fields
- Fields that are absent are treated as absent (i.e., not null).
- Implementations **MUST** document whether they include optional fields with `null` values in canonicalization; by default omit optional fields that are not present.

## Binary Data
- Binary payloads referenced by the snapshot **MUST** be represented by deterministic references (e.g., content hashes) in the snapshot; canonicalization MUST NOT embed non-deterministic binary encodings.

## Backwards Compatibility
- If canonicalization rules evolve, the `canonical_serialization_id` MUST change to reflect a new algorithm or parameter set.
