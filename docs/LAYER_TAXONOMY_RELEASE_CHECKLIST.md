# Layer Taxonomy Release Checklist

Purpose: release gate for documentation and governance changes related to capability layer taxonomy.

Scope of this checklist:
- freeze and consistency of the 4-layer model
- cross-document alignment
- production-readiness evidence for governance and catalog freshness

Out of scope:
- capability contract functional redesign
- runtime binding implementation changes

## Canonical model (must stay unchanged)

Allowed layers only:
- cognitive
- orchestration
- operational
- governance

Authoritative source of classification:
- metadata.layer in each capability contract

Naming rule:
- capability id/domain naming is semantic context, not layer authority by itself

## PR Checklist (Go/No-Go)

### 1) Scope and intent
- [ ] PR summary explicitly states layer-taxonomy objective.
- [ ] PR confirms no new layer category is introduced.
- [ ] PR confirms whether changes are documentation-only or include runtime/code changes.

### 2) Cross-document alignment
- [ ] docs/CAPABILITIES.md reflects the frozen 4-layer model and metadata.layer authority.
- [ ] docs/CAPABILITY_ADMISSION_POLICY.md reflects tie-break precedence and decision.flow/input.route boundary.
- [ ] docs/COGNITIVE_TAXONOMY.md clarifies semantic-family view vs layer source of truth.
- [ ] docs/GOVERNANCE.md includes the frozen taxonomy policy.
- [ ] docs/PROJECT_CONTEXT.md and docs/REGISTRY_STRUCTURE.md are consistent with the same rule.
- [ ] docs/CAPABILITY_STATUS_GUIDE.md states status and layer are orthogonal.

### 3) Ambiguity controls
- [ ] Explicit statement exists: decision.flow.* and decision.input.route can be orchestration when no cognitive inference is added.
- [ ] No document claims that a prefix alone (for example decision.*) determines layer.
- [ ] No contradictory statement remains across docs.

### 4) Validation and governance evidence
- [ ] python tools/validate_registry.py passes.
- [ ] python tools/governance_guardrails.py --fail-on-high-risk-overlap-channels community,official passes.
- [ ] python tools/capability_governance_guardrails.py passes (advisory report generated).
- [ ] python tools/enforce_capability_sunset.py passes.

### 5) Catalog freshness and CI parity
- [ ] python tools/generate_catalog.py executed.
- [ ] python tools/registry_stats.py executed.
- [ ] catalog/ artifacts are committed when changed.
- [ ] Working tree has no unintended drift in catalog/ after generation.

### 6) Risk and rollback
- [ ] PR describes impact level (docs-only, governance-only, or mixed).
- [ ] PR includes rollback procedure:
  - revert the PR commit(s)
  - regenerate catalog
  - rerun validation and guardrails
- [ ] Owners for final approval are assigned.

## Mandatory PR Evidence Block (copy/paste)

Use this block in PR description:

- Objective:
- In scope:
- Out of scope:
- Layer model changed? (must be No):
- Validation commands executed:
  - validate_registry: PASS/FAIL
  - governance_guardrails: PASS/FAIL
  - capability_governance_guardrails: PASS/FAIL
  - enforce_capability_sunset: PASS/FAIL
  - generate_catalog: PASS/FAIL
  - registry_stats: PASS/FAIL
- Catalog drift after regeneration: YES/NO
- Risks:
- Rollback:
- Approvers:

## Approval rule

Go:
- all checklist items complete
- all validation commands pass
- no cross-document contradiction remains

No-Go:
- any new layer category proposal without explicit governance approval
- unresolved contradiction between semantic family docs and metadata.layer authority
- missing validation evidence or catalog freshness evidence
