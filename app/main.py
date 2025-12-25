"""
Jinsie AI Agent Platform
Copyright (c) 2025 Jinsie | AITechFun Lab
SPDX-License-Identifier: MIT
"""

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
