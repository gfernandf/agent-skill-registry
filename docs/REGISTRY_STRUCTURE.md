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

  ## Skill directory structure

Skills are organized by domain to keep the repository navigable as the number of skills grows.

The directory structure is:

skills/<channel>/<domain>/<skill-name>/

Example:

skills/
  official/
    pdf/
      batch-summarize/
        skill.yaml
    text/
      hello-world/
        skill.yaml
  community/
  experimental/

The domain directory is intended only as a lightweight organizational aid and does not define a strict taxonomy.

The canonical identifier of a skill is defined inside `skill.yaml` using the `id` field.

Example:

```yaml
id: pdf.batch-summarize