# Model Domain — Capability Reference

> Domain: `model`  
> Capabilities: 8  
> Last reviewed: 2026-03-24

## Overview

The `model.*` domain provides infrastructure-level capabilities for working
with LLM outputs — generating structured results, validating quality,
scoring risk, sanitizing content, and managing embeddings and prompts.

These capabilities are **not user-facing** in the same way as `text.*` — they
are building blocks used by skills like `analysis.synthesize`,
`eval.validate`, and `research.quality-assess` to orchestrate multi-step
LLM workflows.

### Design principles

| Principle | Rationale |
|-----------|-----------|
| **Output lifecycle** | Capabilities cover the full lifecycle: generate → classify → score → validate → sanitize. Each step has a distinct contract. |
| **Deterministic vs LLM split** | `prompt.template` and `output.sanitize` are deterministic (no LLM needed). All others benefit from LLM evaluation. |
| **Dual bindings** | LLM-dependent capabilities ship with both a Python baseline (heuristic, offline) and an OpenAI binding (production quality). Deterministic capabilities only need pythoncall. |
| **Safety-first** | `risk.score` and `output.sanitize` form a safety gate that can be inserted before any output reaches end users. |

---

## Capability inventory

### Generation

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `model.output.generate` | Generate structured output from instruction + context + JSON schema | No | experimental |
| `model.embedding.generate` | Generate vector embeddings for a text input | Yes* | draft |

*Deterministic with the same model and input; baseline uses hash-based pseudo-embedding.

### Evaluation

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `model.output.classify` | Classify output into candidate categories | No | draft |
| `model.output.score` | Score output on quality dimensions (relevance, fluency, etc.) | No | draft |
| `model.response.validate` | Validate output for coherence, grounding, and completeness | No | experimental |

### Safety

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `model.output.sanitize` | Remove PII, harmful content, and prompt leakage | Yes | draft |
| `model.risk.score` | Assess risk across toxicity, bias, hallucination, prompt injection | No | draft |

### Prompt engineering

| Capability | Purpose | Deterministic | Status |
|-----------|---------|:---:|--------|
| `model.prompt.template` | Render prompt from template + variable bindings | Yes | draft |

---

## Binding matrix

| Capability | Python baseline | OpenAI binding | Default with key | Default without key |
|-----------|:-:|:-:|---|---|
| `model.output.generate` | — (mock) | gpt-4o-mini | openapi | openapi (mock) |
| `model.response.validate` | structural check | gpt-4o-mini | openapi | pythoncall |
| `model.embedding.generate` | hash-based 128d | text-embedding-3-small | openapi | pythoncall |
| `model.output.classify` | keyword/struct heuristic | gpt-4o-mini | openapi | pythoncall |
| `model.output.score` | structural scoring | gpt-4o-mini | openapi | pythoncall |
| `model.output.sanitize` | regex PII/harmful/leakage | — | pythoncall | pythoncall |
| `model.prompt.template` | `${var}` substitution | — | pythoncall | pythoncall |
| `model.risk.score` | pattern-based detection | gpt-4o-mini | openapi | pythoncall |

The environment-aware binding resolver (`OPENAI_API_KEY` detection) applies
to all LLM-dependent capabilities.  See [BINDING_SELECTION.md](../docs/BINDING_SELECTION.md)
in agent-skills for details.

---

## Baseline quality notes

### Full quality (deterministic — no LLM needed)

- **`model.output.sanitize`** — Regex-based deep sanitizer. Recursively walks
  nested objects/arrays. Detects email, phone, SSN, credit card, API keys,
  prompt leakage patterns. Good production baseline.

- **`model.prompt.template`** — `${variable}` substitution with unresolved
  placeholder tracking. Handles nested dot notation (`${user.name}`).

### Functional (heuristic — LLM improves quality)

- **`model.embedding.generate`** — Hash-based pseudo-embedding. Produces
  deterministic normalized float vectors. Useful for pipeline testing but
  not for real semantic similarity. Use OpenAI for production.

- **`model.output.classify`** — Keyword frequency + structural heuristics.
  Inspects field names (`code`, `summary`, `error`, `list`) for structural
  hints. Works for obvious cases; LLM needed for subtle classification.

- **`model.output.score`** — Word overlap for relevance, sentence length for
  fluency, length ratio for completeness, reference overlap for faithfulness.
  Rough but functional. LLM provides nuanced evaluation.

- **`model.response.validate`** — Checks output is non-empty dict, flags
  null/empty fields. Does not check semantic coherence — LLM required for
  real validation.

- **`model.risk.score`** — Pattern-based detection for toxicity (harmful
  keywords), bias (sweeping generalizations), hallucination (novel words vs
  context), prompt injection (known markers like `ignore previous instructions`).
  Catches obvious cases. LLM-based scoring is significantly more reliable.

---

## Skills using model.* capabilities

| Skill | Capabilities used | Purpose |
|-------|------------------|---------|
| `analysis.synthesize` | `model.output.generate` | Single-call synthesis of multi-source evidence |
| `research.quality-assess` | `model.response.validate`, `model.output.generate` | Quality metrics and grounding validation |
| `research.normalize-corpus` | `model.output.generate` | Corpus normalization to structured items |
| `eval.validate` | `model.response.validate` | Consistency checking of artifacts |

---

## Boundary definitions

| If you need to... | Use | Not |
|-------------------|-----|-----|
| Generate structured output from instruction + schema | `model.output.generate` | `text.content.generate` (unstructured text) |
| Embed text for similarity | `model.embedding.generate` | `text.content.embed` (same underlying model, different contract layer) |
| Classify text into labels | `text.content.classify` | `model.output.classify` (for model outputs specifically) |
| Remove PII from text | `security.pii.redact` | `model.output.sanitize` (for model outputs, also covers leakage) |
| Score a model's output quality | `model.output.score` | `eval.output.score` (higher-level evaluation) |
| Check if output is safe | `model.risk.score` | `security.output.gate` (binary gate, not scoring) |
| Render a prompt template | `model.prompt.template` | `text.content.template` (generic `{{var}}` templates) |
