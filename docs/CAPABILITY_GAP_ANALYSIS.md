# Capability Gap Analysis — Process Pattern

> Documented from the `research.generate-briefing` redesign.
> Apply **before** composing any new multi-step skill.

## 1. Define Outcome Requirements First

Before choosing capabilities, describe the **ideal output**:
- What fields must the consumer receive?
- What quality bar does each field need? (actionable, domain-specific, deduplicated, ranked…)
- What would a bad result look like? (generic, duplicated, empty, noise)

## 2. Audit Each Candidate Capability

For every capability the skill would `uses:`, answer:

| Question | Where to look |
|---|---|
| Does the capability YAML exist? | `agent-skill-registry/capabilities/` |
| Does it have the right inputs/outputs for this skill? | Capability YAML `inputs:` / `outputs:` |
| Does a binding exist that meets the quality bar? | `agent-skills/bindings/official/<cap>/` |
| What does the **default policy route** point to? | `policies/official_default_selection.yaml` |
| Is the routed binding an LLM or a Python baseline? | Binding YAML `protocol:` field |
| Does the Python fallback produce **honest** results? | Read the baseline `.py` function |

### Tier Classification

| Tier | Meaning | Action |
|---|---|---|
| **STABLE** | Binding produces quality output for this use case | No change |
| **GOOD** | LLM binding works; Python fallback is weak but acceptable | Improve fallback (P1) |
| **BROKEN** | Only Python baseline exists and it's a placeholder | Create LLM binding (P0) |
| **MISSING** | No capability exists for a required transformation | Create capability + binding |

## 3. Fix Gaps Before Composing

Priority order:
1. **P0 — BROKEN**: Create OpenAI binding following the `openapi` pattern (see below)
2. **P0 — MISSING**: Define capability YAML, then create binding
3. **P1 — Fallbacks**: Make Python baselines honest (mark `_fallback: True`, don't fake quality)
4. **P2 — Prompts**: Tune LLM system prompts (dedup, domain hints, output structure)

## 4. OpenAI Binding Pattern

```yaml
id: openapi_<capability_id_underscored>_openai_chat

capability: <capability.id>
service: model_openai_chat          # or text_openai_chat
protocol: openapi
operation: chat/completions

request:
  model: gpt-4o-mini
  messages:
    - role: system
      content: >
        <detailed instructions, output schema, rules>
    - role: user
      content: "${input.<field>}"
  temperature: 0.0                  # 0.0-0.2 for deterministic tasks
  response_format:
    type: json_object

response:
  <field>: response.choices.0.message.content_json.<field>

metadata:
  method: POST
  response_mode: json
  fallback_binding_id: python_<cap_underscored>
  description: "OpenAI binding for <capability.id> using gpt-4o-mini."
  status: experimental
```

## 5. Policy Routing Update

After creating a new OpenAI binding, update the default policy:

```yaml
# policies/official_default_selection.yaml
  <capability.id>: openapi_<capability_id_underscored>_openai_chat
```

## 6. Validate

1. `python tools/validate_registry.py` — registry integrity
2. `python validate_bindings.py` — binding consistency (from agent-skills)
3. E2E run with real input — check each output field against quality bar

## 7. Lessons from research.generate-briefing

| Before Gap Analysis | After Gap Analysis |
|---|---|
| Keywords: stop-word filter → generic noise | Keywords: LLM extraction → "European green hydrogen market", "electrolysis technology", "EU regulatory framework" |
| Entities: empty `[]` fallback | Entities: deduplicated, canonical forms → "ACER", "BloombergNEF", "EU" |
| Clusters: round-robin → theme_1..5, hardcoded coherence 0.6 | Clusters: semantic grouping → "market_overview" (4 items, 0.9), "trends" (1 item, 0.7) |
| Risks: 2 generic hardcoded | Risks: 5 domain-specific → "renewable hydrogen costs", "regulatory hurdles" |
| Quality score: non-empty ratio → always 85+ | Quality: structural + depth heuristic (P1 improved) |
