"""
Strict JCS (RFC 8785) canonicalization implementation for Probity v1.

Invariants enforced:
- UTF-8 input (no BOM)
- No duplicate keys
- No NaN / Infinity
- No -0
- RFC8785 deterministic number formatting
- No Unicode normalization
"""

import json
import math
import decimal
from decimal import Decimal


class CanonicalizationError(Exception):
    pass


def _reject_duplicate_keys_object_pairs_hook(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise CanonicalizationError("duplicate_keys")
        obj[k] = v
    return obj


def parse_json_strict(text: str):
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys_object_pairs_hook,
            parse_float=Decimal,
            parse_int=Decimal,
        )
    except CanonicalizationError:
        raise
    except Exception as e:
        raise CanonicalizationError("invalid_json") from e


def _serialize_number(n: Decimal) -> str:
    # Reject NaN / Infinity
    if n.is_nan() or n.is_infinite():
        raise CanonicalizationError("invalid_number_format")

    # Reject -0
    if n == 0 and n.as_tuple().sign == 1:
        raise CanonicalizationError("invalid_number_format")

    # Normalize number per RFC8785
    n = n.normalize()

    # Convert to string without scientific notation if possible
    s = format(n, 'f')

    # Remove trailing zeros after decimal
    if '.' in s:
        s = s.rstrip('0').rstrip('.')

    if s == "-0":
        raise CanonicalizationError("invalid_number_format")

    return s


def _serialize(value):
    if value is None:
        return "null"

    if value is True:
        return "true"

    if value is False:
        return "false"

    if isinstance(value, Decimal):
        return _serialize_number(value)

    if isinstance(value, str):
        # JSON string encoding without extra normalization
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    if isinstance(value, list):
        return "[" + ",".join(_serialize(v) for v in value) + "]"

    if isinstance(value, dict):
        # Sort keys by UTF-16 code units per RFC8785
        def utf16_sort_key(k):
            return k.encode("utf-16-be")

        items = sorted(value.items(), key=lambda kv: utf16_sort_key(kv[0]))
        return "{" + ",".join(
            json.dumps(k, ensure_ascii=False, separators=(",", ":")) + ":" + _serialize(v)
            for k, v in items
        ) + "}"

    raise CanonicalizationError("unsupported_type")


def canonicalize(text: str) -> bytes:
    if text.startswith("\ufeff"):
        raise CanonicalizationError("invalid_json")

    parsed = parse_json_strict(text)
    serialized = _serialize(parsed)
    return serialized.encode("utf-8")
