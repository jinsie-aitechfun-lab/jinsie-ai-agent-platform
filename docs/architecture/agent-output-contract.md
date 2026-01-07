# Agent 输出契约说明（Agent Output Contract）

本文档定义 **Jinsie AI Agent Platform** 中 Agent 输出的 **统一 JSON 契约**，
用于保证：

- 机器可消费
- 可校验
- 可扩展
- 可调试

该契约适用于：

- CLI 执行
- API 调用
- 测试样例
- 后续多步 Agent / Workflow

---

## 设计目标

1. **强约束**
   - 禁止自由文本作为最终结果
   - 所有输出必须符合 JSON Schema

2. **稳定性**
   - 下游系统可安全依赖
   - 避免 Prompt 波动带来的破坏

3. **工程可扩展**
   - 支持未来增加字段
   - 不破坏现有消费方

---

## 顶层 JSON 结构

```json
{
  "task_summary": "...",
  "steps": [],
  "assumptions": [],
  "risks": []
}
```

### 字段说明

| 字段 | 类型 | 是否必填 | 说明 |
|----|----|----|----|
| task_summary | string | 是 | 任务摘要 |
| steps | array | 是 | 执行步骤数组 |
| assumptions | array[string] | 是 | 前提假设 |
| risks | array[string] | 是 | 风险点 |

---

## steps 数组结构

```json
{
  "step_id": "step_1",
  "title": "定义任务摘要",
  "description": "生成 task_summary 字段",
  "dependencies": [],
  "deliverable": "task_summary",
  "acceptance": "task_summary 非空"
}
```

### steps 字段说明

| 字段 | 类型 | 是否必填 | 说明 |
|----|----|----|----|
| step_id | string | 是 | 步骤唯一 ID |
| title | string | 是 | 步骤标题 |
| description | string | 是 | 步骤描述 |
| dependencies | array[string] | 是 | 依赖步骤 |
| deliverable | string | 是 | 产出说明 |
| acceptance | string | 是 | 验收标准 |

---

## 校验规则

- steps 必须非空
- step_id 必须唯一
- dependencies 中的值必须存在于已定义 step_id
- 所有 string 字段必须非空

校验逻辑集中于：

```text
app/agents/runner.py
```

---

## 错误处理策略

- JSON 无法解析 → 立即失败
- Schema 不符合 → 立即失败
- 原始模型输出会被落盘以便调试

调试文件路径：

```text
docs-private/_debug/last_agent_raw.txt
```

---

## 扩展建议

未来可扩展字段（向后兼容）：

- metadata
- estimated_time
- owner
- tool_calls

---

## 推荐提交信息

```text
docs(architecture): define agent output JSON contract
```
