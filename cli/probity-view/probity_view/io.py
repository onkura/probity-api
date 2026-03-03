from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple


def iter_jsonl(path: str) -> Iterator[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"JSONL file not found: {path}\n"
            f"Tip: record with the SDK into a JSONL file (e.g. LocalJSONLRecorder('probity.jsonl')) "
            f"or pass the correct log path."
        )
    with p.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                raise ValueError(f"invalid_jsonl at line {line_no}: {e}") from e
            if not isinstance(obj, dict):
                raise ValueError(f"invalid_jsonl at line {line_no}: not an object")
            yield obj


def load_json(path: str) -> Dict[str, Any]:
    p = Path(path)
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("expected JSON object")
    return obj


def find_pre_in_jsonl(path: str, record_id: str) -> Dict[str, Any]:
    for pre in iter_jsonl(path):
        if str(pre.get("record_id", "")) == record_id:
            return pre
    raise KeyError(f"record_id not found: {record_id}")


def resolve_snapshot(pre: Dict[str, Any], base_dir: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Resolve snapshot for export purposes only:
    - embedded pre["snapshot"]
    - pre["snapshot_ref"]["uri"] (local relative path under base_dir)
    """
    if isinstance(pre.get("snapshot"), dict):
        return pre["snapshot"], None

    sref = pre.get("snapshot_ref")
    if not isinstance(sref, dict):
        return None, "snapshot_unresolvable"

    uri = sref.get("uri")
    if not isinstance(uri, str) or not uri:
        return None, "snapshot_unresolvable"

    if uri.startswith("file:"):
        rel = uri[len("file:") :]
    elif "://" in uri:
        return None, "snapshot_unresolvable"
    else:
        rel = uri

    p = Path(base_dir) / rel
    if not p.exists():
        return None, "snapshot_unresolvable"

    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None, "snapshot_unresolvable"

    if not isinstance(obj, dict):
        return None, "snapshot_unresolvable"

    return obj, None