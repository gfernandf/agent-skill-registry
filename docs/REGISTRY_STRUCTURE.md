# Registry structure (v0.1)

This repository stores reusable agent skills and capability definitions.

## Top-level folders

- skills/
  - official/      Skills maintained and supported by the project maintainers.
  - community/     Skills contributed by the community (best-effort support).
  - experimental/  Incubation area. Breaking changes allowed.

- capabilities/
  Canonical capability definitions (contracts). A capability is not a tool.

- catalog/
  Generated index files (do not edit manually).

- tools/
  Utility scripts used to maintain or generate registry assets.

- .github/workflows/
  CI validation for skills and capabilities.