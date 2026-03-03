from __future__ import annotations

import json
from typing import Any, Dict, Optional


def short_intent(pre: Dict[str, Any]) -> str:
    snap = pre.get("snapshot")
    if isinstance(snap, dict):
        intent = snap.get("intent")
        if isinstance(intent, dict):
            at = intent.get("action_type")
            return str(at) if at is not None else ""
    return ""


def print_timeline_row(pre: Dict[str, Any]) -> None:
    created = str(pre.get("created_at", ""))
    rid = str(pre.get("record_id", ""))
    eq = str(pre.get("evidence_quality", ""))
    enc = str(pre.get("encoding_id", ""))
    intent = short_intent(pre)
    print(f"{created}\t{rid}\t{eq}\t{enc}\t{intent}")


def pretty(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"