# Security Domain — Capability Reference

> Domain: `security`  
> Capabilities: 4  
> Last reviewed: 2026-03-24

## Overview

The `security.*` domain provides content-level safety capabilities — detecting
and redacting PII, identifying leaked secrets, and gating outputs against
configurable policies. These capabilities are foundational building blocks
used as mandatory pre-gates in other capabilities (e.g. `email.message.send`)
and as composable steps in safety-conscious skills.

All implementations are **deterministic regex-based** (no LLM dependency),
ensuring consistent, auditable results with zero external calls.

### Design principles

| Principle | Rationale |
|-----------|-----------|
| **Regex-first** | PII and secret patterns are well-defined; regex gives deterministic, fast, auditable results without LLM cost. |
| **Composable gates** | `output.gate` wraps detect capabilities into a single policy-driven decision point, usable as a pre-gate on any capability. |
| **Detect → Redact pipeline** | `pii.detect` identifies findings; `pii.redact` replaces them. They can be used independently or chained. |
| **No side effects** | All 4 capabilities are read-only analysis; they never modify external state. |

---

## Capability inventory

| ID | Status | Deterministic | Side effects | Purpose |
|----|--------|---------------|--------------|---------|
| `security.pii.detect` | stable | regex-based | no | Detect email and phone PII in text |
| `security.pii.redact` | stable | regex-based | no | Replace PII with `REDACTED_*` labels |
| `security.secret.detect` | stable | regex-based | no | Detect API keys (OpenAI sk-*, AWS AKIA, GitHub ghp_) |
| `security.output.gate` | stable | yes | no | Apply composite policy gates (block_pii, block_secrets) |

---

## Binding matrix

| Capability | pythoncall (baseline) | OpenAI | Notes |
|---|---|---|---|
| `security.pii.detect` | `python_security_pii_detect` | — | Regex: email + phone patterns |
| `security.pii.redact` | `python_security_pii_redact` | — | Replaces matches with REDACTED_EMAIL / REDACTED_PHONE |
| `security.secret.detect` | `python_security_secret_detect` | — | Regex: sk-*, AKIA*, ghp_* patterns |
| `security.output.gate` | `python_security_output_gate` | — | Combines detect results against policy flags |

All bindings use the `security_baseline` service (pythoncall). No OpenAI
variants exist because regex detection is preferred over LLM for
reproducibility and auditability.

### Default selection policy

All 4 default to their pythoncall binding (the only binding available).

---

## Baseline quality notes

| Function | Coverage | Patterns |
|----------|----------|----------|
| `detect_pii()` | Email + Phone | `[A-Za-z0-9._%+-]+@...`, `\b\+?\d[\d\s-]{7,}\d\b` |
| `redact_pii()` | Same as detect | Replaces with `REDACTED_EMAIL` / `REDACTED_PHONE` |
| `detect_secret()` | OpenAI, AWS, GitHub | `sk-[A-Za-z0-9]{16,}`, `AKIA[0-9A-Z]{16}`, `ghp_[A-Za-z0-9]{20,}` |
| `gate_output()` | Composite | Checks `policy.block_pii` and `policy.block_secrets` flags |

### Known limitations

- PII detection is limited to email and phone patterns. No coverage for:
  SSN, passport numbers, credit card numbers, physical addresses.
- Secret detection covers 3 providers. Missing: Anthropic, Azure, GCP,
  Stripe, Twilio, and other common API key formats.
- No NER-based PII detection (would require LLM or spaCy).

---

## Safety gate integration

`security.pii.detect` is used as a **mandatory pre-gate** on
`email.message.send`:

```yaml
safety:
  mandatory_pre_gates:
    - capability: security.pii.detect
      on_fail: block
```

This pattern can be applied to any capability that handles sensitive output.
The runtime `SafetyGateRunner` supports four failure modes:
`block`, `warn`, `degrade`, `require_human`.

---

## Boundary definitions

- **security.pii.detect vs security.pii.redact**: `detect` returns findings
  metadata (boolean + array); `redact` returns transformed text with PII
  replaced. Use `detect` for gating decisions, `redact` for output sanitization.
- **security.output.gate vs model.risk.score**: `output.gate` is a
  deterministic policy check (PII/secrets); `model.risk.score` scores broader
  content risk (toxicity, bias, injection) using heuristics or LLM.
- **security.pii.redact vs model.output.sanitize**: `pii.redact` handles
  structured PII patterns; `model.output.sanitize` handles broader harmful
  content, data leakage, and deep recursive sanitization.
