# Changelog

All notable changes to **agent-skill-registry** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — 2026-05-08

### Added

#### Multipurpose agent orchestration pipeline — 18 new capabilities

Complete unified pipeline for autonomous agent task execution: normalized
request ingestion → goal interpretation → plan generation, validation, repair
→ execution gating and orchestration → output synthesis and evaluation. All 18
capabilities follow the canonical grammar and carry full contracts:

- **agent.request.normalize** — Parse and normalize raw user requests.
- **agent.goal.interpret** — Convert normalized request to structured goal.
- **agent.criteria.define** — Extract success/quality/acceptance criteria.
- **agent.catalog.\*** — Registry search, ranking, and gap detection:
  - `agent.catalog.search` — Find relevant capabilities and skills.
  - `agent.catalog.rank` — Rank candidates by relevance.
  - `agent.catalog.detect` — Identify capability gaps.
- **agent.task.plan** — Generate high-level macro plan.
- **agent.plan.\*** — Plan expansion, validation, repair, synthesis, and execution:
  - `agent.plan.split` — Expand plan stage into executable steps.
  - `agent.plan.map` — Bind steps to CognitiveState paths.
  - `agent.plan.validate` — Structural correctness validation (deterministic).
  - `agent.plan.reconcile` — Repair invalid plans.
  - `agent.plan.synthesize` — Compile plan into executable DAG (deterministic).
  - `agent.plan.gate` — Authorization checks before execution.
  - `agent.plan.run` — Execute compiled plan (with side_effects, safety constraints).
- **agent.output.\*** — Output synthesis and reporting:
  - `agent.output.generate` — Produce final user-facing report.
  - `agent.output.synthesize` — Extract reusable skill from execution trace.
- **eval.output.validate** — Validate final output against success criteria.
- **ops.trace.summarize** — Summarize execution trace into compact report.

All 18 have OpenAI + pythoncall bindings, integrated with existing MCP server.
Vocabulary extended: 3 nouns + 2 verbs.

---

## [0.2.0] — 2026-03-30

### Added

#### Composability & coverage wave — 19 new capabilities

Gap analysis of 122 existing capabilities identified missing primitives for
control flow, structural data transforms, and underserved domains. All 19
follow the canonical grammar (`domain.noun.verb`), carry full I/O contracts,
`cognitive_hints`, `properties`, `metadata`, and dual bindings (OpenAI + Python
fallback).

- **agent.flow.\*** — Control-flow primitives:
  - `agent.flow.branch` — conditional branch selection.
  - `agent.flow.iterate` — loop over a collection invoking a capability per item.
  - `agent.flow.wait` — pause execution until condition or timeout.
  - `agent.flow.catch` — error handling with fallback strategies.
- **agent.input.collect** — structured multi-field form collection.
- **data.\*** — Structural data transforms:
  - `data.array.map` — map/transform each element of an array.
  - `data.field.map` — rename/alias fields in a record.
  - `data.record.join` — relational join of two record sets.
  - `data.record.merge` — deep-merge parallel result records.
- **message.content.format** — structure data → human-readable notification.
- **doc.content.generate** — generate markdown/HTML documents from instruction.
- **web.request.send** — generic HTTP request with safety blocks.
- **task.event.schedule** — schedule future/recurring events.
- **text.\*** — Coverage additions:
  - `text.content.compare` — semantic diff of two texts.
  - `text.sentiment.analyze` — polarity and emotion analysis.
- **audio.speaker.diarize** — multi-speaker segmentation.
- **image.content.generate** — text-to-image generation.
- **table.sheet.read** / **table.sheet.write** — CSV/Excel I/O.

Vocabulary updated: 7 new nouns (`flow`, `array`, `field`, `sheet`,
`sentiment`, `speaker`, `request`) and 7 new verbs (`branch`, `iterate`,
`wait`, `catch`, `join`, `diarize`, `collect`).

`_index.yaml` updated. Catalog regenerated (141 capabilities, 36 skills).

### Fixed

- `_index.yaml`: quoted multiline description of `decision.option.justify`
  that broke YAML parsing at line 85 (unquoted second sentence treated as a
  new mapping key).

## [0.1.0] — 2026-03-24

### Added

#### Phase 3 — Registry hygiene
- 52 stub capabilities marked `status: draft` (previously `experimental`).
- `validate_registry.py`: `draft` added to `ALLOWED_STATUS`.
- `registry_stats.py`: emits `by_status` breakdown in stats output.
- README expanded with tooling section and contributor instructions.
- `requirements.txt` added for tooling dependencies.

#### text.* domain review
- **3 new capabilities**:
  - `text.content.generate` — produce new text from instruction + context.
  - `text.content.transform` — rewrite text applying a style/tone directive.
  - `text.response.extract` — answer a question from a context passage.
- **3 capabilities stabilized** (`status: stable`):
  - `text.content.template`
  - `text.content.extract`
  - `text.content.merge`
- `docs/DOMAIN_TEXT.md`: full domain reference with boundary definitions,
  binding matrix, and skill inventory.
- `_index.yaml` updated with all new entries and status changes.
- Catalog regenerated (114 capabilities, 35 skills).

#### web.* domain review
- 5/5 web.* capabilities promoted to `experimental`.
- `docs/DOMAIN_WEB.md`: full domain reference with capability inventory,
  binding matrix, and boundary definitions.
- `_index.yaml` updated with web.* status changes.

#### model.* domain implementation
- **6 capabilities fleshed out** (from draft stubs to full contracts):
  - `model.embedding.generate` — produce vector embedding from text.
  - `model.output.classify` — classify output into a label set.
  - `model.output.score` — score output quality on multiple axes.
  - `model.output.sanitize` — strip PII/harmful/leaked content.
  - `model.prompt.template` — interpolate variables into a prompt template.
  - `model.risk.score` — score content risk (toxicity, bias, injection).
- All 6 promoted to `experimental` status.
- `tags` and `examples` metadata added to all 8 model.* capabilities.
- `docs/DOMAIN_MODEL.md`: full domain reference with capability inventory,
  binding matrix, baseline notes, skills usage, boundary definitions.
- `_index.yaml` updated with all model.* entries and status changes.
- Catalog regenerated.

#### agent.* domain review
- **3 capabilities fleshed out** (from draft stubs to full contracts):
  - `agent.input.route` — route requests to appropriate handler/agent.
  - `agent.plan.generate` — generate structured execution plans.
  - `agent.task.delegate` — delegate tasks with safety controls.
- All 3 promoted from `draft` to `experimental`.
- `tags` and `examples` metadata added to all 5 agent.* capabilities.
- `docs/DOMAIN_AGENT.md`: full domain reference with capability inventory,
  binding matrix, baseline notes, skills usage, boundary definitions.
- `_index.yaml` updated with agent.* status changes and descriptions.
- Catalog regenerated.

#### security.* domain review
- 4 capabilities promoted from `draft` to `stable` in `_index.yaml`.
- `tags` and `examples` metadata added to all 4 security.* capabilities.
- `docs/DOMAIN_SECURITY.md`: full domain reference with capability inventory,
  binding matrix, safety gate integration docs, boundary definitions.
- Catalog regenerated.

#### eval.* domain review
- `eval.output.score` fleshed out from draft stub to full contract with
  rubric dimensions, context input, and quality_level output.
- `eval.output.score` promoted from `draft` to `experimental`.
- `tags` and `examples` metadata added to all 3 eval.* capabilities.
- `docs/DOMAIN_EVAL.md`: full domain reference with decision pipeline
  integration, skill consumption map, boundary definitions.
- `_index.yaml` updated with eval.output.score status and description.
- Catalog regenerated.
