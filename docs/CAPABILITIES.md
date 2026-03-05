# Capabilities (v0.1)

## What is a capability?
A capability is a stable, tool-agnostic contract describing WHAT can be done.
Tools or agents are implementations bound at runtime.

A capability definition must specify:
- capability id (global name)
- version (semver)
- inputs schema
- outputs schema
- semantics (human description)
- execution properties (determinism, side-effects)

## Naming

Capability ids follow dot-namespace.

Primary form:
<domain>.<verb>

Extended form (only when needed):
<domain>.<noun>.<verb>

Examples:

- pdf.read
- text.summarize
- text.template
- web.fetch
- data.csv.read

## Domains (v0.1)

Allowed top-level domains:

- text
- pdf
- web
- data
- fs

New domains require governance approval.

## Verbs

Verbs must come from the list defined in docs/VERBS.md.

## Versioning

Capability ids must not include version suffixes.

Incorrect:
text.summarize.v2

Correct:
id: text.summarize
version: 2.0.0

Versioning follows semantic versioning:

- MAJOR: breaking changes
- MINOR: backward-compatible additions
- PATCH: fixes or clarifications

## Deprecation and aliases

Capabilities may be deprecated with a replacement id.

Aliases may be provided to map legacy ids to canonical ids.

Deprecated capabilities remain available for compatibility but should not be used in new skills.

## Capability file format

Capabilities are stored under:

capabilities/<capability-id>.yaml

Minimum required fields:

- id
- version
- description
- inputs
- outputs

Recommended fields:

- tags
- examples
- properties

Execution properties may include:

- deterministic
- side_effects
- idempotent

## Example

```yaml
id: text.template
version: 1.0.0
description: Render a text template using provided variables.

inputs:
  template:
    type: string
    required: true

  variables:
    type: object
    required: true

outputs:
  text:
    type: string

properties:
  deterministic: true
  side_effects: false
  idempotent: true

  ## Optional metadata

Capabilities may include optional metadata fields.

These fields help runners, catalogs, and agents make better decisions
but are not required for capability registration.

Examples include execution properties, cost hints, tags, or examples.