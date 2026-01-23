from __future__ import annotations

import subprocess
import sys


def _run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(
            "Command failed\n"
            f"cmd: {' '.join(cmd)}\n"
            f"returncode: {p.returncode}\n"
            f"stdout:\n{p.stdout}\n"
            f"stderr:\n{p.stderr}\n"
        )
    return p.stdout


def main() -> int:
    py = sys.executable

    # Case 1: answer-only should be non-empty and should NOT include trace markers by default
    out1 = _run([py, "scripts/run_workflow.py", "帮我总结一下今天我做了什么", "--answer-only"])
    if not out1.strip():
        raise AssertionError("Expected non-empty answer-only output, got empty output.")
    if "--- [1] BEFORE" in out1:
        raise AssertionError("answer-only output should not include trace markers by default.")

    # Case 2: trace mode should include trace markers (BEFORE/AFTER)
    out2 = _run([py, "scripts/run_workflow.py", "帮我总结一下今天我做了什么", "--trace"])
    if "--- [1] BEFORE input" not in out2:
        raise AssertionError("Expected trace markers in output when --trace is set.")

    print("[PASS] workflow CLI verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
