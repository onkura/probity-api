# probity-json.v1 — Normative JSON Encoding (Layer 0)

## Purpose
This document defines **the** normative JSON encoding for Probity v1 records.
It fixes concrete field names, JSON shapes, and encoding constraints so that independent implementations can:
- exchange records,
- canonicalize snapshots into identical bytes, and
- verify integrity and signatures without out-of-band agreement.

This document is normative. The keywords **MUST**, **SHOULD**, **MAY**, and **MUST NOT** are used as defined in RFC 2119.

## Scope
This encoding applies to:
- the Probity Record Envelope (PRE)
- embedded Decision Snapshot payloads
- embedded Identity Objects and Lineage Links
- verifier output JSON emitted by verifiers (when they claim `probity-json:v1` output)

Other internal encodings are permitted, but any system claiming conformance to Probity v1 **MUST** be able to render records into this encoding **losslessly** (except where explicitly allowed) for verification.

## Encoding identifier
- `encoding_id`: `probity-json:v1`

A record encoded according to this document:
- **MUST** set `spec_version` to `probity-v1`
- **MUST** set `encoding_id` to `probity-json:v1`

Protocol invariants for v1 are frozen in:
- `specs/protocol-invariants/probity-v1.invariants.spec.md`

If any conflict exists, the invariants document is authoritative for `probity-json:v1`.

## General JSON rules
1. JSON text **MUST** be encoded as UTF-8, without BOM.
2. Objects **MUST NOT** contain duplicate keys.
3. **Null is disallowed by default**.
   - A field either has a value of its declared type, or the field is omitted.
   - A field may allow `null` only if explicitly stated (v1: none do).
4. Extension data:
   - Envelope objects **MAY** contain extension data only under `extensions`.
   - Snapshot objects **MAY** contain extension data only under `extensions`.
   - Verifiers **MUST** ignore unknown content under `extensions` for semantic interpretation.
5. Timestamp strings **MUST** be RFC3339 in UTC with `Z` suffix (no offsets).
   - Fractional seconds are **OPTIONAL**.
   - If present, fractional seconds **MUST** be 1–9 digits.
   - Examples: `2026-03-01T18:22:33Z`, `2026-03-01T18:22:33.123456789Z`.

## Canonicalization and integrity defaults for this encoding
Records encoded as `probity-json:v1`:
- **MUST** set `canonical_serialization_id` to `jcs:rfc8785`
- **MUST** compute `integrity.digest` over the **canonicalized Decision Snapshot bytes** (not over the envelope)

### Canonical serialization identifier: `jcs:rfc8785`
When `canonical_serialization_id` is `jcs:rfc8785`, the snapshot is canonicalized using RFC 8785 JSON Canonicalization Scheme (JCS), with these additional constraints:
- JSON numbers **MUST** be finite (no NaN/Infinity).
- `-0` **MUST NOT** be used (use `0`).

## Extension container
To preserve the primitive and keep the core schema stable, extensions live under a single reserved object:
- `extensions` (object, optional)

Rules:
- Keys under `extensions` **MUST** be namespaced (e.g., `com.example.foo`).
- Content under `extensions` is covered by integrity **only if** it appears inside the Decision Snapshot that is hashed/signed.

---

# 1. Probity Record Envelope (PRE)

## PRE object shape
A PRE is a JSON object with the following fields.

### Required
- `record_id` (string)
- `spec_version` (string) — **MUST** be `probity-v1`
- `encoding_id` (string) — **MUST** be `probity-json:v1`
- `schema_version` (string) — snapshot schema version identifier (string; v1 implementations typically use `decision-snapshot:v1`)
- `canonical_serialization_id` (string) — **MUST** be `jcs:rfc8785`
- `created_at` (string) — timestamp (see General JSON rules)
- `evidence_quality` (string) — one of `verified|incomplete|late|unverified`
  Note: `absent` is not a PRE value (no PRE exists). It is reserved for operational signals where an expected PRE is missing.
- `integrity` (object) — integrity metadata and expected digest (see below)
- exactly one of:
  - `snapshot` (object) — embedded Decision Snapshot
  - `snapshot_ref` (object) — reference to an external snapshot artifact

### Optional
- `signature` (object) — signature metadata + value (if present)
- `extensions` (object)

### PRE.integrity (required)
- `hash_algo` (string) — e.g., `sha256`, `sha512`
- `hash_encoding` (string) — `hex` or `base64url`
- `digest` (string) — encoded digest of canonicalized snapshot bytes
- `canonical_serialization_id` (string) — duplicated here for self-contained integrity metadata; **MUST** equal PRE `canonical_serialization_id`

Notes:
- `integrity.digest` is the *expected* digest for verification.
- Verifiers compute a digest from the canonicalized snapshot and compare.

