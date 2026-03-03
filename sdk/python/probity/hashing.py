from __future__ import annotations

import base64
import hashlib
from typing import Literal

from .errors import HashingError

HashEncoding = Literal["hex", "base64url"]


def compute_digest(data: bytes, algo: str, encoding: HashEncoding) -> str:
    if algo != "sha256":
        raise HashingError("unsupported_hash_algo")

    h = hashlib.sha256(data).digest()

    if encoding == "hex":
        return h.hex()
    if encoding == "base64url":
        return base64.urlsafe_b64encode(h).decode("ascii").rstrip("=")

    raise HashingError("unsupported_hash_encoding")