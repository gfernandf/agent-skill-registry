# Changelog

All notable changes to **agent-skill-registry** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] — 2026-03-24

### Added

#### Phase 3 — Registry hygiene
- 52 stub capabilities marked `status: draft` (previously `experimental`).
- `validate_registry.py`: `draft` added to `ALLOWED_STATUS`.
- `registry_stats.py`: emits `by_status` breakdown in stats output.
- README expanded with tooling section and contributor instructions.
- `requirements.txt` added for tooling dependencies.

#### text.* domain review
- **3 new capabilities**:
  - `text.content.generate` — produce new text from instruction + context.
  - `text.content.transform` — rewrite text applying a style/tone directive.
  - `text.response.extract` — answer a question from a context passage.
- **3 capabilities stabilized** (`status: stable`):
  - `text.content.template`
  - `text.content.extract`
  - `text.content.merge`
- `docs/DOMAIN_TEXT.md`: full domain reference with boundary definitions,
  binding matrix, and skill inventory.
- `_index.yaml` updated with all new entries and status changes.
- Catalog regenerated (114 capabilities, 35 skills).
