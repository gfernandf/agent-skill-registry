# Capability 100 Target Set

This document records the planning baseline that guided expansion from an
initial 45-capability core toward a 100-capability language target.

Current status:

- The 100-capability milestone has been reached and exceeded.
- Current registry scope is now tracked as 101 capabilities in
    [README.md](../README.md).

Use this document as historical context and taxonomy rationale, not as the
live source of truth for exact capability counts.

For current operational scope and governance, use:

- [README.md](../README.md)
- [CAPABILITIES.md](CAPABILITIES.md)
- [CAPABILITY_ADMISSION_POLICY.md](CAPABILITY_ADMISSION_POLICY.md)
- [CAPABILITY_COMPATIBILITY_POLICY.md](CAPABILITY_COMPATIBILITY_POLICY.md)
- [CAPABILITY_SUNSET_POLICY.md](CAPABILITY_SUNSET_POLICY.md)

## Design Rules Used

1. Keep one clear operation per capability.
2. Prefer domain-specific operations over generic duplicates.
3. Avoid adding synonyms where current operations already express intent.
4. Use new domains (`identity`, `integration`) to separate concerns cleanly.

## Historical Baseline 45

### Agent

- agent.delegate
- agent.plan.generate
- agent.route

### Audio

- audio.transcribe

### Code

- code.diff.extract
- code.execute
- code.format

### Data

- data.json.parse
- data.record.deduplicate
- data.schema.validate

### Doc / PDF / FS

- doc.chunk
- pdf.read
- fs.read

### Email / Message

- email.read
- email.send
- message.send

### Eval

- eval.output.score

### Image / Video

- image.caption.generate
- image.classify
- video.frame.extract

### Memory

- memory.retrieve
- memory.store

### Ops

- ops.budget.estimate
- ops.trace.monitor

### Policy / Security

- policy.constraint.validate
- security.output.gate
- security.pii.detect
- security.pii.redact
- security.secret.detect

### Provenance

- provenance.citation.generate
- provenance.claim.verify

### Table

- table.filter

### Text

- text.classify
- text.embed
- text.entity.extract
- text.extract
- text.keyword.extract
- text.language.detect
- text.summarize
- text.template
- text.translate

### Web

- web.fetch
- web.page.extract
- web.search
- web.source.verify

## Historical Expansion Set 55

These entries were initially tracked as proposed additions to reach the 100
target. Most are now represented in the live registry. Contract maturity,
implementation quality, and production readiness should be evaluated through
the active governance and validation workflows rather than this snapshot.

### Task (15)

- task.case.create
- task.case.update
- task.case.close
- task.case.list
- task.case.get
- task.case.search
- task.assignee.assign
- task.priority.classify
- task.state.transition
- task.milestone.schedule
- task.sla.monitor
- task.approval.approve
- task.approval.reject
- task.incident.create
- task.event.acknowledge

### Integration (12)

- integration.connector.list
- integration.connector.get
- integration.connector.sync
- integration.mapping.transform
- integration.mapping.validate
- integration.record.upsert
- integration.record.create
- integration.record.update
- integration.record.delete
- integration.record.reconcile
- integration.record.compare
- integration.event.acknowledge

### Identity (10)

- identity.role.list
- identity.role.get
- identity.role.assign
- identity.permission.list
- identity.permission.get
- identity.permission.verify
- identity.permission.gate
- identity.assignee.identify
- identity.risk.score
- identity.decision.justify

### Model (8)

- model.prompt.template
- model.output.generate
- model.output.classify
- model.output.score
- model.response.validate
- model.embedding.generate
- model.risk.score
- model.output.sanitize

### Policy (4)

- policy.decision.justify
- policy.risk.classify
- policy.risk.score
- policy.constraint.gate

### Ops (3)

- ops.event.monitor
- ops.event.acknowledge
- ops.trace.analyze

### Memory (2)

- memory.vector.search
- memory.record.store

### Message (1)

- message.priority.classify

## Historical Count Check

- Baseline: 45
- Expansion set: 55
- Planned total: 100

Current live total may differ as the registry continues evolving.

## Internal Conflict Review Summary

The proposed set was filtered to reduce expected overlap:

1. Transactional workflow operations are concentrated in `task.*`.
2. Cross-system state synchronization is concentrated in `integration.*`.
3. Access and authorization concerns are concentrated in `identity.*`.
4. Existing generic text/security capabilities are reused as base language,
   avoiding duplicate new synonyms.

Remaining overlap candidates should continue to be reviewed capability-by-
capability using governance guardrails and admission policy checks.
