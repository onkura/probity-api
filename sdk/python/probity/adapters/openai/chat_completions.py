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
    for attr in ("model_dump", "dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    # last resort: best-effort attribute extraction
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return str(obj)


def map_chat_completion_request(
    *,
    model: str,
    messages: list[dict],
    tools: Optional[list[dict]] = None,
    tool_choice: Optional[Any] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None,
    actor_id: str = "agent:unknown",
    authority_allow: Optional[list[str]] = None,
) -> Dict[str, Any]:
    """
    Map an OpenAI Chat Completions *request* (inputs/config) into a schema-shaped Decision Snapshot skeleton.

    Caller is expected to fill outcome after receiving the response.
    This function returns a dict with {perception, responsibility, intent, selection_basis, outcome}.
    """
    authority_allow = authority_allow or ["llm_call"]

    perception: Dict[str, Any] = {
        "inputs": [
            {
                "type": "openai_chat_messages",
                "ref": "openai:messages",
            }
        ],
        "extensions": {
            "openai": {
                "messages": _to_dict(messages),
                "tools": _to_dict(tools),
                "tool_choice": _to_dict(tool_choice),
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
            "provider": "openai",
            "endpoint": "chat.completions",
            "model": model,
        },
    }

    selection_basis: Dict[str, Any] = {
        "heuristic_tags": ["llm_generation"],
    }
    # Put model params in extensions to avoid claiming they are "selection logic"
    sel_ext: Dict[str, Any] = {
        "temperature": temperature,
        "top_p": top_p,
        "max_output_tokens": max_output_tokens,
    }
    selection_basis["extensions"] = {"openai": {k: v for k, v in sel_ext.items() if v is not None}}

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


def map_chat_completion_response(
    *,
    request_snapshot: Dict[str, Any],
    response: Any,
    observed_at: str,
) -> Dict[str, Any]:
    """
    Given a request_snapshot produced by map_chat_completion_request and an OpenAI response,
    return a complete snapshot dict with an outcome filled in.

    This does not verify correctness; it records observable response content.
    """
    resp = _to_dict(response)

    # Extract minimal useful outcome fields without depending on OpenAI SDK shapes.
    model = None
    choices = None
    usage = None
    try:
        model = resp.get("model")
        choices = resp.get("choices")
        usage = resp.get("usage")
    except Exception:
        pass

    outcome = {
        "observed_result": "succeeded",
        "result_refs": ["openai:chat.completions.response"],
        "observed_at": observed_at,
    }

    # Preserve the raw response under outcome.extensions for replay/debugging.
    outcome["extensions"] = {
        "openai": {
            "model": model,
            "choices": choices,
            "usage": usage,
            "raw_response": resp,
        }
    }

    snap = dict(request_snapshot)
    snap["outcome"] = outcome
    return snap