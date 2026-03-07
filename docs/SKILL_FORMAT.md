# Skill Format

This document defines the structure and rules for **skills** in the Agent Skill Registry.

A skill describes a reusable workflow that composes one or more **capabilities** to perform a task.

Skills are **declarative** and describe a **dataflow graph** where data moves through steps until final outputs are produced.

---

# Core Concept

A skill defines:

- identifier
- metadata
- inputs
- outputs
- steps

Steps invoke **capabilities** or optionally other **skills**.

Skills do not define runtime implementations.

They only define **how capabilities are composed**.

---

# Skill File

Each skill is defined in a file named:

```
skill.yaml
```

Example location:

```
skills/official/text/hello-world/skill.yaml
```

---

# Minimal Skill Structure

```yaml
id: text.hello-world
version: 0.1.0
name: Hello World
description: Minimal example skill demonstrating template rendering.

inputs:
  name:
    type: string
    required: true

outputs:
  greeting:
    type: string
    required: true

steps:
  - id: render
    uses: text.template
    input:
      template: "Hello {{name}}"
      variables:
        name: inputs.name
    output:
      text: outputs.greeting
```

---

# Skill Fields

## id

Canonical identifier of the skill.

Naming convention:

```
domain.skill-name
```

Examples:

```
text.hello-world
pdf.batch-summarize
```

Rules:

- id must be globally unique
- id must follow the domain naming conventions
- id must not include version information

The identifier must match the repository path.

Example:

```
skills/official/text/hello-world/skill.yaml
```

→ expected id:

```
text.hello-world
```

---

## version

Semantic version of the skill.

Examples:

```
0.1.0
1.0.0
```

---

## name

Human-readable name of the skill.

Examples:

```
Hello World
Batch PDF Summarization
```

Rules:

- name is descriptive only
- name is not used as an identifier
- name does not participate in references between skills

---

## description

Short explanation of what the skill does.

---

## metadata (Optional)

Skills may optionally include a `metadata` block used for discovery, categorization, and documentation.

Example:

```yaml
metadata:
  tags:
    - web
    - summarization
  category: content-processing
  status: stable
  use_cases:
    - Summarize a web page from a URL
  examples:
    - description: Summarize an article
      input:
        url: "https://example.com/article"
      output:
        summary: "Short summary..."
```

The `metadata` block is optional and does not affect workflow execution semantics.

If omitted, tools may treat it as an empty/default metadata block.

### Suggested Fields

The following optional fields may appear inside `metadata`:

- `tags`
- `category`
- `status`
- `use_cases`
- `examples`

### Logical Defaults

If metadata is omitted, tools may interpret it as:

```yaml
metadata:
  tags: []
  category: null
  status: unspecified
  use_cases: []
  examples: []
```

These defaults are conceptual and do not need to be materialized in source YAML.

### Intended Purpose

Skill metadata is intended to support:

- discovery
- categorization
- registry browsing
- documentation
- future statistics and analytics

It is not intended to change the meaning of the workflow itself.

---

# Dataflow Model

Skills use an **explicit dataflow model**.

Data flows through three namespaces:

```
inputs
vars
outputs
```

---

## inputs

Parameters provided when the skill is invoked.

Example:

```yaml
inputs:
  file_path:
    type: string
    required: true
```

Rules:

- inputs are provided by the caller
- inputs cannot be modified by steps

---

## vars

Intermediate values produced by steps.

Examples:

```
vars.document_text
vars.summary
```

Rules:

- vars are created by steps
- vars cannot be provided by the user
- vars may be consumed by later steps

---

## outputs

Final results returned by the skill.

Example:

```yaml
outputs:
  summary:
    type: string
    required: true
```

Rules:

- outputs must be declared in the skill
- outputs must be produced by at least one step

---

# Steps

Steps define the workflow execution graph.

Each step invokes a **capability** or optionally another **skill**.

Minimal step structure:

```yaml
- id: step-id
  uses: capability.name
  input:
    parameter: source
  output:
    field: target
```

---

# Step Fields

## id

Unique identifier of the step within the skill.

Rules:

- must be unique inside the skill

---

## uses

Reference to the capability or skill executed by the step.

Examples:

```
uses: text.template
uses: pdf.read
```

Optional skill composition:

```
uses: skill:text.normalize
```

Skill composition is optional and may not be supported by all runtimes.

---

## input

Mapping of parameters passed to the capability.

Values reference the dataflow namespaces.

Example:

```yaml
input:
  text: vars.document_text
  language: inputs.language
```

---

## output

Mapping of values produced by the step.

Targets must reference either:

```
vars.*
outputs.*
```

Example:

```yaml
output:
  summary: outputs.summary
```

---

# Valid References

Skills support only the following reference forms:

```
inputs.*
vars.*
outputs.*
```

Examples:

```
inputs.file_path
vars.document_text
outputs.summary
```

---

# Dataflow Rules

The following rules apply:

1. Steps cannot modify `inputs`.
2. Steps may write only to `vars` or `outputs`.
3. Each target field should be written once.
4. Outputs declared in the skill must be produced by a step.
5. Steps may consume values produced by earlier steps.

Execution order is determined by **data dependencies**.

---

# Execution Model

The skill specification defines **data dependencies**, not execution order.

Runtimes determine the execution order by resolving dependencies between steps.

Steps may execute in parallel when dependencies allow.

---

# Skill Composition (Optional)

Steps may reference other skills.

Example:

```
uses: skill:text.normalize
```

This enables larger workflows to be composed from smaller skills.

Skill composition support depends on the runtime implementation.

---

# Design Principles

Skills follow these principles:

- declarative workflow definition
- explicit dataflow
- separation from runtime implementations
- composability
- portability

Skills describe **how tasks are solved**, not **how they are executed internally**.