# Reference Canonicalization (Phase B2)

This directory contains the strict JCS (RFC 8785) canonicalization implementation
for `encoding_id = probity-json:v1`.

Invariants enforced:
- No duplicate keys
- No NaN / Infinity
- No -0
- UTF-8 only
- No Unicode normalization
- Key sorting by UTF-16 code units

This implementation is intended as a compliance reference, not a performance library.

# Reference Hashing + Verifier (Phase B2/B3)

This directory contains strict, offline reference components used to verify Probity records.

- `hash.py` — deterministic hashing over canonical snapshot bytes
  - `integrity.hash_algo = sha256`
  - `integrity.hash_encoding = hex|base64url`
- `verifier.py` — strict verifier CLI (offline, fail-closed)

Design constraints:
- No network access (snapshot_ref only resolves local file paths or `file:` URIs)
- No silent defaults for unknown canonicalization IDs
- No acceptance of unknown signature targets
- Fail closed when verification inputs are missing/unsupported