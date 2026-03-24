# Agent Domain — Capability Reference

> Domain: `agent`  
> Capabilities: 5  
> Last reviewed: 2026-03-24

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

---

## Binding matrix

| Capability | pythoncall (baseline) | OpenAI chat | Mock |
|---|---|---|---|
| `agent.input.route` | `python_agent_route` — keyword match from agent list | `openapi_agent_route_openai_chat` — gpt-4o-mini, temp 0.1 | `openapi_agent_route_mock` |
| `agent.option.generate` | `python_agent_option_generate` — template-based 4 options | `openapi_agent_option_generate_openai_chat` — gpt-4o-mini, temp 0.4 | — |
| `agent.plan.create` | `python_agent_plan_create` — scaffold_service (LLM or template) | — | — |
| `agent.plan.generate` | `python_agent_plan_generate` — 3-step stub plan | `openapi_agent_plan_generate_openai_chat` — gpt-4o-mini, temp 0.3 | — |
| `agent.task.delegate` | `python_agent_delegate` — always accepts, returns delegation_id | — | — |

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
