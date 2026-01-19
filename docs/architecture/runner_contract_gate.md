# Runner Contract Gate · Architecture Freeze

## Status

**FROZEN** — This document is the single source of truth for the Runner Contract Gate.

## Purpose

Runner Contract Gate is a deterministic CI + local gate designed to keep the behavior of:

- `app/agents/runner.py`
- and its immediate plan contract surface

**stable, reviewable, and reproducible**.

The gate is intentionally **deterministic** and **must NOT call any external LLM API**.

## Single Source of Truth

- **CI source of truth:** `.github/workflows/contract-verification.yml`
- **Local entrypoint:** `make runner-contract`

Local and CI must run the same logical checks. Local is a convenience wrapper, CI is the authority.

## What It Checks (Deterministic)

### 1) Compile-time sanity

Ensures the following modules compile:

- `app/agents/plan_executor.py`
- `app/agents/plan_validator.py`
- `app/agents/runner.py`
- `scripts/verify_execution_semantics.py`
- `scripts/generate_samples.py`

Goal: catch syntax / import / basic compile failures early.

### 2) Contract-level execution semantics

Runs:

- `scripts/verify_execution_semantics.py`

Requirements for this script:

- deterministic
- safe for CI
- no network calls
- no external service dependencies

### 3) Public sample regeneration (optional but deterministic)

Runs:

- `scripts/generate_samples.py`

Goal: regenerate public samples (if any) and assert repo consistency.

### 4) Working tree must remain clean

After scripts run, the repo must have no uncommitted changes:

- `git diff --exit-code`
- `git status --porcelain` must be empty

Goal: prevent “generated files drift” and force explicit updates in PRs.

## How to Run Locally

Recommended single entrypoint:

- `make runner-contract`

Equivalent manual steps:

1) Compile:

- `python -m py_compile app/agents/plan_executor.py`
- `python -m py_compile app/agents/plan_validator.py`
- `python -m py_compile app/agents/runner.py`
- `python -m py_compile scripts/verify_execution_semantics.py`
- `python -m py_compile scripts/generate_samples.py`

2) Semantics:

- `PYTHONPATH=. python scripts/verify_execution_semantics.py`

3) Samples:

- `PYTHONPATH=. python scripts/generate_samples.py`

4) Clean tree:

- `git diff --exit-code`
- `test -z "$(git status --porcelain)"`

## Evolution Rules

### Allowed changes

- tightening semantics in `scripts/verify_execution_semantics.py` (with clear intent)
- adding new deterministic checks that do not require external APIs
- updating sample generation rules, as long as “clean tree” remains enforced

### Forbidden changes

- adding any external LLM/API call into the gate
- making the gate nondeterministic (time, randomness, network dependency)
- splitting into multiple competing CI workflows for the same contract purpose
- weakening the “clean tree” constraint without replacing it with an equivalent safety mechanism

## Change Governance

Any change that affects the gate must:

- be in a PR
- include a clear summary of why
- include evidence the gate still runs deterministically on CI
- keep `.github/workflows/contract-verification.yml` as the authority
