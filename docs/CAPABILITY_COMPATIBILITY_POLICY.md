# Capability Compatibility Policy

This policy defines how capability contracts evolve while preserving stability.

## Stability Target

Capability contracts should be close to immutable once broadly used.

Breaking changes must be exceptional and treated as language evolution events.

## Change Classes

### Non-breaking changes

Examples:

- add optional input
- add optional output
- improve descriptions/examples/metadata

Expected version bump:

- MINOR or PATCH

### Breaking changes

Examples:

- remove or rename required input/output
- change type for required field
- change semantic meaning of existing field

Expected action:

1. create a new capability ID whenever possible
2. mark old capability as deprecated with replacement
3. publish migration notes

Breaking in-place updates should be avoided.

## Required PR Disclosure

When editing a capability contract, PR must include:

1. compatibility classification: non-breaking or breaking
2. impacted skills (if known)
3. migration plan (if breaking)

## Contract Integrity Checklist

Before merge:

1. contract remains provider-agnostic
2. output schema remains predictable
3. error behavior remains normalized at runtime layer
4. unchanged fields preserve original semantics

## Deprecation Link

If a new capability supersedes an old one:

1. old capability metadata.status = deprecated
2. old capability replacement = <new-capability-id>
3. deprecation_date and sunset_date set per `docs/CAPABILITY_SUNSET_POLICY.md`
