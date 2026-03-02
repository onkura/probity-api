# Probity — SPECIFICATION INDEX

This file is the single canonical entrypoint for the Probity specification. It orients readers to the normative content and the correct reading order for implementers, verifiers, and reviewers.

## Reading order (recommended)
1. `docs/00-introduction.md` — concept & purpose (context)
1.5. Layer 0 — Normative Encoding (wire format)
   - `specs/encodings/probity-json.v1.spec.md`
2. Layer 1 — Record Structure
   - `specs/record-envelope.spec.md`
   - `specs/decision-snapshot.schema.spec.md`
   - `specs/identity-object.spec.md`
   - `specs/lineage-link.spec.md`
2.5. Protocol Invariants (Freeze)
   - `specs/protocol-invariants/probity-v1.invariants.spec.md`
3. Layer 2 — Canonicalization & Integrity
   - `specs/canonicalization.spec.md`
   - `specs/hashing.spec.md`
   - `specs/signatures.spec.md`
4. Layer 3 — Recorder Behavior
   - `specs/recording-procedure.spec.md`
   - `specs/late-recording.spec.md`
   - `specs/failure-states.spec.md`
   - `specs/recorder-modes.spec.md`
   - `specs/recorder-alerting.spec.md`
   - `specs/coverage-declaration.spec.md`
5. Layer 4 — Verification & Conformance
   - `specs/verification-algorithm.spec.md`
   - `specs/verifier-output.schema.spec.md`
   - `specs/verification-testvectors.spec.md`

## Normative language
The specification uses RFC2119 keywords. Where the spec uses **MUST**, **SHOULD**, **MAY**, these words are normative and must be interpreted per RFC2119.

## Conformance
See `CONFORMANCE.md` for the minimal tests an implementation must pass to be considered "Probity-conformant" and to interoperate with reference verifiers.

## Test vectors & reference verifier
- `test-vectors/` contains canonical test vectors (PREs, canonical bytes, expected hashes, optional signatures).
- `reference-verifier/` contains a minimal reference verifier (Python) that runs vectors and emits the `verifier-output` JSON.

*(If either folder is not present yet, consult `CONFORMANCE.md` for expected file layout and add them before claiming compliance.)*

## Versioning & governance
- Each PRE includes `spec_version` and `schema_version`. Use those to interpret older records.
- To propose changes: open an issue and a PR in this repo. Major changes that break interpretation semantics require a spec version bump and migration notes.

## Release artifacts
Each release SHOULD include:
- canonical test vectors (Layer 4)
- a minimal reference verifier release (tagged)
- a conformance matrix and short release notes

## Security & responsible disclosure
Report any security issues to the maintainers via the repository security contacts. Do not publish vulnerability details publicly until coordinated disclosure occurs.

## Normative schema artifacts
- `schemas/` contains JSON Schemas for `encoding_id = probity-json:v1`.

## Examples
- `examples/` contains hand-written example PREs and failure cases.

## Walkthroughs
- `docs/walkthroughs/` contains narrative walkthroughs mapping common agent flows to record structure.