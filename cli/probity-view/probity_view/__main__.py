from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .io import iter_jsonl, find_pre_in_jsonl, load_json
from .render import print_timeline_row, pretty
from .verify import run_reference_verifier
from .exporter import export_bundle


def main() -> int:
    ap = argparse.ArgumentParser(prog="probity-view", description="Offline viewer for Probity PREs.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_tl = sub.add_parser("timeline", help="Print a timeline from a JSONL file of PREs.")
    p_tl.add_argument("jsonl", help="Path to JSONL file")

    p_show = sub.add_parser("show", help="Pretty print a record from JSONL by record_id.")
    p_show.add_argument("jsonl", help="Path to JSONL file")
    p_show.add_argument("--record-id", required=True, help="record_id to display")

    p_verify = sub.add_parser("verify", help="Verify a PRE JSON file (wraps reference verifier).")
    p_verify.add_argument("pre", help="Path to pre.json")
    p_verify.add_argument("--base-dir", default=".", help="Base dir for resolving snapshot_ref")
    p_verify.add_argument("--schemas", default=None, help="Path to schemas/ (optional)")
    p_verify.add_argument(
        "--pubkey",
        action="append",
        default=[],
        help="Mapping signer_key_id=path_to_raw_ed25519_pubkey (repeatable)",
    )

    p_export = sub.add_parser("export", help="Export a record bundle from JSONL by record_id.")
    p_export.add_argument("jsonl", help="Path to JSONL file")
    p_export.add_argument("--record-id", required=True, help="record_id to export")
    p_export.add_argument("--out-dir", required=True, help="Output directory")
    p_export.add_argument("--schemas", default=None, help="Path to schemas/ (optional)")
    p_export.add_argument(
        "--pubkey",
        action="append",
        default=[],
        help="Mapping signer_key_id=path_to_raw_ed25519_pubkey (repeatable)",
    )

    args = ap.parse_args()

    if args.cmd == "timeline":
        print("created_at\trecord_id\tevidence_quality\tencoding_id\tintent.action_type")
        for pre in iter_jsonl(args.jsonl):
            print_timeline_row(pre)
        return 0

    if args.cmd == "show":
        pre = find_pre_in_jsonl(args.jsonl, args.record_id)
        sys.stdout.write(pretty(pre))
        return 0

    if args.cmd == "verify":
        out = run_reference_verifier(
            pre_path=args.pre,
            base_dir=args.base_dir,
            schemas_dir=args.schemas,
            pubkeys=list(args.pubkey),
        )
        sys.stdout.write(out)
        return 0

    if args.cmd == "export":
        pre = find_pre_in_jsonl(args.jsonl, args.record_id)
        export_bundle(
            pre=pre,
            base_dir=".",
            out_dir=args.out_dir,
            schemas_dir=args.schemas,
            pubkeys=list(args.pubkey),
        )
        print(f"Wrote bundle to: {args.out_dir}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())