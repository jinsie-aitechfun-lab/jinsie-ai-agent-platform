# CLI Guide: run_agent_once

This guide documents the CLI entry `scripts/run_agent_once.py` for reproducible runs and stability checks.

## Quick start

Run once (print JSON to stdout):

python scripts/run_agent_once.py "your query here"

Run once with full payload (includes steps + execution_results):

python scripts/run_agent_once.py "your query here" --debug

## Schema toggle

Schema is enabled by default. Disable it with `--no-schema`:

python scripts/run_agent_once.py "your query here" --no-schema

## Expected steps (best-effort intent hook)

If you want to guide/enforce the model toward exactly N steps:

python scripts/run_agent_once.py "your query here" --expected-steps 3

## Repeat mode (stability sampling)

Run the same query N times and print a summary:

python scripts/run_agent_once.py "your query here" --repeat 30

Add sleep between runs (milliseconds):

python scripts/run_agent_once.py "your query here" --repeat 200 --sleep-ms 1200

Stop early on rate limit (recommended for clean sampling):

python scripts/run_agent_once.py "your query here" --repeat 200 --sleep-ms 1200 --stop-on-rate-limit

Print each run payload (verbose):

python scripts/run_agent_once.py "your query here" --repeat 10 --print-each

## Output file

Save the last payload to a file:

python scripts/run_agent_once.py "your query here" --repeat 30 --output-file docs/samples/agent_output.json

## Network hardening (timeouts / proxy behavior)

`ChatCompletionService` supports safe defaults and env overrides.

Environment variables:

- OPENAI_TIMEOUT_SECONDS
- OPENAI_CONNECT_TIMEOUT_SECONDS
- OPENAI_READ_TIMEOUT_SECONDS
- OPENAI_MAX_RETRIES
- OPENAI_TRUST_ENV

Notes:

- `OPENAI_TRUST_ENV=false` by default to avoid accidental proxy/IDE env issues.
- Timeouts prevent long hangs during repeated sampling.
