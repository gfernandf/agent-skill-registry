# Architecture

This document describes the architecture of the Agent Skill Registry ecosystem.

The project is designed as a **specification-first system**.

The registry defines the structure and contracts that enable portable AI workflows.

---

# Architectural Philosophy

The architecture is based on separation of concerns.

skills → workflows  
capabilities → functions  
tools → implementations  

This separation enables:

- portability
- interoperability
- reuse
- vendor independence

---

# Layer 1 — Skills

Skills define workflows that solve tasks.

A skill is a declarative specification.

Skills contain:

metadata  
inputs  
outputs  
steps  

Example skill:

pdf.batch-summarize

A skill references capabilities through steps.

Example step:

uses: text.summarize

---

# Skill Dataflow Model

Skills use **explicit dataflow**.

Data moves through three namespaces:

inputs  
vars  
outputs  

### inputs

External parameters provided when invoking the skill.

### vars

Intermediate values produced by steps.

### outputs

Final results exposed by the skill.

---

# Step Execution Model

Steps define the workflow graph.

Each step contains:

id  
uses  
input  
output  

Example:

- id: summarize
  uses: text.summarize

Execution order is determined by data dependencies.

Steps may execute in parallel when dependencies allow.

---

# Layer 2 — Capabilities

Capabilities represent abstract functions.

Capabilities define **what can be done**, not **how it is implemented**.

Example capabilities:

text.summarize  
pdf.read  
fs.read  

Each capability defines:

id  
version  
inputs schema  
outputs schema  

Capabilities may optionally declare dependencies.

Example:

pdf.read
  requires:
    - fs.read

---

# Capability Graph

Capabilities may form dependency graphs.

Example:

pdf.read
  ↓
fs.read

This allows complex functionality to be built from simpler primitives.

---

# Layer 3 — Tool Bindings

Capabilities are satisfied by runtime implementations.

Possible implementations include:

- local libraries
- APIs
- MCP tools
- AI models
- other agents

The registry does not define the runtime layer.

This allows different environments to execute the same skill.

---

# Skill Composition (Future Extension)

Skills may optionally compose other skills.

Example:

contract.review
    ↓
pdf.batch-summarize
    ↓
pdf.read

Skill composition is optional and may be introduced gradually.

The current specification primarily focuses on **skills using capabilities**.

---

# Registry Role

The repository acts as a **registry of definitions**, not an execution environment.

It stores:

skills  
capabilities  
documentation  

Execution runtimes are external to the registry.

---

# Evolution Strategy

The project follows an incremental growth strategy.

Phase 1  
Specification + registry.

Phase 2  
Tooling (CLI, validation, discovery).

Phase 3  
Runtime ecosystem.

Phase 4  
Hosted execution platforms.

---

# Design Goals

The architecture prioritizes:

- simplicity
- extensibility
- composability
- ecosystem growth
- low barrier to contribution