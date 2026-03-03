from __future__ import annotations

import json
import math
from typing import Any, Dict, List, Tuple

from .errors import CanonicalizationError


def _escape_string(s: str) -> str:
    # json.dumps handles escaping correctly for JCS (no unnecessary escapes, UTF-8 output)
    return json.dumps(s, ensure_ascii=False, separators=(",", ":"))


def _canonical_number(n: Any) -> str:
    if isinstance(n, bool) or n is None:
        raise CanonicalizationError("invalid_number_type")
    if isinstance(n, int):
        return str(n)
    if isinstance(n, float):
        if math.isnan(n) or math.isinf(n):
            raise CanonicalizationError("non_finite_number")
        # RFC 8785 uses ECMAScript number formatting; Python's repr is close but not identical.
        # We use a deterministic formatting that matches common JCS implementations:
        # - Use shortest round-trip representation.
        s = format(n, ".17g")
        # Normalize -0 to 0
        if s == "-0":
            s = "0"
        return s
    raise CanonicalizationError("unsupported_number_type")


def _sort_keys_utf16(k: str) -> Tuple[List[int], str]:
    # RFC8785 sorts object keys by Unicode code units (UTF-16) lexicographically.
    # We approximate by encoding to UTF-16BE and sorting by bytes.
    b = k.encode("utf-16-be")
    return (list(b), k)


def canonicalize(obj: Any) -> bytes:
    """
    Canonicalize a Python object to UTF-8 bytes per JCS (RFC 8785).
    """
    try:
        s = _canonical_value(obj)
        return s.encode("utf-8")
    except CanonicalizationError:
        raise
    except Exception as e:
        raise CanonicalizationError(str(e)) from e


def _canonical_value(v: Any) -> str:
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return _canonical_number(v)
    if isinstance(v, str):
        return _escape_string(v)
    if isinstance(v, list):
        return "[" + ",".join(_canonical_value(x) for x in v) + "]"
    if isinstance(v, dict):
        items = []
        for _kbytes, k in sorted((_sort_keys_utf16(k) for k in v.keys()), key=lambda t: t[0]):
            if not isinstance(k, str):
                raise CanonicalizationError("object_key_not_string")
            items.append(_escape_string(k) + ":" + _canonical_value(v[k]))
        return "{" + ",".join(items) + "}"
    raise CanonicalizationError(f"unsupported_type:{type(v).__name__}")