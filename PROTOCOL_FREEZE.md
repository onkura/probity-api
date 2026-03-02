# Probity Protocol Freeze — probity-json:v1

This document formally freezes the invariants for:

encoding_id = probity-json:v1

The following identifiers and behaviors are immutable for v1:

- canonical_serialization_id = jcs:rfc8785
- hash_algo = sha256
- hash_encoding ∈ { hex, base64url }
- Signature targets:
  - snapshot_bytes
  - snapshot_digest
- Canonical verification reason token set
- Offline-only verification
- Fail-closed behavior for unknown identifiers

Any change to these invariants requires:
- A new encoding_id
- A new schema version
- A new test vector suite

The reference implementation does not define the protocol.
The protocol defines the reference implementation.

Date frozen: 2026-03-02
Version: 0.2.0