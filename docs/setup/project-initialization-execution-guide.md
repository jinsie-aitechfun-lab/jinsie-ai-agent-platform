# Day1 Remaining Tasks Execution Guide（Engineering Version）

> 本文档用于 **一步步完成 Day1 剩余工程任务**，全部步骤均可直接复制执行。  
> 适用于已完成环境初始化、项目骨架、基础文档后的最后收尾阶段。  
> 本文档为 **工程执行指南**，不包含学习天数或个人信息，可公开。

---

## 前置条件

- 当前位于项目根目录
- 能看到以下目录结构：
  ```
  app/
  scripts/
  docs/
  ```

---

## Step 0：确认当前工作区干净

在开始创建新分支前，确认当前工作区没有未提交改动：

```bash
git status
```

- 如果工作区是 clean → 继续下一步  
- 如果有未提交文件 → **先不要处理**，将状态发给指导者再继续

---

## Step 1：创建并推送 dev 分支（仅需一次）

```bash
git checkout main
git pull
git checkout -b dev
git push -u origin dev
```

说明：

- `main`：稳定分支  
- `dev`：后续所有开发的集成分支  
- 所有 `feature/*`、`docs/*` 分支均从 `dev` 派生

---

## Step 2：新增 Prompt 模板（feature 分支）

### 2.1 创建 feature 分支

```bash
git checkout dev
git checkout -b feature/add-base-prompts
```

---

### 2.2 创建 prompts 目录与模板文件

```bash
mkdir -p app/prompts
```

#### system_prompt.md

```bash
cat > app/prompts/system_prompt.md <<'EOF'
You are a helpful, reliable AI assistant specializing in analytical reasoning,
task decomposition, and structured content generation.

Your output must follow these rules:
1. Be concise and accurate.
2. Provide structured output when suitable.
3. Avoid unnecessary wording.
4. Format results using Markdown when appropriate.
EOF
```

#### summary_prompt.md

```bash
cat > app/prompts/summary_prompt.md <<'EOF'
Please summarize the following content:

{{input_text}}

Your summary should:
- Capture key insights
- Remove redundancy
- Maintain logical order
- Output in concise Markdown bullet points
EOF
```

#### rag_prompt.md

```bash
cat > app/prompts/rag_prompt.md <<'EOF'
You are assisting with a Retrieval-Augmented Generation task.

Given:
- Query: {{query}}
- Retrieved context:
{{context}}

Generate the final answer with these rules:
1. Prioritize retrieved context over prior knowledge.
2. If context does not contain the answer, explicitly state "context not sufficient".
3. Provide a clear, structured Markdown response.
EOF
```

---

### 2.3 提交并推送 feature 分支

```bash
git add app/prompts
git commit -m "feat(prompts): add reusable system, summary and RAG prompt templates"
git push -u origin feature/add-base-prompts
```

---

## Step 3：新增 API Sample Output 文档（docs 分支）

### 3.1 创建 docs 分支

```bash
git checkout dev
git checkout -b docs/add-sample-outputs
```

---

### 3.2 创建 samples 目录与文件

```bash
mkdir -p docs/learning/samples
```

#### chat_sample_output.md

```bash
cat > docs/learning/samples/chat_sample_output.md <<'EOF'
# Chat API Sample Output

Input:
"Hello, can you introduce what LLMs are?"

Model Output:
"Large Language Models (LLMs) are AI systems trained on large corpora of text to understand and generate human-like language. They can answer questions, summarize content, write code, and assist with reasoning tasks."

Key properties:
- role: "assistant"
- finish_reason: "stop"
EOF
```

#### embedding_sample_output.md

```bash
cat > docs/learning/samples/embedding_sample_output.md <<'EOF'
# Embedding API Sample Output

Input text:
"AI developers build applications using large language models."

Sample embedding metadata:
- Vector dimension: 1024
- Data type: float32
- Typical use cases: similarity search, clustering, semantic retrieval

Example vector (trimmed):
[0.0123, -0.0844, 0.0631, 0.9912, ...]
EOF
```

---

### 3.3 提交并推送 docs 分支

```bash
git add docs/learning/samples
git commit -m "docs(samples): add chat and embedding API output examples"
git push -u origin docs/add-sample-outputs
```

---

## Step 4：完成确认（仅需检查一次）

```bash
git branch --show-current
git log --oneline --decorate -5
```

预期结果：

- `feature/add-base-prompts` 分支存在并已推送  
- `docs/add-sample-outputs` 分支存在并已推送  

---

## 完成状态

至此，Day1 剩余工程任务已全部完成：

- Prompt 模板文件 ✅  
- API 示例输出文档 ✅  
- dev / feature / docs 分支结构 ✅  

项目可正式进入下一阶段开发。

