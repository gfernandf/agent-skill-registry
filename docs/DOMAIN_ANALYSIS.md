# Domain: analysis.*

## Overview

The `analysis.*` domain provides capabilities for structured analytical
reasoning: decomposing complex problems, extracting risks and assumptions,
and grouping items into thematic clusters. These capabilities are designed
to be composed with downstream evaluation and decision capabilities.

## Capability Inventory

| Capability                  | Status       | Description |
|-----------------------------|-------------|-------------|
| `analysis.problem.split`   | experimental | Decompose a problem into components by a chosen strategy axis |
| `analysis.risk.extract`    | experimental | Extract risks, assumptions, failure modes and mitigation ideas |
| `analysis.theme.cluster`   | experimental | Group text items into coherent thematic clusters |

## Binding Matrix

| Capability                  | pythoncall Binding                  | OpenAI Binding                            | Default |
|-----------------------------|--------------------------------------|-------------------------------------------|---------|
| `analysis.problem.split`   | `python_analysis_split`              | `openapi_analysis_split_openai_chat`      | openai  |
| `analysis.risk.extract`    | `python_analysis_risk_extract`       | `openapi_analysis_risk_extract_openai_chat`| openai  |
| `analysis.theme.cluster`   | `python_analysis_theme_cluster`      | `openapi_analysis_theme_cluster_openai_chat`| openai |

All three default to their OpenAI binding when `OPENAI_API_KEY` is present.
The pythoncall baselines are deterministic fallbacks.

## Baseline Notes (`analysis_baseline.py`)

| Function          | Strategy |
|-------------------|----------|
| `split_problem`   | Generates up to `max_components` sequential components along the requested strategy axis. Dependencies are linear (c2→c1, c3→c2 …). |
| `extract_risks`   | Returns 2 generic risks, 1 assumption, 1 failure mode, 1 mitigation idea. Marks output `_fallback: true`. |
| `cluster_themes`  | Round-robin assignment to `hint_labels` (or auto-generated labels). Coherence fixed at 0.6. |

## Cognitive Hints

All three capabilities declare `role: analyze`. `risk.extract` and
`theme.cluster` include full `consumes`/`produces` mappings for the
cognitive-state router. `problem.split` consumes `Context` and produces
`Entity` (components) plus `Risk` (gaps/overlaps).

## Skills Consuming analysis.*

| Skill                  | Capabilities Used |
|------------------------|-------------------|
| `analysis.synthesize`  | `analysis.problem.split`, `text.content.summarize` |
| `analysis.risk-assess` | `analysis.risk.extract`, `eval.option.score` |
| `analysis.compare`     | `analysis.theme.cluster`, `eval.option.analyze` |

## Boundary Definitions

- **problem.split** decomposes but does NOT evaluate or prioritise components.
- **risk.extract** inventories risks but does NOT score or rank them — use
  `eval.option.score` or a dedicated risk-scoring capability downstream.
- **theme.cluster** groups items but does NOT summarise or interpret the
  clusters — that is the consumer's responsibility.
