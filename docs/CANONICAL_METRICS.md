# Canonical Metrics Source

This document defines the canonical source for registry counts and how to compute them.

## Source of Truth

The source of truth for totals is the generated registry catalog in this repository:

- `catalog/capabilities.json`
- `catalog/skills.json`
- `catalog/graph.json`
- `catalog/stats.json`

`catalog/capabilities.json` and `catalog/skills.json` are authoritative for total counts.

## How to Regenerate

From `agent-skill-registry` root:

```powershell
python tools/validate_registry.py
python tools/generate_catalog.py
python tools/registry_stats.py
```

## How to Read Canonical Counts

PowerShell examples:

```powershell
python -c "import json;from pathlib import Path;print(len(json.loads(Path('catalog/capabilities.json').read_text(encoding='utf-8'))))"
python -c "import json;from pathlib import Path;print(len(json.loads(Path('catalog/skills.json').read_text(encoding='utf-8'))))"
```

## Runtime vs Registry Counts

`agent-skills` may report a smaller executable subset (runtime-supported inventory).

That does not change canonical registry totals above.
