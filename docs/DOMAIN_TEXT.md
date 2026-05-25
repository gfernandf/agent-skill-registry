# Text Domain — Capability Reference

> Domain: `text`  
> Capabilities: 15  
> Last reviewed: 2026-03-30

## Overview

The `text.*` domain covers all operations on natural-language text — from
low-level deterministic transformations to LLM-powered generation and analysis.

### Design principles

| Principle | Rationale |
|-----------|-----------|
| **Analyse vs Generate split** | Capabilities are either analytical (classify, detect, extract) or generative (generate, transform, summarize). This keeps contracts predictable. |
| **Deterministic capabilities are marked** | `properties.deterministic: true` signals the runtime that the result is reproducible and cacheable (template, merge, extract, keyword.extract). |
| **Semantic non-overlap** | Each capability has a unique purpose. See [Boundary definitions](#boundary-definitions) for disambiguation. |
| **Dual bindings** | Every capability ships with a Python baseline (offline, degraded) and an OpenAI chat binding (production quality). |

---

## Capability inventory

### Analysis & Detection

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `reasoning.language.detect` | Detect the language of a text | No | experimental |
| `reasoning.content.classify` | Classify text into predefined categories | No | experimental |
| `reasoning.sentiment.analyze` | Polarity and emotion analysis | No | experimental |
| `reasoning.content.compare` | Semantic diff of two texts | No | experimental |

### Extraction

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `perception.keyword.extract` | Extract keywords from text | Yes | experimental |
| `perception.entity.extract` | Extract named entities (people, orgs, places) | No | experimental |
| `perception.content.extract` | Extract clean text from HTML/documents | Yes | **stable** |
| `reasoning.response.extract` | Answer a question from a context passage (extractive QA) | No | experimental |

### Generation

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `reasoning.content.generate` | Produce new text from instruction + optional context | No | experimental |
| `reasoning.content.summarize` | Condense text preserving key ideas | No | experimental |
| `reasoning.content.translate` | Translate text between languages | No | experimental |
| `reasoning.content.transform` | Rewrite text applying a style/tone directive | No | experimental |

### Composition (deterministic)

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `reasoning.content.template` | Render `{{var}}` templates with variables | Yes | **stable** |
| `reasoning.content.merge` | Concatenate text items with configurable separator | Yes | **stable** |

### Vectorization

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `reasoning.content.embed` | Generate vector embeddings from text | No | experimental |

---

## Boundary definitions

These clarify where one capability ends and the next begins:

| Pair | Disambiguation |
|------|---------------|
| **generate** vs **summarize** | `generate` produces new content from an instruction; `summarize` condenses *existing* text. |
| **generate** vs **transform** | `generate` creates from scratch; `transform` modifies existing text (preserves meaning, changes form). |
| **transform** vs **summarize** | `transform` keeps content length flexible (can expand/shorten); `summarize` always reduces. |
| **response.extract** vs **generate** | `response.extract` answers a question from a context (grounded); `generate` produces freely. |
| **response.extract** vs **content.extract** | `response.extract` is LLM-driven Q&A; `content.extract` is deterministic HTML→text cleanup. |
| **keyword.extract** vs **entity.extract** | `keyword.extract` finds topical terms; `entity.extract` finds proper nouns with type labels. |
| **template** vs **generate** | `template` is deterministic variable substitution; `generate` is LLM-driven. |
| **classify** vs **sentiment.analyze** | `classify` assigns arbitrary labels from a user-supplied set; `sentiment.analyze` evaluates polarity/emotion with a fixed output schema. |
| **compare** vs **summarize** | `compare` produces a diff between two texts; `summarize` condenses a single text. |

---

## Binding matrix

Every capability has at least one Python baseline binding (offline, degraded
quality) and optionally an OpenAI binding (production quality).

| Capability | Python baseline | OpenAI binding |
|-----------|:-:|:-:|
| `reasoning.language.detect` | yes | yes |
| `perception.keyword.extract` | yes | yes |
| `perception.entity.extract` | yes | yes |
| `reasoning.content.classify` | yes | yes |
| `reasoning.content.embed` | yes | yes |
| `perception.content.extract` | yes | — |
| `reasoning.content.summarize` | yes | yes |
| `reasoning.content.translate` | yes | yes |
| `reasoning.content.generate` | yes | yes |
| `reasoning.content.transform` | yes | yes |
| `reasoning.response.extract` | yes | yes |
| `reasoning.content.template` | yes | — |
| `reasoning.content.merge` | yes | — |

Deterministic capabilities (template, merge, extract) do not need an LLM
binding — the Python baseline *is* the production implementation.

---

## Skills using text.* capabilities

Existing skills that compose text capabilities:

- `text.translate-summary` → translate + summarize
- `text.detect-language-and-classify` → language.detect + classify
- `text.entity-summary` → entity.extract + summarize
- `text.keyword-summary` → content.extract + keyword.extract + summarize
- `text.language-summary` → language.detect + summarize
- `web.fetch-summary` → content.extract + summarize
- `pdf.read-summary` → summarize
- `doc.chunk-and-embed` → embed
- And 15+ more cross-domain skills

---

## Changelog

| Date | Change |
|------|--------|
| 2026-03-24 | Domain review: added generate, transform, response.extract. Stabilized template, extract, merge. 13/13 validated. |
