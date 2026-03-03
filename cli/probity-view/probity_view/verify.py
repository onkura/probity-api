from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_reference_verifier(
    *,
    pre_path: str,
    base_dir: str,
    schemas_dir: Optional[str],
    pubkeys: List[str],
) -> str:
    """
    Wraps reference/verifier.py to keep a single compliance oracle.
    Returns verifier-output JSON (stdout).
    """
    repo_root = Path(".").resolve()
    verifier = repo_root / "reference" / "verifier.py"
    if not verifier.exists():
        raise FileNotFoundError("reference/verifier.py not found (run from repo root)")

    cmd = [
        sys.executable,
        str(verifier),
        "--pre",
        str(Path(pre_path).resolve()),
        "--base-dir",
        str(Path(base_dir).resolve()),
        "--out",
        "-",
    ]
    if schemas_dir is not None:
        cmd.extend(["--schemas", str(Path(schemas_dir).resolve())])

    for mapping in pubkeys:
        cmd.extend(["--pubkey", mapping])

    p = subprocess.run(
        cmd,
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"reference verifier failed: {p.stderr.strip()}")
    return p.stdout