### PRE.signature (optional)
If present, `signature` is a JSON object with:
- `signature_algo` (string) — e.g., `ed25519`, `rsa-pss-sha256`, `ecdsa-secp256r1-sha256`
- `signer_key_id` (string) — opaque identifier for the signing key
- `target` (string) — one of `snapshot_bytes|snapshot_digest`
- `signature_encoding` (string) — `base64url` (v1 default) or `hex`
- `signature` (string) — signature bytes encoded using `signature_encoding`

Rules:
- If `target == snapshot_bytes`, the signature is computed over the canonicalized snapshot bytes.
- If `target == snapshot_digest`, the signature is computed over the raw digest bytes (decoded from `integrity.digest`).

### PRE.snapshot_ref (optional, mutually exclusive with snapshot)
If `snapshot_ref` is present, it **MUST** contain:
- `uri` (string) — location of the snapshot artifact
- `content_hash` (object) — hash of the snapshot artifact bytes
  - `hash_algo` (string)
  - `hash_encoding` (string) — `hex|base64url`
  - `digest` (string)

Optional fields:
- `content_type` (string) — media type (e.g., `application/json`)
- `size_bytes` (integer)

Rules:
- `content_hash` **MUST** be over the snapshot artifact **exact bytes** as stored at `uri`.
- `content_hash` is distinct from PRE `integrity.digest`:
  - `content_hash` binds the referenced artifact bytes.
  - `integrity.digest` binds the canonicalized snapshot bytes (after parsing and JCS canonicalization).

---

# 2. Decision Snapshot (decision-snapshot:v1)

## Snapshot object shape
The snapshot is a JSON object capturing the decision state at commit time.

### Required
- `perception` (object)
- `responsibility` (object)
- `intent` (object)
- `selection_basis` (object)
- `outcome` (object)

### Optional
- `human_approval` (object)
- `lineage_refs` (array of LineageLink objects)
- `raw_capture_policy` (boolean)
- `evidence_quality` (string) — mirrors the envelope field when present
- `extensions` (object)

### Snapshot.perception (required)
Permitted fields (non-exhaustive; contents are intentionally permissive):
- `inputs` (array, optional) — references/descriptors for user inputs, prompts, triggers
- `evidence_refs` (array, optional) — references (hashes/URIs) to retrieved documents or tool outputs
- `env` (object, optional) — key/value map of relevant environment observations (non-sensitive keys encouraged)
- `extensions` (object, optional)

### Snapshot.responsibility (required)
- `actor_id` (string)
- `actor_type` (string) — one of `human|service|agent|delegated`
- `authority_scope` (object) — permission scope the system believed applied (e.g., role, approval_tier, monetary_limit)
- `extensions` (object, optional)

### Snapshot.intent (required)
- `action_type` (string)
- `action_params` (object)
- `extensions` (object, optional)

### Snapshot.selection_basis (required)
Must include **at least one** of:
- `score_signals` (object, optional)
- `policy_refs` (array, optional)
- `heuristic_tags` (array, optional)

May include:
- `extensions` (object, optional)

### Snapshot.outcome (required)
- `observed_result` (string) — e.g., `succeeded|failed|unknown`
- `result_refs` (array) — references to downstream artifacts (transaction id, API response hash, etc.)
- `observed_at` (string) — timestamp (see General JSON rules)
- `extensions` (object, optional)

---

# 3. Identity Object (identity-object:v1)

## IdentityObject shape
Required:
- `actor_id` (string)
- `actor_type` (string) — one of `human|service|agent|delegated`

Optional:
- `provenance` (object)
- `revocation_state` (string) — `active|revoked|unknown`
- `extensions` (object)

---

# 4. Lineage Link (lineage-link:v1)

## LineageLink shape
Required:
- `parent_record_id` (string)
- `relation_type` (string) — one of `influenced_by|derived_from|approved_by|forked_from`

Optional:
- `context` (object)
- `evidence_ref` (string)
- `extensions` (object)

---

# 5. Verifier Output (verifier-output:v1)

## Verifier output shape
A verifier emitting `probity-json:v1` output **MUST** produce:

Required:
- `record_id` (string)
- `verification_time` (string) — timestamp (see General JSON rules)
- `status` (string) — `verified|unverified|invalid|incomplete`
- `status_reasons` (array of strings)
- `integrity` (object)
  - `hash_algo` (string)
  - `hash_encoding` (string)
  - `computed_digest` (string)
  - `expected_digest` (string)
  - `match` (boolean)

Optional:
- `signature` (object)
  - `signature_algo` (string)
  - `signer_key_id` (string)
  - `signature_valid` (boolean)
  - `target` (string)
- `missing_fields` (array of strings)
- `extensions` (object)