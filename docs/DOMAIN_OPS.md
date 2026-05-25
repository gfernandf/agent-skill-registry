# Ops Domain — Capability Reference

> Domain: `ops`  
> Capabilities: 3  
> Last reviewed: 2026-05-08

## Overview

The `ops.*` domain provides operational and observability capabilities for
agent execution — tracing, monitoring, and auditing runtime behavior. These
capabilities enable visibility into execution timelines, resource usage,
and failure scenarios.

### Design principles

| Principle | Rationale |
|-----------|-----------|
| **Execution transparency** | All ops capabilities focus on observability — extracting facts from traces, not controlling execution. |
| **Deterministic analysis** | `trace.analyze` and `trace.summarize` are deterministic — they extract structured facts from raw execution data without side effects. |
| **Real-time awareness** | `trace.monitor` provides streaming or batch event analysis for operational dashboards and alerting. |
| **Audit-grade records** | Ops capabilities support regulatory compliance through detailed execution trails and decision records. |

---

## Capability inventory

| ID | Status | Deterministic | Purpose |
|----|--------|---------------|---------|
| `evidence.trace.analyze` | experimental | yes | Analyse execution trace for patterns and anomalies |
| `evidence.trace.monitor` | experimental | yes | Monitor live trace events for alerts and dashboards |
| `evidence.trace.summarize` | experimental | yes | Summarize execution trace into compact structured report |

---

## Binding matrix

| Capability | pythoncall (baseline) | OpenAI chat | Notes |
|---|---|---|---|
| `evidence.trace.analyze` | `python_ops_analyze_trace` — structured fact extraction | — | Deterministic analysis, no LLM needed |
| `evidence.trace.monitor` | `python_ops_monitor_trace` — event stream aggregation | — | Real-time streaming capability |
| `evidence.trace.summarize` | `python_ops_trace_summarize` — extract steps/failures/duration | `openapi_ops_trace_summarize_openai_chat` — gpt-4o-mini, temp 0.0 | Natural language summary with LLM |

### Default selection policy

- `evidence.trace.analyze` → pythoncall (deterministic, no LLM needed)
- `evidence.trace.monitor` → pythoncall (streaming-first)
- `evidence.trace.summarize` → OpenAI chat (with pythoncall fallback)

---

## Baseline quality notes

| Function | Quality | Notes |
|----------|---------|-------|
| `analyze_trace()` | Deterministic | Extracts step counts, durations, error patterns — no inference |
| `monitor_trace()` | Deterministic | Aggregates events by type and severity for dashboard feeds |
| `summarize_trace()` | Deterministic baseline | Returns structured summary (steps, decisions, failures, duration, success_rate) |

---

## Skills using ops.* capabilities

| Skill | Capabilities used |
|-------|-------------------|
| `agent.trace` | `evidence.trace.analyze` + `evidence.trace.monitor` (observability sidecar) |

---

## Use cases

### Execution auditing
```
plan.run() → evidence.trace.summarize() → audit_log
```
Captures what was executed, when, and what failed — useful for compliance.

### Real-time dashboards
```
plan.run() (streaming trace) → evidence.trace.monitor() (every 100ms) → dashboard feed
```
Live operational visibility for long-running agents.

### Failure diagnosis
```
Failed execution → evidence.trace.analyze() → error_pattern extraction
```
Quickly identify whether the failure was deterministic, rate-limited, or transient.
