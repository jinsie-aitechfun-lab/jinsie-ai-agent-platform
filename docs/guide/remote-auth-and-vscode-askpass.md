# Git 远端命名与鉴权故障排查（VSCode AskPass / fork-or-origin 误推送）

> 适用场景：同一个本地仓库同时存在 `origin`（主仓）与 `fork`（个人 fork），并遇到 VSCode/Git 鉴权弹窗、`ECONNREFUSED ... vscode-git-*.sock`、误把分支推到 fork 等问题。

## 目标状态（推荐规范）

- `origin`：主仓（组织仓）  
  `https://github.com/jinsie-aitechfun-lab/jinsie-ai-agent-platform.git`（或 SSH 形式）
- `fork`：个人 fork（可保留，方便外部协作 / 练习 PR）  
  `https://github.com/AnneLau/jinsie-ai-agent-platform.git`
- 本地分支：
  - `dev` 跟踪 `origin/dev`
  - `main` 跟踪 `origin/main`
  - 功能分支（如 `feature/*`）默认推到 `origin`，除非你明确要推到 `fork`

用命令验证：

```bash
git remote -v
git branch -vv
```

---

## 为什么会出现“推送到了 fork”？

看分支跟踪关系：

```bash
git branch -vv
```

如果看到：

- `feature/stable-agent-protocol ... [fork/feature/stable-agent-protocol]`

这表示该分支的 upstream（跟踪远端）是 **fork**，所以你在不带参数执行 `git push` 时，会默认推到 fork。

### 修复（把分支改为跟踪 origin）

```bash
git branch --unset-upstream || true
git push -u origin feature/stable-agent-protocol
```

---

## VSCode AskPass 是什么？为什么会导致 ECONNREFUSED？

你环境里出现了这些变量：

```bash
env | egrep "VSCODE_GIT|GIT_ASKPASS|SSH_ASKPASS" || true
```

典型会看到：

- `GIT_ASKPASS=.../vscode/.../askpass.sh`
- `VSCODE_GIT_IPC_HANDLE=/var/.../vscode-git-xxxx.sock`

这表示：当前 shell 被注入了 **VSCode 的 Git 认证代理（AskPass）**。
当 VSCode 的 Git 扩展进程不在、socket 失效、或你在“带着这些环境变量的外部终端”运行 Git 时，就可能触发：

- `Missing or invalid credentials`
- `Error: connect ECONNREFUSED ... vscode-git-xxxx.sock`

### 解决（让命令行 Git 不依赖 VSCode）

```bash
unset GIT_ASKPASS SSH_ASKPASS VSCODE_GIT_ASKPASS_NODE VSCODE_GIT_ASKPASS_MAIN VSCODE_GIT_ASKPASS_EXTRA_ARGS VSCODE_GIT_IPC_HANDLE
```

---

## HTTPS 推送：Password 不是账号密码，而是 PAT

GitHub 对 HTTPS Git 操作不再接受“账号密码”作为 password，需要：

- **用户名**：你的 GitHub 用户名（如 `AnneLau`）
- **密码**：填 **Personal Access Token (PAT)**（不是登录密码）

---

## 合并策略建议（Squash or Merge）

如果你是单人维护、想让 `dev` 分支历史更干净：  
✅ 推荐 **Squash and merge**（把多个提交压成 1 个）

合并时把标题改成一个总括性的 conventional commit，例如：

- `feat(agent): stabilize execution mode and tool registry`

---

## 合并后收尾（建议做）

```bash
git checkout dev
git pull --ff-only origin dev
git branch -D feature/stable-agent-protocol
```

---

## 是否还需要 SSH？

不“必须”。你已经用 HTTPS + PAT 打通了推送，这就够用了。

如果你想以后彻底避免 PAT 弹窗/Keychain 混乱，再做 SSH：
- 生成 key → 加到 GitHub → `origin` 改为 `git@github.com:...` → `ssh -T git@github.com` 测试
