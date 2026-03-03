from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .errors import RecorderError


class Recorder:
    """
    Recorder persists PREs. It must not mutate the PRE.
    """

    def persist(self, pre: Dict[str, Any]) -> None:
        raise NotImplementedError


@dataclass
class LocalJSONLRecorder(Recorder):
    """
    Append-only JSONL recorder.

    Each persist() writes a single line JSON object + newline.
    """

    path: str
    fsync: bool = False

    def persist(self, pre: Dict[str, Any]) -> None:
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            line = json.dumps(pre, ensure_ascii=False, separators=(",", ":")) + "\n"
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line)
                if self.fsync:
                    f.flush()
                    os.fsync(f.fileno())
        except Exception as e:
            raise RecorderError(f"failed_to_persist: {e}") from e


@dataclass
class RotatingFileRecorder(Recorder):
    """
    Rotating JSONL recorder.

    Rotates when current file exceeds max_bytes.
    Rotation names: <base_path>.<unix_ts>.jsonl
    """

    base_path: str
    max_bytes: int = 10_000_000
    fsync: bool = False

    def _current_path(self) -> str:
        return self.base_path

    def _rotate_if_needed(self) -> None:
        path = self._current_path()
        try:
            if os.path.exists(path) and os.path.getsize(path) >= self.max_bytes:
                ts = int(time.time())
                rotated = f"{path}.{ts}.jsonl"
                os.rename(path, rotated)
        except Exception as e:
            raise RecorderError(f"failed_to_rotate: {e}") from e

    def persist(self, pre: Dict[str, Any]) -> None:
        self._rotate_if_needed()
        LocalJSONLRecorder(self._current_path(), fsync=self.fsync).persist(pre)