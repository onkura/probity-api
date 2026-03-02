
# Coverage Declaration Specification (Layer 3)

## Purpose
Enable systems to declare the scope of actions they intend to record and provide a machine-readable way to state coverage expectations (not enforcement).

## Coverage Declaration Object
A system **MAY** publish a Coverage Declaration file or endpoint describing:
- `coverage_id` (string) — unique id for the declaration
- `scope_version` (string) — version of the scope definition
- `action_classes` (array) — list of action classes intended to be recorded (e.g., `financial.refund`, `infra.change`, `access.grant`)
- `coverage_assertion` (object) — optional fields like `expected_percent` (e.g., 100), `sla_ms`, `notes`
- `declared_at` (timestamp) — when the declaration was published

## Usage
- Coverage Declarations are human- and machine-readable commitments to expected recording behavior.
- Investigators and auditors can compare observed PRE coverage (via monitoring) against the declared coverage.

## Evolution
- Coverage Declarations **MUST** be versioned. Changes to scope must increment `scope_version` and be published with a changelog.

