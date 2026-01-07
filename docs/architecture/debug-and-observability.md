# 调试与可观测性设计（Debug & Observability）

本文档说明 **Jinsie AI Agent Platform** 中关于调试与可观测性的工程设计，
目标是保证 Agent 行为 **可解释、可复盘、可定位问题**。

---

## 设计原则

1. **失败可见**
2. **调试信息不污染主流程**
3. **不影响生产路径**
4. **开发态与运行态解耦**

---

## 调试层级

### 1️⃣ 输入级调试

- Prompt 输入来自文件或 CLI
- 可版本化、可复用

### 2️⃣ 模型输出调试

当模型输出不符合 JSON 契约时：

- Runner 立即终止执行
- 原始输出被保存

路径：

```text
docs-private/_debug/last_agent_raw.txt
```

---

## 为什么不用日志打满 stdout？

- CLI 需要保持输出干净（JSON only）
- API 返回需稳定可解析
- 调试信息应与结果解耦

---

## 可观测性扩展方向

- 执行时间统计
- Step-level trace
- Tool 调用记录
- RAG 检索命中率

这些能力可在不破坏现有接口的情况下逐步引入。

---

## 加分点

该设计体现：

- 对失败路径的重视
- 对调试成本的控制
- 对生产可观测性的前瞻性

---

## 推荐提交信息

```text
docs(architecture): document debug and observability strategy
```
