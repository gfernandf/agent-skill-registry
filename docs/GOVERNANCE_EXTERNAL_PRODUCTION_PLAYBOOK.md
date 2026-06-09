# Governance External Production Playbook

Purpose: execute governance-layer hardening as a product-quality program, not as ad-hoc changes.

This playbook is the execution reference for moving governance capabilities from current state to external-production readiness.

## 1) Product Goal

Target perception for external users:
- not dummy
- framework-quality governance layer that can control real production flows

Target behavior:
- consistent access decisions
- policy-aware and context-aware gating
- security-safe output enforcement
- first-class auditability of decisions

## 2) Scope Boundaries

In scope:
- governance capability contracts and semantics
- governance decision model and output envelopes
- governance docs, guardrails, and release checks
- catalog freshness and CI parity

Out of scope:
- redesign of cognitive capability contracts
- replacing existing cognitive inference with governance logic

Rule: governance consumes typed outputs from cognitive/operational capabilities. Governance does not duplicate cognitive reasoning.

## 3) Target Capability Coverage

Current governance capabilities: 26

Planned target for production-grade governance layer: 34

### Keep (baseline set; unchanged contracts)
- identity.assignee.identify
- identity.decision.justify
- identity.permission.gate
- identity.permission.get
- identity.permission.list
- identity.permission.verify
- identity.risk.score
- identity.role.assign
- identity.role.get
- identity.role.list
- policy.constraint.gate
- policy.constraint.validate
- policy.decision.justify
- policy.risk.classify
- policy.risk.score
- security.output.gate
- security.pii.detect
- security.pii.redact
- security.secret.detect

### Add (critical core 8)
- identity.principal.resolve
- identity.access.evaluate
- identity.role.revoke
- resource.sensitivity.classify
- resource.access.scope
- policy.condition.resolve
- security.data.classify
- audit.decision.record

### Add (enterprise robustness 7)
- resource.ownership.resolve
- policy.exception.evaluate
- policy.decision.resolve
- security.secret.redact
- audit.trace.summarize
- audit.evidence.link
- identity.access.justify

## 4) Decision Model Standard (mandatory)

All governance decision capabilities must converge to a shared output envelope:

- decision: allow | deny | conditional_allow | escalate | transform
- conditions: list of executable conditions
- rationale: human-readable explanation
- evidence: structured references
- risk: class and/or score when applicable
- decision_id
- policy_version
- timestamp
- evaluator_version

All mutative operations must require:
- explicit authorization evaluation
- decision evidence
- audit record

## 5) Execution Plan by Phase

## Phase A: Contract Hardening (existing 19)

Goal:
- normalize semantics and remove ambiguity

Work:
- split validate vs gate semantics clearly
- split actor risk vs action risk semantics clearly
- classify mutative vs analytical operations
- align output envelope on all 19 contracts

Exit criteria:
- 19/19 contracts follow the standard decision model where applicable
- no semantic contradiction in docs
- taxonomy and naming rules remain canonical-first

## Phase B: Critical Core (add 8)

Goal:
- make governance viable for real production enforcement

Work:
- add 8 critical capabilities
- wire decision recording into sensitive flows
- enforce resource sensitivity as first-class signal

Exit criteria:
- sensitive flows have end-to-end control from principal+resource+policy+risk to decision
- audit decision records generated for governed flows

## Phase C: Enterprise Robustness (add 7)

Goal:
- remove remaining product-confidence gaps for external adoption

Work:
- add conditional/exception resolution
- add full audit trace linking
- add secret redaction and ownership/scope controls

Exit criteria:
- governance can represent conditional allow and exception handling
- traceability available for external audits and incident review

## 6) No-Slip Controls

### Release gates (must pass)
Run full CI-parity sequence before PR merge:

```bash
python tools/validate_registry.py
python tools/governance_guardrails.py --fail-on-high-risk-overlap-channels community,official
python tools/capability_governance_guardrails.py
python tools/enforce_capability_sunset.py
python tools/generate_catalog.py
python tools/registry_stats.py
```

### PR policy
- every governance PR must include the evidence block from docs/LAYER_TAXONOMY_RELEASE_CHECKLIST.md
- every governance PR must update catalog artifacts when changed
- no merge if catalog drift remains after regeneration

### Compatibility policy
- no breaking changes on stable contracts without migration path
- renames must use alias/deprecation window
- prefer additive evolution

## 7) Work Cadence and Ownership

Weekly cadence:
- Week N planning: select 2-4 capabilities for design/finalization
- Mid-week: contract + docs + tests
- End-week: run release gates and merge if green

Recommended owners:
- Capability owner: semantics and schema
- Governance owner: policy alignment and risk model
- Runtime owner: execution and enforcement integration
- Reviewer: compatibility and external-consumer impact

## 8) Quality KPIs

Minimum KPIs for external-production readiness:
- governance decisions with structured evidence: 100%
- sensitive mutative flows with audit.decision.record: 100%
- unresolved semantic overlaps in governance layer: 0 high-severity
- CI-parity gate pass rate: 100% on release PRs

## 9) Initial Backlog Order (quality-first)

Priority 1:
- identity.access.evaluate
- resource.sensitivity.classify
- policy.condition.resolve
- security.data.classify
- audit.decision.record

Priority 2:
- identity.principal.resolve
- resource.access.scope
- identity.role.revoke

Priority 3:
- policy.exception.evaluate
- policy.decision.resolve
- security.secret.redact
- audit.trace.summarize
- audit.evidence.link
- resource.ownership.resolve
- identity.access.justify

## 10) Governance Review Checklist for Each New Capability

For every new governance capability, confirm:
- no duplication of cognitive inference already provided by typed upstream outputs
- clear place in IAM, policy, security, resource, or audit plane
- clear input contract using principal/action/resource/context where applicable
- output contract compatible with the standard decision model
- explicit tests for success, block, conditional outcomes

## 11) Definition of Done (program level)

The governance layer is externally production-ready when:
- phase A, B, and C exit criteria are complete
- all release gates pass consistently
- docs and PR templates reflect the final policy
- consumers can implement governance flows without guessing semantics
