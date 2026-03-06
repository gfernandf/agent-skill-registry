# Tooling

This document describes the internal tools used to maintain the integrity of the **Agent Skill Registry**.

The registry contains structured definitions of:

- capabilities
- skills

To ensure consistency and correctness across the repository, automated validation tools are provided.

---

# Registry Validator

File:

```
tools/validate_registry.py
```

The registry validator verifies that all **skills** and **capabilities** in the repository follow the specification and maintain internal consistency.

The validator is intended to be used in two ways:

1. **Locally by contributors** before opening a pull request.
2. **Automatically in CI** to validate the registry on every commit.

---

# Usage

From the root of the repository:

```bash
python tools/validate_registry.py
```

This validates the entire registry.

---

## Validate a Specific File

You may validate an individual capability or skill:

```bash
python tools/validate_registry.py capabilities/text.summarize.yaml
```

```bash
python tools/validate_registry.py skills/official/text/hello-world/skill.yaml
```

---

## Validate a Directory

You may validate a subset of the registry:

```bash
python tools/validate_registry.py skills/community/text/
```

---

# What the Validator Checks

## Capability Validation

The validator verifies that each capability:

- contains required fields (`id`, `version`, `description`, `inputs`, `outputs`)
- uses a valid capability identifier
- uses valid semantic versioning
- defines input and output schemas correctly
- references valid dependencies in `requires`
- references valid capabilities in `replacement`
- uses only supported execution properties
- matches the expected filename convention

---

## Skill Validation

The validator verifies that each skill:

- contains required fields (`id`, `version`, `name`, `description`, `inputs`, `outputs`, `steps`)
- uses a valid skill identifier
- uses valid semantic versioning
- contains valid step definitions
- uses unique step identifiers
- references existing capabilities
- references existing skills when using skill composition
- uses valid dataflow references (`inputs.*`, `vars.*`, `outputs.*`)
- does not attempt to write to `inputs`
- produces all declared outputs
- does not write the same target multiple times
- matches the expected repository path

---

# Dataflow Validation

The validator checks that step inputs and outputs follow the defined dataflow model.

Allowed reference forms:

```
inputs.*
vars.*
outputs.*
```

Rules enforced:

- steps may read from `inputs`, `vars`, or `outputs`
- steps may only write to `vars` or `outputs`
- declared outputs must be produced by at least one step
- references must point to existing data fields

---

# What the Validator Does NOT Check

The validator does **not**:

- execute capabilities
- execute skills
- validate runtime implementations
- resolve providers or tool bindings
- evaluate output correctness

Its purpose is strictly to validate the **structure and consistency of the registry**.

---

# Exit Codes

The validator returns standard exit codes:

```
0  validation passed
1  validation failed
```

This behavior allows the tool to be integrated with automated CI pipelines.

---

# Future Tooling

Additional tooling may be added to the `tools/` directory.

Planned tools may include:

- catalog generation
- registry indexing
- documentation generation
- dependency visualization

These tools will also be documented in this file as they are introduced.