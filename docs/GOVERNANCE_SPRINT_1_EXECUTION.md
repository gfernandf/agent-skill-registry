# Governance Sprint 1 Execution

Purpose: execute Priority 1 capabilities from the external production playbook using small, reviewable PR slices.

## Sprint Goal

Deliver initial production-grade governance primitives without breaking compatibility:
- identity.permission.evaluate
- policy.record.classify
- policy.decision.evaluate
- security.content.classify
- provenance.decision.store

## Scope

In scope:
- capability contracts (draft)
- capability index registration
- validation and catalog refresh

Out of scope:
- runtime implementation bindings
- changes to stable governance capability semantics
- renames/deprecations

## PR Slices

### Slice 1: Access decision core
- Add identity.permission.evaluate
- Add policy.record.classify
- Validation gates

### Slice 2: Conditional policy control
- Add policy.decision.evaluate
- Add security.content.classify
- Validation gates

### Slice 3: Auditability baseline
- Add provenance.decision.store
- Validation gates and catalog refresh

## Contract Quality Gates (per slice)

- Clear distinction from existing capabilities (no semantic duplication)
- Inputs/outputs are typed and reusable
- Governance layer is set to metadata.layer=governance
- Cognitive outputs are consumed as structured evidence, not re-inferred

## Program Gates (before merge)

```bash
python tools/validate_registry.py
python tools/governance_guardrails.py --fail-on-high-risk-overlap-channels community,official
python tools/capability_governance_guardrails.py
python tools/enforce_capability_sunset.py
python tools/generate_catalog.py
python tools/registry_stats.py
```

## Acceptance Criteria

- 5 new governance contracts added and index-registered
- Validation and governance scripts pass
- No taxonomy inconsistency introduced
- New contracts align with decision-model orientation (decision, conditions, rationale, evidence, risk where applicable)
