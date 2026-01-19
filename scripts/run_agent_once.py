from __future__ import annotations
# Module: entry_shell
# Boundary: do NOT import app.tools/* or app.agents.plan_executor/plan_validator directly
# See: docs/architecture/modules.md

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from app.agents.runner import load_text, run_agent_once_json


def save_text(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _get_task_status(payload: Dict[str, Any]) -> Optional[str]:
    """
    Best-effort extract task_status from execution_results.__meta__.
    Returns: "COMPLETED"/"FAILED"/"BLOCKED"/None
    """
    results = payload.get("execution_results")
    if not isinstance(results, list):
        return None
    for r in results:
        if isinstance(r, dict) and r.get("step_id") == "__meta__":
            v = r.get("task_status")
            return v if isinstance(v, str) else None
    return None


def _classify_exception(e: Exception) -> str:
    """
    Classify failures into stable buckets for repeat stats.
    This is intentionally string-based to avoid coupling runner internals.
    """
    msg = str(e) or ""
    msg_low = msg.lower()

    # Rate limit / quota / permission restrictions
    # Example seen in your logs:
    # PermissionDeniedError: Error code: 403 - RPM limit exceeded. Please complete identity verification...
    if "rpm limit exceeded" in msg_low or "rate limit" in msg_low:
        return "rate_limited"
    if "error code: 403" in msg_low and ("limit" in msg_low or "rpm" in msg_low):
        return "rate_limited"

    # JSON/repair related
    if "repair output is still not valid json" in msg_low:
        return "repair_json_failed"
    if "no json object found" in msg_low:
        return "parse_json_failed"
    if "jsondecodeerror" in msg_low:
        return "parse_json_failed"
    if "not valid json" in msg_low and "repair" not in msg_low:
        return "parse_json_failed"

    # validator related (contract)
    if "plan contract validation failed" in msg_low:
        return "validator_failed"
    if "step_id sequence must start from step_1" in msg_low:
        return "validator_failed"
    if "step_id sequence must be contiguous" in msg_low:
        return "validator_failed"

    # infra / empty output
    if "model output is empty" in msg_low:
        return "empty_output"

    return "other_exception"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single agent call with strict JSON output.")
    parser.add_argument("query", nargs="?", help="User query text")
    parser.add_argument("--input-file", help="Path to a text file containing the user query")
    parser.add_argument("--output-file", help="Save JSON output to a file (e.g., docs/samples/agent_output.json)")
    parser.add_argument("--debug", action="store_true", help="Print full payload including steps and execution_results")

    # ✅ PCL schema toggle (default: enabled)
    parser.add_argument("--no-schema", action="store_true", help="Disable PCL schema addendum injection")

    # ✅ Expected steps (optional, strict intent hook)
    parser.add_argument(
        "--expected-steps",
        type=int,
        default=None,
        help="If provided, enforce/guide the model to output exactly N steps (best-effort).",
    )

    # ✅ Repeat mode
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Run the same query N times and print failure statistics.",
    )
    parser.add_argument(
        "--print-each",
        action="store_true",
        help="In repeat mode, print payload for each run (otherwise only prints summary and last payload).",
    )
    parser.add_argument(
        "--sleep-ms",
        type=int,
        default=0,
        help="Sleep milliseconds between runs (repeat mode only).",
    )
    parser.add_argument(
        "--stop-on-rate-limit",
        action="store_true",
        help="Stop repeating immediately if a rate limit is hit (recommended for clean stats).",
    )

    args = parser.parse_args()

    if args.repeat < 1:
        print("Error: --repeat must be >= 1", file=sys.stderr)
        raise SystemExit(2)

    if args.input_file:
        user_input = load_text(args.input_file).strip()
    elif args.query:
        user_input = args.query.strip()
    else:
        print("Error: provide query text or --input-file", file=sys.stderr)
        raise SystemExit(2)

    # --- Single run: keep old behavior ---
    if args.repeat == 1:
        payload = run_agent_once_json(
            user_input,
            prompt_path="app/prompts/system/agent_system.md",
            temperature=0.2,
            debug=args.debug,
            schema_enabled=not args.no_schema,
            expected_steps=args.expected_steps,  # type: ignore[arg-type]
        )

        pretty = json.dumps(payload, ensure_ascii=False, indent=2)

        if args.output_file:
            save_text(args.output_file, pretty + "\n")

        print(pretty)
        return

    # --- Repeat mode ---
    stats: Dict[str, int] = {
        "total_runs": 0,
        "effective_runs": 0,  # excluding rate_limited runs
        "success_runs": 0,
        "exception_runs": 0,
        "execution_failed_runs": 0,
        "execution_blocked_runs": 0,
        "execution_completed_runs": 0,
        "rate_limited": 0,
        "parse_json_failed": 0,
        "repair_json_failed": 0,
        "validator_failed": 0,
        "empty_output": 0,
        "other_exception": 0,
    }

    last_payload: Optional[Dict[str, Any]] = None
    last_exception: Optional[str] = None
    stopped_early: bool = False

    for i in range(1, args.repeat + 1):
        stats["total_runs"] += 1
        try:
            payload = run_agent_once_json(
                user_input,
                prompt_path="app/prompts/system/agent_system.md",
                temperature=0.2,
                debug=args.debug,
                schema_enabled=not args.no_schema,
                expected_steps=args.expected_steps,  # type: ignore[arg-type]
            )
            last_payload = payload
            last_exception = None

            task_status = _get_task_status(payload)

            # Effective run (not rate limit)
            stats["effective_runs"] += 1

            if task_status == "COMPLETED":
                stats["execution_completed_runs"] += 1
                stats["success_runs"] += 1
            elif task_status == "FAILED":
                stats["execution_failed_runs"] += 1
            elif task_status == "BLOCKED":
                stats["execution_blocked_runs"] += 1
            else:
                # No meta row: still count as success (no exception)
                stats["success_runs"] += 1

            if args.print_each:
                pretty = json.dumps(payload, ensure_ascii=False, indent=2)
                print(f"\n===== RUN {i}/{args.repeat} =====")
                print(pretty)

        except Exception as e:
            last_payload = None
            last_exception = f"{type(e).__name__}: {e}"
            stats["exception_runs"] += 1

            bucket = _classify_exception(e)
            stats[bucket] = stats.get(bucket, 0) + 1

            # Do NOT count rate-limited runs as effective samples
            if bucket != "rate_limited":
                stats["effective_runs"] += 1

            if args.print_each:
                print(f"\n===== RUN {i}/{args.repeat} (EXCEPTION) =====")
                print(last_exception, file=sys.stderr)

            if bucket == "rate_limited" and args.stop_on_rate_limit:
                stopped_early = True
                break

        if args.sleep_ms > 0 and i != args.repeat:
            time.sleep(args.sleep_ms / 1000.0)

    # Print summary
    print("\n==================== REPEAT SUMMARY ====================")
    print(f"repeat_requested: {args.repeat}")
    print(f"stopped_early: {stopped_early}")
    print(f"schema_enabled: {not args.no_schema}")
    print(f"expected_steps: {args.expected_steps}")
    print(f"sleep_ms: {args.sleep_ms}")
    print(f"stop_on_rate_limit: {args.stop_on_rate_limit}")
    print("--------------------------------------------------------")
    print(f"total_runs: {stats['total_runs']}")
    print(f"rate_limited: {stats['rate_limited']}")
    print(f"effective_runs (excluding rate_limited): {stats['effective_runs']}")
    print("--------------------------------------------------------")
    print(f"success_runs: {stats['success_runs']}")
    print(f"exception_runs: {stats['exception_runs']}")
    print("--------------------------------------------------------")
    print("execution_status (from __meta__.task_status when present):")
    print(f"  COMPLETED: {stats['execution_completed_runs']}")
    print(f"  FAILED:    {stats['execution_failed_runs']}")
    print(f"  BLOCKED:   {stats['execution_blocked_runs']}")
    print("--------------------------------------------------------")
    print("exception_buckets:")
    print(f"  rate_limited:        {stats['rate_limited']}")
    print(f"  parse_json_failed:   {stats['parse_json_failed']}")
    print(f"  repair_json_failed:  {stats['repair_json_failed']}")
    print(f"  validator_failed:    {stats['validator_failed']}")
    print(f"  empty_output:        {stats['empty_output']}")
    print(f"  other_exception:     {stats['other_exception']}")
    print("========================================================")

    if last_payload is not None:
        pretty = json.dumps(last_payload, ensure_ascii=False, indent=2)
        print("\n==================== LAST PAYLOAD ======================")
        print(pretty)

        if args.output_file:
            save_text(args.output_file, pretty + "\n")
    else:
        if last_exception:
            print("\n==================== LAST EXCEPTION ====================")
            print(last_exception, file=sys.stderr)


if __name__ == "__main__":
    main()
