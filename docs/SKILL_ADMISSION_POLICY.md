# Skill Admission Policy

This document defines mandatory admission criteria for new skills and the
**channel model** through which skills flow from user-defined experiments to
the verified official catalog.

## Channel Model

Skills in this registry — and in each local `agent-skills` instance — are
organized into channels.  The channel determines governance requirements,
quality expectations, and who owns maintenance.

| Channel | Location | Maintained by | Requirements |
|---------|----------|---------------|--------------|
| `local` | `<agent-skills>/skills/local/` | Individual instance owner | None — fully private to the instance; never committed to the shared registry |
| `experimental` | `skills/experimental/` | Contributor (PR) | Basic schema validity; `metadata.status: experimental`; no stability guarantee |
| `community` | `skills/community/` | Contributor (PR) | Full admission checklist below; peer review required |
| `official` | `skills/official/` | Maintainers | Admission checklist; two-maintainer review; integration smoke-test passing |

### How a skill moves through channels

```
[instance author] → skills/local/   (runs locally, no PR)
                        ↓  promote
[contributor PR]  → skills/experimental/  (schema valid, self-assessed)
                        ↓  peer review
[contributor PR]  → skills/community/     (full checklist, peer review)
                        ↓  maintainer review
[maintainer PR]   → skills/official/      (two-maintainer sign-off)
```

A skill does **not** have to follow every step.  It is valid to submit
directly to `community/` if the checklist is already complete.

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

## Admission Checklist (Required for `community/` and `official/`)

Every PR introducing a skill at `community/` or `official/` level must answer
all of the following:

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

For `experimental/` channel, only items 1 and 4 are required.

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