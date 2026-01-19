# Runner Contract Gate

This repository uses a deterministic contract gate to keep `app/agents/runner.py` (and its immediate plan contract) stable.

The gate is intentionally **deterministic** and **does not call any external LLM API**. It only runs local Python checks and repository scripts.


## What it checks

### 1) Compile-time sanity

Ensures the following modules compile (syntax/type-level issues are caught early):

- `app/agents/plan_executor.py`
- `app/agents/plan_validator.py`
- `app/agents/runner.py`
- `scripts/verify_execution_semantics.py`
- `scripts/generate_samples.py`


### 2) Contract-level execution semantics (deterministic)

Runs:

- `scripts/verify_execution_semantics.py`

This script is expected to validate the runner's key execution semantics and to be safe for CI (no external calls).


### 3) Public sample regeneration (deterministic)

Runs:

- `scripts/generate_samples.py`

This step regenerates public samples (if any) and verifies that the repository remains consistent.


### 4) Working tree must remain clean

After scripts run, CI asserts there are no uncommitted changes:

- `git diff --exit-code`
- `git status --porcelain` must be empty

This prevents “generated files drift” and keeps changes explicit in PRs.


## How to run locally

Recommended single entrypoint (via Makefile):

- `make runner-contract`

Or run the underlying steps directly (from repo root):

1) Compile checks (example):

```bash
python -m py_compile app/agents/plan_executor.py
python -m py_compile app/agents/plan_validator.py
python -m py_compile app/agents/runner.py
python -m py_compile scripts/verify_execution_semantics.py
python -m py_compile scripts/generate_samples.py
```

2) Semantics verification:

```bash
PYTHONPATH=. python scripts/verify_execution_semantics.py
```

3) Regenerate samples:

```bash
PYTHONPATH=. python scripts/generate_samples.py
```

4) Ensure clean working tree:

```bash
git diff --exit-code
git status --porcelain
```


## CI workflow mapping

The canonical CI workflow for this gate is:

- `.github/workflows/contract-verification.yml`

It runs on:

- Pull requests targeting `dev`
- Pushes to `dev`

This workflow is the **single source of truth** for the contract gate.


## Makefile target (recommended)

Add one target so local and CI share a single command entrypoint:

- `make runner-contract`

This keeps daily workflow simple and reduces “CI passes but local forgot to run X” situations.
