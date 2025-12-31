# 系统架构说明（中文版）

本文件是 `architecture.md` 的中文专业版说明，帮助你在项目开发、面试展示和工程设计中更加清晰地理解本系统的架构逻辑。

---

# 📐 1. 系统整体架构概述

本项目是一个 **AI 多智能体（Multi-Agent）应用平台**，底层采用：

- **LLM（大语言模型）**
- **RAG（检索增强生成）**
- **Agent（多智能体协作框架）**
- **向量数据库（Milvus / OpenSearch）**
- **API 服务层（FastAPI）**
- **通义千问增强层（Qwen Enhanced Layer）**

整个系统通过模块化拆分、分层设计、可扩展架构来实现高度可维护、高扩展性的 AI 应用工程项目。

---

# 🧩 2. 架构分层说明

系统由六个核心层次组成：

## ✔ 2.1 LLM Layer（大模型层）

负责所有与大模型的交互，包括：

- DeepSeek / Qwen 模型调用
- 多模型路由（Model Router）
- 流式输出（Streaming）
- 结构化输出（JSON Mode）

封装逻辑位于：

```
app/core/llm/
```

---

## ✔ 2.2 RAG Layer（检索增强生成）

负责：

- 文档加载（Loader）
- 文本分块（Chunking）
- 向量化（Embedding）
- 存储与检索（VectorStore）
- 查询融合（RAG Query Pipeline）

模块位置：

```
app/graphs/rag/
```

支持的向量库：

- Milvus（默认）
- OpenSearch（通义增强可选）

---

## ✔ 2.3 Agent Layer（智能体层）

基于 **LangChain / LangGraph** 构建：

- Planner（规划器）
- Tool Router（工具路由）
- Executor（执行器）
- 多工具调用（Tool Calling）
- 状态管理（State Graph）

模块位置：

```
app/agents/
app/tools/
```

---

## ✔ 2.4 Service Layer（服务协调层）

所有业务逻辑、工作流 orchestration 放在这里：

- 请求解析  
- 工作流调度  
- 聚合 LLM / RAG / Agent 结果  
- 数据合法化  
- 日志落盘  

模块位置：

```
app/services/
```

---

## ✔ 2.5 API Layer（接口层）

基于 **FastAPI**，提供统一 API 接口：

- Chat API
- RAG Query API
- Agent 执行 API
- 健康检查接口

模块位置：

```
app/routers/
app/main.py
```

---

## ✔ 2.6 通义千问增强层（Qwen Enhanced Layer）

这是专为你的求职方向（阿里云·通义千问团队）强化设计的增强层。

包含：

- Qwen API 封装（LLM Router）
- Qwen Embedding 接入
- 阿里云语义检索 OpenSearch 支持
- 通义多 Agent 示例
- 通义 Function Calling support

模块位置：

```
app/core/qwen/
app/agents/qwen_examples/
```

---

# 🔄 3. 系统工作流流程（中文解释）

1. **用户发起请求** → API 层接收  
2. 根据请求类型进入对应服务  
3. 服务层判断需要：
   - 直接模型推理？  
   - 检索增强？  
   - 工具调用？  
4. Service 调用：
   - LLM 层  
   - RAG 管道  
   - Agent 工具链  
5. 汇总结果 → 返回 API → 用户得到结果（可流式）

整个流程高度模块化，便于扩展和维护。

---

# 📦 4. 项目结构（中文解释）

```
app/
  agents/         # 多智能体
  core/           # 核心逻辑（LLM / 配置 / 向量库）
  graphs/         # 工作流 & 状态图（RAG / Agent）
  models/         # 数据模型（schemas）
  routers/        # FastAPI 路由
  services/       # 服务协调层
  tools/          # Agent 工具
  utils/          # 通用工具
  __init__.py     # Python 包声明
  main.py         # 项目入口
```

---

# 🏢 5. 为什么这个架构适合阿里云 / 大厂面试？

- 多层架构 = 工程化能力  
- RAG + Agent = 当前最热门的企业需求  
- 模块化目录结构 = 大厂代码规范  
- 通义增强层 = 强命中阿里云  
- 架构清晰 = 面试讲解逻辑通顺  
- 可扩展性强 = 体现工程思维  

你的项目架构在大厂视角是“工程师级别”的，不是学生练习。

---

# 🧭 6. 文件存放建议

请将本文件放入：

```
docs/architecture/architecture-zh.md
```

与主架构文档配套使用。

---

# ✔ 总结

本中文架构说明可以作为：

- 面试时讲解架构的材料  
- 内部文档  
- 工程化说明  
- 项目结构理解指南  

如你需要，我可以进一步帮你：

- 生成「架构讲解口述稿」  
- 生成架构图 PNG  
- 生成 architecture-private（含更深层技术细节）  
