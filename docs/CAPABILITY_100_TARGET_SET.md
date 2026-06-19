# Capability 100 Target Set

This document records the planning baseline that guided expansion from an
initial 45-capability core toward a 100-capability language target.

Why this document still matters:

1. It explains how the vocabulary grew without collapsing into redundant synonyms.
2. It shows that the registry now favors clear, governable capability boundaries over raw count growth.
3. It provides historical context for why the current taxonomy is easier to validate and maintain.

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

- decision.task.delegate
- reasoning.plan.generate
- decision.input.route

### Audio

- audio.speech.transcribe

### Code

- code.diff.extract
- code.snippet.execute
- code.source.format

### Data

- data.json.parse
- data.record.deduplicate
- data.schema.validate

### Doc / PDF / FS

- doc.content.chunk
- pdf.document.read
- fs.file.read

### Email / Message

- email.inbox.read
- email.message.send
- message.notification.send

### Eval

- evaluation.output.score

### Image / Video

- image.caption.generate
- image.content.classify
- video.frame.extract

### Memory

- memory.entry.retrieve
- memory.record.store

### Ops

- ops.budget.estimate
- evidence.trace.monitor

### Policy / Security

- policy.constraint.validate
- security.output.gate
- security.pii.detect
- security.pii.redact
- security.secret.detect

### Provenance

- evidence.citation.generate
- evidence.claim.verify

### Table

- table.row.filter

### Text

- reasoning.content.classify
- reasoning.content.embed
- perception.entity.extract
- perception.content.extract
- perception.keyword.extract
- reasoning.language.detect
- reasoning.content.summarize
- reasoning.content.template
- reasoning.content.translate

### Web

- web.page.fetch
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
- perception.case.list
- perception.case.get
- perception.case.search
- task.assignee.assign
- reasoning.priority.classify
- task.state.transition
- task.milestone.schedule
- perception.sla.monitor
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

- reasoning.prompt.template
- reasoning.output.generate
- reasoning.output.classify
- evaluation.output.score
- evaluation.response.validate
- reasoning.embedding.generate
- evaluation.risk.score
- reasoning.output.sanitize

### Policy (4)

- policy.decision.justify
- policy.risk.classify
- policy.risk.score
- policy.constraint.gate

### Ops (3)

- perception.event.monitor
- ops.event.acknowledge
- evidence.trace.analyze

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

The important point is not the count by itself. The value is that the live
registry can now grow while keeping contract names, governance rules, and
family boundaries much clearer than an unstructured expansion would allow.

## Internal Conflict Review Summary

The proposed set was filtered to reduce expected overlap:

1. Transactional workflow operations are concentrated in `task.*`.
2. Cross-system state synchronization is concentrated in `integration.*`.
3. Access and authorization concerns are concentrated in `identity.*`.
4. Existing generic text/security capabilities are reused as base language,
   avoiding duplicate new synonyms.

Remaining overlap candidates should continue to be reviewed capability-by-
capability using governance guardrails and admission policy checks.
