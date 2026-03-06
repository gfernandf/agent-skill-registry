# Tooling

This document describes the internal tools used to maintain the integrity and usability of the **Agent Skill Registry**.

The registry contains structured definitions of:

- capabilities
- skills

To ensure the registry remains consistent and easy to consume, the repository includes a small set of tooling scripts located in:

```
tools/
```

These tools validate the registry and generate derived artifacts used for discovery and indexing.

---

# Registry Validator

File:

```
tools/validate_registry.py
```

The registry validator verifies that all **skills** and **capabilities** follow the specification and remain internally consistent.

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
- uses supported execution properties
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

This allows the tool to be integrated with CI pipelines.

---

# Catalog Generator

File:

```
tools/generate_catalog.py
```

The catalog generator produces **derived index files** that describe the contents of the registry.

These files provide a machine-readable overview of all capabilities and skills.

The catalog is generated from the YAML definitions in the repository.

---

# Generated Files

The generator produces the following files:

```
catalog/capabilities.json
catalog/skills.json
```

These files are **derived artifacts** and represent a snapshot of the current registry.

They are regenerated whenever the registry changes.

---

# Usage

From the root of the repository:

```bash
python tools/generate_catalog.py
```

The script will:

1. discover all capabilities and skills
2. extract relevant metadata
3. generate deterministic JSON indexes
4. overwrite the catalog files

Example output:

```
CATALOG GENERATED
Capabilities: 4
Skills: 1
Written:
- catalog/capabilities.json
- catalog/skills.json
```

---

# Catalog Design

The catalog is intentionally simple and static.

Key design principles:

- the catalog is **derived from source definitions**
- it is **fully regenerated each time**
- it is **deterministic and sorted**
- it is **versioned with the repository**

This ensures that the catalog always reflects the current state of the registry.

---

# Why the Catalog Is Regenerated

The catalog is rebuilt from scratch instead of updated incrementally.

This approach guarantees:

- consistency with the source YAML files
- no stale entries after renames or deletions
- deterministic output
- simpler tooling logic

Even for large registries, regenerating the catalog remains inexpensive.

---

# Catalog Consumers

The catalog enables external tools and systems to easily consume the registry.

Examples:

- skill discovery tools
- documentation generators
- registry browsers
- agent runtimes
- future web interfaces

Because the catalog is static JSON, it can be consumed directly from the repository.

---

# Future Tooling

Additional tools may be added to the `tools/` directory in the future.

Possible extensions include:

- dependency visualization
- registry documentation generators
- schema validation tools
- CLI helpers for skill creation
- registry statistics

All future tools will be documented in this file.