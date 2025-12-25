# Jinsie AI Agent Platform

A multi-agent automation platform built with **LangGraph** (on top of LangChain) and FastAPI.  
Targeting enterprise-grade, cloud-native AI applications such as knowledge worker automation, RAG services, and intelligent operations.

## Tech Stack

- Python, FastAPI
- LangGraph (graph-based, stateful orchestration)
- LangChain components (tools, RAG pipelines)
- Milvus (vector database)
- Docker + Alibaba Cloud (cloud deployment, later)

## Architecture (High-level)

- **Orchestration Layer**: LangGraph graphs for stateful multi-agent workflows  
- **LLM & Tools Layer**: LangChain components (LLM wrappers, tools, RAG chains)  
- **API Layer**: FastAPI endpoints for task submission, status querying, and results  
- **Vector Store**: Milvus for document embeddings and retrieval  
- **Observability (planned)**: logging, tracing, and run history for LLMOps

More details in [`docs/architecture.md`](docs/architecture.md).

## Repository Structure

- `app/graphs/` – LangGraph graphs defining multi-agent workflows  
- `app/agents/` – individual agents (planner, retriever, analyst, executor, etc.)  
- `app/tools/` – tools used by agents (search, RAG query, external APIs)  
- `app/services/` – business use cases composed from graphs and tools  
- `app/routers/` – FastAPI routes (HTTP API)  
- `app/core/` – config, logging, dependency injection  
- `docs/` – architecture, roadmap, learning notes, and project logs  
- `tests/` – unit and integration tests

## Progress Log

- 2025-12-26: Initialize LangGraph-based project skeleton.
