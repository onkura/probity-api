
# Evidence Semantics Model

## Purpose
A Probity record is evidence of system state at the moment of action.
It is not proof of correctness, intent, authorization, or compliance.

## Normative Clarification

A Probity record is **evidentiary**, not **assertory**.

> A Probity record **MUST NOT** be interpreted as proof that the action was authorized, approved, or legally correct.  
> It records the system's attribution and perception at the moment of commitment. Human interpretation and organizational investigation are required to make legal or policy determinations.

## What a Record Means
A record asserts only:
- the system associated an action with a decision context
- the context existed at recording time
- the record has not been altered

## What a Record Does NOT Mean
A record does not prove:
- the action was allowed
- the action was correct
- the organization approved the action
- the action met policy or legal standards

## Responsibility vs Permission
Probity records attribution, not permission.
Attribution reflects system belief, not organizational endorsement.

## Interpretive Use
Records allow reconstruction of the decision environment.
They support investigation but do not replace human judgment.

## Absence Semantics

Fields not present in a record are treated as unknown, not false.

Probity does not assume omitted information did not exist.
Only recorded information is asserted by the record.

## Outcome Interpretation

The outcome field records what the system observed or believed after commitment.

It does not guarantee the external world reached that state.
It represents the system’s observed result, not ground truth.