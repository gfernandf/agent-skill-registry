# Capabilities

Capabilities define the **primitive operations** available in the Agent Skill Registry.

They represent reusable functional building blocks that can be composed into workflows using skills.

Capabilities form the **core language of the registry** and are therefore governed by a controlled vocabulary.

---

# Purpose

A capability represents a **single functional operation** that can be reused across many workflows.

Examples include:

```
text.summarize
text.classify
text.keyword.extract
web.fetch
data.json.parse
fs.read
```

Capabilities should be:

- reusable
- composable
- predictable
- domain-independent when possible

Skills combine capabilities into higher-level workflows.

---

# Capability Identifier

Each capability is identified by an **ID**.

Allowed forms:

```
domain.verb
domain.noun.verb
```

Examples:

```
text.summarize
fs.read
web.fetch
data.json.parse
text.keyword.extract
web.page.fetch
```

The maximum number of identifier segments is **three**.

Invalid examples:

```
data.json.schema.validate
web.page.article.extract
text.entity.named.extract
```

Capability identifiers must conform to the **controlled vocabulary** defined in:

```
vocabulary/vocabulary.json
```

Human-readable guidance is provided in:

```
docs/VOCABULARY.md
```

---

# File Location

Capabilities are stored as individual YAML files.

```
capabilities/<capability-id>.yaml
```

Examples:

```
capabilities/text.summarize.yaml
capabilities/text.keyword.extract.yaml
capabilities/data.json.parse.yaml
capabilities/web.fetch.yaml
```

The filename must match the capability ID.

---

# Capability Format

A capability file is written in YAML and follows a defined structure.

Example:

```yaml
id: text.summarize
version: 1.0.0
description: Produce a concise summary of text content.

inputs:
  text:
    type: string
    required: true
    description: Text to summarize.

outputs:
  summary:
    type: string
    required: true
    description: Generated summary.

properties:
  deterministic: false
  side_effects: false
  idempotent: true
```

---

# Required Fields

## id

Unique identifier of the capability.

Must follow the allowed identifier structure and vocabulary rules.

Example:

```
text.summarize
data.json.parse
text.keyword.extract
```

---

## version

Version of the capability definition.

Example:

```
1.0.0
```

Versioning allows capability definitions to evolve while preserving compatibility.

---

## description

Human-readable description of the capability's purpose.

This should explain what the capability does and when it should be used.

---

## inputs

Defines the inputs required by the capability.

Each input must specify:

- type
- whether it is required
- optional description

Example:

```
inputs:
  text:
    type: string
    required: true
```

---

## outputs

Defines the outputs produced by the capability.

Each output must specify:

- type
- whether it is required
- optional description

Example:

```
outputs:
  summary:
    type: string
    required: true
```

---

# Optional Fields

## metadata (Optional)

Capabilities may optionally include a `metadata` block used for discovery, categorization, and documentation.

Example:

```yaml
metadata:
  tags:
    - text
    - analysis
  category: analysis
  status: stable
  examples:
    - description: Classify an input text
      input:
        text: "I want a refund"
        labels: ["billing", "refund", "technical"]
      output:
        label: "refund"
```

The `metadata` block is optional and does not change the functional meaning of the capability.

If omitted, tools may treat it as an empty/default metadata block.

### Suggested Fields

The following optional fields may appear inside `metadata`:

- `tags`
- `category`
- `status`
- `examples`

### Logical Defaults

If metadata is omitted, tools may interpret it as:

```yaml
metadata:
  tags: []
  category: null
  status: unspecified
  examples: []
```

These defaults are conceptual and do not need to be materialized in source YAML.

### Intended Purpose

Capability metadata is intended to support:

- discovery
- categorization
- registry browsing
- documentation
- future statistics and analytics

It is not intended to change execution behavior.

### Deprecation Lifecycle Metadata

When `metadata.status` is set to `deprecated`, lifecycle dates are required by
policy:

- `metadata.deprecation_date` (YYYY-MM-DD)
- `metadata.sunset_date` (YYYY-MM-DD)

Deprecated capabilities must also define top-level `replacement`.

See:

- `docs/CAPABILITY_SUNSET_POLICY.md`

---

## properties

Capabilities may declare execution properties.

Example:

```
properties:
  deterministic: false
  side_effects: false
  idempotent: true
```

### deterministic

Whether the capability always produces the same output for the same input.

Examples:

- `true` for deterministic parsing
- `false` for LLM-based summarization

---

### side_effects

Whether the capability produces side effects.

Examples:

- writing to a file
- modifying a database
- sending a request

Capabilities without side effects are easier to compose safely.

---

### idempotent

Whether repeated execution with the same input produces the same result without additional effects.

---

# Design Principles

Capabilities should follow these principles:

### Single Responsibility

A capability should perform **one clear operation**.

Good example:

```
text.summarize
```

Poor example:

```
text.extract-and-summarize
```

That logic should be expressed as a **skill**.

---

### Reusability

Capabilities should be designed to be reused across many workflows.

Avoid overly specific capabilities.

Example:

Prefer:

```
text.classify
```

Over:

```
text.sentiment.classify
```

unless the distinction is meaningful.

---

### Vocabulary Consistency

Capability identifiers must use the controlled vocabulary defined in:

```
vocabulary/vocabulary.json
```

This ensures:

- consistent naming
- predictable discovery
- long-term ecosystem stability

---

# Relationship to Skills

Capabilities are invoked from skills.

Example step in a skill:

```
uses: text.summarize
```

Skills may also compose other skills:

```
uses: skill:text.simple-summarize
```

Capabilities therefore represent the **primitive operations**, while skills define workflows.

---

# Validation

Capabilities are validated automatically using the registry validator.

The validator checks:

- YAML structure
- required fields
- identifier format
- controlled vocabulary compliance
- reference consistency

Validation is performed using:

```
tools/validate_registry.py
```

If validation fails, the capability cannot be merged into the registry.

---

# Evolution of Capabilities

Capabilities may evolve over time.

Possible changes include:

- improvements to descriptions
- additional optional inputs
- improved metadata

Breaking changes should be avoided unless the capability version is incremented appropriately.

---

# Summary

Capabilities are the **foundation of the registry language**.

They define the reusable operations from which all skills are composed.

By enforcing:

- a controlled vocabulary
- strict identifier rules
- validation tooling

the registry ensures a consistent and scalable ecosystem of reusable workflows.