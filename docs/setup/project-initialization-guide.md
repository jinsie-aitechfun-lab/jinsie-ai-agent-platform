# 项目工程初始化指南（公开版）

> **适用范围**  
> 本文档用于说明一个 AI 应用工程项目的**可复现、可协作、可公开**的初始化流程，涵盖：
> - Python 环境管理（conda）
> - 安全的环境变量管理（direnv + `.envrc`）
> - OpenAI-compatible 接口的最小可运行链路（Chat / Embedding）
> - 仓库目录结构约定
> - 最小 Git 工程闭环（分支 → PR → merge → 清理）

> 本文件适合放在 `docs/` 目录，**不包含个人学习过程或踩坑记录**。

---

## 1. 前置条件

- macOS / Linux（推荐）
- 已安装 `conda`（Miniconda / Anaconda 均可）
- 已安装 `git`
- 已安装 `direnv`（强烈推荐）
- VSCode（可选，推荐）

---

## 2. 推荐的仓库结构

```
app/            # Python 应用包
scripts/        # 可执行脚本入口（本地 / CI / 容器）
prompts/        # Prompt 模板
samples/        # 示例输入 / 输出
docs/           # 公开工程文档
docs-private/   # 私密学习与复盘文档
```

> 说明：  
> - `app/` 必须包含 `__init__.py`（即使是空文件），以保证包导入稳定

---

## 3. Python 环境管理（conda）

### 3.1 创建并激活环境

```bash
conda create -n <ENV_NAME> python=3.11 -y
conda activate <ENV_NAME>
```

### 3.2 升级基础工具

```bash
python -m pip install -U pip setuptools wheel
```

### 3.3 安装依赖

```bash
python -m pip install -r requirements.txt
```

---

## 4. 安全配置管理（direnv + .envrc）

### 4.1 为什么使用 direnv
- 避免「终端能跑、VSCode 不能跑」
- 环境变量自动加载，减少人为遗漏
- 明确区分**示例配置**与**真实密钥**

### 4.2 文件规范

- `.envrc.example`（提交到仓库）
- `.envrc`（本地使用，不提交）

示例 `.envrc.example`：

```bash
export OPENAI_API_KEY="your_key_here"
export OPENAI_BASE_URL="https://api.siliconflow.cn/v1"
export OPENAI_MODEL="your_chat_model"
export OPENAI_EMBED_MODEL="your_embedding_model"
```

初始化流程：

```bash
cp .envrc.example .envrc
# 编辑 .envrc 填入真实值
direnv allow
```

---

## 5. OpenAI-compatible API 最小可运行链路

### 5.1 Chat 调用验证

```bash
python scripts/chat_demo.py
```

期望结果：
- 成功返回模型生成文本
- 未在代码中硬编码 key

### 5.2 Embedding 调用验证

```bash
python scripts/embedding_demo.py
```

期望结果：
- 成功返回 embedding
- 输出向量维度或摘要信息

---

## 6. 工程辅助工具（可选）

### 6.1 Makefile
建议封装常用命令：
- `make env-check`
- `make run-chat`
- `make run-embed`

### 6.2 环境检查脚本
`scripts/env_check.py` 可输出：
- Python 路径
- `sys.path`
- 关键环境变量是否存在（不打印值）

---

## 7. Git 工程规范

### 7.1 `.gitignore` 要点
- `.envrc`
- `.env`
- `__pycache__/`
- `.pytest_cache/`
- `.vscode/`（可选）

### 7.2 最小工程闭环

```bash
git checkout -b docs/update-initialization-guide
git add docs/项目工程初始化指南-公开版.md
git commit -m "docs: add project initialization guide"
git push -u origin docs/update-initialization-guide
```

GitHub 上：
- 创建 PR
- merge 到 `dev`
- 删除分支

---

## 8. 快速自检清单

- conda 环境可正常激活
- direnv 正常加载变量
- Chat / Embedding 脚本可运行
- 仓库中无密钥泄露
- 稳定分支干净

---

## 9. 深度问题说明

详细的**问题成因分析、踩坑记录与排查路径**，请参考：
`docs-private/工程初始化复盘笔记-学习版.md`
