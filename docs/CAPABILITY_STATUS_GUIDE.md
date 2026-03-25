# Capability Status Guide

> Lifecycle statuses, promotion paths, and what each status means.

---

## Status values

The validator (`tools/validate_registry.py`) enforces these statuses:

| Status | Meaning |
|---|---|
| **draft** | Stub — has an ID and minimal metadata but no finalized contract (inputs/outputs may be incomplete or placeholder). Not executable. |
| **experimental** | Has a full contract (inputs, outputs, properties). Under validation; may change without notice. |
| **stable** | Tested, reviewed, and production-ready. Breaking changes require a deprecation cycle. |
| **deprecated** | Scheduled for removal. Must declare `replacement`, `deprecation_date`, and `sunset_date`. |
| **unspecified** | Legacy or uncategorized. Treated as experimental for governance purposes. |

---

## Current registry snapshot

As of v0.1.0:

- **6 capabilities** marked `draft` — stubs with placeholder contracts.
- **109 capabilities** marked `experimental` — contracts defined, under validation.
- **7 capabilities** marked `stable` — contracts finalized, production-ready.
- **0 capabilities** marked `deprecated`.

---

## Promotion path

```
draft  →  experimental  →  stable  →  (deprecated → removed)
```

### draft → experimental

Requirements:
- Complete `inputs` and `outputs` with types and descriptions.
- Valid `description` (not a placeholder).
- Capability ID passes vocabulary compliance (`validate_registry.py`).
- At least one binding exists in `agent-skills` (Python baseline preferred).

### experimental → stable

Requirements:
- At least one binding tested end-to-end (`test_capabilities_batch.py` passes).
- `cognitive_hints` block present and vocabulary-compliant (if applicable).
- `metadata.tags` populated.
- `metadata.examples` populated with at least one example.
- No unresolved governance alerts for this capability.

### stable → deprecated

Requirements:
- `metadata.status: deprecated`
- `replacement` field pointing to the successor capability ID.
- `metadata.deprecation_date` (ISO 8601) — when deprecation was declared.
- `metadata.sunset_date` (ISO 8601) — when the capability will be removed.
- Sunset window must be ≥ 30 days (enforced by `tools/enforce_capability_sunset.py`).
- `sunset_date` must be in the future (expired sunsets fail CI).

---

## Governance enforcement

### `validate_registry.py`

Validates status is one of the 5 allowed values. Also checks:
- Capability ID vocabulary compliance (domain, noun, verb).
- Required fields: `id`, `version`, `description`, `inputs`, `outputs`.
- `cognitive_hints` field/type alignment against `cognitive_types.yaml`.
- `safety` block presence when `properties.side_effects: true`.

### `capability_governance_guardrails.py`

Advisory checks on the entire capability set:
- **Semantic family alerts**: flags capabilities sharing the same `(domain, verb)` pair
  with different nouns — review whether they should be merged.
- **Duplicate descriptions**: flags capabilities with identical normalized descriptions.
- **Uncovered domains**: domains listed in vocabulary but with zero capabilities.
- **Metadata issues**: missing `tags` or `examples`.

### `governance_guardrails.py`

Skill-level checks (not capability-level), but relevant because skills reference
capabilities:
- **Unknown capability references**: skills referencing non-existent capability IDs.
- **Overlap alerts**: skill pairs with high Jaccard similarity on capabilities/outputs.
- **Metadata quality**: missing `use_cases`, `examples`, `tags`, `classification`.

### `enforce_capability_sunset.py`

- Deprecated capabilities must have `replacement`, `deprecation_date`, `sunset_date`.
- `sunset_date > deprecation_date`.
- Sunset window ≥ 30 days.
- `sunset_date` must not be expired.

---

## How to check status

```bash
# Count by status
python tools/registry_stats.py

# Full validation
python tools/validate_registry.py

# Governance report
python tools/capability_governance_guardrails.py
```

The generated `catalog/stats.json` includes a `by_status` breakdown when
statuses are populated.
