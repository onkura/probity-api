# Contributing to Probity

Thanks for contributing! This document contains basic contribution rules.

## How to propose changes
1. Open an issue describing the problem or proposed change.
2. If the change is non-trivial, open a PR with:
   - a short rationale
   - migration guidance if the change affects `spec_version` or `schema_version`
   - updated test vectors if the change affects canonicalization/hashing behavior

## Normative changes
- Changes that affect interpretation semantics **MUST** bump `spec_version` and include a migration guide.
- Non-normative editorial fixes may be merged with less formal process.

## Tests & CI
- Add or update test vectors in `test-vectors/` for changes that affect canonicalization, hashing, or verification behavior.
- Add unit tests for the reference verifier where helpful.

## Code of conduct
Follow the repository Code of Conduct (see `CODE_OF_CONDUCT.md` if present) — be kind and collaborative.