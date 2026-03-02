#!/usr/bin/env python3
"""
Run Probity verification test vectors against a verifier command.

Default: runs the repo reference verifier.

Comparison rules:
- expected_verifier_output.json must match exactly, except:
  - verification_time is ignored (must exist in actual output)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import shlex
from pathlib import Path
from typing import Any, Dict, Tuple, List


IGNORE_FIELDS = {"verification_time"}


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(obj: Dict[str, Any]) -> Dict[str, Any]:
    # shallow ignore for known time field
    o = dict(obj)
    for k in IGNORE_FIELDS:
        o.pop(k, None)
    return o


def run_cmd(cmd: List[str], cwd: Path) -> Tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return p.returncode, p.stdout, p.stderr


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--verifier-cmd",
        default=None,
        help=(
            "Command to run verifier. Use '{pre}', '{base}', '{schemas}' placeholders. "
            "Example: \"python reference/verifier.py --pre {pre} --base-dir {base} --schemas {schemas} --out -\""
        ),
    )
    ap.add_argument("--schemas", default="schemas", help="Path to schemas/ (passed to verifier-cmd).")
    ap.add_argument("--test-vectors", default="test-vectors", help="Path to test-vectors/")
    ap.add_argument("--only", default=None, help="Run only one vector dir name (e.g. 06-missing-field).")
    args = ap.parse_args()

    repo_root = Path(".").resolve()
    tv_root = (repo_root / args.test_vectors).resolve()
    schemas = (repo_root / args.schemas).resolve()

    if not tv_root.exists():
        print(f"test-vectors root not found: {tv_root}", file=sys.stderr)
        return 2

    # default verifier command: reference verifier
    py = shlex.quote(sys.executable)

    if args.verifier_cmd is None:
        verifier_cmd_tpl = f"{py} reference/verifier.py --pre {{pre}} --base-dir {{base}} --schemas {{schemas}} --out -"
    else:
        verifier_cmd_tpl = args.verifier_cmd

    # vector dirs: siblings of canonicalization/
    vector_dirs = []
    for p in sorted(tv_root.iterdir()):
        if not p.is_dir():
            continue
        if p.name == "canonicalization":
            continue
        if args.only and p.name != args.only:
            continue
        # Only accept dirs that have expected_verifier_output.json
        if (p / "expected_verifier_output.json").exists():
            vector_dirs.append(p)

    if not vector_dirs:
        print("No verification vectors found.", file=sys.stderr)
        return 2

    failures = 0

    for vdir in vector_dirs:
        pre_path = (vdir / "pre.json").resolve()
        expected_path = (vdir / "expected_verifier_output.json").resolve()
        if not pre_path.exists():
            print(f"[FAIL] {vdir.name}: missing pre.json")
            failures += 1
            continue

        base_dir = vdir.resolve()

        cmd_str = verifier_cmd_tpl.format(
            pre=str(pre_path),
            base=str(base_dir),
            schemas=str(schemas),
        )
        cmd = shlex.split(cmd_str)

        # Auto-provide pubkey for signature vectors when available.
        # Convention: vector dir contains pubkey.ed25519.raw and PRE contains signature.signer_key_id.
        pubkey_path = (vdir / "pubkey.ed25519.raw").resolve()
        if pubkey_path.exists():
            try:
                pre_obj = load_json(pre_path)
                sig = pre_obj.get("signature")
                signer_key_id = None
                if isinstance(sig, dict):
                    signer_key_id = sig.get("signer_key_id")
                if isinstance(signer_key_id, str) and signer_key_id:
                    cmd.extend(["--pubkey", f"{signer_key_id}={str(pubkey_path)}"])
            except Exception:
                # If anything goes wrong, don't guess — let verifier fail closed.
                pass

        rc, out, err = run_cmd(cmd, cwd=repo_root)

        if rc != 0:
            print(f"[FAIL] {vdir.name}: verifier exited {rc}\n{err}")
            failures += 1
            continue

        try:
            actual = json.loads(out)
        except Exception:
            print(f"[FAIL] {vdir.name}: verifier output is not JSON\nSTDOUT:\n{out}\nSTDERR:\n{err}")
            failures += 1
            continue

        # enforcement: actual must contain verification_time even though we ignore its value
        if "verification_time" not in actual:
            print(f"[FAIL] {vdir.name}: verifier output missing 'verification_time'")
            failures += 1
            continue

        expected = load_json(expected_path)

        a = normalize(actual)
        e = normalize(expected)

        if a != e:
            print(f"[FAIL] {vdir.name}: output mismatch")
            print("---- expected (normalized) ----")
            print(json.dumps(e, indent=2, ensure_ascii=False))
            print("---- actual (normalized) ----")
            print(json.dumps(a, indent=2, ensure_ascii=False))
            failures += 1
        else:
            print(f"[OK]   {vdir.name}")

    if failures:
        print(f"\n{failures} vector(s) failed.")
        return 1

    print("\nAll verification vectors passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())