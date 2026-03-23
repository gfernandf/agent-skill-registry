# Vocabulary

This document describes the **controlled vocabulary** used by the Agent Skill Registry.

The registry uses a constrained language for capability identifiers in order to preserve:

- consistency
- clarity
- reuse
- discoverability
- long-term ecosystem coherence

The **source of truth** for the controlled vocabulary is:

```
vocabulary/vocabulary.json
```

A second vocabulary file defines **cognitive semantic types** used by
`cognitive_hints` in capability contracts:

```
vocabulary/cognitive_types.yaml
```

This document explains how these vocabularies should be interpreted and extended.

---

# Purpose

Capabilities are part of the core language of the registry.

Unlike skills, which compose existing capabilities into workflows, capabilities define the reusable functional vocabulary used across the ecosystem.

For that reason, capability identifiers must follow a **controlled vocabulary**.

This prevents fragmentation such as:

- multiple verbs for the same action
- inconsistent nouns for the same object
- overlapping domains
- ambiguous capability names

---

# Capability Identifier Forms

Capability identifiers may use one of the following forms:

```
domain.verb
domain.noun.verb
```

Examples:

```
text.content.summarize
fs.file.read
data.json.parse
text.keyword.extract
web.page.fetch
```

The registry currently allows **a maximum of three segments** in a capability identifier.

Identifiers with more than three segments are not allowed.

Examples of invalid forms:

```
data.json.schema.validate
web.article.main.extract
text.named.entity.extract
```

---

# Controlled Vocabulary Components

The controlled vocabulary defines three classes of terms:

- domains
- nouns
- verbs

These are stored in:

```
vocabulary/vocabulary.json
```

---

## Domains

A **domain** defines the broad functional area of a capability.

Examples:

- `text`
- `web`
- `data`
- `pdf`
- `fs`

Use an existing domain whenever possible.

A new domain should be introduced only when the capability clearly belongs to a distinct functional area that cannot be expressed cleanly using the current vocabulary.

---

## Nouns

A **noun** defines the specific object that the capability operates on when additional disambiguation is needed.

Examples:

- `json`
- `page`
- `language`
- `keyword`
- `schema`

Use the `domain.noun.verb` form only when it improves clarity or avoids ambiguity.

For example:

```
data.json.parse
text.keyword.extract
web.page.fetch
```

### Noun Rules

Nouns should be:

- singular
- canonical
- concise

Preferred:

```
text.keyword.extract
text.entity.extract
web.page.fetch
```

Avoid:

```
text.keywords.extract
text.entities.extract
web.pages.fetch
```

Do not introduce multiple nouns for the same concept unless there is a real semantic distinction.

---

## Verbs

A **verb** defines the action performed by the capability.

Examples:

- `read`
- `fetch`
- `extract`
- `summarize`
- `parse`
- `classify`
- `validate`

Verbs must come from the controlled vocabulary.

Do not invent a new verb when an existing one already expresses the action.

For example, if `extract` already exists, do not introduce alternatives such as:

- `pull`
- `retrieve`
- `mine`

unless there is a meaningful semantic difference accepted by governance.

---

# Naming Guidance

The default form should be:

```
domain.verb
```

Use:

```
domain.noun.verb
```

only when necessary to disambiguate the target object.

### Good examples

```
text.content.summarize
text.content.classify
fs.file.read
web.page.fetch
data.parse
data.json.parse
text.keyword.extract
```

### Less desirable examples

```
text.keywords
data.do-parse
web.content.get-page
```

### Invalid examples

```
data.json.schema.validate
text.article.main.extract
web.page.html.content.fetch
```

---

# Design Principles

The controlled vocabulary follows these principles:

- prefer the simplest valid identifier
- use nouns only when they add real clarity
- use singular canonical nouns
- use approved verbs only
- avoid synonyms and semantic duplication
- avoid overly deep hierarchies

The goal is not to encode every nuance in the identifier.

The goal is to create a language that remains:

- predictable
- searchable
- reusable
- stable over time

---

# Domain Design Criteria

Domains are shared between capabilities and skills, but serve different roles
in each context.

## For capabilities

A capability domain describes a **functional area of the system** — the
technical surface where the operation runs.

Examples: `text`, `model`, `data`, `ops`, `security`.

A capability domain should be chosen based on **what type of operation** the
capability performs, not what business problem it serves.

## For skills

A skill domain describes the **problem space** the workflow addresses — the
kind of transformation or cognitive process it represents.

Examples: `analysis`, `decision`, `agent`, `research`.

A skill domain should be chosen based on **what kind of problem** the skill
solves for the user, not what capabilities it uses internally.

## Domain classification

Some domains are naturally technical (used primarily by capabilities):

```
text, web, data, pdf, fs, image, audio, video, table, model, code, doc,
memory, email, message, security, policy, identity, integration
```

Some domains are naturally cognitive or process-oriented (used primarily by
skills):

```
analysis, decision
```

Some domains serve both levels naturally:

```
agent, research, ops, task, eval, provenance
```

There is no formal prohibition — a skill may use a technical domain if the
problem space genuinely matches (e.g. `pdf.batch-summarize` is a valid skill).
The guidance is about **default intent**, not hard rules.

## When to create a new domain

A new domain is justified when:

1. Existing domains cannot cleanly express the problem space or functional area.
2. Multiple capabilities or skills would naturally live under it.
3. It does not substantially overlap with an existing domain.

A new domain is **not** justified when:

- It would contain only one capability or skill with no foreseeable growth.
- It can be expressed as a noun within an existing domain.
- It is a synonym or subset of an existing domain.

