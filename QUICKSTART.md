# Probity Quickstart (5 Minutes)

This guide demonstrates the complete loop:

1. Install SDK
2. Record an LLM decision
3. View timeline
4. Verify integrity

No network services required.

---

## 1. Install (editable)

From repo root:

```bash
pip install -e sdk/python
pip install -e cli/probity-view
```

---

## 2. Record a Decision (OpenAI Example)

Create `example.py`:

```python
from probity import LocalJSONLRecorder, record_action
from probity.helpers import permission_scope
from probity.timeutil import utc_now_rfc3339
from probity.adapters.openai import (
    map_chat_completion_request,
    map_chat_completion_response,
)

# Create recorder
rec = LocalJSONLRecorder("probity.jsonl")

# Build request snapshot
request_snapshot = map_chat_completion_request(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": "Say hello"}],
    actor_id="agent:demo",
)

# Simulated response (replace with real OpenAI call)
response = {
    "model": "gpt-4.1-mini",
    "choices": [{"message": {"role": "assistant", "content": "Hello!"}}],
    "usage": {"prompt_tokens": 5, "completion_tokens": 2},
}

# Fill outcome
snapshot = map_chat_completion_response(
    request_snapshot=request_snapshot,
    response=response,
    observed_at=utc_now_rfc3339(),
)

# Persist PRE
record_action(recorder=rec, **snapshot)

print("Wrote probity.jsonl")
```

Run:

```bash
python example.py
```

You now have `probity.jsonl`.

---

## 3. View Timeline

```bash
probity-view timeline probity.jsonl
```

Example output:

```
created_at            record_id     evidence_quality  encoding_id        intent.action_type
2026-03-03T18:00:00Z  pre-...       verified          probity-json:v1   llm_call
```

---

## 4. Expand a Record

```bash
probity-view show probity.jsonl --record-id <record_id>
```

---

## 5. Verify Integrity

```bash
probity-view verify probity.jsonl --base-dir . --schemas schemas
```

Verification runs strictly offline and must match protocol invariants.
Schema checks are minimal required-field checks (dependency-free). Full JSON Schema validation is out of scope for the reference verifier.

---

## What You Now Have

- A tamper-evident decision record
- Canonical serialization (RFC 8785)
- SHA-256 integrity linkage
- Deterministic verification
- Portable JSON artifact

No vendor dependency.
No hosted service required.
