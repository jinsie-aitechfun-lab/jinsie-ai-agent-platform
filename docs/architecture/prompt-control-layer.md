# Prompt Control Layer (PCL) · Architecture Contract v1

## Purpose

This project treats prompts as an **application-level semantic control layer** (protocol/API), not ad-hoc instructions.
The goal is to make Agent / Workflow / RAG systems **controllable, reproducible, maintainable, and extensible**.

This document freezes:
- A 10-mode prompt control taxonomy
- Module boundaries and recommended code locations
- Stage-based adoption (no extra roadmap cost)
- Acceptance criteria (how to verify)

---

## Scope

Prompt Control Layer consists of **10 modes**, each representing a distinct engineering responsibility.

Core principles:
- Prompts are versioned artifacts (like APIs).
- Outputs are structured and verifiable whenever required.
- Failure handling is consistent and testable.
- Safety boundaries are explicit and enforceable.

---

## The 10 Prompt Modes (Frozen)

> Convention: each mode should map to an auditable module (file/function) and be referenced by the runtime (workflow/agent runner).

| # | Mode | Engineering Responsibility | Typical Trigger | Recommended Location | Acceptance Criteria |
|---|------|----------------------------|-----------------|----------------------|---------------------|
| 1 | System | Global behavior contract (role, boundaries, output style, prohibitions, failure policy) | Any model invocation | `app/workflow/prompts/system.py` | All runs inject System; contract is auditable |
| 2 | Task | Task injection (turn input into executable context, goals, constraints) | Workflow API entry | `app/workflow/prompts/task.py` | Task structure stable and explicit |
| 3 | Schema | Structured output constraints (JSON-first, fields/types/enums) | Parseable outputs | `app/workflow/prompts/schema.py` | Outputs parse reliably |
| 4 | Validator | Validation & self-repair | After schema usage | `app/workflow/prompts/validator.py` | Invalid → repaired output |
| 5 | Router | Decision routing | Tool / flow branching | `app/workflow/prompts/router.py` | Routing is explainable |
| 6 | Tool | Tool protocol | Tool registry exists | `app/workflow/prompts/tool.py` | Tool usage is auditable |
| 7 | Memory | Memory injection & forgetting policy | Multi-turn / RAG | `app/workflow/prompts/memory.py` | Memory formats defined |
| 8 | Fallback | Failure handling strategy | Production mindset | `app/workflow/prompts/fallback.py` | Behavior is consistent |
| 9 | Safety | Safety & compliance boundaries | Public/external | `app/workflow/prompts/safety.py` | Safety policies explicit |
|10| Multi-Agent | Collaboration protocol | Multi-agent orchestration | `app/workflow/prompts/multi_agent.py` | Message schema unified |

---

## Recommended Directory Layout (Frozen)

```text
app/workflow/
  prompts/
    __init__.py
    system.py
    task.py
    schema.py
    validator.py
    router.py
    tool.py
    memory.py
    fallback.py
    safety.py
    multi_agent.py
```

---

## Stage-Based Adoption (No Extra Roadmap Cost)

This control layer is introduced by **engineering triggers**, not separate study tasks.

- Workflow Skeleton: System / Task / Schema (Validator minimal recommended)
- Tool System: Tool / Router / Schema / Validator
- Stability Hardening: Fallback / Validator (enhanced)
- RAG + Memory: Memory / Schema / Safety (baseline)
- Multi-Agent: Multi-Agent / Router / Memory / Validator

---

## Acceptance Checklist

### 1) Structure (Static)
- All 10 mode files exist at the recommended locations (or equivalent mapping is documented).

### 2) Injection (Runtime)
- Runner/engine injects System for every call.
- Router/Validator/Tool calls reference corresponding mode prompts.

### 3) Behavior (Functional)
- Schema outputs parse reliably.
- Routing decisions are explainable and stable.
- Fallback behavior is consistent.
- Safety boundaries are explicit.
- Multi-agent message format is unified.
# Prompt Control Layer (PCL) · Architecture Contract (A) · v1 (Frozen)

## 0. Status (Frozen Decision)

- Current status: **A (Architecture Contract)**
- Future plan: **Upgrade to B (Runtime Spec)** when runtime wiring is stable and worth standardizing.
- This document **does not require immediate code refactor**. It defines **the contract and mapping**.

---

## 1. Purpose

This project treats prompts as an **application-level semantic control layer** (protocol/API), not ad-hoc instructions.

Goals:
- Make Agent / Workflow / RAG systems **controllable**
- Keep behaviors **reproducible**
- Make changes **auditable** (diffable prompt artifacts)
- Keep the system **maintainable and extensible**

Prompts are treated like APIs:
- versioned
- testable (at least at interface level)
- reviewable

---

## 2. Scope

