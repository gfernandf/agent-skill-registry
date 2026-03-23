# Capabilities

Capabilities define the **primitive operations** available in the Agent Skill Registry.

They represent reusable functional building blocks that can be composed into workflows using skills.

Capabilities form the **core language of the registry** and are therefore governed by a controlled vocabulary.

---

# Purpose

A capability represents a **single functional operation** that can be reused across many workflows.

Examples include:

```
text.content.summarize
text.content.classify
text.keyword.extract
web.page.fetch
data.json.parse
fs.file.read
```

Capabilities should be:

- reusable
- composable
- predictable
- domain-independent when possible

Skills combine capabilities into higher-level workflows.

---

# Capability Identifier

Each capability is identified by an **ID**.

Allowed forms:

```
domain.verb
domain.noun.verb
```

Examples:

```
text.content.summarize
fs.file.read
web.page.fetch
data.json.parse
text.keyword.extract
web.page.fetch
```

The maximum number of identifier segments is **three**.

Invalid examples:

```
data.json.schema.validate
web.page.article.extract
text.entity.named.extract
```

Capability identifiers must conform to the **controlled vocabulary** defined in:

```
vocabulary/vocabulary.json
```

Human-readable guidance is provided in:

```
docs/VOCABULARY.md
```

---

# File Location

Capabilities are stored as individual YAML files.

```
capabilities/<capability-id>.yaml
```

Examples:

```
capabilities/text.content.summarize.yaml
capabilities/text.keyword.extract.yaml
capabilities/data.json.parse.yaml
capabilities/web.page.fetch.yaml
```

The filename must match the capability ID.

---

# Capability Format

A capability file is written in YAML and follows a defined structure.

Example:

```yaml
id: text.content.summarize
version: 1.0.0
description: Produce a concise summary of text content.

inputs:
  text:
    type: string
    required: true
    description: Text to summarize.

outputs:
  summary:
    type: string
    required: true
    description: Generated summary.

properties:
  deterministic: false
  side_effects: false
  idempotent: true
```

---

# Required Fields

## id

Unique identifier of the capability.

Must follow the allowed identifier structure and vocabulary rules.

Example:

```
text.content.summarize
data.json.parse
text.keyword.extract
```

---

## version

Version of the capability definition.

Example:

```
1.0.0
```

Versioning allows capability definitions to evolve while preserving compatibility.

---

## description

Human-readable description of the capability's purpose.

This should explain what the capability does and when it should be used.

---

## inputs

Defines the inputs required by the capability.

Each input must specify:

- type
- whether it is required
- optional description

Example:

```
inputs:
  text:
    type: string
    required: true
```

---

## outputs

Defines the outputs produced by the capability.

Each output must specify:

- type
- whether it is required
- optional description

Example:

```
outputs:
  summary:
    type: string
    required: true
```

---

# Optional Fields

## metadata (Optional)

Capabilities may optionally include a `metadata` block used for discovery, categorization, and documentation.

Example:

```yaml
metadata:
  tags:
    - text
    - analysis
  category: analysis
  status: stable
  examples:
    - description: Classify an input text
      input:
        text: "I want a refund"
        labels: ["billing", "refund", "technical"]
      output:
        label: "refund"
```

The `metadata` block is optional and does not change the functional meaning of the capability.

If omitted, tools may treat it as an empty/default metadata block.

### Suggested Fields

The following optional fields may appear inside `metadata`:

- `tags`
- `category`
- `status`
- `examples`

### Logical Defaults

If metadata is omitted, tools may interpret it as:

```yaml
metadata:
  tags: []
  category: null
  status: unspecified
  examples: []
```

These defaults are conceptual and do not need to be materialized in source YAML.

### Intended Purpose

Capability metadata is intended to support:

- discovery
- categorization
- registry browsing
- documentation
- future statistics and analytics

It is not intended to change execution behavior.

### Deprecation Lifecycle Metadata

When `metadata.status` is set to `deprecated`, lifecycle dates are required by
policy:

- `metadata.deprecation_date` (YYYY-MM-DD)
- `metadata.sunset_date` (YYYY-MM-DD)

Deprecated capabilities must also define top-level `replacement`.

See:

- `docs/CAPABILITY_SUNSET_POLICY.md`

---

## cognitive_hints (Optional)

Capabilities may optionally include a `cognitive_hints` block that declares how
the capability interacts with the CognitiveState runtime layer.

When present, the block is **normative** — meaning validators enforce its
structure and the runtime uses it for auto-wiring. When absent, the capability
operates without cognitive-layer integration.

### Schema

