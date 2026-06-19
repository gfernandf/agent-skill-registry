# Cognitive Taxonomy

This document defines the **pure cognitive layer** of the registry.

Current status: the cognitive taxonomy is fully represented in the live
registry capability set.

## Design goals

- keep the cognitive layer complete and coherent
- keep operational/runtime control capabilities out of the pure cognitive core
- avoid duplicate semantics unless a compatibility alias is explicitly required

## Layer boundaries

### Pure cognitive layer

Canonical cognitive families:

- `decision.*`
- `evaluation.*`
- `evidence.*`
- `memory.*`
- `perception.*`
- `reasoning.*`

### Legacy compatibility aliases

`eval.*` remains available for backward compatibility in existing skills and
integrations. New capability design should prefer the canonical family names
listed above.

### Operational support layer (non-cognitive core)

Capabilities such as flow-control, routing, and delegation support execution
behavior and should not be treated as cognitive reasoning primitives.

## Live registry inventory (pure cognitive families)

### decision (8)

- `decision.flow.branch`
- `decision.flow.catch`
- `decision.input.route`
- `decision.option.justify`
- `decision.option.select`
- `decision.strategy.select`
- `decision.task.delegate`
- `decision.uncertainty.prioritize`

### evaluation (18)

- `evaluation.assumption.validate`
- `evaluation.catalog.detect`
- `evaluation.catalog.rank`
- `evaluation.constraint.validate`
- `evaluation.failure.analyze`
- `evaluation.framework.detect`
- `evaluation.framework.rank`
- `evaluation.hypothesis.compare`
- `evaluation.hypothesis.evaluate`
- `evaluation.option.score`
- `evaluation.output.score`
- `evaluation.output.validate`
- `evaluation.plan.gate`
- `evaluation.plan.validate`
- `evaluation.response.score`
- `evaluation.response.validate`
- `evaluation.risk.score`
- `evaluation.uncertainty.score`

### evidence (8)

- `evidence.citation.generate`
- `evidence.claim.verify`
- `evidence.conflict.detect`
- `evidence.gap.detect`
- `evidence.source.assess`
- `evidence.trace.analyze`
- `evidence.trace.monitor`
- `evidence.trace.summarize`

### memory (10)

- `memory.context.compress`
- `memory.context.reconcile`
- `memory.context.retrieve`
- `memory.context.store`
- `memory.context.summarize`
- `memory.context.update`
- `memory.entry.retrieve`
- `memory.record.store`
- `memory.vector.search`

### perception (12)

- `perception.case.get`
- `perception.case.list`
- `perception.case.search`
- `perception.catalog.search`
- `perception.content.extract`
- `perception.entity.extract`
- `perception.event.monitor`
- `perception.input.collect`
- `perception.input.structure`
- `perception.keyword.extract`
- `perception.language.detect`
- `perception.sla.monitor`

### reasoning (44)

- `reasoning.assumption.extract`
- `reasoning.constraint.extract`
- `reasoning.constraint.reconcile`
- `reasoning.content.classify`
- `reasoning.content.compare`
- `reasoning.content.embed`
- `reasoning.content.generate`
- `reasoning.content.merge`
- `reasoning.content.summarize`
- `reasoning.content.template`
- `reasoning.content.transform`
- `reasoning.content.translate`
- `reasoning.criteria.define`
- `reasoning.embedding.generate`
- `reasoning.goal.interpret`
- `reasoning.hypothesis.generate`
- `reasoning.language.detect`
- `reasoning.option.analyze`
- `reasoning.option.generate`
- `reasoning.output.classify`
- `reasoning.output.generate`
- `reasoning.output.normalize`
- `reasoning.output.sanitize`
- `reasoning.output.synthesize`
- `reasoning.plan.create`
- `reasoning.plan.decompose`
- `reasoning.plan.generate`
- `reasoning.plan.map`
- `reasoning.plan.reconcile`
- `reasoning.plan.split`
- `reasoning.plan.synthesize`
- `reasoning.priority.classify`
- `reasoning.problem.decompose`
- `reasoning.problem.split`
- `reasoning.prompt.template`
- `reasoning.request.normalize`
- `reasoning.response.extract`
- `reasoning.response.generate`
- `reasoning.risk.extract`
- `reasoning.sentiment.analyze`
- `reasoning.task.decompose`
- `reasoning.task.plan`
- `reasoning.theme.cluster`
- `reasoning.uncertainty.extract`

## Governance rule for future additions

When introducing new cognitive capabilities:

- place them in one of the canonical cognitive families
- avoid creating synonym capabilities with the same semantics
- if an alias is required for compatibility, mark and document it explicitly