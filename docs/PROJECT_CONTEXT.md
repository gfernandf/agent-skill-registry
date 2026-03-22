# Project Context

The Agent Skill Registry provides a structured environment for defining, sharing, and discovering reusable **agent workflows**.

The project separates two fundamental concepts:

- **Capabilities** — primitive functional operations
- **Skills** — workflows that compose capabilities

This separation allows the ecosystem to evolve in a modular and scalable way.

---

# Problem Statement

Modern AI systems often rely on complex workflows composed of many operations such as:

- retrieving data
- processing text
- transforming structured information
- interacting with external resources

Without a shared framework, these workflows become:

- inconsistent
- difficult to reuse
- hard to discover
- difficult to maintain

The Agent Skill Registry addresses this by providing:

- a **standard vocabulary for capabilities**
- a **structured format for workflows**
- **validation tooling**
- **discoverable catalogs**

---

# Key Concepts

## Capabilities

Capabilities represent **primitive operations** that can be reused across workflows.

Examples:

```
text.content.summarize
text.content.classify
text.keyword.extract
data.json.parse
web.page.fetch
fs.file.read
```

Capabilities are defined in:

```
capabilities/<capability-id>.yaml
```

They follow strict naming rules enforced by a controlled vocabulary.

---

## Skills

Skills represent **workflows composed from capabilities**.

A skill may invoke:

- one or more capabilities
- other skills

Skills are defined in:

```
skills/<channel>/<domain>/<skill-name>/skill.yaml
```

Example workflow:

```
web.fetch-summary

web.page.fetch
→ text.content.extract
→ text.content.summarize
```

---

# Controlled Vocabulary

Capability identifiers are governed by a **controlled vocabulary**.

The authoritative vocabulary is defined in:

```
vocabulary/vocabulary.json
```

This vocabulary defines:

- domains
- nouns
- verbs
- identifier composition rules

Examples of valid identifiers:

```
text.content.summarize
data.json.parse
text.keyword.extract
web.page.fetch
```

Human-readable documentation is available in:

```
docs/VOCABULARY.md
```

---

# Registry Structure

The registry is organized into several components.

```
capabilities/
skills/
catalog/
vocabulary/
tools/
docs/
```

Each component plays a specific role in defining, validating, and discovering workflows.

---

# Validation

All registry content is validated automatically using:

```
tools/validate_registry.py
```

Validation ensures:

- correct YAML structure
- valid capability identifiers
- controlled vocabulary compliance
- valid skill references
- workflow consistency

This guarantees that the registry remains internally coherent.

---

# Catalog Generation

Machine-readable catalogs are generated automatically:

```
catalog/capabilities.json
catalog/skills.json
```

These catalogs allow tools, agents, and external systems to discover available functionality.

Catalogs are generated using:

```
tools/generate_catalog.py
```

---

# Contribution Model

The registry supports contributions from both maintainers and the community.

Skills are organized into channels that reflect stability:

```
official
community
experimental
```

Capabilities are more strictly governed because they define the shared vocabulary of the ecosystem.

---

# Project Goals

The registry aims to provide:

- a **shared language for agent workflows**
- reusable functional primitives
- composable workflow definitions
- machine-readable catalogs
- strong validation guarantees

This foundation enables a growing ecosystem of reusable workflows that remain consistent and discoverable over time.