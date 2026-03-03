# Probity Changelog

All notable changes to Probity are documented here.

The format follows a simple release log with compatibility notes.

---

## [0.3.0] — 2026-03-03 — Full Open Source Product (Phase C)

This release completes Stage C of the open source roadmap:
Probity is now both a verifiable protocol and a usable capture + inspection toolchain.

### Added

- Python Capture SDK
  - `record_action`
  - `LocalJSONLRecorder`
  - `RotatingFileRecorder`
  - Snapshot builder helpers
  - Deterministic integrity generation (JCS + SHA-256)
- CLI Viewer (`probity-view`)
  - Timeline view for JSONL logs
  - Record expansion
  - Offline integrity verification wrapper
  - Export bundle (PRE + snapshot + canonical + verifier output)
- Thin adapters:
  - OpenAI Chat Completions
  - Anthropic Messages
- Quickstart guide

### Guarantees

An engineer can now:

1. Install SDK
2. Record LLM decisions
3. View decision timeline
4. Verify integrity offline
5. Export portable bundles

No hosted services required.

### Compatibility

- No changes to protocol invariants.
- Fully compatible with `probity-json:v1`.

---

## [0.2.0] — 2026-03-02 — Verifiable Standard (Phase B)

This release transitions Probity from a conceptual specification
to a mechanically verifiable protocol.

### Added

- Deterministic canonicalization freeze:
  - `canonical_serialization_id = jcs:rfc8785`
  - No Unicode normalization
  - UTF-16 key sorting
  - Deterministic number formatting
- Frozen hash algorithm identifiers:
  - `sha256`
- Frozen digest encodings:
  - `hex`
  - `base64url`
- Frozen verification reason token set
- Frozen signature targets:
  - `snapshot_bytes`
  - `snapshot_digest`
- Reference canonicalizer (JCS RFC 8785)
- Deterministic SHA-256 hashing implementation
- Strict, offline reference verifier (fail-closed)
- Ed25519 signature support (dependency-free reference implementation)
- Canonical adversarial canonicalization test vectors
- Full verification test vector suite:
  - 01-basic-verified
  - 02-integrity-mismatch
  - 03-embedded-snapshot
  - 04-external-snapshot
  - 05-late-record
  - 06-missing-field
  - 07-unknown-canonical-id
  - 08-signed-record-valid
  - 09-signed-record-invalid

### Tightening

- Snapshot schema alignment across test vectors
- Deterministic `missing_fields` reporting
- Explicit requirement: `canonical.txt` MUST NOT contain trailing newline
- Strict offline verification (no network resolution)
- Fail-closed behavior for unknown canonicalization IDs, hash algorithms, and signature targets

### Compatibility

- Records claiming `encoding_id = probity-json:v1` MUST conform to the frozen invariants.
- Older draft references to `signature_meta` remain readable but are not valid for new v1 records.

### Impact

With this release:

Two independent implementations in different languages
can produce identical verification results
over the same Probity Record.

This establishes Probity as a protocol, not a proposal.

---

## [0.1.0] — Initial Layered Specification

- Layer 1–4 architecture defined
- Envelope and Decision Snapshot structure
- Hashing, tamper evidence, and signature models
- Conformance checklist
- Example records and walkthroughs
