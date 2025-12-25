<p align="center">
  <img src="docs/assets/logo.png" alt="Jinsie | AITechFun Lab" width="120" />
</p>

<h1 align="center">Jinsie AI Agent Platform</h1>

<p align="center">
  Cloud-native AI Applications · RAG Systems · Multi-Agent Workflows
</p>

<p align="center">
  <a href="https://github.com/jinsie-aitechfun-lab/jinsie-ai-agent-platform/stargazers">
    <img src="https://img.shields.io/github/stars/jinsie-aitechfun-lab/jinsie-ai-agent-platform?style=social" alt="GitHub Stars">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" />
  <img src="https://img.shields.io/badge/FastAPI-Production--Ready-009688.svg" />
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg" />
  <img src="https://img.shields.io/badge/VectorDB-Milvus-5A2DFF.svg" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" />
  <img src="https://img.shields.io/badge/Status-Active-success.svg" />
</p>

---


# 🎉 **Jinsie AI Agent Platform**

### *Cloud-native AI Applications · RAG Systems · Multi-Agent Workflows*

<div align="left">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Production--Ready-009688.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)
![Milvus](https://img.shields.io/badge/VectorDB-Milvus-5A2DFF.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

</div>

**Jinsie AI Agent Platform** 是一个基于 **LangGraph + FastAPI** 构建的 **企业级 AI 应用工程化模板**，旨在帮助开发者快速搭建可部署、可扩展、可维护的 RAG 与 Multi-Agent 系统。

由 **Jinsie | AITechFun Lab** 维护，是你构建 Cloud-native AI Applications 的最佳起点。

---

# 🚀 Features（特性亮点）

### 🔹 1. LangGraph 多智能体工作流

* 可视化节点（Node）+ 执行图（Graph）
* 多 Agent 协作、多步骤推理
* 可调试，可扩展，可组合

### 🔹 2. 企业级 RAG 体系

* 文档解析 / 清洗 / 切片 / 嵌入 / 向量检索
* 支持 Milvus / FAISS
* 内置知识库服务接口
* 兼容任意 OpenAI API 格式模型

### 🔹 3. 生产级 FastAPI 服务

* 健康检查
* 全局异常处理
* 统一日志中间件
* 可直接部署到阿里云 / K8s / Docker Compose

### 🔹 4. 工程化最佳实践（符合阿里云要求）

```
app/
  ├── agents/     # LangGraph Agent Nodes
  ├── graphs/     # Multi-Agent Graphs
  ├── core/       # 配置、日志、中间件
  ├── services/   # RAG / 模型 / 知识库服务
  ├── routers/    # API 路由
  ├── tools/      # 工具方法
  └── utils/      # 公共工具
docs/             # 文档 & Roadmap
tests/            # 单元测试
```

---

# 📦 Installation（安装）

## 方式一：本地运行（推荐开发者方式）

### 1. Clone 仓库

```bash
git clone https://github.com/jinsie-aitechfun-lab/jinsie-ai-agent-platform.git
cd jinsie-ai-agent-platform
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动服务

```bash
python main_server.py
```

服务将运行在：
👉 [http://0.0.0.0:8000](http://0.0.0.0:8000)
👉 健康检查 API: `/health`

---

## 方式二：Docker 启动（生产环境一致）

### 1. 启动服务

```bash
docker compose up --build
```

访问：
👉 [http://localhost:8000](http://localhost:8000)

---

# 📁 Project Structure（项目结构说明）

```
app/
  ├── core/           # 配置、日志、异常处理
  ├── agents/         # LangGraph Agent 定义
  ├── graphs/         # Graph 工作流（多智能体）
  ├── services/       # RAG / VectorDB / 模型调用逻辑
  ├── routers/        # API 路由模块
  ├── tools/          # 工具模块
  ├── utils/          # 公共函数
  └── main.py         # FastAPI 主入口
docs/
  ├── architecture.md # 架构说明
  ├── roadmap.md      # 项目规划
tests/                # 单元测试
docker-compose.yml    # 一键部署
main_server.py        # 启动脚本
```

---

# 🧠 Architecture（架构说明）

**整体架构：**

```
                     ┌──────────────────────────┐
                     │     FastAPI Service      │
                     │  (Routers + Middlewares) │
                     └─────────────┬────────────┘
                                   │
                     ┌─────────────▼─────────────┐
                     │       Core Services        │
                     │  (RAG / Models / VectorDB) │
                     └─────────────┬─────────────┘
                                   │
                  ┌────────────────▼────────────────┐
                  │         LangGraph Engine         │
                  │  Multi-Agent Graph Coordinator   │
                  └────────────────┬─────────────────┘
                                   │
                   ┌──────────────▼──────────────┐
                   │      Tools & Utilities       │
                   └──────────────────────────────┘
```

---

# 🔌 API 使用示例

## 健康检查

```
GET /health

Response:
{
    "status": "ok",
    "version": "1.0.0",
    "service": "Jinsie AI Agent Platform"
}
```

更多 API 会在 Graph/RAG 功能上线后逐步添加。

---

# 🗺️ Roadmap（项目路线图）

## Q1（当前）

* [x] 基础工程骨架搭建
* [x] FastAPI + Health Check
* [x] 项目版权与 MIT License
* [ ] RAG 知识库模块接入
* [ ] LangGraph Demo Graph
* [ ] 基础 Agent Node 模板

## Q2

* [ ] 企业级 RAG Pipeline
* [ ] 向量数据库 Milvus 适配
* [ ] 文档解析与批量导入工具
* [ ] 多工具 Agent（Toolformer 模式）

## Q3

* [ ] 多智能体工作流（Workflow）
* [ ] 任务调度 / 工作流执行器
* [ ] 任务可观测性（Tracing + Logging）

## Q4

* [ ] 企业级部署模板（阿里云 ACK）
* [ ] 模型调度与 LLMOps（多模型路由）
* [ ] 插件生态（扩展 Graph / Tools）

---

# 🤝 Contributing（如何贡献）

欢迎提交 PR、Issue、Feature Request。

贡献步骤：

1. Fork 仓库
2. 创建功能分支：

   ```bash
   git checkout -b feature/xxx
   ```
3. 提交修改
4. 创建 Pull Request

我们遵循 **MIT License**，允许自由使用和二次开发。

---

# 📜 License

本项目采用 **MIT License**，可自由用于商业/非商业用途。

---

# 👩‍💻 Maintainer

**Jinsie | AITechFun Lab**
AI 应用工程 · RAG 系统 · Multi-Agent Workflows
GitHub: [https://github.com/jinsie-aitechfun-lab](https://github.com/jinsie-aitechfun-lab)

---

