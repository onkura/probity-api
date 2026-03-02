# Probity

Probity is an open specification for producing tamper-evident records of autonomous system decisions.

It defines a minimal, portable evidence layer that allows independent verification of:

- what a system perceived  
- what authority it operated under  
- what it selected  
- why it was allowed  
- what it committed  
- and cryptographic proof that the record was not altered  

Probity does **not** judge correctness.  
Probity does **not** enforce policy.  
Probity preserves reconstructable evidence.

---

# Status

**Version:** v0.2.0  
**State:** Verifiable protocol (Phase B complete)

With this release:

Two independent implementations in different languages can produce identical verification results over the same Probity Record.

Probity is now a mechanically verifiable standard.

---

# Repository Structure

This repository contains the complete specification and compliance surface for `encoding_id = probity-json:v1`.

- `docs/` — conceptual documentation and walkthroughs  
- `specs/` — normative layered specifications (Layer 1–4)  
- `schemas/` — JSON Schemas for all normative structures  
- `examples/` — illustrative PRE examples and failure cases  
- `reference/` — strict reference canonicalizer, hashing, and verifier  
- `test-vectors/` — adversarial canonicalization vectors and full verification compliance suite  

---

# Specification Overview

Probity is layered:

### Layer 1 — Record Structure
Defines the Probity Record Envelope (PRE) and Decision Snapshot semantics.

### Layer 2 — Determinism & Integrity
Defines canonicalization (`jcs:rfc8785`), hashing (`sha256`), and optional signatures (`ed25519`).

### Layer 3 — Recorder Behavior
Defines when and how records are emitted, including evidence quality states.

### Layer 4 — Verification
Defines the deterministic verification algorithm and verifier output structure.

---

# Frozen Protocol Invariants (v1)

The following are frozen for `probity-json:v1`:

- `canonical_serialization_id = jcs:rfc8785`
- `hash_algo = sha256`
- `hash_encoding ∈ { hex, base64url }`
- Signature targets:
  - `snapshot_bytes`
  - `snapshot_digest`
- Canonical verification reason token set
- Offline-only verification (no network resolution)
- Fail-closed behavior for unknown identifiers

These invariants MUST NOT change for `probity-json:v1`.

Future revisions require a new `encoding_id`.

---

# Verification & Compliance

The repository includes:

- Deterministic canonicalization adversarial vectors  
- Full verification vectors (01–09)  
- Signed and unsigned record cases  
- Schema validation cases  
- Integrity mismatch cases  
- Unknown canonicalization cases  

A conformant implementation:

1. Canonicalizes the Decision Snapshot using RFC 8785 (JCS)
2. Computes SHA-256 over canonical bytes
3. Compares against `integrity.digest`
4. Optionally verifies Ed25519 signatures
5. Produces verifier output matching the compliance vectors

Success condition:

A verifier written in Rust, Go, Java, or Python can pass all verification vectors without referencing the Python implementation.

---

# Non-Goals

Probity is not:

- an observability tool  
- a monitoring platform  
- a policy engine  
- a guardrail system  
- a governance framework  
- a behavioral scoring layer  

Probity establishes reconstructability of decisions.
Interpretation layers belong above the protocol.

---

# Contributing

This repository is protocol infrastructure.

Changes that alter:
- canonicalization
- hashing
- signature identifiers
- reason token sets
- schema invariants

require a new version (`encoding_id`).

Before proposing changes, read:

- `CONFORMANCE.md`
- `specs/verification-algorithm.spec.md`
- `specs/failure-states.spec.md`

---

# License

See `LICENSE` in the repository root.