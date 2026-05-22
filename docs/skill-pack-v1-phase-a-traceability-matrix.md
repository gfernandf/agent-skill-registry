# Skill Pack V1 - Phase A Traceability Matrix

Date: 2026-05-12
Scope: task.frame, decision.make, web.search-summary, data.parse-and-validate, security.safe-summarize

## Purpose

This document freezes the Phase A baseline with evidence-based traceability:

- canonical skill contract in registry
- capability dependency graph
- runtime binding path and default selection behavior
- existing test evidence
- P0/P1/P2 risks to drive Phase B hardening

## Cross-repo baseline controls

- Contract source of truth: `agent-skill-registry/skills/official/**/skill.yaml`.
- Dependency source: `agent-skill-registry/catalog/graph.json`.
- Runtime default selection: `agent-skills/policies/official_default_selection.yaml`.
- Runtime resolver behavior: `agent-skills/runtime/binding_resolver.py`.
- Historical execution evidence: `agent-skills/test_results/*`, `agent-skills/artifacts/runtime_skill_audit.jsonl`.

## Matrix

## 1) data.parse-and-validate

- Skill contract:
  - `agent-skill-registry/skills/official/data/parse-and-validate/skill.yaml`
- Capabilities (registry graph):
  - `data.json.parse`
  - `data.schema.validate`
- Runtime bindings (official):
  - `agent-skills/bindings/official/data.json.parse/python_data_json_parse.yaml`
  - `agent-skills/bindings/official/data.schema.validate/python_data_schema_validate.yaml`
  - Additional experimental binding present for schema validate:
    - `agent-skills/bindings/official/data.schema.validate/openapi_data_schema_validate_mock.yaml`
- Default selection:
  - `data.json.parse: python_data_json_parse`
  - `data.schema.validate: python_data_schema_validate`
  - Source: `agent-skills/policies/official_default_selection.yaml`
- Test evidence found:
  - Sweep pass entry: `agent-skills/test_results/skill_sweep_v3.txt` (shows PASS for `data.parse-and-validate`)
  - Runtime audit historical failures/success snapshots present in `agent-skills/artifacts/runtime_skill_audit.jsonl`
- Maturity (Phase A): `partial-ready`
- Risks:
  - P0: none identified for current baseline.
  - P1: catalog metadata status remains unspecified for this skill in generated artifacts.
  - P1: example IO naming drift (`raw_data`/`parsed`) vs contract (`text`/`data`) in metadata generator patterns.
  - P2: explicit parse-error vs schema-error taxonomy not standardized in skill-level docs.

## 2) web.search-summary

- Skill contract:
  - `agent-skill-registry/skills/official/web/search-summary/skill.yaml`
- Capabilities (registry graph):
  - `web.source.search`
  - `text.content.merge`
  - `text.content.summarize`
- Runtime bindings (official):
  - `agent-skills/bindings/official/web.source.search/python_web_source_search.yaml`
  - `agent-skills/bindings/official/text.content.merge/pythoncall.yaml`
  - `agent-skills/bindings/official/text.content.summarize/python_text_summarize.yaml`
  - OpenAPI alternative exists for summarize:
    - `agent-skills/bindings/official/text.content.summarize/openapi_text_summarize_openai_chat.yaml`
- Default selection:
  - `web.source.search: python_web_source_search`
  - `text.content.merge: python_text_merge`
  - `text.content.summarize: python_text_summarize`
  - Source: `agent-skills/policies/official_default_selection.yaml`
- Test evidence found:
  - Historical failure traces for this skill in `agent-skills/test_results/skill_sweep.txt`
  - Later sweep includes this skill in PASS run set in `agent-skills/test_results/skill_sweep_v3.txt`
- Maturity (Phase A): `partial-ready`
- Risks:
  - P0: no active blocker after latest pass evidence.
  - P1: contract under-specifies behavior for empty search results and noisy inputs.
  - P1: `limit` has weak constraints (bounds/default semantics unspecified).
  - P2: summary quality envelope not explicitly standardized (length/structure expectations).

## 3) task.frame

- Skill contract:
  - `agent-skill-registry/skills/official/task/frame/skill.yaml`
- Capabilities (registry graph):
  - `text.content.classify`
  - `text.content.extract`
  - `agent.plan.generate`
  - `agent.input.route`
- Runtime bindings (official):
  - `agent-skills/bindings/official/text.content.classify/python_text_classify.yaml`
  - `agent-skills/bindings/official/text.content.extract/python_text_extract.yaml`
  - `agent-skills/bindings/official/agent.plan.generate/python_agent_plan_generate.yaml`
  - `agent-skills/bindings/official/agent.input.route/python_agent_route.yaml`
  - OpenAPI alternatives exist for classify/plan.generate/input.route and can be selected by environment-preferred policy.
- Default selection:
  - `text.content.classify: openapi_text_classify_openai_chat`
  - `text.content.extract: python_text_extract`
  - `agent.plan.generate: openapi_agent_plan_generate_openai_chat`
  - `agent.input.route: openapi_agent_route_openai_chat`
  - Source: `agent-skills/policies/official_default_selection.yaml`
- Resolver behavior relevant:
  - Environment-aware preference and python-preferred list in `agent-skills/runtime/binding_resolver.py`
  - `agent.plan.generate` and `agent.input.route` are not in python-preferred capability set.
