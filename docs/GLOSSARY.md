# Probity Glossary (short)

- **PRE** — Probity Record Envelope. The immutable container around a Decision Snapshot and integrity/signature metadata.
- **Decision Snapshot** — structured representation of what the system perceived, responsibility context, committed intent, selection basis, and observed outcome.
- **Decision Boundary** — moment the system commits from reasoning into an externally meaningful action (see docs/concepts/decision-boundary.md).
- **canonical_serialization_id** — identifier for the canonicalization algorithm used to produce canonical snapshot bytes for hashing/signing.
- **integrity** — PRE object containing hash parameters and expected digest:
  - `hash_algo`, `hash_encoding`, `digest`, `canonical_serialization_id`.
- **integrity.digest** — expected digest over canonicalized snapshot bytes, used for tamper evidence verification.
- **signature** — optional PRE object carrying signature metadata and signature value; may target `snapshot_bytes` or `snapshot_digest`.
- **evidence_quality** — enumerated quality state in a PRE: `verified|incomplete|late|unverified`.
  - `absent` is reserved for operational signals where no PRE exists for an expected decision.
- **selection_basis** — structured summary of signals/criteria that led the system to choose the committed action.