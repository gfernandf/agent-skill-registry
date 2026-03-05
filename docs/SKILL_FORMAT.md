# Skill format specification (v0.1)

This document defines the structure of a skill definition.

Skills describe executable workflows using capabilities.

A skill is a declarative specification and does not bind to specific tools or providers.

---

# Core concepts

A skill consists of:

- metadata
- inputs
- outputs
- steps

Steps form a dataflow graph where outputs of one step can feed inputs of another.

---

# Dataflow model

The system uses explicit dataflow.

Data can move through three namespaces:

inputs  
External values provided when the skill is executed.

vars  
Intermediate values produced by steps.

outputs  
Final results exposed by the skill.

The `vars` namespace is reserved for intermediate values produced by steps.  
Users cannot directly populate `vars` when invoking a skill.

---

# Skill structure

Example minimal skill:

```yaml
name: hello-world
version: 0.1.0
description: Minimal example skill.

inputs:
  name:
    type: string

outputs:
  greeting:
    type: string

steps:
  - id: render
    uses: text.template

    input:
      template: "Hello {{name}}"
      variables:
        name: inputs.name

    output:
      text: outputs.greeting