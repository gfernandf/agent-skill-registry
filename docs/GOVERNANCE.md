# Governance

This document defines the governance model for the **Agent Skill Registry**.

The goal of governance is to balance:

- openness to community contributions
- consistency of the registry
- long-term ecosystem stability

The registry distinguishes between two main artifact types:

- **capabilities** — reusable functional primitives
- **skills** — workflows that compose capabilities

Because capabilities define the **core language of the registry**, they are governed more strictly than skills.

---

# Governance Principles

The registry governance follows these principles:

### Stability of the Core Language

Capabilities define the vocabulary used by the ecosystem.

The registry therefore enforces:

- controlled vocabulary
- strict identifier rules
- automated validation

---

### Openness to Contributions

Community members are encouraged to contribute:

- new skills
- improvements to existing skills
- new capabilities when justified

All contributions are validated automatically.

---

### Predictable Evolution

Changes to the registry should prioritize:

- backward compatibility
- clarity of naming
- long-term maintainability

---

# Controlled Vocabulary

Capability identifiers must follow the **controlled vocabulary** defined in:

```
vocabulary/vocabulary.json
```

This vocabulary defines:

- allowed **domains**
- allowed **nouns**
- allowed **verbs**
- allowed identifier structures

Human-readable documentation is available in:

```
docs/VOCABULARY.md
```

The machine-readable JSON file is the **source of truth**.

---

# Capability Identifier Rules

Capabilities must follow one of the allowed identifier forms:

```
domain.verb
domain.noun.verb
```

Examples:

```
text.summarize
text.keyword.extract
data.json.parse
web.page.fetch
```

The maximum number of segments is **three**.

Identifiers that violate these rules will fail validation.

---

# Contribution Types

The registry accepts several types of contributions.

---

# Contributing Skills

Skills define workflows that compose capabilities.

They are stored in:

```
skills/<channel>/<domain>/<skill-name>/skill.yaml
```

Skills are relatively easy to contribute and primarily require:

- correct YAML structure
- valid references to capabilities or skills
- passing registry validation

Skills may be added to the:

```
community
experimental
```

channels by external contributors.

The `official` channel is typically curated by maintainers.

---

# Contributing Capabilities

Capabilities represent the **core operations of the registry**.

Because they affect the shared vocabulary, capability contributions are more strictly governed.

A new capability must:

- follow identifier rules
- use only allowed vocabulary terms
- provide a clear description
- define inputs and outputs
- pass validation

Capabilities must be stored as:

```
capabilities/<capability-id>.yaml
```

Example:

```
capabilities/text.summarize.yaml
capabilities/data.json.parse.yaml
```

---

# Proposing Vocabulary Changes

If a capability requires a **new domain, noun, or verb**, the contributor must update:

```
vocabulary/vocabulary.json
```

Vocabulary changes should include:

- the new term
- a short description of its meaning
- justification for why existing terms are insufficient

Because vocabulary changes affect the registry language, they may require stricter review.

---

# Validation

All contributions are automatically validated using:

```
tools/validate_registry.py
```

The validator checks:

- YAML structure
- required fields
- capability identifier structure
- controlled vocabulary compliance
- skill references
- dataflow structure

If validation fails, the contribution cannot be merged.

---

# Catalog Generation

Registry catalogs are generated automatically using:

```
tools/generate_catalog.py
```

Generated files include:

```
catalog/capabilities.json
catalog/skills.json
```

These catalogs provide machine-readable indexes of registry contents.

Catalog files should not be edited manually.

---

# Channels and Stability

Skills are organized into channels reflecting stability.

---

## official

```
skills/official/
```

Characteristics:

- maintained by core maintainers
- stable and curated
- recommended for production use

---

## community

```
skills/community/
```

Characteristics:

- community-contributed
- validated automatically
- maintained on a best-effort basis

---

## experimental

```
skills/experimental/
```

Characteristics:

- early prototypes
- unstable
- breaking changes allowed

Experimental skills allow rapid iteration without affecting stable workflows.

---

# Capability Stability

Capabilities should be relatively stable.

Once widely used, changes should avoid breaking existing skills.

If a capability requires significant redesign, consider introducing a **new capability identifier** instead of modifying the original.

---

# Deprecation

Capabilities or skills may be deprecated when:

- a better alternative exists
- the capability was poorly defined
- the functionality is no longer relevant

Deprecation should be documented and communicated clearly.

Existing references should continue to function whenever possible.

---

# Maintainers

Repository maintainers are responsible for:

- reviewing contributions
- preserving vocabulary coherence
- ensuring registry stability
- guiding the evolution of the ecosystem

Maintainers may request changes to contributions before merging.

---

# Summary

The governance model ensures that the registry remains:

- consistent
- extensible
- community-driven
- stable over time

By combining:

- controlled vocabulary
- automated validation
- structured contribution channels

the registry can grow while maintaining a coherent and reusable language for agent workflows.