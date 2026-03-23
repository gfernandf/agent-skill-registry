# Agent Skill Registry

An open registry of reusable **AI agent skills** and **capability
definitions**.

## Quick Start

```bash
pip install -r requirements.txt
python tools/validate_registry.py
python tools/generate_catalog.py
```

See the companion runtime at [agent-skills](https://github.com/gfernandf/agent-skills) for execution.

## License

Apache 2.0 — see [LICENSE](LICENSE).

---

The registry provides a standardized, declarative way to define:

-   primitive **capabilities**
-   composable **skills (workflows)**
-   shared **vocabulary**
-   machine-readable **catalogs**

It acts as the **source of truth for agent workflows** that can be
executed by compatible runtimes.

------------------------------------------------------------------------

# Why this exists

AI agents increasingly rely on structured tools and workflows.

However, most implementations today are:

-   tightly coupled to a specific framework
-   implemented imperatively in code
-   difficult to reuse across systems
-   inconsistent in naming and structure

The **Agent Skill Registry** addresses this by providing:

-   a **common vocabulary**
-   a **declarative workflow model**
-   a **shared registry of reusable skills**
-   a **machine-readable catalog for runtimes**

The goal is to make agent capabilities **discoverable, composable, and
reusable**.

------------------------------------------------------------------------

# Core Concepts

The registry defines two fundamental building blocks.

## Capabilities

Capabilities represent **primitive operations**.

They define a **contract** describing what an operation does, including:

-   inputs
-   outputs
-   execution properties
-   optional metadata

Examples:

text.content.summarize\
web.page.fetch\
pdf.document.read\
audio.speech.transcribe\
code.diff.extract

Capabilities are **not implementations**.

They define **what a runtime must implement**, not how.

------------------------------------------------------------------------

## Skills

Skills are **composable workflows** built from capabilities.

A skill defines:

-   inputs
-   outputs
-   steps
-   capability usage
-   optional nested skill usage

Example skill:

web.fetch-summary

Workflow:

web.page.fetch → web.page.extract → text.content.summarize

Skills allow building reusable agent behavior without writing imperative
code.

------------------------------------------------------------------------

# Registry Structure

agent-skill-registry\
│\
├─ capabilities/\
│ Capability definitions\
│\
├─ skills/\
│ Reusable workflows\
│\
├─ catalog/\
│ Generated machine-readable catalogs\
│\
├─ tools/\
│ Registry tooling\
│\
└─ docs/\
Specifications and language documentation

------------------------------------------------------------------------

# Vocabulary

The registry enforces a **controlled vocabulary** to maintain
consistency.

Capability identifiers follow the pattern:

domain.noun.verb

Examples:

text.keyword.extract\
image.caption.generate\
data.schema.validate\
code.diff.extract

The vocabulary is defined in:

vocabulary.json

This ensures:

-   consistent naming
-   predictable semantics
-   long-term maintainability

------------------------------------------------------------------------

# Skills as Dataflow

Skills are **declarative workflows**.

Each step references a capability or another skill.

Example:

steps:

-   id: fetch uses: web.page.fetch input: url: inputs.url output: content:
    vars.page

-   id: extract uses: web.page.extract input: content: vars.page output:
    text: vars.text

-   id: summarize uses: text.content.summarize input: text: vars.text output:
    summary: outputs.summary

Execution semantics:

inputs → steps → outputs

No imperative logic is embedded in the skill definition.

------------------------------------------------------------------------

# Generated Catalog

The registry generates machine-readable catalogs used by runtimes.

catalog/capabilities.json\
catalog/skills.json\
catalog/graph.json\
catalog/stats.json

These provide:

-   skill discovery
-   dependency graphs
-   usage statistics
-   capability relationships

Catalogs are generated using:

tools/generate_catalog.py

------------------------------------------------------------------------

# Validation

All registry content is validated using:

tools/validate_registry.py

Validation checks:

-   schema correctness
-   vocabulary compliance
-   capability references
-   skill dependency cycles
-   identifier correctness

Run validation:

python tools/validate_registry.py

------------------------------------------------------------------------

# Statistics

Registry statistics are generated automatically.

python tools/registry_stats.py

This produces:

catalog/stats.json

Including:

-   capability usage
-   unused primitives
-   skill counts by domain
-   metadata coverage

------------------------------------------------------------------------

# Contributing

Contributions are welcome.

You may contribute:

-   new capabilities
-   new skills
-   improvements to metadata
-   documentation updates

Typical workflow:

1.  Add capability or skill\
2.  Run validator\
3.  Regenerate catalog\
4.  Submit pull request

Commands:

python tools/validate_registry.py\
python tools/generate_catalog.py\
python tools/registry_stats.py\
python tools/governance_guardrails.py\
python tools/capability_governance_guardrails.py\
python tools/enforce_capability_sunset.py

------------------------------------------------------------------------

# Design Principles

The registry follows several core principles.

### Declarative

Skills describe **what happens**, not how.

### Runtime-agnostic

The registry does not define execution engines.

Different runtimes may implement capabilities differently.

### Composable

Skills can reuse capabilities and other skills.

### Vocabulary-controlled

Naming follows a strict vocabulary to avoid fragmentation.

### Open and extensible

The registry is designed to grow through community contributions.

------------------------------------------------------------------------

# Relationship with Runtimes

This repository **does not execute skills**.

It defines the language and registry.

Execution is handled by compatible runtimes.

A runtime typically performs:

skill → step resolution → capability provider → execution

------------------------------------------------------------------------

# Current Registry Scope

Current registry includes:

-   111 capabilities
-   35 skills
-   validation tooling
-   dependency graph generation
-   registry statistics

This represents the first usable registry version.

------------------------------------------------------------------------

# Documentation

Additional documentation:

docs/LANGUAGE.md\
docs/CAPABILITIES.md\
docs/SKILL_FORMAT.md\
docs/GOVERNANCE.md\
docs/SKILL_ADMISSION_POLICY.md\
docs/SEMANTIC_FAMILY_MAP.md\
docs/CAPABILITY_ADMISSION_POLICY.md\
docs/CAPABILITY_COMPATIBILITY_POLICY.md\
docs/CAPABILITY_SUNSET_POLICY.md\
docs/VOCABULARY_BUSINESS_WORKFLOW_COVERAGE.md
docs/CANONICAL_METRICS.md

Governance artifact:

catalog/governance_guardrails.json\
catalog/capability_governance_guardrails.json

------------------------------------------------------------------------

# Vision

The long-term goal is to create a **shared ecosystem of agent skills**
that can be:

-   discovered
-   reused
-   composed
-   executed across runtimes

A common language for AI agent workflows.
