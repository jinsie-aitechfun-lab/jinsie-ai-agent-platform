# Agent 执行链路里程碑说明（公开工程版）

> 用途：对外说明当前 Agent 的最小可运行能力与输出契约。  
> 建议存放：`docs/architecture/agent_execution_milestone.md`（可公开）

---

## 目标能力

当前版本提供一个可运行的 Agent 执行管线（execution pipeline），实现：

- 模型生成结构化计划（plan）
- 计划驱动的工具（tool）顺序执行
- 执行轨迹可追溯（execution trace）
- 对外输出契约稳定（JSON-safe）

---

## 核心组件

- Runner：负责模型调用、plan 解析、触发执行并返回结果
- Plan Executor：遍历 steps 并执行对应工具
- Tool Registry：注册并分发工具调用
- Tools：以函数形式实现、返回 JSON-safe 结果

---

## 执行流程

```
User Input
 → Agent Plan (JSON)
 → Tool Execution (ordered)
 → Execution Results (trace)
 → Final Output (contract)
```

---

## 输出契约

每次工具执行都会产生一个结果记录（execution trace），用于调试与审计。  
最终对外输出可采用两种策略：

- 返回完整 payload（包含计划与执行轨迹）
- 返回最终工具输出（简洁、面向调用方）

无论采用哪种策略，输出必须是 JSON-safe。

---

## 验证方式（示例）

可使用 `echo_tool` 执行最小闭环验证：

```bash
python scripts/run_agent_once.py "请调用一个名为 echo_tool 的工具，参数为 {"text":"hi"}，然后把工具结果原样输出为严格JSON"
```

期望行为：

- 工具被正确调用
- 执行结果包含 `{"echo": "hi"}`（在最终输出或执行轨迹中体现）
- 输出为严格 JSON

---

## 可扩展性

新增工具无需修改 Runner 控制流，只需：

1. 实现工具函数（返回 JSON-safe）
2. 注册到 Tool Registry
3. 在 prompt/工具描述中暴露工具名与参数 schema（如适用）

该模式支持按需逐步扩展（例如文件读写、HTTP 获取等），并可进一步演进为“模型→工具→模型”的多轮执行闭环。
