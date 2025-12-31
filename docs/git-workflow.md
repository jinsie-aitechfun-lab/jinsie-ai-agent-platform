# Git 分支与工作流规范（Git Workflow）

本仓库采用 **轻量级 Git Flow** 模型，适用于：

- 多 Agent 平台  
- 企业级 RAG 智能客服  
- 行为/性能分析平台  

目标：  
**提交历史清晰、功能可追踪、结构可审查、未来人才引进材料可审计。**

---

## 1. 分支类型说明

### 1.1 `main`（主分支）
- 永远保持可运行、可部署状态  
- 发布版本均来自此分支  
- 禁止直接在 main 上开发功能  

### 1.2 `dev`（开发主线）
- 日常开发聚合分支  
- 所有功能、修复代码都先合并到 `dev`  
- 经自测后合并回 `main`

### 1.3 `feature/*`（功能分支）
- 用于开发新功能、新 Agent、新 Graph、新 RAG 流程  
- 命名规则：

```
feature/<scope>-<short-desc>
```

示例：

```
feature/chat-endpoint
feature/agent-task-scheduler
feature/rag-customer-support
feature/analytics-pageview-stats
```

### 1.4 `fix/*`（修复分支）

```
fix/chat-empty-prompt
fix/rag-invalid-embedding-dim
```

### 1.5 可选分支
- `chore/*`：依赖升级、脚手架、非功能性修改  
- `experiment/*`：实验性代码，不建议合并主线  

---

## 2. 日常开发流程（推荐）

以新增 `/chat` 接口为示例：

### Step 1：从 dev 创建功能分支

```
git checkout dev
git pull origin dev
git checkout -b feature/chat-endpoint
```

### Step 2：在功能分支开发并提交  

提交信息遵循 Conventional Commits：

```
feat: add /chat endpoint using Qwen completion
test: add tests for /chat endpoint with empty prompt
```

### Step 3：本地测试通过后合并回 dev

```
git checkout dev
git merge --no-ff feature/chat-endpoint
git push origin dev
```

### Step 4：将 dev 合并回 main（阶段性成果）

```
git checkout main
git pull origin main
git merge --no-ff dev
git push origin main
```

### Step 5：可选的版本标签（用于发布）

```
git tag -a v0.1.0 -m "first demo version of agent platform"
git push origin v0.1.0
```

---

## 3. 提交流程要求（配合 commit style）

1. 每次提交只做一件事  
2. 提交信息遵循 `docs/git-commit-style.md`  
3. 使用原形动词（add / update / fix）  
4. 大功能合并前可选择 squash  
5. 提交前务必运行：

```
git status
git diff
```

确保改动无误。

---

## 4. 三大主项目的分支建议

你可以为每个主项目保留长期开发分支：

```
dev-agent-platform
dev-rag-support
dev-analytics
```

示例流程：

1. 从对应项目分支创建新功能：

```
git checkout dev-agent-platform
git checkout -b feature/agent-executor-graph
```

2. 功能完成后合并回对应项目分支  
3. 阶段性成果完成后再合并到总 `dev`，最后进入 `main`

当前你一个人开发，简单使用：

```
main
dev
feature/*
fix/*
```

即可。

---

## 5. 推荐首次设置流程（你现在就可以做）

### Step 1：同步 main

```
git checkout main
git pull origin main
```

### Step 2：创建 dev

```
git checkout -b dev
git push -u origin dev
```

### Step 3：所有新功能从 dev 开分支

```
git checkout dev
git checkout -b feature/<name>
```

---

## 6. 团队化／多人协作发展路径（未来使用）

- 功能分支通过 Pull Request  
- Reviewer 至少一人  
- main 合并必须通过 CI  
- tag 后自动发布版本  
- Issue / Milestone 进行任务管理  

---

## 7. 文件放置建议

请将本文件放置于：

```
docs/git-workflow.md
```

并在 `CONTRIBUTING.md` 中添加：

```
For workflow conventions, see:
./docs/git-workflow.md
```

---

本规范适用于你的三大主项目，确保工程结构清晰、可持续、可协作、可对外展示。
