# Cognitive Taxonomy

This document defines the **pure cognitive layer** of the registry and how it
maps to the current live capability set.

The goal is to keep the cognitive layer **complete, coherent, and minimal**:

- keep only capabilities that perform cognitive work
- avoid operational / workflow-control capabilities in the pure layer
- call out compatibility surfaces explicitly so old names do not leak into the
  taxonomy

## Layer boundaries

### Pure cognitive layer

These families belong to the cognitive layer:

- `decision.*`
- `evaluation.*`
- `evidence.*`
- `memory.*`
- `perception.*`
- `reasoning.*`

### Compatibility layer

The live registry still exposes a smaller legacy surface for evaluation:

- `eval.*` is the current registry surface for the evaluation family
- `evaluation.*` is the new family name used by the expanded cognitive taxonomy

### Operational support layer

These capabilities help execute workflows but are not part of the pure cognitive
layer:

- `decision.flow.*`
- `decision.input.route`
- `decision.task.delegate`

## Canonical inventory

The tables below list the current cognitive capabilities by family.

### decision

Canonical registry capability:

- `decision.option.justify`

Expanded cognitive family in bindings:

- `decision.flow.branch`
- `decision.flow.catch`
- `decision.input.route`
- `decision.option.justify`
- `decision.option.select`
- `decision.strategy.select`
- `decision.task.delegate`
- `decision.uncertainty.prioritize`

### evaluation

Expanded cognitive family in bindings:

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

Compatibility registry surface:

- `eval.option.analyze`
- `eval.option.score`
- `eval.output.score`

### evidence

Expanded cognitive family in bindings:

- `evidence.citation.generate`
- `evidence.claim.verify`
- `evidence.conflict.detect`
- `evidence.gap.detect`
- `evidence.source.assess`
- `evidence.trace.analyze`
- `evidence.trace.monitor`
- `evidence.trace.summarize`

### memory

Canonical registry capabilities:

- `memory.entry.retrieve`
- `memory.entry.store`
- `memory.record.store`
- `memory.vector.search`

Expanded cognitive family in bindings:

- `memory.context.compress`
- `memory.context.reconcile`
- `memory.context.retrieve`
- `memory.context.store`
- `memory.context.summarize`
- `memory.context.update`
- `memory.entry.retrieve`
- `memory.entry.store`
- `memory.record.store`
- `memory.vector.search`

### perception

Expanded cognitive family in bindings:

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

### reasoning

Expanded cognitive family in bindings:

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

## Registry gap summary

Current live registry coverage is narrower than the expanded cognitive
taxonomy:

- current registry canonical decision surface: `decision.option.justify`
- current registry evaluation surface: `eval.option.analyze`, `eval.option.score`, `eval.output.score`
- current registry memory surface: `memory.entry.retrieve`, `memory.entry.store`, `memory.record.store`, `memory.vector.search`
- binding-only cognitive domains still to be reflected in the registry docs or migration plan: `evaluation.*`, `evidence.*`, `perception.*`, `reasoning.*`

The taxonomy doc is intentionally explicit so future additions do not reintroduce
operational utilities into the cognitive core.