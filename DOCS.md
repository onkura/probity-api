# Probity Docs

This directory contains the normative Probity documentation.

The documentation defines meaning, not implementation.

A system conforms to Probity if its records can be interpreted according to these documents.

---

## Reading Order

1. `00-introduction.md`
2. `01-evidence-semantics.md`

### Conceptual Layer — What a record represents
- decision-boundary
- decision-snapshot
- identity-responsibility
- reproducibility

### Behavioral Layer — How records behave
- event-chain
- recording-semantics
- failure-semantics

### Trust Layer — Why records can be trusted
- threat-model
- tamper-evidence

### Operational Layer — How records are used
- reconstruction
- integration-patterns
- negative-case
- non-goals

---

## Normative Language

The keywords **MUST**, **SHOULD**, and **MAY** are used as defined in RFC 2119.

---

## Compatibility Principle

Implementations may differ internally.  
Two systems are compatible if an independent reviewer would interpret their records the same way.

---

## Non-Goals of the Documentation

The documentation does not define:

- APIs
- storage formats
- cryptographic algorithms
- enforcement mechanisms
- runtime architectures

Only record meaning is standardized.