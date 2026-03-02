# Probity Hashing Specification (Layer 2)

## Purpose
Define hashing requirements for computing the expected digest (PRE `integrity.digest`) over canonicalized Decision Snapshot byte sequences.

This document is normative. The keywords **MUST**, **SHOULD**, and **MAY** are used as defined in RFC 2119.

## Overview
The expected digest (PRE `integrity.digest`) is computed over the canonicalized Decision Snapshot bytes as defined by `canonical_serialization_id`.
The PRE `integrity` object **MUST** enable independent verification by any party that can access the snapshot and reproduce canonical bytes.

## Required Properties
1. **Determinism**: Given identical canonicalized bytes and hashing parameters, the computed digest **MUST** be identical across implementations.
2. **Algorithm Identification**: The PRE **MUST** include a machine-readable `integrity` object declaring:
   - `hash_algo`
   - `hash_encoding`
   - `digest` (expected)
   - `canonical_serialization_id`
3. **Collision Resistance**: Implementations **SHOULD** use cryptographically secure hash functions (e.g., SHA-256 or SHA-512). MD5 and SHA-1 **MUST NOT** be used for new records.
4. **Hash Encoding**: Hash digests **MUST** be encoded using lowercase hex or base64url. The encoding **MUST** be declared in `integrity.hash_encoding`.

## Hash Composition Rules
- The expected digest (PRE `integrity.digest`) **MUST** be computed solely over the canonicalized Decision Snapshot bytes (not over the PRE wrapper) unless the PRE explicitly documents an alternative composition.
- If the snapshot references external artifacts (e.g., `evidence_refs`), those artifacts **MUST** be represented by their content hashes within the snapshot; hashing the snapshot therefore indirectly covers referenced artifacts by their hashes.

## Hash Agility
- Implementations **MAY** support multiple hash algorithms.
- The selected hash algorithm and digest encoding **MUST** be indicated in the PRE `integrity` object:
  - `integrity.hash_algo`
  - `integrity.hash_encoding`
- Verifiers **MUST NOT** require any signature metadata to verify hash integrity.

## Nested Hashes and Merkleization (optional)
- For large snapshots or to support partial verification, implementations **MAY** use Merkle trees or nested hashing schemes. When used, the PRE MUST identify the composition scheme in a verifiable way (e.g., via a dedicated `canonical_serialization_id` or an explicitly versioned hash composition identifier) so independent verifiers can compute and verify roots.