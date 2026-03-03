from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from .constants import SPEC_VERSION, ENCODING_ID, SCHEMA_VERSION, CANONICAL_SERIALIZATION_ID
from .timeutil import utc_now_rfc3339
from .snapshot import build_snapshot
from .integrity import compute_integrity
from .recorder import Recorder


def build_pre(
    *,
    snapshot: Dict[str, Any],
    record_id: Optional[str] = None,
    created_at: Optional[str] = None,
    evidence_quality: str = "verified",
    canonical_serialization_id: str = CANONICAL_SERIALIZATION_ID,
    hash_algo: str = "sha256",
    hash_encoding: str = "hex",
) -> Dict[str, Any]:
    rid = record_id or f"pre-{uuid.uuid4()}"
    ts = created_at or utc_now_rfc3339()

    _canonical_bytes, integrity = compute_integrity(
        snapshot,
        canonical_serialization_id=canonical_serialization_id,
        hash_algo=hash_algo,
        hash_encoding=hash_encoding,
    )

    pre: Dict[str, Any] = {
        "record_id": rid,
        "spec_version": SPEC_VERSION,
        "encoding_id": ENCODING_ID,
        "schema_version": SCHEMA_VERSION,
        "canonical_serialization_id": canonical_serialization_id,
        "created_at": ts,
        "evidence_quality": evidence_quality,
        "snapshot": snapshot,
        "integrity": integrity,
    }
    return pre


def record_action(
    *,
    recorder: Recorder,
    perception: Dict[str, Any],
    responsibility: Dict[str, Any],
    intent: Dict[str, Any],
    selection_basis: Dict[str, Any],
    outcome: Dict[str, Any],
    extensions: Optional[Dict[str, Any]] = None,
    evidence_quality: str = "verified",
    record_id: Optional[str] = None,
) -> Dict[str, Any]:
    snapshot = build_snapshot(
        perception=perception,
        responsibility=responsibility,
        intent=intent,
        selection_basis=selection_basis,
        outcome=outcome,
        extensions=extensions,
    )
    pre = build_pre(snapshot=snapshot, evidence_quality=evidence_quality, record_id=record_id)
    recorder.persist(pre)
    return pre


def record_step(
    *,
    recorder: Recorder,
    step_name: str,
    perception: Dict[str, Any],
    responsibility: Dict[str, Any],
    intent: Dict[str, Any],
    selection_basis: Dict[str, Any],
    outcome: Dict[str, Any],
    extensions: Optional[Dict[str, Any]] = None,
    evidence_quality: str = "verified",
    record_id: Optional[str] = None,
) -> Dict[str, Any]:
    ext = dict(extensions or {})
    ext.setdefault("step", {"name": step_name})
    return record_action(
        recorder=recorder,
        perception=perception,
        responsibility=responsibility,
        intent=intent,
        selection_basis=selection_basis,
        outcome=outcome,
        extensions=ext,
        evidence_quality=evidence_quality,
        record_id=record_id,
    )


def record_tool_call(
    *,
    recorder: Recorder,
    tool_name: str,
    tool_input: Any,
    tool_output: Any,
    perception: Dict[str, Any],
    responsibility: Dict[str, Any],
    intent: Dict[str, Any],
    selection_basis: Dict[str, Any],
    outcome: Dict[str, Any],
    extensions: Optional[Dict[str, Any]] = None,
    evidence_quality: str = "verified",
    record_id: Optional[str] = None,
) -> Dict[str, Any]:
    ext = dict(extensions or {})
    ext.setdefault("tool_call", {"name": tool_name, "input": tool_input, "output": tool_output})
    return record_action(
        recorder=recorder,
        perception=perception,
        responsibility=responsibility,
        intent=intent,
        selection_basis=selection_basis,
        outcome=outcome,
        extensions=ext,
        evidence_quality=evidence_quality,
        record_id=record_id,
    )