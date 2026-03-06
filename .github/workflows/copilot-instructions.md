# Copilot Instructions for Agent Skill Registry

This repository defines a specification and registry for reusable AI agent workflows called skills.

The project separates three layers:

skills → workflows that solve tasks  
capabilities → abstract functions used by workflows  
tools/agents → implementations that satisfy capabilities

Copilot must respect this architecture when generating content.

---

# Repository structure

skills/
  official/
  community/
  experimental/

Skills are organized by domain:

skills/<channel>/<domain>/<skill-name>/skill.yaml

Examples:

skills/official/text/hello-world/skill.yaml

---

# Skill definition rules

Skills are defined using the format described in docs/SKILL_FORMAT.md.

A skill contains:

- id
- version
- name
- description
- inputs
- outputs
- steps

Steps reference capabilities using the `uses` field.

Example:

uses: text.template

Variables in workflows follow the syntax:

inputs.<name>  
vars.<name>  
outputs.<name>

---

# Capability definitions

Capabilities are defined in:

capabilities/<capability-id>.yaml

Examples:

capabilities/text.template.yaml
capabilities/pdf.read.yaml

Capabilities may optionally declare dependencies using:

requires:
  - capability.id

Example:

pdf.read requires fs.read.

---

# Naming conventions

Capabilities follow the format:

domain.verb

Examples:

text.summarize  
pdf.read  
fs.read  

Skills follow the format:

domain.task-name

Examples:

pdf.batch-summarize  
text.hello-world  

---

# Contribution expectations

When generating new skills:

- follow the TEMPLATE in skills/TEMPLATE
- only reference capabilities defined in capabilities/_index.yaml
- keep skills simple and readable

When generating capabilities:

- ensure they are registered in capabilities/_index.yaml
- keep schemas minimal