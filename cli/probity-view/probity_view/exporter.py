from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, List

from probity.integrity import compute_integrity
from .io import resolve_snapshot
from .verify import run_reference_verifier


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_bundle(
    *,
    pre: Dict[str, Any],
    base_dir: str,
    out_dir: str,
    schemas_dir: Optional[str],
    pubkeys: List[str],
) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Write PRE
    _write_json(out / "pre.json", pre)

    # Resolve snapshot (embedded or snapshot_ref)
    snapshot, err = resolve_snapshot(pre, base_dir)
    if snapshot is not None:
        _write_json(out / "snapshot.json", snapshot)

        # Canonicalize + hash using SDK (deterministic)
        canonical_bytes, integrity = compute_integrity(
            snapshot,
            canonical_serialization_id=pre.get("canonical_serialization_id", "jcs:rfc8785"),
            hash_algo=pre.get("integrity", {}).get("hash_algo", "sha256"),
            hash_encoding=pre.get("integrity", {}).get("hash_encoding", "hex"),
        )
        (out / "canonical.txt").write_bytes(canonical_bytes)
        (out / "computed_digest.txt").write_text(str(integrity["digest"]) + "\n", encoding="utf-8")

    # Run reference verifier output (compliance oracle)
    # We verify the *original* pre file only if present; here we have object, so we write temp-ish.
    # For simplicity, verify against the exported pre.json and bundle base dir.
    vo = run_reference_verifier(
        pre_path=str(out / "pre.json"),
        base_dir=out_dir,
        schemas_dir=schemas_dir,
        pubkeys=pubkeys,
    )
    (out / "verifier_output.json").write_text(vo, encoding="utf-8")