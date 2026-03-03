# Probity

Probity is an open specification and reference implementation
for producing tamper-evident records of autonomous system decisions.

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

**Version:** v0.3.0  
**State:** Verifiable protocol + usable SDK (Phase C complete)

With this release:

- The protocol is mechanically verifiable.
- A capture SDK exists.
- A CLI viewer exists.
- Thin adapters exist for OpenAI and Anthropic.
- Engineers can record and inspect decisions without vendor dependency.

Probity is now both a standard and a usable open source product.

---

# Quickstart

See: `QUICKSTART.md`

In under 5 minutes you can:

1. Install the SDK
2. Record an LLM decision
3. View a timeline
4. Verify integrity offline

---

# Repository Structure

This repository contains the complete specification and implementation surface for `probity-json:v1`.

- `docs/` — conceptual documentation and walkthroughs  
- `specs/` — normative layered specifications (Layer 1–4)  
- `schemas/` — JSON Schemas for all normative structures  
- `examples/` — illustrative PRE examples and failure cases  
- `reference/` — strict reference canonicalizer, hashing, and verifier  
- `test-vectors/` — canonicalization and verification compliance suite  
- `sdk/python/` — capture SDK  
- `cli/probity-view/` — offline CLI viewer  
- `sdk/python/probity/adapters/` — thin framework adapters  

---

# Specification Overview

Probity is layered:

### Layer 1 — Record Structure
Defines the Probity Record Envelope (PRE) and Decision Snapshot semantics.

### Layer 2 — Determinism & Integrity
Defines canonicalization (`jcs:rfc8785`), hashing (`sha256`), and optional signatures (`ed25519`).

### Layer 3 — Recorder Behavior
Defines when and how records are emitted.

### Layer 4 — Verification
Defines deterministic, offline verification.

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
- Offline-only verification
- Fail-closed behavior for unknown identifiers

Future changes require a new `encoding_id`.

---

# What Probity Is Not

Probity is not:

- an observability tool  
- a monitoring platform  
- a policy engine  
- a guardrail system  
- a governance framework  
- a behavioral scoring system  

Interpretation layers belong above the protocol.

---

# License

See `LICENSE` in the repository root.
