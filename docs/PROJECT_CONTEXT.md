# Project Context

## Project Name

Agent Skill Registry

## Vision

Agent Skill Registry is an open specification and repository for reusable AI agent workflows called **skills**.

The goal is to create a shared ecosystem where workflows can be:

- defined once
- reused across environments
- executed by different agents or runtimes

The system separates **workflow logic from implementation details**.

---

# Core Concept

A **skill** describes how to solve a task using abstract capabilities.

Example task:

Summarize a set of PDF documents.

A skill defines the workflow:

1. read PDFs
2. process text
3. summarize
4. produce final result

Skills do not bind to specific tools or AI models.

They only reference **capabilities**.

---

# Architectural Layers

The system separates three layers:

skills → workflows  
capabilities → abstract functions  
tools / agents → implementations  

### Skills

Reusable workflows that solve tasks.

Skills are portable and declarative.

### Capabilities

Abstract functions used by skills.

Examples:

text.summarize  
pdf.read  
fs.read  

Capabilities define **contracts**, not implementations.

### Tools / Agents

Actual implementations that satisfy capabilities.

Examples:

- local tools
- MCP tools
- APIs
- AI models

---

# Repository Structure

skills/
  official/
  community/
  experimental/
  TEMPLATE/

capabilities/
  _index.yaml
  *.yaml

docs/
  REGISTRY_STRUCTURE.md
  SKILL_FORMAT.md
  CAPABILITIES.md
  VERBS.md
  GOVERNANCE.md
  PROJECT_CONTEXT.md
  ARCHITECTURE.md

catalog/
tools/
.github/

---

# Skill Organization

Skills are organized by domain:

skills/<channel>/<domain>/<skill-name>/

Example:

skills/official/text/hello-world/

Channels represent governance level:

official  
community  
experimental  

The canonical skill identifier is defined in `skill.yaml`.

Example:

id: text.hello-world

---

# Capability Model

Capabilities define:

- inputs schema
- outputs schema
- optional dependencies

Example capability:

pdf.read

may declare:

requires:
  - fs.read

Dependencies are optional and used primarily for discovery and planning.

---

# Skill Execution Model

Skills define workflows as explicit dataflow graphs.

Namespaces used in workflows:

inputs.*  
vars.*  
outputs.*  

Example references:

inputs.file  
vars.document_text  
outputs.summary  

Steps execute based on dependency resolution.

Steps may run sequentially or in parallel depending on data dependencies.

---

# Current Status

Specification version:

v0.1

Implemented elements:

- registry structure
- skill specification
- capability specification
- governance rules
- initial capabilities
- example skill

---

# Future Directions

Possible future components:

- CLI tooling
- capability discovery
- skill validation tools
- runtime execution engine
- hosted execution environment
- skill marketplace

The project currently focuses on **the specification and registry**, not the runtime.