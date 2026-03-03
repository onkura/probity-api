from __future__ import annotations

from typing import Any, Dict, Optional

from ...helpers import permission_scope


def _to_dict(obj: Any) -> Any:
    """
    Convert common SDK response objects into dicts without depending on SDK packages.
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool, list, dict)):
        return obj
    for attr in ("model_dump", "dict", "to_dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return str(obj)


def map_messages_request(
    *,
    model: str,
    messages: list[dict],
    tools: Optional[list[dict]] = None,
    system: Optional[Any] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_tokens: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None,
    actor_id: str = "agent:unknown",
    authority_allow: Optional[list[str]] = None,
) -> Dict[str, Any]:
    """
    Map an Anthropic Messages *request* into a schema-shaped Decision Snapshot skeleton.
    """
    authority_allow = authority_allow or ["llm_call"]

    perception: Dict[str, Any] = {
        "inputs": [
            {"type": "anthropic_messages", "ref": "anthropic:messages"},
        ],
        "extensions": {
            "anthropic": {
                "messages": _to_dict(messages),
                "tools": _to_dict(tools),
                "system": _to_dict(system),
            }
        },
    }

    responsibility = {
        "actor_id": actor_id,
        "actor_type": "agent",
        "authority_scope": permission_scope(*authority_allow),
    }

    intent = {
        "action_type": "llm_call",
        "action_params": {
            "provider": "anthropic",
            "endpoint": "messages",
            "model": model,
        },
    }

    selection_basis: Dict[str, Any] = {
        "heuristic_tags": ["llm_generation"],
    }
    selection_basis["extensions"] = {
        "anthropic": {k: v for k, v in {
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }.items() if v is not None}
    }

    outcome = {
        "observed_result": "unknown",
        "result_refs": [],
        "observed_at": None,
    }

    snap = {
        "perception": perception,
        "responsibility": responsibility,
        "intent": intent,
        "selection_basis": selection_basis,
        "outcome": outcome,
    }

    if extra:
        snap.setdefault("extensions", {})
        snap["extensions"]["extra"] = extra

    return snap


def map_messages_response(
    *,
    request_snapshot: Dict[str, Any],
    response: Any,
    observed_at: str,
) -> Dict[str, Any]:
    """
    Fill in outcome for Anthropic Messages response.

    Stores raw response under outcome.extensions for replay/debug.
    """
    resp = _to_dict(response)

    model = None
    content = None
    usage = None
    stop_reason = None
    try:
        model = resp.get("model")
        content = resp.get("content")
        usage = resp.get("usage")
        stop_reason = resp.get("stop_reason")
    except Exception:
        pass

    outcome = {
        "observed_result": "succeeded",
        "result_refs": ["anthropic:messages.response"],
        "observed_at": observed_at,
    }
    outcome["extensions"] = {
        "anthropic": {
            "model": model,
            "content": content,
            "usage": usage,
            "stop_reason": stop_reason,
            "raw_response": resp,
        }
    }

    snap = dict(request_snapshot)
    snap["outcome"] = outcome
    return snap