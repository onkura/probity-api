# example.py
#
# Minimal Probity example:
# - Uses OpenAI adapter (no network call required for demo)
# - Records a single LLM decision
# - Writes to probity.jsonl
#
# Run:
#   python example.py
#
# Then:
#   probity-view timeline probity.jsonl

from probity import LocalJSONLRecorder, record_action
from probity.timeutil import utc_now_rfc3339
from probity.adapters.openai import (
    map_chat_completion_request,
    map_chat_completion_response,
)

def main():
    # Create recorder (JSONL log file)
    recorder = LocalJSONLRecorder("probity.jsonl")

    # Build request snapshot (before LLM call)
    request_snapshot = map_chat_completion_request(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": "Say hello"}],
        actor_id="agent:demo",
    )

    # Simulated LLM response (replace with real OpenAI call in production)
    response = {
        "model": "gpt-4.1-mini",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello!"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 5,
            "completion_tokens": 2
        }
    }

    # Complete snapshot with outcome
    snapshot = map_chat_completion_response(
        request_snapshot=request_snapshot,
        response=response,
        observed_at=utc_now_rfc3339(),
    )

    # Persist PRE
    record_action(recorder=recorder, **snapshot)

    print("Wrote probity.jsonl")


if __name__ == "__main__":
    main()
