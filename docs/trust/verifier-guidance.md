# Verifier Guidance

## Purpose
Describe the minimal behavior required for an independent verifier to evaluate a Probity record.

A verifier interprets, not executes, the system.

---

## Verification Steps

A verifier SHOULD:

1. Parse the record using the declared schema version
2. Recreate the canonical serialization
3. Validate the integrity reference
4. Evaluate evidence quality state
5. Report verification result

---

## Verification Result States

- verified — integrity intact
- unverifiable — insufficient verification data
- invalid — integrity mismatch

Verification does not evaluate correctness of the decision.

---

## Independence Requirement

Verification MUST NOT require:

- original runtime environment
- proprietary system components
- model execution

All necessary interpretation information must exist in the record.

---

## Output

A verifier produces a report describing:

- record validity
- evidence quality
- integrity status

The verifier does not render judgments about behavior.