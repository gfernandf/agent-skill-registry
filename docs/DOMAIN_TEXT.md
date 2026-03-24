# Text Domain — Capability Reference

> Domain: `text`  
> Capabilities: 13  
> Last reviewed: 2026-03-24

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
| `text.language.detect` | Detect the language of a text | No | experimental |
| `text.content.classify` | Classify text into predefined categories | No | experimental |

### Extraction

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `text.keyword.extract` | Extract keywords from text | Yes | experimental |
| `text.entity.extract` | Extract named entities (people, orgs, places) | No | experimental |
| `text.content.extract` | Extract clean text from HTML/documents | Yes | **stable** |
| `text.response.extract` | Answer a question from a context passage (extractive QA) | No | experimental |

### Generation

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `text.content.generate` | Produce new text from instruction + optional context | No | experimental |
| `text.content.summarize` | Condense text preserving key ideas | No | experimental |
| `text.content.translate` | Translate text between languages | No | experimental |
| `text.content.transform` | Rewrite text applying a style/tone directive | No | experimental |

### Composition (deterministic)

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `text.content.template` | Render `{{var}}` templates with variables | Yes | **stable** |
| `text.content.merge` | Concatenate text items with configurable separator | Yes | **stable** |

### Vectorization

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `text.content.embed` | Generate vector embeddings from text | No | experimental |

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

---

## Binding matrix

Every capability has at least one Python baseline binding (offline, degraded
quality) and optionally an OpenAI binding (production quality).

| Capability | Python baseline | OpenAI binding |
|-----------|:-:|:-:|
| `text.language.detect` | yes | yes |
| `text.keyword.extract` | yes | yes |
| `text.entity.extract` | yes | yes |
| `text.content.classify` | yes | yes |
| `text.content.embed` | yes | yes |
| `text.content.extract` | yes | — |
| `text.content.summarize` | yes | yes |
| `text.content.translate` | yes | yes |
| `text.content.generate` | yes | yes |
| `text.content.transform` | yes | yes |
| `text.response.extract` | yes | yes |
| `text.content.template` | yes | — |
| `text.content.merge` | yes | — |

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
