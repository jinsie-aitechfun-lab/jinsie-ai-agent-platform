# Contract verification guide

This repo includes a small, runnable contract verification suite that enforces:

- Plan payload schema (planner contract)
- Dependency semantics (blocked vs failed)
- Tool whitelist behavior (unknown tool fails, downstream skipped)
- Execution summary / meta status invariants

## Quick commands

### 1) Compile-time sanity checks

```bash
python -m py_compile app/agents/plan_executor.py
python -m py_compile app/agents/plan_validator.py
python -m py_compile app/agents/runner.py
python -m py_compile scripts/verify_execution_semantics.py
python -m py_compile scripts/generate_samples.py
```

### 2) Verify execution semantics

```bash
PYTHONPATH=. python scripts/verify_execution_semantics.py
```

Expected output ends with:

- `[PASS] contract execution semantics verified`

### 3) Regenerate public samples

```bash
PYTHONPATH=. python scripts/generate_samples.py
```

This writes/updates:

- `docs/samples/agent_plan_sample.json`
- `docs/samples/agent_execution_plan_sample.json`

## References

- `docs/architecture/planner-contract.md`
- `docs/architecture/plan_execution_contract.md`
- `docs/architecture/plan-executor-semantics.md`
- `docs/architecture/execution-contract-closure.md`
