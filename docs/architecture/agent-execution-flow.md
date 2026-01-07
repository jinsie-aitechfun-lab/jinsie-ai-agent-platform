# Agent 执行流程说明

本文档说明本项目中 **单次 Agent 执行（single-run）** 的完整工程流程。

## 执行入口

```text
scripts/run_agent_once.py
  → app/agents/runner.py
    → ChatCompletionService
```

## Runner 职责

- 调用模型
- 清洗输出
- JSON 解析与校验
- 失败时落盘原始输出

## 输出契约

顶层字段：

- task_summary
- steps
- assumptions
- risks

steps 中每个元素必须包含：

- step_id
- title
- description
- dependencies
- deliverable
- acceptance

## 调试文件

当解析失败时，原始输出会保存到：

```text
docs-private/_debug/last_agent_raw.txt
```

## 扩展方向

- LangGraph 多步 Workflow
- RAG + Tool 执行
- Trace / 日志 / 可观测性
