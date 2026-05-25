# Capability Admission Policy

Capabilities define the core language used by all skills.

This policy is stricter than skill admission because capability proliferation
creates long-term semantic and operational debt.

## Admission Principle

A new capability ID is accepted only when:

1. no existing capability can express the operation without semantic distortion
2. the operation is reusable across multiple workflows
3. the contract boundary is clear and provider-agnostic

If the same outcome can be modeled by composing existing capabilities in a
skill, prefer skill composition over new capability creation.

## Mandatory Review Questions

Every new capability proposal must answer:

1. Which existing capability IDs are closest in semantics?
2. Why are they insufficient?
3. What reusable boundary does the new capability add?
4. What workflows will consume it immediately?
5. What compatibility and deprecation strategy applies if it evolves?

PRs missing these answers should not be merged.

## Canonical Language Rule

Prefer one canonical operation per semantic intent.

Avoid introducing near-synonyms that fragment discoverability
(for example multiple verbs/nouns expressing the same operation).

Use `tools/capability_governance_guardrails.py` to inspect overlap signals.

## Acceptance Gates

Required gates before merge:

1. `tools/validate_registry.py` passes
2. `tools/generate_catalog.py` passes
3. `tools/capability_governance_guardrails.py` report reviewed
4. compatibility impact is documented (see `docs/CAPABILITY_COMPATIBILITY_POLICY.md`)

Additionally, every capability must declare execution governance properties:

- `properties.state_access` in `{none, read, write, read_write}`
- `properties.audit_level` in `{basic, standard, strict}`
- `metadata.layer` in `{cognitive, orchestration, operational, governance}`

These fields are mandatory for catalog profiling and runtime governance.

### Layer tie-break policy

When a capability appears semantically ambiguous, classify in this precedence:

1. governance
2. orchestration
3. cognitive
4. operational

Additional tie-break rules:

- Policy/security/identity capabilities are governance by default.
- `agent.plan.*`, `agent.flow.*`, `agent.input.*`, `agent.request.*`, `agent.catalog.*`, `agent.task.*` are orchestration by default.
- Cognitive role hints (`analyze`, `evaluate`, `decide`, `synthesize`, `reflect`, `perceive`) can override orchestration default to cognitive.
- Side-effecting capabilities default to operational unless governance/orchestration rules apply.

### Phase 1 baseline policy (current)

To keep catalog behavior consistent during the first governance pass:

- All `text.*` capabilities use `properties.audit_level: standard`
- The following capabilities also use `properties.audit_level: standard`:
	- `code.diff.extract`
	- `code.source.analyze`
	- `data.schema.validate`
	- `doc.content.generate`
- Pure adapter/utility capabilities remain `basic` unless side effects,
	safety, or policy requirements justify higher audit strictness.

This baseline is intentionally conservative and can be revised in subsequent
governance phases based on empirical audit and evaluation evidence.

## Rejection Heuristics

Reject when any condition holds:

1. Only naming style differs from an existing capability.
2. Operation is single-workflow specific and not broadly reusable.
3. Proposal depends on provider-specific behavior in public contract.
4. Business value is not measurable or not stated.

## References

- `docs/CAPABILITIES.md`
- `docs/CAPABILITY_COMPATIBILITY_POLICY.md`
- `docs/CAPABILITY_SUNSET_POLICY.md`
- `tools/capability_governance_guardrails.py`
