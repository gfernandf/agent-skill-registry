# Skill Pack V1 Hardening Plan

Date: 2026-05-12
Scope: task.frame, decision.make, web.search-summary, data.parse-and-validate, security.safe-summarize
Objective: deliver a closed, deterministic, and testable production-grade set with no cross-repo contract drift.

## 1) Rules of engagement

- Source of truth for contracts: agent-skill-registry.
- Runtime behavior must match registry contracts exactly.
- No breaking changes during v1 hardening. If needed, bump version and document migration.
- A skill is not considered closed unless all Go/No-Go checks pass.

## 2) Workstreams (parallel)

- WS1 Contracts: normalize inputs/outputs, required fields, examples, metadata.status.
- WS2 Runtime defaults: deterministic binding path, timeout/retry policy, error normalization.
- WS3 Safety: guardrails, risk notes, and explicit failure behavior.
- WS4 QA: contract tests, E2E tests, adversarial tests, protocol-equivalence checks.
- WS5 Observability: trace completeness, replay key integrity, audit payload consistency.

## 3) Phase plan

### Phase A - Freeze and baseline (Day 1)

- Confirm canonical skill versions and freeze interface changes.
- Build traceability matrix per skill:
  - skill.yaml
  - used capabilities
  - bindings used in runtime
  - test coverage
- Mark initial maturity per skill: ready, partial, not-ready.

Exit criteria:
- Matrix completed for all 5 skills.
- All known gaps classified as P0/P1/P2.

### Phase B - Skill-by-skill hardening (Days 2-5)

Execution order:
1. data.parse-and-validate
2. web.search-summary
3. task.frame
4. security.safe-summarize
5. decision.make

Per skill workflow:
1. Contract cleanup in registry.
2. Runtime alignment in agent-skills.
3. Tests added/updated.
4. Catalog regeneration and governance checks.
5. Local validation pass and sign-off.

Exit criteria:
- Each skill individually passes all Go/No-Go checks.

### Phase C - Cross-skill consistency pass (Day 6)

- Enforce common output envelope in skill-level outputs or response metadata handling:
  - run_id
  - status
  - trace_id
  - warnings
- Validate error schema consistency across the 5 skills.
- Validate deterministic defaults and fallback behavior.

Exit criteria:
- No output/error shape drift across skills.
- Replay key fields available for every run.

### Phase D - Release candidate (Day 7)

- Full CI passes in both repos.
- Catalog freshness and governance checks pass with zero diff.
- Publish release notes and known limitations.

Exit criteria:
- Skill Pack V1 ready for external allowlist selection.

## 4) Go/No-Go checklist (must pass per skill)

1. Contract I/O stable and validated.
2. Required/optional semantics are explicit and consistent.
3. Deterministic binding defaults are configured.
4. Timeout/retry policy is defined and tested.
5. Errors are normalized and documented.
6. Trace emits step-level and run-level identifiers.
7. Replay tuple is reproducible: run_id + skill_version + normalized_inputs.
8. Tests cover happy path, edge path, adversarial path.
9. Catalog regenerated and governance pipeline passes.

## 4.1) Canonical validation flow

Use the supported runner path for every skill we harden:

1. Validate the registry.
2. Regenerate the catalog artifacts.
3. Execute the skill through the engine-backed runner (`tooling.skill_authoring.run_skill_test` or the CLI `test` command).
4. Capture the resulting trace and outputs.
5. Keep the ad hoc `test_new_skills.py` script only as a legacy convenience wrapper, not as the source of truth.

The legacy sweep is useful for broad sanity checks, but it is not the release gate for the v1 pack because it still contains unrelated legacy skills that can time out independently of the skill under hardening.

This avoids the earlier harness mismatch where the script built the engine without a host root and failed before skill execution.

## 5) Current gap backlog from initial audit

## data.parse-and-validate

Status: closest to closure.

Gaps:
- metadata.status is unspecified in catalog artifacts.
- Example payload naming is inconsistent (raw_data vs text, parsed vs data).
- No explicit error taxonomy for parse failure vs schema failure.

Actions:
- Set metadata.status to stable.
- Align examples to canonical input/output names.
- Add negative tests: malformed JSON, schema mismatch, oversized payload.

## web.search-summary

Status: medium readiness.

Gaps:
- Minimal contract surface (limit is weakly constrained).
- No explicit behavior for empty/noisy result sets.
- Summary quality may vary without deterministic constraints.

Actions:
- Constrain limit bounds and define defaults.
- Define empty-result behavior contract.
- Add tests for no results, duplicate results, non-English query.

## task.frame

Status: strong value but mapping inconsistencies detected.

Gaps:
- Runtime mapping hints show potential input-name mismatch risk (task vs goal).
- Optional outputs (objectives, constraints_extracted, information_needed) need explicit presence policy.
- suggested_next_skills shape should be strict (ids + rationale schema).

Actions:
- Enforce runtime input mapping to canonical task.
- Define null/empty behavior for optional outputs.
- Add schema-level checks for suggested_next_skills entries.

## security.safe-summarize

Status: high strategic value, currently experimental.

Gaps:
- metadata.status is experimental.
- Gate behavior must be deterministic for blocked outputs.
- Needs strong adversarial test coverage for PII leakage edge cases.

Actions:
- Promote to stable after tests.
- Lock blocked-output sentinel behavior.
- Add adversarial corpus tests (emails, phones, IDs, mixed-language PII).

## decision.make

Status: high complexity, highest risk.

Gaps:
- Large output surface increases drift risk.
- Requires strict defaulting for risk_tolerance and option generation behavior.
- Needs explicit quality threshold behavior for low-confidence outcomes.

Actions:
- Freeze and validate all required output fields.
- Add deterministic handling when context_items or options are missing.
- Add policy for low-confidence result (warnings/escalation).

## 6) Validation commands (registry)

Run full sequence before push:

python tools/validate_registry.py
python tools/governance_guardrails.py --fail-on-high-risk-overlap-channels community,official
python tools/capability_governance_guardrails.py
python tools/enforce_capability_sunset.py
python tools/generate_catalog.py
python tools/registry_stats.py

## 7) Definition of done for Skill Pack V1

Skill Pack V1 is complete only when:

- 5/5 skills pass Go/No-Go.
- No contract/runtime drift detected.
- Full governance and catalog generation pass clean.
- Reproducible replay keys are available in traces for all skills.
- A single release note documents constraints and known non-goals.