# 🗺️ Project Roadmap (Public, Professional Edition)

本 Roadmap 旨在呈现项目的工程化规划、能力演进路径与长期扩展方向，
用于指导系统迭代与模块化建设。

---

# 🎯 Vision
构建一套 **端到端的 AI 应用工程体系**，支持：

- 基础 LLM 应用开发（多轮对话 / Streaming）
- 企业级 RAG 智能问答
- 多 Agent 协作能力
- 模块化、可扩展的 LLMOps 工程化流程
- 兼容通义千问生态（Qwen API / Qwen Embedding / OpenSearch）

目标：提供一套 **可复用的 AI 应用工程骨架（Boilerplate + Best Practices）**，用于快速构建企业级智能应用。

---

# 🧱 Milestone 1 — 基础工程环境（已完成）
- Python 虚拟环境与依赖隔离  
- VSCode 调试环境配置  
- Makefile（安装 / 运行 / 环境检查）  
- 项目目录结构初始化  
- 初版文档体系（docs）  

---

# 🤖 Milestone 2 — LLM 基础能力链路（已完成）
- 模型 API 调用（ChatCompletion）  
- 多轮对话最小链路（session memory）  
- 流式输出（SSE / Streaming）  
- Prompt 模块化  

输出：`src/core/llm/`

---

# 📚 Milestone 3 — 文档体系与架构沉淀（已完成）
- architecture.md（通义增强版）  
- Milestone Timeline（公开版）  
- 私密文档体系 interview/（不提交到 GitHub）  
- 项目能力说明文档（notes）  

---

# 🔍 Milestone 4 — RAG 基础能力（进行中）
规划与开发：
- 文档解析与分块（chunking）  
- Embedding 接入（Qwen-Embedding / OpenAI 可选）  
- 向量存储（Milvus / OpenSearch）  
- 检索（Top-K）  
- RAG Pipeline（检索增强问答）  

输出：`src/core/rag/`、`src/core/vectorstore/`

---

# 🧠 Milestone 5 — Agent 能力建设（计划中）
- Planner Agent（任务拆解）  
- Worker Agents（工具执行）  
- Function Calling / ToolCall 封装  
- RAG-Agent 协作  
- 多模型路由（Qwen / DeepSeek / OpenAI / Doubao）  

输出：`src/agents/`

---

# 🚀 Milestone 6 — 部署与服务化（计划中）
- FastAPI 服务层  
- Docker 镜像构建  
- 阿里云 ECS / Serverless 部署  
- 日志采集与可观察性设计  

输出：`infra/`、Dockerfile、部署脚本

---

# 🌐 Milestone 7 — 增强层（未来扩展）
### 通义千问增强层（Qwen Enhanced Layer）
- Qwen-Max / Qwen-Long / Qwen-Agent 支持  
- Qwen-Embedding 优化  
- OpenSearch 生态集成  
- 阿里云特性能力适配  

### 其它潜在扩展
- 多模态能力（图像/音频）  
- Agent 工具市场  
- UI Dashboard（可选）  

---

# 🏁 Final Deliverables（最终交付）
1. 企业级 AI 应用工程骨架  
2. RAG + Agent 完整链路  
3. 可部署的在线 LLM 服务  
4. 规范化文档体系（公开 + 私密）  
5. 阿里云增强版（Qwen + OpenSearch 集成）  
