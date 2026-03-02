"""
CLI tool for JCS canonicalization (Probity v1).

Usage:
  python canonicalize.py input.json output.txt
"""

import sys
from jcs_rfc8785 import canonicalize, CanonicalizationError


def main():
    if len(sys.argv) != 3:
        print("Usage: python canonicalize.py input.json output.txt")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = f.read()

        canonical_bytes = canonicalize(data)

        with open(output_path, "wb") as f:
            f.write(canonical_bytes)

    except CanonicalizationError as e:
        print(f"Canonicalization error: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
