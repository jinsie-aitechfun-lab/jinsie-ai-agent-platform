# CLI repeat & chat client hardening (timeouts / trust_env)

This repo provides a minimal CLI (`scripts/run_agent_once.py`) to validate agent JSON contracts.

Key hardening:
- httpx timeouts enabled to avoid hanging requests
- `trust_env` default is false to prevent accidental proxy env issues
- `--repeat` mode to quantify stability; `--stop-on-rate-limit` for clean runs

Quick verification examples:
- `python scripts/run_agent_once.py "<prompt>" --expected-steps 3`
- `python scripts/run_agent_once.py "<prompt>" --expected-steps 3 --repeat 5 --sleep-ms 600 --stop-on-rate-limit`
