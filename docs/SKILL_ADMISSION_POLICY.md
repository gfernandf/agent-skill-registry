# Skill Admission Policy

This document defines mandatory admission criteria for new skills to prevent
catalog proliferation and maintain a high-value core set.

## Policy Goal

The registry must optimize for:

- clear product value per skill
- low semantic duplication
- simple adoption
- long-term maintainability

## Canonical-First Rule

For each job-to-be-done, prefer one canonical skill.

A new skill must not be introduced if the same business outcome can be
achieved by adding parameters, profiles, or metadata to an existing canonical
skill.

## Admission Checklist (Required)

Every PR introducing a new skill must answer all of the following:

1. Problem statement:
- What concrete user workflow does this skill solve?

2. Differentiation:
- Which existing skills overlap?
- Why can the requirement not be covered by extending one of them?

3. Business value:
- Which measurable outcome improves (time, quality, risk, cost)?

4. Contract clarity:
- Are inputs/outputs stable and reusable across multiple verticals?

5. Governance readiness:
- Does metadata include tags, use_cases, and examples?

6. Sunset plan:
- If this supersedes another skill, identify deprecation target and migration path.

PRs missing the checklist should not be merged.

## Anti-Proliferation Heuristics

A proposed skill should be rejected or merged into an existing one when:

- capability graph overlap is high and outputs are nearly equivalent
- only naming/wording differs
- no measurable product delta is provided

Use `tools/governance_guardrails.py` to inspect overlap signals.

## Promotion and Lifecycle

Skill lifecycle states remain:

- draft
- validated
- lab-verified
- trusted
- recommended

A new skill should begin as `draft` until evidence supports promotion.

## Sunset and Consolidation

When overlap is confirmed and usage is low, maintainers should:

1. keep one canonical skill
2. mark duplicate skills as deprecated in metadata
3. document migration guidance in the PR

## References

- `docs/GOVERNANCE.md`
- `docs/SKILL_FORMAT.md`
- `tools/governance_guardrails.py`