# Eval Domain — Capability Reference

> Domain: `eval`  
> Capabilities: 4  
> Last reviewed: 2026-05-08

> Note: `eval.*` remains as a compatibility alias. New capability design should
> prefer canonical names in the `evaluation.*` family as documented in
> [COGNITIVE_TAXONOMY.md](COGNITIVE_TAXONOMY.md).

## Overview

The evaluation domain provides scoring and validation capabilities for decision
workflows and output quality assessment. It covers three complementary steps:
qualitative analysis of options, quantitative multi-criteria scoring, and
general-purpose output quality scoring.

These capabilities are heavily consumed by decision-making skills
(`decision.make`, `analysis.compare`) and validation pipelines
(`eval.validate`, `research.quality-assess`).

### Design principles

| Principle | Rationale |
|-----------|-----------|
| **Qualitative before quantitative** | `option.analyze` produces structured evidence (pros/cons/risks) that `option.score` consumes for informed scoring. |
| **Multi-criteria transparency** | `option.score` makes criteria, weights, and per-criterion scores visible — no opaque single number. |
| **Universal quality gate** | `output.score` can evaluate any structured artifact, making it reusable as a quality gate across domains. |
| **LLM-enhanced, baseline-safe** | The core capabilities ship with OpenAI bindings (production) and pythoncall baselines (offline/testing). |

---

## Capability inventory

| ID | Status | Deterministic | Purpose |
|----|--------|---------------|---------|
| `reasoning.option.analyze` | experimental | no | Qualitative pros/cons/risks/assumptions per option |
| `evaluation.option.score` | experimental | no | Multi-criteria weighted scoring with tradeoff analysis |
| `evaluation.output.score` | experimental | no | General output quality scoring against rubric |
| `evaluation.output.validate` | experimental | no | Validate final output against success criteria |

---

## Binding matrix

| Capability | pythoncall (baseline) | OpenAI chat | Notes |
|---|---|---|---|
| `reasoning.option.analyze` | `python_eval_option_analyze` — 1 pro/con/risk per option | `openapi_eval_option_analyze_openai_chat` — gpt-4o-mini, temp 0.2 | Deeper analysis with LLM |
| `evaluation.option.score` | `python_eval_option_score` — field-fill heuristic scoring | `openapi_eval_option_score_openai_chat` — gpt-4o-mini, temp 0.1 | Real criteria evaluation with LLM |
| `evaluation.output.score` | `python_eval_output_score` — coverage + depth heuristic | `openapi_eval_output_score_openai_chat` — gpt-4o-mini, temp 0.1 | Dimension-aware quality scoring |
| `evaluation.output.validate` | `python_eval_output_validate` — baseline: assign 0.7 score per criterion | `openapi_eval_output_validate_openai_chat` — gpt-4o-mini, temp 0.1 | Per-criterion validation with LLM |

### Default selection policy

All 4 default to OpenAI chat bindings, with pythoncall fallbacks:
- `reasoning.option.analyze` → `openapi_eval_option_analyze_openai_chat`
- `evaluation.option.score` → `openapi_eval_option_score_openai_chat`
- `evaluation.output.score` → `openapi_eval_output_score_openai_chat`
- `evaluation.output.validate` → `openapi_eval_output_validate_openai_chat`

---

## Baseline quality notes

| Function | Quality | Strategy |
|----------|---------|----------|
| `analyze_options()` | Template | One generic pro/con/risk/assumption per option from label |
| `score_options()` | Heuristic | Field-fill ratio × 80 + 10 base; auto-infers 3 criteria |
| `score_output()` | Heuristic | Coverage (non-empty fields) + depth (structural complexity); returns quality_level |

---

## Decision pipeline integration

The evaluation capabilities form the backbone of decision workflows:

```
reasoning.option.generate → reasoning.option.analyze → evaluation.option.score → decision.option.justify
       (options)           (pros/cons/risks)      (ranked scores)        (recommendation)
```

### Skills consuming evaluation capabilities

| Skill | capabilities used |
|-------|-------------------------|
| `decision.make` | `reasoning.option.analyze` → `evaluation.option.score` → `decision.option.justify` |
| `analysis.compare` | `reasoning.option.analyze` + `evaluation.option.score` |
| `eval.validate` | `evaluation.output.score` as quality gate |
| `research.quality-assess` | `evaluation.output.score` for output validation |
| `analysis.decompose` | `evaluation.output.score` for quality gating |
| `analysis.risk-assess` | `evaluation.output.score` for quality gating |

---

## Boundary definitions

- **reasoning.option.analyze vs evaluation.option.score**: `analyze` is qualitative
  (pros, cons, risks, assumptions); `score` is quantitative (0–1 scores per
  criterion). `analyze` feeds `score` in the decision pipeline.
- **evaluation.output.score vs model.output.score**: `evaluation.output.score` is a
  general-purpose quality scorer for any artifact; `model.output.score`
  specifically evaluates model output quality.
- **evaluation.option.score vs decision.option.justify**: `score` ranks options;
  `justify` selects one and produces the justification narrative with
  confidence, failure modes, and next steps.
