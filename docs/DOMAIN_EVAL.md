# Eval Domain — Capability Reference

> Domain: `eval`  
> Capabilities: 3  
> Last reviewed: 2026-03-24

## Overview

The `eval.*` domain provides evaluation and scoring capabilities for decision
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
| **LLM-enhanced, baseline-safe** | All 3 capabilities ship with OpenAI bindings (production) and pythoncall baselines (offline/testing). |

---

## Capability inventory

| ID | Status | Deterministic | Purpose |
|----|--------|---------------|---------|
| `eval.option.analyze` | experimental | no | Qualitative pros/cons/risks/assumptions per option |
| `eval.option.score` | experimental | no | Multi-criteria weighted scoring with tradeoff analysis |
| `eval.output.score` | experimental | no | General output quality scoring against rubric |

---

## Binding matrix

| Capability | pythoncall (baseline) | OpenAI chat | Notes |
|---|---|---|---|
| `eval.option.analyze` | `python_eval_option_analyze` — 1 pro/con/risk per option | `openapi_eval_option_analyze_openai_chat` — gpt-4o-mini, temp 0.2 | Deeper analysis with LLM |
| `eval.option.score` | `python_eval_option_score` — field-fill heuristic scoring | `openapi_eval_option_score_openai_chat` — gpt-4o-mini, temp 0.1 | Real criteria evaluation with LLM |
| `eval.output.score` | `python_eval_output_score` — coverage + depth heuristic | `openapi_eval_output_score_openai_chat` — gpt-4o-mini, temp 0.1 | Dimension-aware quality scoring |

### Default selection policy

All 3 default to OpenAI chat bindings, with pythoncall fallbacks:
- `eval.option.analyze` → `openapi_eval_option_analyze_openai_chat`
- `eval.option.score` → `openapi_eval_option_score_openai_chat`
- `eval.output.score` → `openapi_eval_output_score_openai_chat`

---

## Baseline quality notes

| Function | Quality | Strategy |
|----------|---------|----------|
| `analyze_options()` | Template | One generic pro/con/risk/assumption per option from label |
| `score_options()` | Heuristic | Field-fill ratio × 80 + 10 base; auto-infers 3 criteria |
| `score_output()` | Heuristic | Coverage (non-empty fields) + depth (structural complexity); returns quality_level |

---

## Decision pipeline integration

The eval.* capabilities form the evaluation backbone of decision workflows:

```
agent.option.generate → eval.option.analyze → eval.option.score → decision.option.justify
       (options)           (pros/cons/risks)      (ranked scores)        (recommendation)
```

### Skills consuming eval.*

| Skill | eval.* capabilities used |
|-------|-------------------------|
| `decision.make` | `eval.option.analyze` → `eval.option.score` → `decision.option.justify` |
| `analysis.compare` | `eval.option.analyze` + `eval.option.score` |
| `eval.validate` | `eval.output.score` as quality gate |
| `research.quality-assess` | `eval.output.score` for output validation |
| `analysis.decompose` | `eval.output.score` for quality gating |
| `analysis.risk-assess` | `eval.output.score` for quality gating |

---

## Boundary definitions

- **eval.option.analyze vs eval.option.score**: `analyze` is qualitative
  (pros, cons, risks, assumptions); `score` is quantitative (0–1 scores per
  criterion). `analyze` feeds `score` in the decision pipeline.
- **eval.output.score vs model.output.score**: `eval.output.score` is a
  general-purpose quality scorer for any artifact; `model.output.score`
  specifically evaluates LLM output quality (word overlap, sentence metrics).
- **eval.option.score vs decision.option.justify**: `score` ranks options;
  `justify` selects one and produces the justification narrative with
  confidence, failure modes, and next steps.
