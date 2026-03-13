# Capability Sunset Policy

This policy defines the lifecycle for deprecated capabilities.

## Required Fields for Deprecated Capabilities

When a capability is deprecated, the YAML must include:

1. `metadata.status: deprecated`
2. `replacement: <capability-id>`
3. `metadata.deprecation_date: YYYY-MM-DD`
4. `metadata.sunset_date: YYYY-MM-DD`

## Minimum Sunset Window

`sunset_date - deprecation_date` must be at least 30 days.

Rationale:

- allow migration planning for downstream skills and runtimes

## Enforcement

`tools/enforce_capability_sunset.py` enforces:

1. required fields for deprecated capabilities
2. valid ISO date format
3. minimum sunset window
4. no expired sunset dates in active registry

Expired sunset dates fail CI and must be resolved by:

1. removing capability from active set, or
2. extending sunset date with documented rationale (exceptional)

## Migration Guidance

Deprecation PRs should include:

1. replacement capability
2. migration examples
3. known impacted skills
