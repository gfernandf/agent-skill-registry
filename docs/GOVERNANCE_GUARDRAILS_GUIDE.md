# Governance Guardrails Guide

> What each governance tool checks, how to run them, and how CI enforces them.

---

## Overview

The registry includes four governance tools that run in sequence:

```bash
python tools/validate_registry.py
python tools/governance_guardrails.py --fail-on-high-risk-overlap-channels community,official
python tools/capability_governance_guardrails.py
python tools/enforce_capability_sunset.py
```

CI runs them before `generate_catalog.py`. All must pass for CI to succeed.

---

## 1. `validate_registry.py` — Schema & Vocabulary Compliance

**What it checks:**

| Check | Scope | Severity |
|---|---|---|
| Required fields (`id`, `version`, `description`, `inputs`, `outputs`) | Capabilities | Error |
| Capability ID vocabulary compliance (domain, noun, verb) | Capabilities | Error |
| `metadata.status` is one of `draft`, `experimental`, `stable`, `deprecated`, `unspecified` | Both | Error |
| `cognitive_hints.role` matches `cognitive_types.yaml` roles | Capabilities | Error |
| `cognitive_hints.produces` fields match declared outputs | Capabilities | Error |
| `cognitive_hints.produces.*.type` matches `cognitive_types.yaml` types | Capabilities | Error |
| `safety` block required when `properties.side_effects: true` | Capabilities | Error |
| `safety.*` fields match `safety_vocabulary.yaml` enumerations | Capabilities | Error |
| Skill step references, input/output mapping | Skills | Error |
| Classification block required for `official`/`community` skills | Skills | Error |

**How to run:**

```bash
python tools/validate_registry.py
python tools/validate_registry.py --base /path/to/registry  # custom root
```

**Exit codes:** 0 = pass, 1 = validation errors.

---

## 2. `governance_guardrails.py` — Skill Overlap & Metadata Quality

**What it checks:**

### Overlap detection

Compares every pair of skills by:
1. **Capability Jaccard**: overlap of `uses_capabilities` sets.
2. **Output Jaccard**: overlap of output field names.
3. **Combined score**: `0.75 × cap_jaccard + 0.25 × output_jaccard`.

Alerts are emitted when:
- `combined_score ≥ overlap_threshold` (default 0.8).
- The pair shares at least `min_shared_capabilities` (default 2).

Risk classification:
- **high**: combined ≥ 0.9
- **medium**: combined ≥ 0.8 but < 0.9

### Metadata quality

For each skill, checks for:
- `missing_metadata` — no `metadata` block at all.
- `missing_use_cases` — empty or absent `metadata.use_cases`.
- `missing_examples` — empty or absent `metadata.examples`.
- `missing_tags` — empty or absent `metadata.tags`.
- `missing_classification` — no `metadata.classification.role`.

### Unknown capability references

Skills referencing capability IDs that don't exist in the catalog.

**Key CLI flags:**

| Flag | Effect |
|---|---|
| `--overlap-threshold 0.8` | Minimum combined score to flag a pair |
| `--min-shared-capabilities 2` | Minimum shared capabilities to consider |
| `--fail-on-overlap` | Exit 1 on any overlap alert |
| `--fail-on-high-risk-overlap-channels community,official` | Exit 1 on high-risk overlaps in specified channels |
| `--fail-on-metadata-channels official` | Exit 1 on metadata issues in specified channels |
| `--fail-on-metadata-issues missing_metadata` | Which issue IDs are blockers |

**Output:** `catalog/governance_guardrails.json`

---

## 3. `capability_governance_guardrails.py` — Semantic Families & Domain Coverage

**What it checks:**

### Semantic family alerts

Groups capabilities by `(domain, verb)`. When multiple capabilities share
the same domain and verb (e.g., `eval.option.score` and `eval.output.score`),
it flags them for review — are they genuinely distinct, or should they be
merged into one capability with a broader noun?

### Duplicate descriptions

Flags capabilities whose normalized descriptions are identical — they may
represent the same operation under different IDs.

### Uncovered domains

Compares the set of domains used by capabilities against the domains defined
in `vocabulary/vocabulary.json`. Domains with zero capabilities are flagged.

### Metadata issues

- `missing_tags` — no `metadata.tags` or empty list.
- `missing_examples` — no `metadata.examples` or empty list.
- `missing_metadata` — no `metadata` block.

**Output:** `catalog/capability_governance_guardrails.json`

---

## 4. `enforce_capability_sunset.py` — Deprecated Capability Lifecycle

**What it checks:**

For every capability with `metadata.status: deprecated` or `deprecated: true`:

| Rule | Detail |
|---|---|
| `replacement` must be a non-empty string | Points to the successor capability |
| `metadata.deprecation_date` must be ISO 8601 | When deprecation was declared |
| `metadata.sunset_date` must be ISO 8601 | When the capability will be removed |
| `sunset_date > deprecation_date` | Logical ordering |
| Window ≥ 30 days | Minimum grace period (configurable via `--minimum-window-days`) |
| `sunset_date` not expired | Expired sunsets → remove or extend |

**How to run:**

```bash
python tools/enforce_capability_sunset.py
python tools/enforce_capability_sunset.py --minimum-window-days 60
```

---

## CI integration

CI runs the full sequence:

```bash
python tools/validate_registry.py
python tools/governance_guardrails.py --fail-on-high-risk-overlap-channels community,official
python tools/capability_governance_guardrails.py
python tools/enforce_capability_sunset.py
python tools/generate_catalog.py
python tools/registry_stats.py
```

After generation, CI checks catalog freshness:

```bash
git diff --exit-code -- catalog
```

If any catalog file differs from what's committed, CI fails. This ensures
the catalog is always regenerated and committed together with source changes.

---

## Common failure scenarios

| Symptom | Cause | Fix |
|---|---|---|
| `unknown domain 'foo'` | Capability ID uses a domain not in vocabulary | Add domain to `vocabulary.json` or fix the ID |
| `unknown verb 'bar'` | Verb not in vocabulary | Add verb to `vocabulary.json` or fix the ID |
| `high-risk overlap` in CI | Two skills share ≥90% capabilities | Merge skills or differentiate their capability sets |
| `sunset_date is expired` | Deprecated capability past removal date | Remove the capability or extend the sunset date |
| `git diff --exit-code -- catalog` fails | Catalog not regenerated after changes | Run the full sequence and commit catalog changes |
