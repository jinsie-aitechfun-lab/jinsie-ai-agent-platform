# Plan Execution Contract & Semantic Validation

**Intended public location:** `docs/architecture/plan-execution-contract.md`

> Public, production-oriented documentation. No learning or day-based semantics.

---

## 1. Purpose

This document defines the **execution contract** between three components:

1. **Planner** – produces a structured plan payload.
2. **Executor** – executes the plan step by step.
3. **Validator** – enforces the contract for both input and output.

The goal is to guarantee:
- Predictable behavior
- Stable semantics
- Clear failure modes
- Machine-checkable correctness

---

## 2. High-level Architecture

```
Planner → (payload) → Validator → Executor → (results) → Validator → Consumer/UI
```

The validator acts as a **contract gatekeeper**:
- Input validation: catches malformed or inconsistent plans early.
- Output validation: ensures executor semantics remain stable.

---

## 3. Plan Payload Contract

### 3.1 Required Fields

Each plan payload must contain:

```json
{
  "steps": [ ... ]
}
```

### 3.2 Step Schema

Each step must follow this shape:

```json
{
  "step_id": "string",
  "title": "string (optional)",
  "dependencies": ["step_id", ...],
  "tool": "tool_name"
}
```

or

```json
{
  "step_id": "string",
  "dependencies": [],
  "tool": {
    "name": "tool_name",
    "args": { ... }
  }
}
```

### 3.3 Constraints

- `step_id` must be unique and non-empty.
- `dependencies` must be a list of valid `step_id`s.
- `tool` must be either:
  - a non-empty string, or
  - an object with `{ name, args }`.
- `args` must be an object.
- Do not mix `step.args` and `tool.args`.

### Step ID Sequence

When using the `step_{k}` convention, step ids must be sequential and contiguous:

- Must start from `step_1`
- Must be contiguous: `step_1..step_N`
- No gaps (e.g., `step_1, step_3`) and no missing prefixes (e.g., only `step_2, step_3`)


---

## 4. Execution Semantics

### 4.1 Step-level Semantics

| Situation                          | Behavior            |
|-----------------------------------|---------------------|
| Dependency does not exist          | Fail-fast           |
| Dependency failed                 | Skip current step  |
| Dependency skipped                | Skip current step  |
| Tool not found                    | Step fails         |
| Tool throws runtime error         | Step fails         |

---

### 4.2 Step Result Schema

Each step execution produces:

```json
{
  "step_id": "string",
  "tool": "string | null",
  "ok": true | false,
  "skipped": true | false,
  "reason": "string | null",
  "error": "string | null",
  "output": "any (optional)"
}
```

#### Constraints

- `skipped = true` → `ok` must be `false`
- `ok = true` → `error` must be `null`
- `ok = false && skipped = false` → must include `error` or `reason`

---

## 5. Meta Summary Contract

Executor must append a final `__meta__` entry as the last item:

```json
{
  "step_id": "__meta__",
  "ok": true | false,
  "skipped": false,
  "reason": "string | null",
  "task_status": "COMPLETED | PARTIAL | FAILED | BLOCKED",
  "stats": {
    "total_steps": 2,
    "ok": 1,
    "skipped": 1,
    "failed": 0
  },
  "blocked_steps": ["step_id", ...],
  "failed_steps": ["step_id", ...]
}
```

### 5.1 task_status Semantics

| Status     | Meaning                                                  |
|------------|----------------------------------------------------------|
| COMPLETED  | All steps executed successfully                          |
| PARTIAL    | Some steps skipped, none blocked or failed               |
| FAILED     | At least one step failed                                 |
| BLOCKED    | Dependency resolution prevented execution                |

---

## 6. Validator Responsibilities

### 6.1 Payload Validator

Validates:
- Schema shape
- Dependency references
- Tool field structure
- Step ID uniqueness

### 6.2 Execution Result Validator

Validates:
- Result shape
- `__meta__` existence and position
- Semantic consistency of `ok/skipped/error`
- Valid `task_status`
- Stats presence

---

## 7. Why This Contract Matters

Without a contract:
- Planner bugs silently propagate
- Executor behavior becomes unpredictable
- UI cannot reliably infer status
- Regression is hard to detect

With this contract:
- Planner, executor, and UI are decoupled
- Behavior is testable
- Failure modes are explicit
- Semantics remain stable over time

---

## 8. Recommended Usage

### Development

- Run semantic verification script after changes
- Treat contract violations as test failures

### CI

- Validate both payloads and execution results
- Block merges if contract breaks

### UI / API

- Use `task_status` for high-level state
- Use per-step `ok/skipped/reason/error` for detail

---

## 9. Versioning

If this contract changes:
- Bump a semantic version
- Update validator
- Add regression cases

Never change semantics silently.

---

## 10. Summary

This execution contract formalizes:
- What a plan is
- How it executes
- How failure propagates
- How outcomes are summarized

It is a **production-level design**, not a tutorial artifact.