```yaml
cognitive_hints:
  role: string | [string]     # required — cognitive role(s)
  consumes:                   # optional — semantic types read
    - TypeName
  produces:                   # required — per-output-field type mapping
    field_name:
      type: TypeName          # required — from vocabulary/cognitive_types.yaml
      merge: append | replace | deep_merge   # optional — override default
      target: working.slot    # optional — override default_slot
```

### role

The cognitive role(s) the capability plays in a reasoning pipeline.

Valid values come from the `roles` list in `vocabulary/cognitive_types.yaml`:

| Role | Meaning |
|---|---|
| `perceive` | Ingests raw data from external sources |
| `analyze` | Decomposes, identifies patterns, extracts structure |
| `evaluate` | Scores, compares, ranks against criteria |
| `decide` | Makes an explicit choice, resolves ambiguity |
| `synthesize` | Combines inputs into a new coherent output |
| `act` | Performs a side-effect (send, write, deploy) |
| `reflect` | Examines the agent's own reasoning trace |

A capability may declare multiple roles as a list:

```yaml
cognitive_hints:
  role: [analyze, evaluate]
```

### produces

Maps each cognitively relevant output field to a semantic type from the
vocabulary. Every key in `produces` must exist as a declared output field.
Not all output fields need to appear — only those with meaningful cognitive
semantics.

```yaml
produces:
  risks:
    type: Risk
  assumptions:
    type: Evidence
  comparative_summary:
    type: Summary
    merge: replace
    target: output.summary
```

Optional sub-keys:

- `merge` — overrides the default merge strategy from the type's `cardinality`
- `target` — overrides the type's `default_slot` for auto-wire placement

### consumes

Declares which semantic object types the capability expects to find in the
CognitiveState before execution. Used by the planner to validate that upstream
steps have produced the required types.

```yaml
consumes:
  - Option
  - Criterion
```

### Three-layer resolution

Cognitive wiring resolves through three layers:

1. **Vocabulary** (`vocabulary/cognitive_types.yaml`) — defines default_slot
   and cardinality per type
2. **Capability hints** (`cognitive_hints.produces`) — may override merge
   and target per field
3. **Skill output mapping** (`steps[].output`) — final authority; the skill
   author wires fields to explicit state paths

If a skill step has no output mapping but its capability has `cognitive_hints`,
the runtime auto-wires using type defaults.

### Example

```yaml
cognitive_hints:
  role: analyze
  consumes:
    - Artifact
    - Context
  produces:
    risks:
      type: Risk
    assumptions:
      type: Evidence
    failure_modes:
      type: Risk
    mitigation_ideas:
      type: Context
    extraction_notes:
      type: Summary
```

---

## safety (Conditional)

The `safety` block declares security, trust, and operational guardrails for a
capability. It is **required** for any capability that declares
`properties.side_effects: true`. For pure-read capabilities it is optional.

When present, the block is **normative** — the runtime enforces its constraints.

### Schema

```yaml
safety:
  trust_level: sandbox | standard | elevated | privileged    # required
  data_classification: public | internal | pii | confidential | restricted
  reversible: true | false
  requires_confirmation: true | false
  allowed_targets:
    - internal_only
    - approved_connectors
    - same_tenant
  mandatory_pre_gates:
    - capability: security.pii.detect
      on_fail: block | warn | degrade | require_human
  mandatory_post_gates:
    - capability: security.output.gate
      on_fail: warn
  scope_constraints:
    - sandboxed_execution
    - read_only
    - no_credential_passthrough
    - no_external_network
    - ephemeral_only
```

### trust_level (required)

Declares the minimum trust context needed to execute this capability.

| Level | Rank | Meaning |
|---|---|---|
| `sandbox` | 0 | No external effects, no sensitive data. Free execution. |
| `standard` | 1 | May read internal data or perform low-risk mutations. |
| `elevated` | 2 | Significant mutations, sensitive data, or external comms. |
| `privileged` | 3 | Arbitrary code, credentials, irreversible high-impact ops. |

The runtime rejects execution when the execution context's trust level is
lower than the capability's declared level.

### data_classification

Declares the highest sensitivity of data the capability handles.

| Classification | Rank | Enforcement |
|---|---|---|
| `public` | 0 | No restrictions. |
| `internal` | 1 | Standard audit. |
| `pii` | 2 | PII gates recommended. Full audit enforced. |
| `confidential` | 3 | Encryption expected. Full audit enforced. |
| `restricted` | 4 | Maximum safeguards. Human approval for release. |

### reversible

Whether the effects of the capability can be undone.

