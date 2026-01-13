# Plan Execution Workflow Summary

本文件总结“计划生成 → 合约校验 → 依赖解析 → 工具执行 → 结果汇总”的执行链路，作为后续迭代与回归验证的基线说明。

## Components

- `app/agents/plan_validator.py`
  - 计划合约（plan contract）的单一事实来源（single source of truth）
  - 对 top-level 字段、steps schema、step_id 序列、依赖合法性、tool 结构做校验
- `app/agents/plan_executor.py`
  - 执行器：按依赖关系执行 steps，输出 `execution_results` 与 `__meta__`
  - 关键语义：FAILED / BLOCKED / COMPLETED（以及按依赖跳过的 step）
- `app/agents/runner.py`
  - runner：负责模型输出解析 → 合约校验 → 调用执行器 → 按返回 contract 输出结果
- `scripts/verify_execution_semantics.py`
  - 回归验证脚本：验证执行语义是否满足合约预期
- `scripts/generate_samples.py`
  - samples 生成脚本：生成 `docs/samples/*.json`，确保样例与合约一致

## Execution Results Contract

执行结果写入 `payload["execution_results"]`，结构包含：

- 每个 step 的执行结果（按 step_id）
  - `ok`: bool
  - `skipped`: bool（依赖未满足时为 true）
  - `tool`: 工具名（未知工具时会在 executor 阶段报错）
  - `reason` / `error`: 可诊断信息
- `__meta__` 汇总项（最后一条）
  - `task_status`: FAILED / BLOCKED / COMPLETED
  - `stats`: { total_steps, ok, skipped, failed }
  - `blocked_steps`, `failed_steps`: 用于诊断

## Verified Scenarios

`verify_execution_semantics.py` 覆盖并验证以下场景：

1. step_id 序列非法（例如从 step_2 开始）→ 合约校验失败
2. 未知工具 → step FAILED，依赖步骤 SKIPPED，任务 FAILED
3. 依赖不存在 → step BLOCKED，任务 BLOCKED

## Operational Notes

- `docs/samples/*.json` 为可公开样例，建议由 `scripts/generate_samples.py` 生成，避免手工漂移
- 合约更新时，必须同步：
  1) `plan_validator.py`
  2) `verify_execution_semantics.py`
  3) `generate_samples.py` 与 samples 输出
