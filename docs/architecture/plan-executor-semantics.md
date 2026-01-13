# Plan Executor Execution Semantics

This document explains the execution semantics of `execute_plan` and the meaning of the special `__meta__` summary record.

## 1. Execution Order

Steps are executed **sequentially** in the order they appear in `payload["steps"]`.

For each step, the executor performs:

1. **Dependency existence check**
2. **Dependency status check**
3. **Tool execution (if allowed)**
4. **Result recording**

---

## 2. Dependency Rules

### 2.1 Unknown Dependency → FAIL (Hard Error)

If a step depends on a step ID that does not exist:

```json
{
  "ok": false,
  "skipped": false,
  "reason": "unknown dependency: [...]"
}
```

This is treated as a **BLOCKED** task state.

---

### 2.2 Failed or Skipped Dependency → SKIP

If a dependency:

- failed (`ok=false`), or
- was skipped

Then the current step is **skipped**:

```json
{
  "ok": false,
  "skipped": true,
  "reason": "dependency not satisfied: [...]"
}
```

---

## 3. Tool Execution Errors

If a tool raises an exception:

```json
{
  "ok": false,
  "skipped": false,
  "error": "..."
}
```

This is treated as a **FAILED** step.

---

## 4. The `__meta__` Record

At the end of execution, the executor appends a synthetic record:

```json
{
  "step_id": "__meta__",
  "ok": true | false,
  "skipped": false,
  "reason": "..."
}
```

### Purpose

- Summarizes the entire plan execution
- Does **not** represent a real step
- Always appended **last**

### Logic

| Condition                         | __meta__.ok | task_status |
|----------------------------------|-------------|-------------|
| All steps succeeded              | true        | COMPLETED  |
| Some skipped, some ok            | false       | PARTIAL    |
| Any dependency blocked execution | false       | BLOCKED    |
| Any tool failed                  | false       | FAILED     |

---

## 5. `compute_task_status()`

This helper computes the final state:

- `BLOCKED`
- `FAILED`
- `PARTIAL`
- `COMPLETED`

The result is embedded into `__meta__.reason`.

---

## 6. Design Principles

- Execution is **deterministic**
- Failures are **local**
- Dependency graph is **enforced**
- Summary is **explicit**
- Output is **machine-readable**

---

## 7. Why `__meta__` Is Not a Step

`__meta__` is:

❌ Not executable  
❌ Not a tool  
❌ Not a dependency  

It is:

✅ A status record  
✅ A summary node  
✅ A contract-level output  

---

## 8. Example Output

```json
[
  {"step_id": "step_1", "ok": true},
  {"step_id": "step_2", "ok": false},
  {"step_id": "step_3", "skipped": true},
  {"step_id": "__meta__", "ok": false, "reason": "one or more steps failed; task_status=FAILED"}
]
```

---

This contract allows UI, agents, and workflows to reason about execution reliably.
