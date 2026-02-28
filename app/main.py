"""
Jinsie AI Agent Platform
Copyright (c) 2025 Jinsie | AITechFun Lab
SPDX-License-Identifier: MIT
"""

from dotenv import load_dotenv
load_dotenv(override=False)

from fastapi import FastAPI
from pydantic import BaseModel
from time import perf_counter

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
    t0 = perf_counter()
    result = run_minimal_workflow(
        req.input,
        trace=req.trace,
        retriever="keyword",
        reasoner="simple",
        top_k=2,
    )
    total_ms = (perf_counter() - t0) * 1000.0

    # pull timings from state/result if present
    retrieval_ms = 0.0
    llm_ms = 0.0
    if isinstance(result, dict):
        retrieval_ms = float(result.get("retrieval_ms", 0.0) or 0.0)
        llm_ms = float(result.get("llm_ms", 0.0) or 0.0)
        result["metrics"] = {
            "total_ms": float(total_ms),
            "retrieval_ms": float(retrieval_ms),
            "llm_ms": float(llm_ms),
        }

    answer = _extract_answer(result)
    return {"answer": answer, "result": result}