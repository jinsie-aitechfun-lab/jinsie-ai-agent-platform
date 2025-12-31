# Git 提交信息规范（Git Commit Message Style）

本项目采用 **Conventional Commits** 规范，适用于 AI 应用工程、RAG 系统、多 Agent 平台等工程化项目。

---

## 1. 提交信息格式

每条提交必须采用以下格式：

```
type: short description
```

- `type`：提交类型（见下一节）
- `short description`：简短英文描述，不超过 72 字符

如需追加详细说明，可在标题下一行空行后继续写：

```
feat: add basic RAG pipeline with Qwen embedding

- add markdown document loader
- integrate Milvus as vector store
- add /rag-search endpoint
```

---

## 2. 提交类型说明（type）

| 类型 | 含义 |
|------|------|
| **feat** | 新功能、新接口、新模块、新 Agent、新 Graph |
| **fix** | Bug 修复 |
| **docs** | 文档类改动，如 README、docs/、注释等 |
| **refactor** | 重构（不改变外部行为，但调整内部结构） |
| **test** | 修改或新增 tests/ 下的测试 |
| **chore** | 杂项，如依赖升级、脚本、配置、空文件等 |
| **perf** | 性能优化 |
| **style** | 风格调整（格式化、空格、缩进，不影响逻辑） |
| **build** | 构建相关（Dockerfile、打包脚本） |
| **ci** | CI/CD 管线配置修改 |

---

## 3. 示例

### 功能开发
```
feat: add task scheduler agent for multi-step workflows
```

### 添加接口
```
feat: add /chat endpoint using Qwen completion
```

### 修复 Bug
```
fix: handle empty prompt in chat endpoint
```

### 文档更新
```
docs: update architecture overview for agent graphs
```

### 项目结构调整
```
refactor: split router definitions into dedicated modules
```

### 测试
```
test: add unit tests for env_check script
```

### 添加 Python 包初始化文件
```
chore: add __init__.py to make app a Python package
```

### 构建相关
```
build: tweak docker-compose for local development
```

---

## 4. 编写规范建议

1. 标题不超过 **72 字符**  
2. 使用 **动词原形**（add、update、fix、refactor）  
3. 一次 commit 只做一件事  
4. 关联 issue 时可写：  
   ```
   feat: add xxx (#12)
   ```

---

## 5. VSCode 书写建议

安装 VSCode 扩展：

- **Conventional Commits**
- **Git Commit Message Editor**

自动辅助选择 type，避免写错格式。

开启提交标题长度限制提醒：

```json
{
  "git.inputValidationSubjectLength": 72
}
```

---

## 6. 适用于本项目的约定

三大主项目（多 Agent 平台、RAG 客服、分析平台）  
在后续提交中，**建议持续遵守本规范**，确保：

- 工程结构可读性高  
- 提交历史清晰、可审计  
- 方便未来团队协作或阿里云人才引进材料准备

---


