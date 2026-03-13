# Tooling

This document describes the internal tools used to maintain the integrity and usability of the **Agent Skill Registry**.

The registry contains structured definitions of:

- capabilities
- skills

To ensure the registry remains consistent and easy to consume, the repository includes a small set of tooling scripts located in:

```
tools/
```

These tools validate the registry, scaffold new artifacts, and generate derived catalogs used for discovery and indexing.

Governance-specific guardrails are also available to detect overlap and
metadata quality issues for skills.

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
- matches the controlled vocabulary
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

# Vocabulary Validation

Capability identifiers are validated against the controlled vocabulary defined in:

```
vocabulary/vocabulary.json
```

This includes validation of:

- domains
- nouns
- verbs
- allowed identifier structure

The validator enforces the allowed identifier forms:

```
domain.verb
domain.noun.verb
```

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
catalog/graph.json
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
Capabilities: 7
Skills: 4
Written:
- catalog/capabilities.json
- catalog/skills.json
- catalog/graph.json
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

# Graph Generation

The catalog generator also produces a dependency graph describing how skills depend on capabilities and other skills.

Output file:

```
catalog/graph.json
```

The graph contains the dependencies of each skill.

Example:

```json
{
  "skills": {
    "web.fetch-summary": {
      "capabilities": [
        "web.fetch",
        "text.extract",
        "text.summarize"
      ],
      "skills": []
    }
  }
}
```

Two dependency types are tracked:

- **capabilities** — capabilities used by the skill
- **skills** — other skills invoked by the skill

Dependencies are extracted from the `uses` field of each step.

---

# Governance Guardrails

File:

```
tools/governance_guardrails.py
```

This script analyzes generated catalogs and produces a governance report with:

- skills missing governance-oriented metadata
- high-overlap skill pairs (possible duplication)
- unknown capability references in skill dependency lists

Default output:

```
catalog/governance_guardrails.json
```

Usage:

```bash
python tools/governance_guardrails.py
```

Useful options:

```bash
python tools/governance_guardrails.py --overlap-threshold 0.85
python tools/governance_guardrails.py --fail-on-overlap
```

This tool is intended as an anti-proliferation signal and complements
`tools/validate_registry.py`.

Example step:

```
uses: text.summarize
```

or

```
uses: skill:text.simple-summarize
```

The graph allows tools and agents to:

- analyze registry structure
- detect commonly used capabilities
- visualize workflow dependencies
- discover reusable components

The graph is generated automatically by:

```
tools/generate_catalog.py
```

and should not be edited manually.

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

# Skill Creation Tool

File:

```
tools/create_skill.py
```

This tool generates a new skill skeleton following the repository structure.

It simplifies the process of adding new skills to the registry and ensures that the correct directory layout and identifiers are used.

---

# Usage

From the root of the repository:

```bash
python tools/create_skill.py --channel <channel> --domain <domain> --slug <slug>
```

Example:

```bash
python tools/create_skill.py --channel official --domain text --slug simple-summarize
```

This will generate:

```
skills/official/text/simple-summarize/skill.yaml
```

---

# Parameters

| Parameter | Description |
|----------|-------------|
| `--channel` | Registry channel (e.g. `official`, `community`, `experimental`) |
| `--domain` | Skill domain (e.g. `text`, `web`, `data`) |
| `--slug` | Skill name used in the path |

The canonical skill identifier is generated automatically:

```
id = <domain>.<slug>
```

Example:

```
text.simple-summarize
```

---

# Generated Skill Template

The tool creates a minimal skill definition:

```yaml
id: text.simple-summarize
version: 0.1.0
name: Simple Summarize
description: Describe what this skill does.

inputs: {}

outputs: {}

steps: []
```

The user should edit this file to define:

- inputs
- outputs
- workflow steps

---

# Typical Contribution Workflow for Skills

1. Create a skill skeleton:

```
python tools/create_skill.py --channel community --domain text --slug my-skill
```

2. Edit the generated `skill.yaml`.

3. Validate the registry:

```
python tools/validate_registry.py
```

4. Regenerate the catalog:

```
python tools/generate_catalog.py
```

5. Commit and submit a pull request.

---

# Safety Behavior for Skill Creation

The tool will **not overwrite existing skills**.

If the destination file already exists, the command will fail to prevent accidental data loss.

---

# Capability Creation Tool

File:

```
tools/create_capability.py
```

This tool generates a new capability skeleton following the repository conventions and controlled vocabulary model.

It supports the two allowed capability identifier forms:

```
domain.verb
domain.noun.verb
```

---

# Usage

Create a capability without noun:

```bash
python tools/create_capability.py --domain text --verb summarize
```

This will generate:

```
capabilities/text.summarize.yaml
```

Create a capability with noun:

```bash
python tools/create_capability.py --domain data --noun json --verb parse
```

This will generate:

```
capabilities/data.json.parse.yaml
```

---

# Parameters

| Parameter | Description |
|----------|-------------|
| `--domain` | Capability domain (e.g. `text`, `web`, `data`) |
| `--verb` | Capability verb (e.g. `summarize`, `fetch`, `parse`) |
| `--noun` | Optional noun used in the `domain.noun.verb` form |

The canonical capability identifier is generated automatically.

Examples:

```
text.summarize
data.json.parse
text.keyword.extract
```

---

# Vocabulary Enforcement in Capability Creation

Capability creation is governed by the controlled vocabulary defined in:

```
vocabulary/vocabulary.json
```

The capability creation process should respect the same naming model enforced by the validator:

- allowed domains
- allowed nouns
- allowed verbs
- allowed identifier structure

This helps preserve consistency in the registry core language.

---

# Generated Capability Template

The tool creates a minimal capability definition:

```yaml
id: text.classify
version: 1.0.0
description: Describe what this capability does.

inputs: {}

outputs: {}

properties:
  deterministic: true
  side_effects: false
  idempotent: true
```

The user should edit this file to define:

- description
- inputs
- outputs
- execution properties when needed

---

# Typical Contribution Workflow for Capabilities

1. Create a capability skeleton:

```
python tools/create_capability.py --domain text --verb classify
```

or:

```
python tools/create_capability.py --domain text --noun keyword --verb extract
```

2. Edit the generated capability YAML.

3. Validate the registry:

```
python tools/validate_registry.py
```

4. Regenerate the catalog:

```
python tools/generate_catalog.py
```

5. Commit and submit a pull request.

---

# Safety Behavior for Capability Creation

The tool will **not overwrite existing capabilities**.

If the destination file already exists, the command will fail to prevent accidental data loss.

---

# Future Tooling

Additional tools may be added to the `tools/` directory in the future.

Possible extensions include:

- dependency visualization
- registry documentation generators
- schema validation tools
- CLI helpers for registry maintenance
- registry statistics

All future tools will be documented in this file.