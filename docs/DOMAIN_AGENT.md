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
| `agent.input.route` | experimental | no | no | pythoncall, OpenAI chat, mock |
| `agent.option.generate` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.plan.create` | experimental | no | no | pythoncall (scaffold_service) |
| `agent.plan.generate` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.task.delegate` | experimental | no | yes | pythoncall |
| `agent.flow.branch` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.flow.iterate` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.flow.wait` | experimental | no | yes | pythoncall |
| `agent.flow.catch` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.input.collect` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.request.normalize` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.goal.interpret` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.criteria.define` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.catalog.search` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.catalog.rank` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.catalog.detect` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.task.plan` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.plan.split` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.plan.map` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.plan.validate` | experimental | yes | no | pythoncall, OpenAI chat |
| `agent.plan.reconcile` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.plan.synthesize` | experimental | yes | no | pythoncall, OpenAI chat |
| `agent.plan.gate` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.plan.run` | experimental | no | yes | pythoncall, OpenAI chat |
| `agent.output.generate` | experimental | no | no | pythoncall, OpenAI chat |
| `agent.output.synthesize` | experimental | no | no | pythoncall, OpenAI chat |

---

## Binding matrix

| Capability | pythoncall (baseline) | OpenAI chat | Mock |
|---|---|---|---|
| `agent.input.route` | `python_agent_route` — keyword match from agent list | `openapi_agent_route_openai_chat` — gpt-4o-mini, temp 0.1 | `openapi_agent_route_mock` |
| `agent.option.generate` | `python_agent_option_generate` — template-based 4 options | `openapi_agent_option_generate_openai_chat` — gpt-4o-mini, temp 0.4 | — |
| `agent.plan.create` | `python_agent_plan_create` — scaffold_service (LLM or template) | — | — |
| `agent.plan.generate` | `python_agent_plan_generate` — 3-step stub plan | `openapi_agent_plan_generate_openai_chat` — gpt-4o-mini, temp 0.3 | — |
| `agent.task.delegate` | `python_agent_delegate` — always accepts, returns delegation_id | — | — |
| `agent.flow.branch` | `python_agent_flow_branch` — keyword match on condition | `openapi_agent_flow_branch_openai_chat` — gpt-4o-mini | — |
| `agent.flow.iterate` | `python_agent_flow_iterate` — sequential loop | — | — |
| `agent.flow.wait` | `python_agent_flow_wait` — immediate timeout stub | — | — |
| `agent.flow.catch` | `python_agent_flow_catch` — returns default_value | `openapi_agent_flow_catch_openai_chat` — gpt-4o-mini | — |
| `agent.input.collect` | `python_agent_input_collect` — echo fields as defaults | `openapi_agent_input_collect_openai_chat` — gpt-4o-mini | — |
| `agent.request.normalize` | `python_agent_request_normalize` — parse user message into structured object | `openapi_agent_request_normalize_openai_chat` — gpt-4o-mini, temp 0.3 | — |
| `agent.goal.interpret` | `python_agent_goal_interpret` — convert normalized request to goal | `openapi_agent_goal_interpret_openai_chat` — gpt-4o-mini, temp 0.3 | — |
| `agent.criteria.define` | `python_agent_criteria_define` — extract success/quality criteria | `openapi_agent_criteria_define_openai_chat` — gpt-4o-mini | — |
| `agent.catalog.search` | `python_agent_catalog_search` — baseline: return fixed candidates | `openapi_agent_catalog_search_openai_chat` — gpt-4o-mini | — |
| `agent.catalog.rank` | `python_agent_catalog_rank` — sort candidates by relevance score | `openapi_agent_catalog_rank_openai_chat` — gpt-4o-mini | — |
| `agent.catalog.detect` | `python_agent_catalog_detect` — identify missing capabilities/skills | `openapi_agent_catalog_detect_openai_chat` — gpt-4o-mini | — |
| `agent.task.plan` | `python_agent_task_plan` — generate 3-stage macro plan | `openapi_agent_task_plan_openai_chat` — gpt-4o-mini | — |
| `agent.plan.split` | `python_agent_plan_split` — expand stage into executable steps | `openapi_agent_plan_split_openai_chat` — gpt-4o-mini | — |
| `agent.plan.map` | `python_agent_plan_map` — bind steps to $state.* paths | `openapi_agent_plan_map_openai_chat` — gpt-4o-mini | — |
| `agent.plan.validate` | `python_agent_plan_validate` — structural correctness (deterministic) | `openapi_agent_plan_validate_openai_chat` — gpt-4o-mini | — |
| `agent.plan.reconcile` | `python_agent_plan_reconcile` — repair invalid plans | `openapi_agent_plan_reconcile_openai_chat` — gpt-4o-mini | — |
| `agent.plan.synthesize` | `python_agent_plan_synthesize` — compile plan into DAG (deterministic) | `openapi_agent_plan_synthesize_openai_chat` — gpt-4o-mini | — |
| `agent.plan.gate` | `python_agent_plan_gate` — authorization check before execution | `openapi_agent_plan_gate_openai_chat` — gpt-4o-mini | — |
| `agent.plan.run` | `python_agent_plan_run` — execute compiled plan (stub: returns success) | `openapi_agent_plan_run_openai_chat` — gpt-4o-mini, temp 0.1 | — |
| `agent.output.generate` | `python_agent_output_generate` — produce final user-facing report | `openapi_agent_output_generate_openai_chat` — gpt-4o-mini | — |
| `agent.output.synthesize` | `python_agent_output_synthesize` — extract reusable skill from trace | `openapi_agent_output_synthesize_openai_chat` — gpt-4o-mini, temp 0.3 | — |

### Default selection policy

- `agent.input.route` → OpenAI chat (with pythoncall fallback)
- `agent.option.generate` → OpenAI chat (with pythoncall fallback)
- `agent.plan.create` → pythoncall (scaffold_service)
- `agent.plan.generate` → OpenAI chat (with pythoncall fallback)
- `agent.task.delegate` → pythoncall

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
| `agent.plan-and-route` | `agent.plan.generate` → `agent.input.route` |
| `agent.trace` | Sidecar for execution tracing; uses `ops.trace.analyze` + `ops.trace.monitor` |

---

## Boundary definitions

- **agent.input.route vs agent.task.delegate**: `input.route` selects WHERE to
  send a request (read-only decision); `task.delegate` actually DISPATCHES work
  to another agent (side effect, requires confirmation).
- **agent.plan.generate vs agent.plan.create**: `plan.generate` produces an
  abstract execution plan; `plan.create` produces a concrete skill YAML file
  that can be saved and run.
- **agent.option.generate vs eval.option.score**: `option.generate` creates
  options; `eval.option.score` evaluates and ranks them. They are complementary
  steps in decision workflows.
- **agent.flow.branch vs agent.input.route**: `flow.branch` evaluates a local
  condition and selects a labelled branch; `input.route` selects which external
  agent or handler receives the request.
- **agent.flow.iterate vs data.array.map**: `flow.iterate` invokes a full
  capability per item (orchestration); `data.array.map` applies a lightweight
  expression (data transform).
- **agent.flow.catch vs policy.constraint.gate**: `flow.catch` handles runtime
  errors (retry, default_value, escalate); `constraint.gate` blocks requests
  that violate policy rules.
- **agent.input.collect vs agent.input.route**: `input.collect` gathers structured
  fields from a user; `input.route` decides where an already-formed request goes.
