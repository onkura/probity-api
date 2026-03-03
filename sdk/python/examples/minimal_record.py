from probity import LocalJSONLRecorder, record_action
from probity.helpers import permission_scope

rec = LocalJSONLRecorder("probity.jsonl")

pre = record_action(
    recorder=rec,
    perception={"inputs": [{"type": "user_text", "ref": "input:1"}]},
    responsibility={"actor_id": "agent:demo", "actor_type": "agent", "authority_scope": permission_scope("purchase")},
    intent={"action_type": "purchase", "action_params": {"target": "item:123", "qty": 1}},
    selection_basis={"heuristic_tags": ["lowest_cost_within_policy"]},
    outcome={"observed_result": "succeeded", "result_refs": ["order:abc123"], "observed_at": "2026-03-02T00:00:01Z"},
)

print(pre["record_id"])