Prompt Control Layer consists of **10 modes**.
Each mode represents a distinct engineering responsibility and should map to:
- an auditable artifact (file/function)
- a clear “when to inject/use” trigger (runtime later, in B)

This A contract freezes:
- the 10-mode taxonomy
- naming conventions
- recommended locations (publicly auditable)
- acceptance checklist for A

---

## 3. The 10 Prompt Modes (Frozen)

> Convention: each mode maps to an auditable module (file/function) and can be referenced by runtime later.

| # | Mode | Engineering Responsibility | Typical Trigger | Recommended Location (Frozen) | A Acceptance Criteria |
|---|------|----------------------------|-----------------|------------------------------|-----------------------|
| 1 | System | Global behavior contract (role, boundaries, output style, prohibitions, failure policy) | Any model invocation | `app/prompts/pcl/system.py` | Artifact exists and is reviewable |
| 2 | Task | Turn input into executable context (goals, constraints, success criteria) | Workflow entry / agent entry | `app/prompts/pcl/task.py` | Artifact exists and is reviewable |
| 3 | Schema | Structured output constraints (JSON-first, fields/types/enums) | Parseable outputs required | `app/prompts/pcl/schema.py` | Artifact exists and is reviewable |
| 4 | Validator | Validation rules & repair policy (self-repair prompt protocol) | After schema usage | `app/prompts/pcl/validator.py` | Artifact exists and is reviewable |
| 5 | Router | Decision routing (tool/flow branching policy) | Tool selection / workflow branching | `app/prompts/pcl/router.py` | Artifact exists and is reviewable |
| 6 | Tool | Tool protocol (how to call tools, args discipline, allowed tool list) | Tool invocation | `app/prompts/pcl/tool.py` | Artifact exists and is reviewable |
| 7 | Memory | Memory injection + forgetting policy (what, when, format) | Multi-turn / RAG | `app/prompts/pcl/memory.py` | Artifact exists and is reviewable |
| 8 | Fallback | Degradation strategy (clarify, partial, safe failure) | When blocked/ambiguous | `app/prompts/pcl/fallback.py` | Artifact exists and is reviewable |
| 9 | Safety | Safety/compliance boundaries (refusal & safe completion strategy) | External/public usage | `app/prompts/pcl/safety.py` | Artifact exists and is reviewable |
|10| Multi-Agent | Multi-agent collaboration protocol (message schema, roles, turn-taking) | Multi-agent orchestration | `app/prompts/pcl/multi_agent.py` | Artifact exists and is reviewable |

---

## 4. Recommended Directory Layout (Frozen)

```text
app/prompts/
  pcl/
    __init__.py
    system.py
    task.py
    schema.py
    validator.py
    router.py
    tool.py
    memory.py
    fallback.py
    safety.py
    multi_agent.py
```

Notes:
- If runtime modules later prefer other paths, **keep an explicit mapping** (see section 5).
- The “mode taxonomy” is stable even if code locations evolve.

---

## 5. Mapping Rule (Frozen)

If runtime wiring uses different module names/paths, you MUST keep a mapping table in the runtime spec (B) later.

Example mapping format (for B, not required now):
- Mode: Schema → Runtime injection: agent runner system-addendum
- Mode: Router → Runtime injection: tool-selection stage

For A, the minimum requirement is:
- the 10 artifacts exist in `app/prompts/pcl/`
- their responsibility is clear from file/module docstrings

---

## 6. Stage-Based Adoption (No Extra Roadmap Cost)

PCL adoption is introduced by **engineering triggers**, not separate study tasks:

- Workflow Skeleton: System / Task / Schema (Validator minimal recommended)
- Tool System: Tool / Router / Schema / Validator
- Stability Hardening: Fallback / Validator (enhanced)
- RAG + Memory: Memory / Schema / Safety (baseline)
- Multi-Agent: Multi-Agent / Router / Memory / Validator

---

## 7. Acceptance Checklist (A)

### 7.1 Structure (Static)
- [ ] All 10 mode files exist at `app/prompts/pcl/`
- [ ] Each file contains a short module docstring explaining its responsibility

### 7.2 Non-goals in A (Explicit)
A does NOT require:
- [ ] runtime injection wiring
- [ ] auto-repair loops
- [ ] schema toggle flags
- [ ] refactoring existing runner/executor modules

Those belong to **B (Runtime Spec)**.

---

## 8. When This Document Will Be Used (Practical)

This document is used by:
- reviewers (you / future collaborators) to understand “what PCL is”
- code authors to keep prompt artifacts consistent across features
- future runtime spec work (B) as the source-of-truth taxonomy

In day-to-day engineering:
- it prevents “one giant prompt blob” from growing uncontrolled
- it makes prompt changes auditable and reviewable like code
