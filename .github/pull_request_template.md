## Change Type

- [ ] New skill
- [ ] Skill update
- [ ] New capability
- [ ] Capability update
- [ ] Vocabulary change
- [ ] Documentation/tooling only

## Problem Statement

Describe the user workflow and business outcome this change targets.

## Differentiation Check (Required for new skills/capabilities)

List overlapping existing IDs and explain why extension/reuse is insufficient.

- Overlapping IDs:
- Why not extend existing artifact:

## Canonical-First Check

- [ ] I reviewed `docs/SKILL_ADMISSION_POLICY.md`
- [ ] I verified this does not introduce avoidable semantic duplication
- [ ] If overlap exists, I documented merge/deprecation rationale

## Contract and Metadata Quality

- [ ] Inputs/outputs are stable and reusable
- [ ] Metadata includes tags
- [ ] Skill metadata includes use_cases and examples (when applicable)

## Lifecycle and Sunset

- [ ] Lifecycle intent is documented (`draft` / `validated` / etc.)
- [ ] If this supersedes an artifact, migration/sunset notes are included

## Validation Evidence

Paste command outputs:

```bash
python tools/validate_registry.py
python tools/generate_catalog.py
python tools/governance_guardrails.py
```

## Notes for Maintainers

Any risk, tradeoff, or open question relevant for merge decision.