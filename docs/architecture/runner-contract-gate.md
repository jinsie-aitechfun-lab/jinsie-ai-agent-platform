# Runner Contract Gate — Documentation Suite (Frozen v1)

> **Status:** Frozen
> **Purpose:** This suite defines the *single source of truth* for how the Runner Contract Gate works, how it is used, and what rules future changes must follow.

---

## 1. Overview

The **Runner Contract Gate** is a deterministic, offline, CI-aligned validation layer that protects the stability of `app/agents/runner.py` and its execution contract.

It enforces:

* Stable step semantics
* Deterministic behavior (no external LLM/API calls)
* Consistent public artifacts
* Clean working tree guarantees

This gate is designed to fail fast and loudly when contract-breaking changes are introduced.

---

## 2. Scope

The gate applies to:

* `app/agents/runner.py`
* `app/agents/plan_executor.py`
* `app/agents/plan_validator.py`
* `scripts/verify_execution_semantics.py`
* `scripts/generate_samples.py`

Changes to these components must pass the contract gate.

---

## 3. Design Principles

### 3.1 Deterministic

* No network calls
* No external APIs
* No nondeterministic sources
* Same input → same output

### 3.2 Offline

* Must run locally without credentials
* Must run in CI without secrets

### 3.3 Contract-Oriented

* Validates *behavioral promises*, not just syntax
* Protects invariants over time

### 3.4 Single Source of Truth

* CI workflow is canonical
* Local Makefile target mirrors CI exactly

---

## 4. What the Gate Enforces

### 4.1 Compile-time Sanity

The following files must compile:

* `app/agents/plan_executor.py`
* `app/agents/plan_validator.py`
* `app/agents/runner.py`
* `scripts/verify_execution_semantics.py`
* `scripts/generate_samples.py`

This prevents accidental syntax or import errors.

---

### 4.2 Execution Semantics Validation

Runs:

```bash
PYTHONPATH=. python scripts/verify_execution_semantics.py
```

This script validates:

* Step normalization
* Dependency integrity
* Expected step enforcement
* Degraded execution behavior
* Contract invariants

---

### 4.3 Public Artifact Regeneration

Runs:

```bash
PYTHONPATH=. python scripts/generate_samples.py
```

Ensures that:

* Samples are reproducible
* Generated files are up-to-date
* No silent drift occurs

---

### 4.4 Clean Working Tree Guarantee

After all steps:

```bash
git diff --exit-code
git status --porcelain
```

Must be empty.

This ensures:

* All generated changes are committed
* No hidden diffs remain

---

## 5. Canonical CI Definition

The **single source of truth** is:

```
.github/workflows/contract-verification.yml
```

It defines:

* When the gate runs
* What commands execute
* What files are protected

Local scripts must never diverge from this behavior.

---

## 6. Local Entry Point

Local execution must go through:

```bash
make runner-contract
```

This target must always match CI behavior.

---

## 7. Makefile Contract

The Makefile target `runner-contract` is the only supported local interface.

Rules:

* Must mirror CI exactly
* Must remain deterministic
* Must not call external APIs
* Must fail on drift

---

## 8. Change Rules (Frozen)

Any of the following require an explicit architecture PR:

* Adding/removing a gate step
* Changing validation semantics
* Relaxing any invariant
* Introducing nondeterminism
* Introducing network calls

---

## 9. What This Gate Is NOT

* Not a test framework
* Not a benchmark system
* Not a training pipeline
* Not an LLM evaluator

It is a **contract firewall**.

---

## 10. Governance

This document is **frozen**.

Changes require:

* New architecture PR
* Explicit justification
* Migration plan

---

## 11. Summary

The Runner Contract Gate protects:

* Behavioral stability
* Reproducibility
* CI/Local parity
* Developer sanity

This suite is the canonical reference.

---

**End of Frozen Spec**
