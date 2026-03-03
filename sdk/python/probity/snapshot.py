from __future__ import annotations

from typing import Any, Dict, Optional


def build_snapshot(
    *,
    perception: Dict[str, Any],
    responsibility: Dict[str, Any],
    intent: Dict[str, Any],
    selection_basis: Dict[str, Any],
    outcome: Dict[str, Any],
    extensions: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a Decision Snapshot shaped to the Probity schema.

    The SDK does not interpret or coerce semantics. Caller provides schema-shaped objects.
    """
    snap: Dict[str, Any] = {
        "perception": perception,
        "responsibility": responsibility,
        "intent": intent,
        "selection_basis": selection_basis,
        "outcome": outcome,
    }
    if extensions is not None:
        snap["extensions"] = extensions
    return snap