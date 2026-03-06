# Skill Format

This document defines the structure and rules for **skills** in the Agent Skill Registry.

A skill describes a reusable workflow that composes one or more **capabilities** to perform a task.

Skills are **declarative** and describe a **dataflow graph** where data moves through steps until final outputs are produced.

---

# Core Concept

A skill defines:

- metadata
- inputs
- outputs
- steps

Steps invoke **capabilities** or other **skills**.

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
name: text.hello-world
version: 0.1.0
description: Minimal example skill.

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

## name

Unique identifier of the skill.

Naming convention:

```
domain.skill-name
```

Examples:

```
text.hello-world
pdf.batch-summarize
```

The skill name should match its repository location.

Example:

```
skills/official/text/hello-world/skill.yaml
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

## description

Short explanation of what the skill does.

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

Each step invokes a **capability** or another **skill**.

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

## Step Fields

### id

Unique identifier of the step within the skill.

---

### uses

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

Skill composition is an optional extension and may not be supported by all runtimes.

---

### input

Mapping of parameters passed to the capability.

Values reference the dataflow namespaces.

Example:

```yaml
input:
  text: vars.document_text
  language: inputs.language
```

---

### output

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