
# Decision Boundary Model
A record exists when a system commits to an externally meaningful action.

A decision occurs when:
- a specific action is selected
- the action can affect external state

Reasoning, ranking, and drafting are not decisions.

Retries do not create new decisions unless inputs or intent change.

Async rule:
If a task is queued, the boundary occurs at enqueue time.

Absence of a record indicates unknown evidence, not invalid behavior.

### Boundary Invariant

All compliant implementations MUST create a record at the moment an action becomes externally irreversible without a compensating action.

An action is considered externally irreversible if at least one of the following occurs:
- durable mutation of system state outside the model’s internal computation
- communication observable by an external actor
- transfer or exercise of authority
- initiation of a financial, legal, or operational effect

Implementations MUST NOT delay recording until after the effect completes.
Implementations MUST NOT record during internal planning or option evaluation.