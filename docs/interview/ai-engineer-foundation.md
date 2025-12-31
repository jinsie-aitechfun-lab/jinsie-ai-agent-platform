# 📘 大模型应用工程基础 · 学习与工程实践记录（第1篇）


目标方向：**AI 应用工程师（RAG / Agent / LLMOps）**
框架体系：Python + FastAPI + LangChain/LangGraph + Milvus + 阿里云生态

---

# ⭐ 1. 大模型基础能力（LLM Fundamentals）

已系统掌握以下内容：

### ✔ 大语言模型基础认知

* 大语言模型的核心原理
* 语言理解 / 生成的能力边界
* Embedding 的作用、向量空间意义与检索机制
* Token、上下文窗口、模型能力差异

### ✔ Prompt Engineering 基础

* Prompt 模板化
* System / User / Assistant 角色分工
* Few-shot、结构化提示方式
* 面向 RAG/Agent 的 Prompt 组织方式

---

# 🧪 2. 模型调用与 API 工程化实践

围绕国内外通用的大模型接口（阿里云百炼 / SiliconFlow / OpenAI SDK），完成以下工程内容：

### ✔ 基础调用能力

* 请求体结构（messages / input / model / parameters）
* temperature、top_p、max_tokens 参数控制
* 统一 headers 与 API Key 安全管理
* JSON 响应解析、错误处理

### ✔ 多轮对话工程实现

* 会话上下文管理
* Chat loop（类似 ChatGPT 连续对话）
* 消息体规范化
* 可扩展的 session 存储方案（本地版）

### ✔ 流式输出（SSE Streaming）

* 实现 chunk-by-chunk 解析
* Token 级输出（打字机流式效果）
* SSE 数据流解析与事件监听
* 流式与非流式调用差异理解

---

# 🧱 3. 工程环境与开发体系建设

已完成针对 AI 应用工程的底层环境建设，并确保未来三大项目可稳定运行。

### ✔ Python & VSCode 工程环境

* Python 3.x 环境管理
* .venv 虚拟环境隔离
* VSCode 解释器绑定
* pip 国内源设置与依赖管理优化

### ✔ 工程化工具链

* Makefile 初始化（run、install、check 等任务）
* `env_check.py` （环境自动验证脚本）
* `.env.example` 环境变量模板
* API Key 管控机制（安全层 + 可扩展层）

---

# 🧩 4. 核心最小可运行脚本（MVP）

以下模块已全部实现并运行成功：

### ✔ Chat 最小可运行脚本（10 行版）

* 完成一次请求 → 返回文本
* 结构清晰、可直接扩展到多轮对话

### ✔ Embedding 最小可运行脚本（10 行版）

* 向量生成成功
* 维度正确（1024）
* 可扩展为后续 RAG 向量检索部分

### ✔ Prompt 三模板（可复用）

* 基础对话模板
* 信息总结模板
* RAG 检索增强模板

这些在未来三个主项目中都会直接复用。

---

# 📚 5. 项目文档体系

已完成以下工程文档：

* `git-workflow.md`（分支策略、PR 流程）
* `git-commit-style.md`（提交规范）
* 项目 README 初版
* environment / usage / setup 文档
* 可学习记录与工程说明


---

# 🔧 6. 工程规范（追求可维护、可协作）

* 标准化目录结构
* 标准化提交规范（Conventional Commits）
* feature/fix/docs 分支策略
* 明确的文档分类层级（公开层 / 私密层）
* 环境与参数的可复现性（Makefile + .env）

---

# 🚀 7. 核心能力总结（可直接对标岗位）

已具备 AI 应用工程岗位要求中的：

### ✔ 模型 API 调用能力

### ✔ SSE 流式输出理解

### ✔ Prompt 工程能力

### ✔ 基本 RAG 关键模块（Embedding）

### ✔ 工程化项目搭建能力

### ✔ 文档体系与 Git 工作流规范

### ✔ 能快速定位和解决工程问题

具备继续构建以下三大项目的基础：

1. **多智能体平台（旗舰项目）**
2. **企业级 RAG 知识库客服系统**
3. **AI 驱动用户行为 & 性能分析平台**

---

# 🏁 8. 小结

本工程记录仅展示：

* 已掌握的技术能力
* 已完成的工程成果
* 可量化实践内容

