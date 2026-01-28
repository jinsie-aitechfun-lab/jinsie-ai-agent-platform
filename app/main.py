"""
Jinsie AI Agent Platform
Copyright (c) 2025 Jinsie | AITechFun Lab
SPDX-License-Identifier: MIT
"""

from dotenv import load_dotenv
load_dotenv(override=False)

from fastapi import FastAPI
from pydantic import BaseModel

from app.graphs.workflow_runner import run_minimal_workflow

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    return {"ok": True}


class WorkflowRunRequest(BaseModel):
    input: str
    trace: bool = False


class WorkflowRunResponse(BaseModel):
    answer: str
    result: dict


def _extract_answer(result: dict) -> str:
    """
    Best-effort extraction of a user-facing answer from workflow result.

    We do NOT assume a specific output schema yet. Keep it stable:
    - Prefer common keys if present
    - Otherwise fall back to a compact string
    """
    if not isinstance(result, dict):
        return str(result)

    # Common candidates (current/next iterations may use any of these)
    for k in ("answer", "final_answer", "output", "result", "response", "text"):
        v = result.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()

    # Some nodes may write nested payloads
    output = result.get("output")
    if isinstance(output, dict):
        for k in ("answer", "final_answer", "text", "content"):
            v = output.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()

    # Last resort
    return str(result)


@app.post("/v1/workflow/run", response_model=WorkflowRunResponse)
def workflow_run(req: WorkflowRunRequest):
    # We keep today’s contract minimal:
    # - raw_input: user's input text
    # - trace: whether to print node snapshots (for debug)
    result = run_minimal_workflow(
        req.input,
        trace=req.trace,
        retriever="keyword",
        reasoner="simple",
        top_k=2,
    )
    answer = _extract_answer(result)
    return {"answer": answer, "result": result}
