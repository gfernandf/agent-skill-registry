# Contributing to agent-skill-registry

Thank you for your interest in contributing! This guide explains how to
propose changes, the review process, and what to expect.

---

## Quick Start

```bash
git clone https://github.com/gfernandf/agent-skill-registry.git
cd agent-skill-registry
pip install -r requirements.txt
python tools/validate_registry.py
```

---

## How to Contribute

### Bug reports & feature requests

Open a [GitHub Issue](https://github.com/gfernandf/agent-skill-registry/issues)
using the appropriate template (bug / feature).

### Capability contributions

1. **Fork** the repo and create a branch from `main`.
2. Create a new YAML file under `capabilities/` following the naming
   convention: `<domain>.<entity>.<action>.yaml`.
3. Run validation: `python tools/validate_registry.py`
4. Run governance checks: `python tools/governance_guardrails.py`
5. Regenerate the catalog: `python tools/generate_catalog.py`
6. **Open a PR** against `main` with a clear description.

See the [Capability Admission Policy](docs/CAPABILITY_ADMISSION_POLICY.md)
for detailed requirements.

### Skill contributions

1. Create a new YAML file under `skills/`.
2. Reference only capabilities already in the registry.
3. Run validation and catalog regeneration (same as above).
4. **Open a PR** with a description of what your skill does.

See the [Skill Admission Policy](docs/SKILL_ADMISSION_POLICY.md).

---

## Review Process

- A maintainer will review your PR within **3–5 business days**.
- Automated CI validates YAML syntax, governance guardrails, and catalog
  freshness.
- All PRs require at least one approving review.

---

## Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(capabilities): add text.summary.bullet
fix(skills): correct step order in research-briefing
docs: update vocabulary reference
```

---

## Code of Conduct

Please read our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). We are committed
to a welcoming, inclusive community.
