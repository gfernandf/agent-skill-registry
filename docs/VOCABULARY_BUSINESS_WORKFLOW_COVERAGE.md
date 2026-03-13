# Vocabulary Coverage for Business Workflows

This document explains how the controlled vocabulary supports broad business
workflow coverage and what was added to improve readiness toward an 85-90% target.

## Coverage Goal

Target: support the majority of business workflows through composable
capabilities without forcing ad-hoc or provider-specific naming.

## New Vocabulary Added (Current Update)

### Domains

- `identity`
- `integration`

### Nouns

- `obligation`
- `priority`
- `ticket`
- `case`
- `incident`
- `approval`
- `sla`
- `state`
- `milestone`
- `assignee`
- `role`
- `permission`
- `connector`
- `mapping`
- `event`

### Verbs

- `assign`
- `approve`
- `reject`
- `schedule`
- `sync`
- `upsert`
- `close`
- `acknowledge`
- `transition`

## Why These Terms Matter

These terms strengthen the language for:

1. transactional workflows (ticket/case lifecycle)
2. governance workflows (approval, escalation, SLA/state transitions)
3. enterprise system interoperability (integration connectors and sync/upsert)
4. identity-aware workflow decisions (role/permission semantics)

## Current Coverage Status

With this vocabulary expansion, language-level readiness for business workflows
is significantly improved, while keeping controlled naming constraints intact.

This update does not create new capabilities; it only broadens what can be
expressed consistently.

## Remaining Considerations

Some vertical-specific scenarios may still require additional terms in future
releases. Any future additions should follow:

- `docs/CAPABILITY_ADMISSION_POLICY.md`
- `docs/CAPABILITY_COMPATIBILITY_POLICY.md`
- `docs/CAPABILITY_SUNSET_POLICY.md`
