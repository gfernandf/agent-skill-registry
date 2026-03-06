# Governance (v0.1)

This document defines how skills and capabilities evolve without fragmenting the ecosystem.

## Skills contribution

Skills must be placed in one of the following folders:

- skills/official
- skills/community
- skills/experimental

official  
Maintained and supported by project maintainers.

community  
Contributed by external contributors with best-effort support.

experimental  
Incubation area where breaking changes are allowed.

## Capabilities contribution

### Rule 1: reuse before create

If an existing capability matches the required behavior, it must be reused.

### Rule 2: new capability proposal

A new capability requires:

- a YAML definition file under capabilities/
- the capability id added to capabilities/_index.yaml
- at least one example
- naming compliant with docs/CAPABILITIES.md
- verb compliant with docs/VERBS.md

### Rule 3: resolving duplicates

If two capabilities overlap:

- prefer the more general contract
- keep a single canonical id
- deprecated ids may remain as aliases

## Deprecation policy

A deprecated capability must specify a replacement id.

Deprecated capabilities remain available for compatibility but should not be used in new skills.

## Decision authority

Project maintainers decide on:

- new domains
- new verbs
- canonical capability ids
- deprecations

Community members may propose changes through pull requests and issue discussions.


Skills that use skill composition (uses: skill:...) should be placed in skills/experimental unless explicitly promoted by maintainers.