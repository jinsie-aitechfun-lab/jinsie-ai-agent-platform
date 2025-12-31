# 项目结构说明（Project Structure Overview）

本文件用于说明当前 AI Agent 平台项目的工程结构，帮助你自己和未来的维护者快速理解各目录的职责。

---

# 1. 顶层结构（Repository Root）

大致结构如下：

- app/                 核心应用代码（FastAPI + LLM + RAG + Agent）
- docs/                文档体系（架构、Roadmap、内部说明等）
- scripts/             开发辅助脚本（env_check 等）
- tests/               单元测试与集成测试
- requirements.txt     Python 依赖列表
- Makefile             常用开发命令（run、test、env-check 等）
- docker-compose.yml   容器化与本地编排（可选）
- LICENSE              开源协议
- README.md            项目总览（公开版）

---

# 2. app/ 目录结构

app/ 是整个项目的核心应用包，通过 __init__.py 声明为 Python 包。

示例结构：

- app/
  - agents/        多智能体（Agent）相关逻辑
  - core/          核心基础能力（LLM 封装、配置、向量库等）
  - graphs/        工作流与状态图（RAG Flow、Agent Flow 等）
  - models/        数据模型与 Pydantic Schema
  - routers/       FastAPI 路由（HTTP API）
  - services/      业务服务层（协调 LLM / RAG / Agent）
  - tools/         提供给 Agent 使用的工具（Tool Functions）
  - utils/         通用工具函数
  - main.py        应用入口（FastAPI app 对象）
  - __init__.py    标记 app 为 Python 包

各目录职能说明：

## 2.1 agents/

- 定义不同类型的智能体（Planner、Worker、Critic 等）
- 封装多智能体协作逻辑（如对话引导、任务拆分、结果汇总）
- 未来可扩展 Qwen 专用 Agent、Tool Router 等

## 2.2 core/

- LLM 客户端封装（如 DeepSeek、Qwen）
- 配置管理（settings / env）
- Embedding 和向量库接口
- 日志、监控等底层能力（可逐步增加）

## 2.3 graphs/

- 使用 LangGraph 或其他框架构建的「有状态工作流」
- 如：RAG 检索流程、Agent 状态机、对话流程图

## 2.4 models/

- Pydantic 数据模型
- 请求/响应结构定义
- 内部领域对象（Domain Models）

## 2.5 routers/

- 各种 HTTP API 路由
- 例如：/chat、/rag-query、/agent-run、/healthz 等
- 只负责协议层（请求解析与调用 services）

## 2.6 services/

- 核心业务服务层
- 负责协调 LLM、RAG、Agent、工具调用
- 对外隐藏复杂细节，对上层暴露简单接口

## 2.7 tools/

- 提供给 Agent / Workflow 调用的工具函数
- 如：搜索、数据库查询、RAG 查询、HTTP 调用等

## 2.8 utils/

- 与业务无关的通用小工具
- 如：时间格式化、日志封装、小型帮助函数等

## 2.9 main.py

- FastAPI 应用入口
- 挂载路由
- 配置中间件
- 提供给 Uvicorn 启动的 app 对象

---

# 3. docs/ 文档结构（简要）

建议结构示例：

- docs/
  - architecture/
    - architecture.md           系统架构（英文公开版）
    - architecture-zh.md        系统架构（中文版）
    - why-app-needs-init.md     为什么 app 需要 __init__.py（英文）
    - why-app-needs-init-zh.md  上述文档的中文说明
  - tools/
    - env-check.md              环境检查脚本说明
  - interview/                  面试相关私密文档（不公开）
  - roadmap.md                  项目 Roadmap（公开版）
  - README-Timeline-Milestone.md  里程碑时间线（公开版）

---

# 4. scripts/ 与 tests/

## 4.1 scripts/

- 存放开发辅助脚本：
  - env_check.py：环境依赖检查脚本
  - 未来可加入：数据初始化脚本、批量任务脚本等
- 所有脚本统一从项目根目录运行：
  - python scripts/env_check.py

## 4.2 tests/

- 存放单元测试与集成测试
- 建议与 app/ 下模块对应：
  - tests/test_services_xxx.py
  - tests/test_agents_xxx.py

---

# 5. 设计原则小结

- 「先跑通 → 再打磨」：结构可以逐步演化，但主骨架已满足企业级标准。
- 「功能模块化，目录有边界」：每个文件夹只负责一类职责。
- 「公开与私密分层」：docs 中明确哪些可公开，哪些只在面试或内部使用。
- 「兼顾阿里云通义方向」：保留 Qwen / OpenSearch 等增强位。

本文件可放置在：

- docs/architecture/project-structure.md

用于向面试官、未来合作者或“未来的你”快速说明整个项目工程结构。
