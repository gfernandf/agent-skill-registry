# Agent Domain — Capability Reference

> Domain: `agent`  
> Capabilities: 24  
> Last reviewed: 2026-05-08

## Overview

The `agent.*` domain provides core orchestration capabilities for autonomous
agent behaviour — routing inputs, generating plans, creating skills,
delegating tasks, and generating decision options. These capabilities are
the backbone of agentic workflows and skill composition.

### Design principles

| Principle | Rationale |
|-----------|-----------|
| **Orchestration core** | All 5 capabilities deal with agent-level control flow (route, plan, delegate), not domain-specific processing. |
| **LLM-enhanced, baseline-safe** | `input.route`, `plan.generate`, and `option.generate` ship with OpenAI + pythoncall bindings. Baselines are always available offline. |
| **Elevated safety for side effects** | `task.delegate` requires user confirmation (`trust_level: elevated`) because it dispatches work to external agents. |
| **Meta-capability** | `plan.create` is a meta-capability — it generates skill YAMLs from natural language, using the registry as context. |

---

## Capability inventory

| ID | Status | Deterministic | Side effects | Bindings |
|----|--------|---------------|--------------|----------|
| `decision.input.route` | experimental | no | no | pythoncall, OpenAI chat, mock |
| `reasoning.option.generate` | experimental | no | no | pythoncall, OpenAI chat |
| `reasoning.plan.create` | experimental | no | no | pythoncall (scaffold_service) |
| `reasoning.plan.generate` | experimental | no | no | pythoncall, OpenAI chat |
| `decision.task.delegate` | experimental | no | yes | pythoncall |
| `decision.flow.branch` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.flow.iterate` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.flow.wait` | experimental | no | yes | pythoncall |
| `decision.flow.catch` | experimental | no | no | pythoncall, OpenAI chat |
| `perception.input.collect` | experimental | no | no | pythoncall, OpenAI chat |
| `reasoning.request.normalize` | experimental | no | no | pythoncall, OpenAI chat |
| `reasoning.goal.interpret` | experimental | no | no | pythoncall, OpenAI chat |
| `reasoning.criteria.define` | experimental | no | no | pythoncall, OpenAI chat |
| `perception.catalog.search` | experimental | no | no | pythoncall, OpenAI chat |
| `evaluation.catalog.rank` | experimental | no | no | pythoncall, OpenAI chat |
| `evaluation.catalog.detect` | experimental | no | no | pythoncall, OpenAI chat |
| `reasoning.task.plan` | experimental | no | no | pythoncall, OpenAI chat |
| `reasoning.plan.split` | experimental | no | no | pythoncall, OpenAI chat |
| `reasoning.plan.map` | experimental | no | no | pythoncall, OpenAI chat |
| `evaluation.plan.validate` | experimental | yes | no | pythoncall, OpenAI chat |
| `reasoning.plan.reconcile` | experimental | no | no | pythoncall, OpenAI chat |
| `reasoning.plan.synthesize` | experimental | yes | no | pythoncall, OpenAI chat |
| `evaluation.plan.gate` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.plan.execute` | stable | no | yes | pythoncall |
| `reasoning.output.generate` | experimental | no | no | pythoncall, OpenAI chat |
| `reasoning.output.synthesize` | experimental | no | no | pythoncall, OpenAI chat |

---

## Binding matrix

| Capability | pythoncall (baseline) | OpenAI chat | Mock |
|---|---|---|---|
| `decision.input.route` | `python_agent_route` — keyword match from agent list | `openapi_agent_route_openai_chat` — gpt-4o-mini, temp 0.1 | `openapi_agent_route_mock` |
| `reasoning.option.generate` | `python_agent_option_generate` — template-based 4 options | `openapi_agent_option_generate_openai_chat` — gpt-4o-mini, temp 0.4 | — |
| `reasoning.plan.create` | `python_agent_plan_create` — scaffold_service (LLM or template) | — | — |
| `reasoning.plan.generate` | `python_agent_plan_generate` — 3-step stub plan | `openapi_agent_plan_generate_openai_chat` — gpt-4o-mini, temp 0.3 | — |
| `decision.task.delegate` | `python_agent_delegate` — always accepts, returns delegation_id | — | — |
| `decision.flow.branch` | `python_agent_flow_branch` — keyword match on condition | `openapi_agent_flow_branch_openai_chat` — gpt-4o-mini | — |
| `agent.flow.iterate` | `python_agent_flow_iterate` — sequential loop | — | — |
| `agent.flow.wait` | `python_agent_flow_wait` — immediate timeout stub | — | — |
| `decision.flow.catch` | `python_agent_flow_catch` — returns default_value | `openapi_agent_flow_catch_openai_chat` — gpt-4o-mini | — |
| `perception.input.collect` | `python_agent_input_collect` — echo fields as defaults | `openapi_agent_input_collect_openai_chat` — gpt-4o-mini | — |
| `reasoning.request.normalize` | `python_agent_request_normalize` — parse user message into structured object | `openapi_agent_request_normalize_openai_chat` — gpt-4o-mini, temp 0.3 | — |
| `reasoning.goal.interpret` | `python_agent_goal_interpret` — convert normalized request to goal | `openapi_agent_goal_interpret_openai_chat` — gpt-4o-mini, temp 0.3 | — |
| `reasoning.criteria.define` | `python_agent_criteria_define` — extract success/quality criteria | `openapi_agent_criteria_define_openai_chat` — gpt-4o-mini | — |
| `perception.catalog.search` | `python_agent_catalog_search` — baseline: return fixed candidates | `openapi_agent_catalog_search_openai_chat` — gpt-4o-mini | — |
| `evaluation.catalog.rank` | `python_agent_catalog_rank` — sort candidates by relevance score | `openapi_agent_catalog_rank_openai_chat` — gpt-4o-mini | — |
| `evaluation.catalog.detect` | `python_agent_catalog_detect` — identify missing capabilities/skills | `openapi_agent_catalog_detect_openai_chat` — gpt-4o-mini | — |
| `reasoning.task.plan` | `python_agent_task_plan` — generate 3-stage macro plan | `openapi_agent_task_plan_openai_chat` — gpt-4o-mini | — |
| `reasoning.plan.split` | `python_agent_plan_split` — expand stage into executable steps | `openapi_agent_plan_split_openai_chat` — gpt-4o-mini | — |
| `reasoning.plan.map` | `python_agent_plan_map` — bind steps to $state.* paths | `openapi_agent_plan_map_openai_chat` — gpt-4o-mini | — |
| `evaluation.plan.validate` | `python_agent_plan_validate` — structural correctness (deterministic) | `openapi_agent_plan_validate_openai_chat` — gpt-4o-mini | — |
| `reasoning.plan.reconcile` | `python_agent_plan_reconcile` — repair invalid plans | `openapi_agent_plan_reconcile_openai_chat` — gpt-4o-mini | — |
| `reasoning.plan.synthesize` | `python_agent_plan_synthesize` — compile plan into DAG (deterministic) | `openapi_agent_plan_synthesize_openai_chat` — gpt-4o-mini | — |
| `evaluation.plan.gate` | `python_agent_plan_gate` — authorization check before execution | `openapi_agent_plan_gate_openai_chat` — gpt-4o-mini | — |
| `agent.plan.execute` | `python_agent_plan_execute` — execute compiled ORCA DAG with runtime enforcement | — | — |
| `reasoning.output.generate` | `python_agent_output_generate` — produce final user-facing report | `openapi_agent_output_generate_openai_chat` — gpt-4o-mini | — |
| `reasoning.output.synthesize` | `python_agent_output_synthesize` — extract reusable skill from trace | `openapi_agent_output_synthesize_openai_chat` — gpt-4o-mini, temp 0.3 | — |

### Default selection policy

- `decision.input.route` → OpenAI chat (with pythoncall fallback)
- `reasoning.option.generate` → OpenAI chat (with pythoncall fallback)
- `reasoning.plan.create` → pythoncall (scaffold_service)
- `reasoning.plan.generate` → OpenAI chat (with pythoncall fallback)
- `decision.task.delegate` → pythoncall

---

## Baseline quality notes

| Baseline | Quality | Notes |
|----------|---------|-------|
| `route_agent()` | Heuristic | Keyword match against agent names, falls back to first agent |
| `generate_options()` | Template | Returns 4 generic option archetypes (conservative/balanced/aggressive/alternative) |
| `generate_plan()` | Stub | Returns 3-step generic plan (analyse → execute → verify) |
| `generate_skill_from_prompt()` | Functional | scaffold_service — auto-detects registry, uses LLM if available, otherwise template |
| `delegate_agent()` | Stub | Always accepts; returns deterministic delegation_id |

---

## Skills using agent.* capabilities

| Skill | Capabilities used |
|-------|-------------------|
| `agent.plan-and-route` | `reasoning.plan.generate` → `decision.input.route` |
| `agent.trace` | Sidecar for execution tracing; uses `evidence.trace.analyze` + `evidence.trace.monitor` |

---

## Boundary definitions

- **decision.input.route vs decision.task.delegate**: `input.route` selects WHERE to
  send a request (read-only decision); `task.delegate` actually DISPATCHES work
  to another agent (side effect, requires confirmation).
- **reasoning.plan.generate vs reasoning.plan.create**: `plan.generate` produces an
  abstract execution plan; `plan.create` produces a concrete skill YAML file
  that can be saved and run.
- **reasoning.option.generate vs evaluation.option.score**: `option.generate` creates
  options; `evaluation.option.score` evaluates and ranks them. They are complementary
  steps in decision workflows.
- **decision.flow.branch vs decision.input.route**: `flow.branch` evaluates a local
  condition and selects a labelled branch; `input.route` selects which external
  agent or handler receives the request.
- **agent.flow.iterate vs data.array.map**: `flow.iterate` invokes a full
  capability per item (orchestration); `data.array.map` applies a lightweight
  expression (data transform).
- **decision.flow.catch vs policy.constraint.gate**: `flow.catch` handles runtime
  errors (retry, default_value, escalate); `constraint.gate` blocks requests
  that violate policy rules.
- **perception.input.collect vs decision.input.route**: `input.collect` gathers structured
  fields from a user; `input.route` decides where an already-formed request goes.
