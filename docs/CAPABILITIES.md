# Capabilities

This document defines the structure and rules for **capabilities** in the Agent Skill Registry.

Capabilities represent **abstract functions** that can be used by skills.

They define **what can be done**, not **how it is implemented**.

Capabilities are **tool-agnostic** and describe only the interface between a workflow and an implementation.

---

# Core Concept

A capability defines a **contract** consisting of:

- identifier
- version
- description
- input schema
- output schema

Skills invoke capabilities through workflow steps.

Capabilities do not define runtime implementations.

---

# Capability File

Each capability is defined in a YAML file located in:

```
capabilities/
```

Example:

```
capabilities/text.summarize.yaml
```

---

# Minimal Capability Structure

```yaml
id: text.summarize
version: 1.0.0
description: Summarize a block of text.

inputs:
  text:
    type: string
    required: true

outputs:
  summary:
    type: string
    required: true
```

---

# Capability Fields

## id

Unique identifier of the capability.

Naming convention:

```
<domain>.<verb>
```

or when needed:

```
<domain>.<noun>.<verb>
```

Examples:

```
text.summarize
pdf.read
data.json.parse
```

Rules:

- id must be globally unique
- id must not include version information
- id must follow the domain and verb conventions

---

## version

Semantic version of the capability.

Examples:

```
1.0.0
1.2.0
2.0.0
```

Version is independent from the identifier.

Breaking interface changes require a major version increase.

---

## description

Short explanation of what the capability does.

---

# Inputs

Inputs define the parameters required by the capability.

Example:

```yaml
inputs:
  text:
    type: string
    required: true
```

Each input field may define:

```
type
required
description
```

Example:

```yaml
inputs:
  text:
    type: string
    required: true
    description: Text to summarize
```

---

# Outputs

Outputs define the results returned by the capability.

Example:

```yaml
outputs:
  summary:
    type: string
    required: true
```

Each output field may define:

```
type
required
description
```

---

# Properties (Optional)

Capabilities may define execution characteristics.

Example:

```yaml
properties:
  deterministic: true
  side_effects: false
  idempotent: true
```

Properties allow runtimes to reason about execution behavior.

Available properties:

```
deterministic
side_effects
idempotent
```

---

# Dependencies (Optional)

Capabilities may declare dependencies on other capabilities.

Example:

```yaml
requires:
  - fs.read
```

Dependencies indicate that an implementation of this capability may require other capabilities to function.

Dependencies are used for discovery and planning.

---

# Deprecation (Optional)

Capabilities may be marked as deprecated.

Example:

```yaml
deprecated: true
replacement: text.extract
```

Deprecation indicates that a capability should no longer be used for new skills.

Existing skills may continue to function.

---

# Aliases (Optional)

Capabilities may define aliases for backwards compatibility.

Example:

```yaml
aliases:
  - text.summarise
```

Aliases allow migration from older identifiers.

---

# Examples (Optional)

Capabilities may include usage examples.

Example:

```yaml
examples:
  - description: Summarize a paragraph
    input:
      text: "Long article text..."
    output:
      summary: "Short summary..."
```

Examples help contributors understand how the capability is intended to be used.

---

# Design Principles

Capabilities follow these principles:

- tool-agnostic
- stable interface contracts
- reusable across environments
- independent from runtime implementations

Capabilities describe **what can be done**, not **how it is executed**.