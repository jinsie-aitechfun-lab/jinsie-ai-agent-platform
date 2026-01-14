# System Modules

## Module 1: entry_shell

**Purpose**: CLI / entry scripts. Parse args, invoke orchestration, print/save outputs.
 **Owns**: scripts/*.py (entry)
 **Must NOT**: call tools directly; implement contract rules; implement execution.

## Module 2: agent_orchestration

**Purpose**: Orchestrate one run: prompt -> llm -> parse json -> validate -> execute -> finalize output.
 **Owns**: app/agents/runner.py
 **Must NOT**: define contract rules; dispatch tools; implement step dependency logic.

## Module 3: contract_prompt

**Purpose**: Define output contract + runtime validation + system prompt.
 **Owns**: app/agents/plan_validator.py, app/prompts/system/agent_system.md
 **Must NOT**: execute steps; call tools; call llm.

## Module 4: execution_engine

**Purpose**: Execute steps with dependency rules; produce execution_results + **meta**.
 **Owns**: app/agents/plan_executor.py
 **Must NOT**: generate plans; validate payload shape; implement tool registry.

## Module 5: tool_runtime

**Purpose**: Register/list/dispatch tools; provide default tools; keep tool surface stable.
 **Owns**: app/tools/*
 **Must NOT**: orchestrate runs; enforce plan contract; decide step ordering.

## Dependency Rules (import direction)

entry_shell -> agent_orchestration -> execution_engine -> tool_runtime
 agent_orchestration -> contract_prompt
 execution_engine -> contract_prompt (only if you do post-checks)
 contract_prompt must not import others (except stdlib)

> NOTE: This document defines *module boundaries* not folder structure.