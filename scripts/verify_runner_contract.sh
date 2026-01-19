#!/usr/bin/env bash
set -euo pipefail

QUERY="生成一个3步计划：step_2 使用 no_such_tool，step_3 依赖 step_2 且使用 get_time"

echo "== Runner contract: single run (expected_steps=3) =="
PYTHONPATH=. python scripts/run_agent_once.py \
  "${QUERY}" \
  --debug --expected-steps 3 >/dev/null

echo "== Runner contract: repeat stability (stop on rate limit) =="
# CI/本地都可能遇到 RPM 限制，所以默认 stop-on-rate-limit
# repeat 5 足够覆盖“漂移/repair/replan”常见路径，同时不会太耗额度
PYTHONPATH=. python scripts/run_agent_once.py \
  "${QUERY}" \
  --debug --expected-steps 3 --repeat 5 --stop-on-rate-limit >/dev/null

echo "[PASS] runner contract gate OK"
