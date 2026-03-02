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

## Repository Structure

This repository contains the complete Stage A specification:

- `docs/` — conceptual documentation and walkthroughs
- `specs/` — normative layered specifications (Structure, Canonicalization, Recording, Verification)
- `schemas/` — JSON Schemas for `encoding_id = probity-json:v1`
- `examples/` — example Probity Record Envelopes (PREs) and failure cases

No reference implementation is included at this stage.
This repository defines the protocol surface required for independent implementations.

---

## Specification Overview

Probity is layered:

- **Layer 1 — Record Structure**  
  Defines the Probity Record Envelope (PRE) and Decision Snapshot semantics.

- **Layer 2 — Determinism & Integrity**  
  Defines canonicalization (`jcs:rfc8785`), hashing (`sha256`), and optional signatures.

- **Layer 3 — Recorder Behavior**  
  Defines when and how records are emitted, including evidence quality states.

- **Layer 4 — Verification**  
  Defines the deterministic verification algorithm and verifier output structure.

Protocol invariants for `probity-json:v1` are frozen in:
