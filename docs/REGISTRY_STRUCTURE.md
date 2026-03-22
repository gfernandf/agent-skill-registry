# Registry Structure

This document describes the directory structure of the **Agent Skill Registry** and the role of each component.

The registry is designed to provide a structured, versioned environment for defining:

- **capabilities** (reusable functional primitives)
- **skills** (composed workflows built from capabilities)

It also includes tooling and generated catalogs to support validation and discovery.

---

# Repository Layout

The repository is organized as follows:

```
agent-skill-registry/

capabilities/
  *.yaml

skills/
  official/
  community/
  experimental/

catalog/

vocabulary/
  vocabulary.json

tools/

docs/
```

Each of these components serves a specific purpose in the registry.

---

# Capabilities

```
capabilities/
  <capability-id>.yaml
```

Capabilities define **reusable functional operations** that skills can invoke.

Each capability is stored as an individual YAML file.

Example:

```
capabilities/text.content.summarize.yaml
capabilities/text.keyword.extract.yaml
capabilities/data.json.parse.yaml
```

Capabilities represent the **core vocabulary of the registry** and must follow the controlled vocabulary rules.

The identifier must follow one of the allowed forms:

```
domain.verb
domain.noun.verb
```

Examples:

```
text.content.summarize
text.keyword.extract
web.page.fetch
data.json.parse
```

Capability identifiers are validated against the controlled vocabulary defined in:

```
vocabulary/vocabulary.json
```

---

# Skills

```
skills/<channel>/<domain>/<skill-name>/skill.yaml
```

Skills define **workflows that compose capabilities** into higher-level operations.

Example:

```
skills/
  official/
    text/
      simple-summarize/
        skill.yaml
```

A skill may call:

- capabilities
- other skills

via the `uses` field.

Example step:

```
uses: text.content.summarize
```

or

```
uses: skill:text.simple-summarize
```

Skills are grouped by **channel** and **domain**.

---

# Channels

Skills are organized into channels that reflect stability and governance level.

## official

```
skills/official/
```

Maintained by the core maintainers.

Characteristics:

- stable
- reviewed
- recommended for production use

---

## community

```
skills/community/
```

Community-contributed skills.

Characteristics:

- open contributions
- validated automatically
- maintained on a best-effort basis

---

## experimental

```
skills/experimental/
```

Used for early ideas and evolving workflows.

Characteristics:

- unstable
- breaking changes allowed
- rapid iteration

---

# Vocabulary

```
vocabulary/vocabulary.json
```

Defines the **controlled vocabulary** used by capability identifiers.

The vocabulary contains:

- domains
- nouns
- verbs
- composition rules

Example sections:

```
domains
nouns
verbs
rules
```

The vocabulary is the **source of truth** used by validation and tooling.

Human-readable documentation of the vocabulary is provided in:

```
docs/VOCABULARY.md
```

---

# Catalog

```
catalog/
```

Contains generated indexes of registry content.

These files are produced automatically by tooling and should not be edited manually.

Typical outputs include:

```
catalog/capabilities.json
catalog/skills.json
```

These catalogs allow tools, agents, or external systems to:

- discover available capabilities
- discover available skills
- analyze dependencies

The catalog is regenerated using tooling.

---

# Tooling

```
tools/
```

Contains scripts used to maintain and validate the registry.

Examples include:

```
tools/validate_registry.py
tools/generate_catalog.py
tools/create_skill.py
tools/create_capability.py
```

These tools support tasks such as:

- validating registry consistency
- enforcing vocabulary rules
- generating catalogs
- scaffolding new capabilities and skills

---

# Documentation

```
docs/
```

Contains explanatory documentation describing the registry design.

Key documents include:

```
CAPABILITIES.md
SKILL_FORMAT.md
REGISTRY_STRUCTURE.md
VOCABULARY.md
GOVERNANCE.md
```

These documents explain the design principles, formats, and governance rules used in the registry.

---

# Design Philosophy

The registry structure follows several principles:

- **clarity** — simple and predictable directory layout
- **discoverability** — content easily browsed and indexed
- **validation** — automated consistency checks
- **controlled vocabulary** — stable naming of capabilities
- **composability** — skills can build on other capabilities or skills

This structure supports long-term growth of the ecosystem while maintaining consistency and readability.