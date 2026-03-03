from __future__ import annotations

import os
import platform
import sys
from typing import Any, Dict, Optional


def environment_snapshot(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Returns a minimal environment snapshot suitable for inclusion in perception.env or extensions.

    This is intentionally conservative: no secrets, no network calls, no heavy introspection.
    """
    snap: Dict[str, Any] = {
        "python": {"version": sys.version.split()[0], "impl": platform.python_implementation()},
        "platform": {"system": platform.system(), "release": platform.release(), "machine": platform.machine()},
        "process": {"pid": os.getpid()},
    }
    if extra:
        snap["extra"] = extra
    return snap


def permission_scope(*allow: str, deny: Optional[list[str]] = None, notes: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper to construct a responsibility.authority_scope object.

    Schema in your repo expects an object; keep this minimal and explicit.
    """
    scope: Dict[str, Any] = {"allow": list(allow)}
    if deny:
        scope["deny"] = list(deny)
    if notes:
        scope["notes"] = notes
    return scope


def session_lineage(session_id: str, parent_session_id: Optional[str] = None, trace_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Minimal lineage helper. Intended to be placed in snapshot.extensions or perception.env,
    not interpreted by Probity core.
    """
    out: Dict[str, Any] = {"session_id": session_id}
    if parent_session_id:
        out["parent_session_id"] = parent_session_id
    if trace_id:
        out["trace_id"] = trace_id
    return out