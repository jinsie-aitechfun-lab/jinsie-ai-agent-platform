# Jinsie AI Agent Platform (RAG seed)

This repository provides:
- Multi-agent execution runner
- Tool registry and tool calling
- Prompt control layer (PCL)
- Workflow skeleton and nodes
- Retriever/reasoner/render pipeline

Goal: load docs, chunk them, embed, retrieve top-k chunks, and answer with citations.
## Architecture notes (extended)

### Core modules
- app/agents: planner, executor, validator, runner orchestration.
- app/tools: tool schema, registry, built-in tools (echo/time/search/summarize).
- app/graphs: workflow nodes, retrievers, reasoners, workflow runner.
- app/services: OpenAI-compatible client wrapper and chat completion service.

### Execution semantics
- Plan is a list of steps with dependencies.
- Each step produces structured outputs validated by contracts.
- Failures are handled with fallback rules and retry policies.
- The runner records traces for debugging and observability.

### RAG pipeline
- Load local documents (markdown/text).
- Normalize and chunk documents.
- Embed chunks with an embeddings model.
- Retrieve top-k by cosine similarity.
- Build a bounded context window with chunk ids.
- Ask the LLM to answer using ONLY the provided context and cite chunk ids.

### Future extensions
- Replace in-memory store with Milvus/OpenSearch.
- Add reranking and metadata filters.
- Add evaluation harness for recall/precision.
- Add caching for embeddings and retrieval results.
