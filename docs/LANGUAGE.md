# Registry Language

The Agent Skill Registry uses YAML as a serialization format, but the
actual meaning of files is defined by a **registry-specific declarative
language**.

This document describes that language.

------------------------------------------------------------------------

# YAML as a Container

YAML is used only as a structured representation.

The registry defines the semantics.

Files represent one of two constructs:

-   **Capability definitions**
-   **Skill definitions**

------------------------------------------------------------------------

# Capability Definition Language

Capabilities describe **primitive operations**.

They define:

-   identity
-   inputs
-   outputs
-   execution properties
-   metadata

Example:

``` yaml
id: text.content.summarize
version: 0.1.0

description: Generate a summary from text.

inputs:
  text:
    type: string
    required: true

outputs:
  summary:
    type: string
    required: true
```

Capabilities are **contracts**, not implementations.

They define **what a runtime must implement**, not how.

------------------------------------------------------------------------

# Skill Definition Language

Skills describe **workflows composed of capabilities**.

Example:

``` yaml
id: web.fetch-summary

inputs:
  url:
    type: string
    required: true

outputs:
  summary:
    type: string
    required: true
```

Skills contain **steps**.

Each step executes either:

-   a **capability**
-   another **skill**

------------------------------------------------------------------------

# Steps

Steps define execution nodes.

Example:

``` yaml
steps:

  - id: fetch
    uses: web.page.fetch

  - id: summarize
    uses: text.content.summarize
```

Each step defines:

-   `id`
-   `uses`
-   `input`
-   `output`

------------------------------------------------------------------------

# Reference Syntax

The registry language supports references between values.

Supported reference types (legacy):

    inputs.<field>
    vars.<field>
    outputs.<field>

CognitiveState v1 reference types (runtime extension):

    frame.<path>
    working.<path>
    output.<path>
    extensions.<path>

CognitiveState v1 namespaces are supported by the `agent-skills` runtime.
They provide structured cognitive processing for multi-step reasoning skills.
Legacy references remain the default and work in all runtimes.

Path traversal supports nested access (dict keys, list indices):

    frame.constraints.budget
    working.entities.0.name

Examples:

    inputs.url
    vars.text
    outputs.summary
    frame.goal
    working.artifacts.draft

------------------------------------------------------------------------

# Dataflow Model

Skills follow a **dataflow execution model**.

    inputs → steps → outputs

Data may flow through:

-   `inputs`
-   `vars`
-   `outputs`

CognitiveState v1 adds four additional namespaces (runtime extension):

-   `frame` (read-only reasoning context)
-   `working` (mutable cognitive working memory)
-   `output` (structured result metadata)
-   `extensions` (open namespace for plugins)

### Inputs

Provided by the caller.

### Vars

Intermediate step outputs.

### Outputs

Final results returned by the skill.

------------------------------------------------------------------------

# Skill Composition

Skills may call other skills.

Example:

    uses: skill:text.simple-summarize

This allows building complex workflows from reusable components.

------------------------------------------------------------------------

# Capability References

Capabilities are referenced by identifier.

Example:

    uses: text.content.summarize

The runtime resolves the capability implementation.

------------------------------------------------------------------------

# Execution Semantics

The registry does not define a runtime.

Execution is expected to follow:

1.  load skill
2.  resolve step dependencies
3.  invoke capabilities
4.  propagate outputs

Actual implementations may vary.

------------------------------------------------------------------------

# Determinism and Properties

Capabilities may declare properties:

-   deterministic
-   side_effects
-   idempotent

These properties help runtimes make execution decisions.

------------------------------------------------------------------------

# Grammar Summary

Simplified reference grammar:

    reference := inputs.field | vars.field | outputs.field

CognitiveState v1 extended grammar (runtime extension):

    reference := inputs.field | vars.field | outputs.field
               | frame.path | working.path | output.path | extensions.path

Capability identifier grammar:

    domain.noun.verb

Examples:

    text.keyword.extract
    image.caption.generate
    data.schema.validate

------------------------------------------------------------------------

# Extensibility

The language is designed to evolve.

Future versions may introduce:

-   conditional steps
-   parallel execution
-   policies
-   retries
-   caching

The current version focuses on **simple composable workflows**.
