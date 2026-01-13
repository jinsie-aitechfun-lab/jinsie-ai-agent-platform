# Planner Contract: Structured Plan Generation

**Public location:** `docs/architecture/planner-contract.md`

---

## 1. Purpose

This document defines the **contractual responsibilities of the Planner** component.

The planner is responsible for producing a **deterministic, executable, and structurally valid plan** that can be:
- Validated by the contract validator
- Executed by the executor
- Interpreted by UI and downstream systems

This contract prevents ambiguous or malformed plans from propagating into runtime.

---

## 2. Planner Responsibilities

The planner MUST:

1. Produce a single valid JSON object
2. Conform to the Output Contract
3. Follow the Step Index Contract
4. Respect the Tool Registry whitelist
5. Produce deterministic output for identical input
6. Avoid free-form or explanatory text

---

## 3. Step Index Contract

When using the `step_{k}` convention, the planner MUST:

- Start from `step_1`
- Use contiguous numbering: `step_1..step_N`
- Never skip indices
- Never emit `step_2` or `step_3` without `step_1`
- Emit steps in ascending order

### Examples

#### ❌ Invalid

```
step_2, step_3
```

```
step_1, step_3
```

#### ✅ Valid

```
step_1, step_2, step_3
```

---

## 4. Step Count Contract

If the user specifies the number of steps (e.g., "generate a 3-step plan"), the planner MUST:

- Emit exactly N steps
- Number them `step_1..step_N`
- Ensure the number of steps matches the numbering

---

## 5. Dependency Contract

Dependencies MUST:

- Reference only declared `step_id`s
- Reference only earlier steps
- Never reference future steps
- Never reference missing steps

---

## 6. Tool Contract

Each step MUST contain a `tool` field.

### 6.1 Allowed Tools

Only tools in the whitelist may be used:

- `echo_tool`
- `get_time`

### 6.2 Fallback Rule

If a requested tool is not available:

- Use `echo_tool`
- Document the downgrade in the step description and deliverable

---

## 7. Determinism Contract

The planner MUST:

- Produce stable structure for identical input
- Avoid stylistic variance
- Avoid randomness
- Avoid reordering

---

## 8. Failure Modes

The planner MUST NOT:

- Emit malformed JSON
- Emit missing fields
- Emit extra fields
- Skip step indices
- Emit unregistered tools
- Emit forward dependencies

---

## 9. Enforcement

This contract is enforced by:

- `validate_plan_payload`
- Regression test cases

Any violation MUST be treated as a hard failure.

---

## 10. Summary

The planner is a **contractual producer** of executable plans.

It is not a chat assistant.
It is not a free-form generator.

It is a deterministic, contract-bound system component.

