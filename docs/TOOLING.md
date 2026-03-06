# Tooling

This document describes the internal tools used to maintain the Agent Skill Registry.

---

## Registry Validator

File:

```text
tools/validate_registry.py
```

Purpose:

- validate capability files
- validate skill files
- validate references across the registry
- fail on structural or semantic inconsistencies

The validator is intended to be used in two ways:

1. locally by contributors before opening a pull request
2. automatically in CI for every push and pull request

### Usage

Validate the full registry:

```bash
python tools/validate_registry.py
```

Validate a specific file or directory:

```bash
python tools/validate_registry.py capabilities/text.summarize.yaml
python tools/validate_registry.py skills/official/text/hello-world/skill.yaml
python tools/validate_registry.py skills/community/text/
```

### What it validates

For capabilities:

- required fields
- identifier format
- semantic version format
- input and output schema structure
- dependency references
- replacement references
- filename consistency

For skills:

- required fields
- name format
- semantic version format
- step structure
- unique step ids
- capability references
- optional skill composition references
- valid dataflow references
- output production
- path consistency

### What it does not validate

The validator does not:

- execute skills
- execute capabilities
- resolve runtime providers
- validate implementation quality
- validate runtime compatibility

It validates only registry integrity.