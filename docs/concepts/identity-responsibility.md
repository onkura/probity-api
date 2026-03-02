
# Identity & Responsibility Model
Records attribute actions to actors.

Actors may be:
- human
- service account
- agent

The attribution reflects system belief at execution time.

It does not grant permission or prove authorization.

## Authority Scope

Responsibility MUST include the scope of authority under which the actor was permitted to make the decision.

This does not enforce policy correctness.
It records the decision-making authority the system believed it was operating under at the moment of action.

## Attribution Rule

Responsibility reflects the actor the system believed was authorizing the action at commitment time.

This may differ from the technical executor of the action.
Execution infrastructure is not automatically considered the responsible actor.