---

# Governance of Vocabulary Changes

Changes to the controlled vocabulary must update:

```
vocabulary/vocabulary.json
```

Examples of vocabulary changes:

- adding a new domain
- adding a new noun
- adding a new verb
- deprecating an existing term
- clarifying the intended scope of a term

Because vocabulary changes affect the core language of the registry, they should be reviewed more strictly than ordinary skill additions.

---

# Relationship to Validation

The registry validator uses the controlled vocabulary to validate capability identifiers.

This means that a capability may fail validation if:

- its domain is not allowed
- its noun is not allowed
- its verb is not allowed
- it uses too many identifier segments

The capability creation tool may also use the same vocabulary to prevent invalid capability creation.

---

# Source of Truth

The authoritative machine-readable vocabulary is:

```
vocabulary/vocabulary.json
```

This document is explanatory only.

If this document and the JSON file ever differ, the JSON file takes precedence.

---

# Skill Naming

Skills and capabilities serve different purposes and follow **different naming
conventions**.

Capabilities define the **functional vocabulary** of the system — reusable,
atomic operations with controlled identifiers.

Skills define **workflows visible to humans and agents** — compositions of
capabilities that solve a recognizable problem.

Their naming rules reflect this distinction.

---

## Skill Identifier Form

```
domain.slug
```

- **domain**: must be a valid domain from `vocabulary.json`.
- **slug**: a free-form kebab-case string describing the skill's intent.

The slug is **not** governed by the controlled vocabulary of nouns and verbs.
It should be chosen for clarity and discoverability, not to match capability
terms.

---

## Skill Naming Principles

### 1. Name the problem, not the technique

A skill name should describe what problem it solves for the user, not what
capabilities it uses internally.

Good:

```
analysis.synthesize          — synthesize research materials
decision.make                — produce a decision under uncertainty
ops.trace-execution          — observe and trace an agent execution
```

Avoid:

```
model.generate-structured    — names the internal mechanism
text.run-pipeline            — too generic
agent.call-llm-and-score     — exposes implementation
```

### 2. The domain should reflect the problem space

Choose the domain that best represents **the kind of problem** the skill
addresses, not the primary capability it happens to use.

Guidelines for domain selection:

| If the skill... | Prefer domain |
|---|---|
| synthesizes, analyzes, or investigates information | `research` |
| makes a choice, evaluates options, produces recommendations | `agent` |
| traces, monitors, or audits execution | `ops` |
| manages tasks, decomposes objectives, tracks progress | `task` |
| transforms or produces text, documents, media | the content domain (`text`, `pdf`, `doc`, etc.) |
| handles communication (email, messages) | the channel domain (`email`, `message`) |

When in doubt, ask: "If a user searched for this skill by domain, where would
they look first?"

### 3. The slug should be specific and outcome-oriented

Good slugs:

```
synthesize              — clear cognitive outcome
decide                  — clear action
trace-execution         — specific observable behavior
batch-summarize         — concrete operation
classify-and-reply      — describes the workflow
```

Bad slugs:

```
run                     — too generic
process                 — meaningless
handle                  — vague
do-stuff                — obviously bad
v2                      — version in name
```

### 4. Avoid overloading `agent` as a catch-all domain

`agent` is appropriate when the skill is about **agent-level cognitive
behavior**: deciding, planning, delegating, routing.

It is **not** appropriate as a default for "anything an agent does". Every
skill is ultimately used by an agent — that does not make every skill an
`agent.*` skill.

---

## Skill Naming Anti-Patterns

| Anti-pattern | Why it's wrong | Better alternative |
|---|---|---|
| `model.generate-report` | Exposes the engine, not the problem | `research.generate-report` or `doc.generate-report` |
| `agent.do-everything` | Catch-all domain + generic slug | Pick a specific domain and outcome |
| `text.step1-step2-step3` | Lists implementation steps | Name the outcome instead |
| `data.run-pipeline` | Generic verb, says nothing | Name what the pipeline produces |

---

## Comparison: Capability vs Skill Naming

| Aspect | Capabilities | Skills |
|---|---|---|
| Purpose | Functional vocabulary | Workflow descriptions |
| Form | `domain.verb` or `domain.noun.verb` | `domain.slug` |
| Domain source | `vocabulary.json` (required) | `vocabulary.json` (required) |
| Verb/noun source | `vocabulary.json` (required) | Free-form (guided, not controlled) |
| Max segments | 3 | 2 |
| Validation | Strict — rejected if terms not in vocabulary | Domain validated; slug is free |
| Naming goal | Predictable, searchable, composable | Clear, discoverable, outcome-oriented |

---

# Safety Vocabulary

The file `vocabulary/safety_vocabulary.yaml` defines the controlled enumerations
used by the `safety` block in capability contracts.

It declares:

-   **trust_levels** — sandbox (0), standard (1), elevated (2), privileged (3)
-   **data_classifications** — public (0), internal (1), pii (2), confidential (3), restricted (4)
-   **failure_policies** — block, warn, degrade, require_human
-   **allowed_targets** — internal_only, approved_connectors, same_tenant
-   **scope_constraints** — read_only, sandboxed_execution, no_credential_passthrough, no_external_network, ephemeral_only

Ranked enumerations (trust_levels, data_classifications) carry a numeric `rank`
used by the runtime for enforcement comparisons.

This vocabulary is normative: the registry validator rejects any `safety` block
value that does not appear in `safety_vocabulary.yaml`.

See `docs/CAPABILITIES.md` for the full `safety` schema reference.