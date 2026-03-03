# Probity Python SDK (Capture)

This package helps produce Probity Record Envelopes (PREs) for `encoding_id = probity-json:v1`.

Non-goals:
- No verification (use `reference/verifier.py`)
- No policy enforcement
- No behavior interpretation

Install (editable from repo root):
```bash
pip install -e sdk/python
```
---

## Package code

### 3) `sdk/python/probity/__init__.py`
```py
from .wrappers import record_action, record_step, record_tool_call
from .recorder import Recorder, LocalJSONLRecorder, RotatingFileRecorder
from .helpers import environment_snapshot, permission_scope, session_lineage

__all__ = [
    "record_action",
    "record_step",
    "record_tool_call",
    "Recorder",
    "LocalJSONLRecorder",
    "RotatingFileRecorder",
    "environment_snapshot",
    "permission_scope",
    "session_lineage",
]