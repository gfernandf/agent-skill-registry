# code.change-approval-gate

**Channel**: experimental  **Version**: 0.1.0  **Category**: code

## What this skill does

Evaluates a software change (PR or release) against **explicit, readable policy rules** and produces a structured, auditable approval decision: `approve`, `block`, or `escalate`.

This is **not a semantic code reviewer**. It is a bounded execution gate that:

1. Summarizes what changed (technical language)
2. Extracts risks, fragile assumptions, and failure modes from the change package
3. Classifies the overall risk level (`low` / `medium` / `high` / `critical`)
4. Applies explicit policy constraints (required fields, forbidden patterns)
5. Branches to a final decision based on gate outcome × risk level
6. Justifies the decision with explicit rule references and missing evidence

## Decision taxonomy

| Decision  | Condition |
|-----------|-----------|
| `approve` | Gate passed **and** risk level ≤ threshold |
| `block`   | Gate blocked (required fields missing or forbidden patterns present) |
| `escalate`| Gate passed **but** risk classified as critical — insufficient evidence to block, but human review required |

The three-outcome taxonomy prevents the false binary of approve/block that masks uncertain evidence. **An opaque LLM reviewer will almost never say "escalate" without explicit instruction — and will say different things each time.**

## Inputs

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `change_package` | object | ✓ | Normalized change representation — see required subfields below |
| `policy_profile` | object | ✓ | Explicit policy to enforce — readable before execution |

### `change_package` required subfields

| Subfield | Type | Notes |
|----------|------|-------|
| `change_id` | string | Stable identifier |
| `change_type` | string | `"pr"` or `"release"` |
| `title` | string | Human-readable title |
| `diff_text` | string | Unified diff or plain-text description |
| `target_environment` | string | `"dev"`, `"staging"`, or `"prod"` |
| `changed_files` | array | Affected file paths |

Optional: `author_summary`, `labels`, `test_evidence`, `rollback_plan`, `release_notes`.

### `policy_profile` structure

```json
{
  "name": "standard",
  "gate": {
    "rules": {
      "required_keys": ["diff_text", "changed_files", "author_summary"],
      "forbidden_keys": []
    },
    "action": "block"
  },
  "risk": {
    "max_level": "medium",
    "escalate_on_critical": true,
    "categories": ["low", "medium", "high", "critical"]
  }
}
```

## Outputs

| Field | Type | Notes |
|-------|------|-------|
| `decision` | string | `approve` / `block` / `escalate` |
| `change_summary` | string | Technical summary of the diff |
| `executive_summary` | string | Non-technical summary for stakeholders |
| `identified_risks` | array | Structured risks with severity hints |
| `risk_level` | string | `low` / `medium` / `high` / `critical` |
| `violated_rules` | array | Empty when decision is `approve` |
| `required_followups` | array | Actionable steps to proceed |
| `rationale` | string | Explicit rule-linked justification |
| `confidence` | number | 0.0–1.0 |

## Pipeline

```
summarize_change   (text.content.summarize)
       │
extract_risks      (analysis.risk.extract)
       │
classify_risk      (policy.risk.classify)
       │
apply_policy_gate  (policy.constraint.gate)
       │
determine_decision (agent.flow.branch)
       │
justify_decision   (policy.decision.justify)
       │
summarize_executive (text.content.summarize)
```

## Traceability

Attach `agent.trace` as a sidecar to obtain a full step-by-step decision graph:

```python
engine.execute(request, sidecar="agent.trace")
```

Each step's inputs, outputs, and intermediate `vars` are captured, making the decision fully reproducible and auditable.

## Comparison with prompt-based approach

See the experiment in `agent-skills/experiments/change_approval_gate/` for a structured comparison of this skill against a direct prompt-based reviewer, including:

- 8 reproducible fixtures with ground-truth expected outcomes
- 3 policy profiles (`fast_track`, `standard`, `strict_prod`)
- Metrics: decision agreement, rule grounding, risk coverage, stability across repetitions

The core finding: the prompt baseline produces plausible-sounding rationales that are **not grounded in the policy profile** you provided. Different runs produce different decisions on the same fixture. ORCA's gate is bounded to its input contract.

## Related skills

- `analysis.risk-assess` — standalone risk assessment without a policy gate
- `agent.trace` — sidecar for step-level audit trail
- `decision.make` — general structured decision (no policy enforcement)
