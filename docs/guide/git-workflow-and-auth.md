
# Git 标准工作流 & 认证使用说明（终端 / VSCode 通用版）

本文件用于规范你在本项目中的 **日常 Git 操作方式**，避免分支混乱、误 push、鉴权混乱等问题。

---

## 0）每次开工前的 10 秒自检

```bash
git status -sb
git remote -v
git branch -vv
```

你需要看到：

- 当前分支是 `dev`（或你准备工作的分支）
- `origin` 是主仓库，并且 `(push)` 可用
- `fork` 的 `(push)` 是 `DISABLED`

---

## 1）标准工作流模板（强烈推荐：一个功能一条分支）

### 1.1 从 dev 拉最新

```bash
git checkout dev
git pull --ff-only
```

### 1.2 新建功能分支（命名规则）

推荐前缀：

| 类型 | 前缀 |
|------|------|
| 新功能 | feature/ |
| 修复 | fix/ |
| 文档 | docs/ |
| 工程杂务 | chore/ |

```bash
git checkout -b feature/<short-topic>
```

### 1.3 开发 + 小步提交

```bash
git status
git add -A
git commit -m "feat(scope): <message>"
```

你当前已经在使用 Conventional Commits，继续沿用即可。

---

### 1.4 推送到主仓库（关键动作）

```bash
git push -u origin HEAD
```

说明：

- `HEAD` 表示当前分支
- 不用手写分支名
- 最安全
- 不容易写错

---

### 1.5 开 PR（base = dev）

- GitHub 页面会提示 “Create pull request”
- base 选择：`dev`
- 写清楚：
  - 做了什么
  - 为什么要做
  - 如何验证

---

### 1.6 合并策略选择

推荐默认：

> **Squash and merge**

原因：

- 历史干净
- 面试展示友好
- 不污染主分支
- 适合个人主仓库

仅当你想保留完整提交历史时，才使用：

> Create a merge commit

---

## 2）PR 合并后的收尾动作（非常重要）

### 2.1 同步本地 dev

```bash
git checkout dev
git pull --ff-only
```

---

### 2.2 删除本地分支

```bash
git branch -d feature/<short-topic>
```

---

### 2.3 删除远端分支

```bash
git push origin --delete feature/<short-topic>
git fetch --prune
```

---

## 3）终端 vs VSCode：到底谁在处理鉴权？

你当前使用的是：

> **HTTPS + PAT（Personal Access Token）**

### 终端：

- 使用 macOS Keychain
- 由 `credential.helper=osxkeychain` 管理
- 存储你的 PAT

### VSCode：

- 使用它自己的 Askpass / Git 插件机制
- 有时会劫持终端变量（你已经修复了这个问题）

---

## 4）你加到 ~/.zshrc 的那段配置是干嘛的？

你加的内容：

```bash
unset GIT_ASKPASS SSH_ASKPASS \
      VSCODE_GIT_ASKPASS_NODE VSCODE_GIT_ASKPASS_MAIN \
      VSCODE_GIT_ASKPASS_EXTRA_ARGS VSCODE_GIT_IPC_HANDLE
```

它的作用是：

> 防止 VSCode 的 Git Askpass 机制污染外部终端

它 **不会**：

- 删除你的 PAT
- 取消你的 Git 登录
- 影响 Keychain

---

## 5）最稳的 push 姿势（我强烈建议你永远用这个）

在任何功能分支上：

```bash
git push -u origin HEAD
```

在 dev 上同步：

```bash
git pull --ff-only
git fetch --prune
```

---

## 6）每日开工固定模板（复制即用）

```bash
# 切回 dev 并同步
git checkout dev
git pull --ff-only

# 检查状态
git status -sb
git remote -v

# 开新分支
git checkout -b feature/<topic>

# 开发完成后
git add -A
git commit -m "feat(scope): <msg>"

# 推送
git push -u origin HEAD
```

---


