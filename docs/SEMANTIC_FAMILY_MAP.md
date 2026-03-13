# Semantic Family Map

This map helps maintainers avoid near-duplicate skills by grouping skills into
semantic families and marking canonical entries.

Status keys:

- `canonical`: preferred skill for the family
- `variant`: acceptable variant with meaningful contract differences
- `candidate-merge`: likely overlap; review for consolidation

## Message Triage

- family_id: `message-triage-routing`
- canonical: `message.triage-and-route` (planned)
- variants: none
- candidate-merge: none

## Language + Classification

- family_id: `text-language-classification`
- canonical: `text.detect-language-and-classify`
- variants: none
- candidate-merge:
  - `text.classify-input`

## Keyword / Entity Extraction Summaries

- family_id: `text-extraction-summary`
- canonical: `text.keyword-summary`
- variants:
  - `text.entity-summary`
- candidate-merge:
  - `text.extract-keywords`
  - `text.extract-entities`

## Web Summarization

- family_id: `web-summary`
- canonical: `web.fetch-summary`
- variants:
  - `web.page-summary`
  - `web.search-summary`
- candidate-merge: none

## Note

This file is governance guidance, not an execution contract.

Changes should be coordinated with:

- `docs/SKILL_ADMISSION_POLICY.md`
- `catalog/governance_guardrails.json`