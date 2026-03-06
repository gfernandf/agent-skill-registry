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

This document explains how that vocabulary should be interpreted and extended.

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
text.summarize
fs.read
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
text.summarize
text.classify
fs.read
web.fetch
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