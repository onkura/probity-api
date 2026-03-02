
# Threat Model

## Purpose
Define the classes of threats Probity addresses at a conceptual level.

Probity protects the integrity of decision evidence, not system behavior.

## Assumed Adversaries
The model considers the following attackers:

- Post‑incident operator attempting to alter historical records
- Insider modifying logs to hide actions
- Compromised service rewriting decision history
- External actor attempting to inject fabricated records

## Non‑Adversaries
Probity does NOT attempt to defend against:

- incorrect model decisions
- malicious but correctly recorded behavior
- compromised upstream systems that legitimately produced a decision

## Security Goal
An investigator can determine whether a record:
- existed at the time claimed
- was altered after creation

## Out of Scope
Probity does not guarantee:
- prevention of harmful actions
- real‑time attack detection
- correctness of system permissions

It only protects the trustworthiness of historical evidence.

## Attacker Capabilities Considered

Probity assumes adversaries may possess one or more of the following capabilities:

- modify or delete local storage containing records
- control or manipulate system clocks (clock-skew/rollback)
- rewrite or intercept logs during a service compromise
- inject fabricated records if key material is exposed

Implication: designs that rely solely on a single host’s filesystem for integrity are insufficient. Implementations SHOULD consider external anchoring, append-only logs, or signature key separation as mitigation strategies (see Tamper Evidence).


## Omission Risk

Probity detects alteration of recorded decisions but cannot inherently detect decisions that were never recorded.

Systems SHOULD provide mechanisms to demonstrate recording coverage for actions within scope.

Absence of a record is not proof that no action occurred unless coverage guarantees exist.