- Test evidence found:
  - Included in `agent-skills/test_new_skills.py`
  - Historical failure samples for output mapping in `agent-skills/artifacts/runtime_skill_audit.jsonl`
  - OpenAI trace evidence in `agent-skills/test_results/openai_frame_trace.txt`
- Maturity (Phase A): `partial-ready`
- Risks:
  - P0: none confirmed active in latest pass set, but historical mapping failures exist and warrant guard tests.
  - P1: optional output presence policy is implicit (not explicit for `objectives`, `constraints_extracted`, `information_needed`).
  - P1: metadata examples show naming drift (`goal` in example input vs `task` in contract).
  - P2: mixed OpenAPI/Python defaults can increase output variance without deterministic profile gate.

## 4) security.safe-summarize

- Skill contract:
  - `agent-skill-registry/skills/official/security/safe-summarize/skill.yaml`
- Capabilities (registry graph):
  - `security.pii.detect`
  - `security.pii.redact`
  - `text.content.summarize`
  - `security.output.gate`
  - `text.content.transform`
- Runtime bindings (official):
  - `agent-skills/bindings/official/security.pii.detect/python_security_pii_detect.yaml`
  - `agent-skills/bindings/official/security.pii.redact/python_security_pii_redact.yaml`
  - `agent-skills/bindings/official/text.content.summarize/python_text_summarize.yaml`
  - `agent-skills/bindings/official/security.output.gate/python_security_output_gate.yaml`
  - `agent-skills/bindings/official/text.content.transform/python_text_transform.yaml`
- Default selection:
  - `security.pii.detect: python_security_pii_detect`
  - `security.pii.redact: python_security_pii_redact`
  - `security.output.gate: python_security_output_gate`
  - `text.content.summarize: python_text_summarize`
  - `text.content.transform: openapi_text_transform_openai_chat`
  - Source: `agent-skills/policies/official_default_selection.yaml`
- Test evidence found:
  - Historical failure in `agent-skills/test_results/skill_sweep.txt`
  - Later sweep PASS in `agent-skills/test_results/skill_sweep_v3.txt`
- Maturity (Phase A): `partial-ready (status currently experimental in registry metadata)`
- Risks:
  - P0: production-readiness blocker at governance level due to `metadata.status: experimental` in skill contract.
  - P1: blocked-output determinism should be pinned by tests (sentinel text path is policy-critical).
  - P1: adversarial PII coverage not visible in current dedicated test set.
  - P2: transform step defaulting to OpenAPI can introduce variance in blocked/non-blocked final wording.

## 5) decision.make

- Skill contract:
  - `agent-skill-registry/skills/official/decision/make/skill.yaml`
- Capabilities (registry graph):
  - `text.content.merge`
  - `agent.option.generate`
  - `eval.option.analyze`
  - `eval.option.score`
  - `decision.option.justify`
  - `eval.output.score`
- Runtime bindings (official):
  - `agent-skills/bindings/official/text.content.merge/pythoncall.yaml`
  - `agent-skills/bindings/official/agent.option.generate/python_agent_option_generate.yaml`
  - `agent-skills/bindings/official/eval.option.analyze/python_eval_option_analyze.yaml`
  - `agent-skills/bindings/official/eval.option.score/python_eval_option_score.yaml`
  - `agent-skills/bindings/official/decision.option.justify/python_decision_option_justify.yaml`
  - `agent-skills/bindings/official/eval.output.score/python_eval_output_score.yaml`
  - OpenAPI alternatives exist for several of these steps and appear in real traces.
- Default selection:
  - `agent.option.generate: openapi_agent_option_generate_openai_chat`
  - `eval.option.analyze: openapi_eval_option_analyze_openai_chat`
  - `eval.option.score: openapi_eval_option_score_openai_chat`
  - `decision.option.justify: openapi_decision_option_justify_openai_chat`
  - `eval.output.score: openapi_eval_output_score_openai_chat`
  - `text.content.merge: python_text_merge`
  - Source: `agent-skills/policies/official_default_selection.yaml`
- Test evidence found:
  - Included in `agent-skills/test_new_skills.py`
  - OpenAI trace evidence in `agent-skills/test_results/openai_decision_trace.txt`
  - Historical failures and later pass trajectory in `agent-skills/artifacts/runtime_skill_audit.jsonl` and `agent-skills/test_results/skill_sweep_v3.txt`
- Maturity (Phase A): `partial-ready (high-complexity)`
- Risks:
  - P0: no active hard blocker confirmed in latest sweep, but this skill has the highest drift surface due to many required outputs.
  - P1: deterministic behavior must be pinned for missing `context_items`, `options`, and default `risk_tolerance`.
  - P1: quality-gate behavior for low-confidence outcomes lacks explicit release policy contract.
  - P2: mixed python/openapi execution paths can create output variance without profile constraints.

## Phase A summary status

- `data.parse-and-validate`: partial-ready
- `web.search-summary`: partial-ready
- `task.frame`: partial-ready
- `security.safe-summarize`: partial-ready (governance blocker: experimental status)
- `decision.make`: partial-ready (highest complexity/risk)

## Phase B entry backlog (ordered)

1. data.parse-and-validate
2. web.search-summary
3. task.frame
4. security.safe-summarize
5. decision.make

Reason for order:

- start from lowest contract complexity and fastest closure
- then stabilize search + framing
- then harden safety gate skill
- finish with highest output-surface decision skill