- `true` — effects can be reverted (e.g. delete a draft, undo a store).
- `false` — effects are permanent (e.g. send an email, execute code).

When omitted on a capability with `side_effects: true`, the runtime treats it
as `false` (conservative default). When `side_effects: false`, the field is
irrelevant.

### requires_confirmation

When `true`, the runtime pauses execution and requests human confirmation
before proceeding. Without confirmation, the step is not executed.

### allowed_targets

Controlled vocabulary of deployment-scoped target restrictions. The deployment
defines what each target name means in `.agent-skills/safety_policy.yaml`.

| Target | Meaning |
|---|---|
| `internal_only` | Endpoints must resolve to internal domains. |
| `approved_connectors` | Must be in deployment's approved connector list. |
| `same_tenant` | Must belong to the same organizational tenant. |

### mandatory_pre_gates / mandatory_post_gates

Lists of capability IDs that the runtime must execute before/after the
capability. Each gate can be specified as:

- **Short form**: just the capability ID string (defaults to `on_fail: block`)
- **Full form**: `{capability: <id>, on_fail: <policy>}`

| on_fail | Meaning |
|---|---|
| `block` | Abort the step and the skill. (default) |
| `warn` | Emit warning event, continue execution. |
| `degrade` | Skip the step, skill continues with null output. |
| `require_human` | Pause for human confirmation despite gate failure. |

### scope_constraints

Deployment-enforced restrictions applied to the binding/service at execution
time.

| Constraint | Meaning |
|---|---|
| `sandboxed_execution` | Code runs in isolated sandbox. |
| `read_only` | No write operations allowed. |
| `no_credential_passthrough` | Must not forward caller credentials. |
| `no_external_network` | No outbound network requests. |
| `ephemeral_only` | Data must not persist beyond current run. |

### Enforcement policy

The `safety` block follows an escalating enforcement policy:

- **v2 (current)**: `safety` is required for all capabilities with
  `properties.side_effects: true`. Omitting it is a validation error.
- Capabilities without side effects may optionally declare `safety` if they
  handle sensitive data (e.g. a read-only PII extraction capability).

### Example

```yaml
safety:
  trust_level: elevated
  data_classification: pii
  reversible: false
  requires_confirmation: true
  allowed_targets:
    - internal_only
  mandatory_pre_gates:
    - capability: security.pii.detect
      on_fail: block
```

---

## properties

Capabilities may declare execution properties.

Example:

```
properties:
  deterministic: false
  side_effects: false
  idempotent: true
```

### deterministic

Whether the capability always produces the same output for the same input.

Examples:

- `true` for deterministic parsing
- `false` for LLM-based summarization

---

### side_effects

Whether the capability produces side effects.

Examples:

- writing to a file
- modifying a database
- sending a request

Capabilities without side effects are easier to compose safely.

---

### idempotent

Whether repeated execution with the same input produces the same result without additional effects.

---

# Design Principles

Capabilities should follow these principles:

### Single Responsibility

A capability should perform **one clear operation**.

Good example:

```
text.content.summarize
```

Poor example:

```
text.extract-and-summarize
```

That logic should be expressed as a **skill**.

---

### Reusability

Capabilities should be designed to be reused across many workflows.

Avoid overly specific capabilities.

Example:

Prefer:

```
text.content.classify
```

Over:

```
text.sentiment.classify
```

unless the distinction is meaningful.

---

### Vocabulary Consistency

Capability identifiers must use the controlled vocabulary defined in:

```
vocabulary/vocabulary.json
```

This ensures:

- consistent naming
- predictable discovery
- long-term ecosystem stability

---

# Relationship to Skills

Capabilities are invoked from skills.

Example step in a skill:

```
uses: text.content.summarize
```

Skills may also compose other skills:

```
uses: skill:text.simple-summarize
```

Capabilities therefore represent the **primitive operations**, while skills define workflows.

---

# Validation

Capabilities are validated automatically using the registry validator.

The validator checks:

- YAML structure
- required fields
- identifier format
- controlled vocabulary compliance
- reference consistency

Validation is performed using:

```
tools/validate_registry.py
```

If validation fails, the capability cannot be merged into the registry.

---

# Evolution of Capabilities

Capabilities may evolve over time.

Possible changes include:

- improvements to descriptions
- additional optional inputs
- improved metadata

Breaking changes should be avoided unless the capability version is incremented appropriately.

---

# Summary

Capabilities are the **foundation of the registry language**.

They define the reusable operations from which all skills are composed.

By enforcing:

- a controlled vocabulary
- strict identifier rules
- validation tooling

the registry ensures a consistent and scalable ecosystem of reusable workflows.