# Git 分支保护与回滚实践（工程版）

> 本文记录一次 **main 分支误提交后的标准修复流程**，以及适用于个人/小团队项目的 **Git 分支保护最小可行配置**。
> 目标：保证主分支安全，同时不牺牲开发效率。

---

## 一、问题背景

在开发过程中，曾发生以下情况：
- 在 `main` 分支发生直接提交（非 PR）
- 主分支历史被污染
- GitHub UI 出现 `main ahead of dev` 的差异提示

该问题需要 **在不使用 force push 的前提下** 修复。

---

## 二、标准修复方案（推荐做法）

### 1. 使用 revert 而非 reset
- 不重写历史
- 保留完整审计记录

### 2. 通过修复分支提交 PR
```text
fix/rollback-main → main
```

### 3. 使用 Squash merge
- 将多次回滚过程合并为一个语义清晰的提交

示例提交信息：
```
Rollback unintended direct commits to main
```

---

## 三、关于 GitHub 中的 ahead / behind 提示

- GitHub 的 ahead/behind 基于 **commit 数量差异**
- 不代表最终代码内容不同

当 dev 与 main 指向同一 commit 后，该提示会自动消失。

---

## 四、main 分支推荐保护规则（单人/小团队）

### 必选
- Require a pull request before merging
- Block force pushes
- Restrict deletions
- Require linear history

### 不建议开启（早期）
- Restrict updates（易锁死 PR merge）
- Require status checks（无 CI 阶段）
- Require approvals（单人仓库）

---

## 五、本地防呆补充（可选但推荐）

通过本地 `pre-push` hook 阻止直接 push main：

```bash
# .git/hooks/pre-push
#!/bin/sh
branch="$(git symbolic-ref --short HEAD 2>/dev/null)"
if [ "$branch" = "main" ]; then
  echo "Blocked: do not push directly to main."
  exit 1
fi
exit 0
```

说明：
- 仅影响本地
- 不进入仓库
- 不影响 PR merge

---

## 六、最终工程状态

- main 仅接受 PR 合入
- dev 用于日常开发
- feature 分支 → dev → main
- 主分支安全与开发效率达成平衡

---

## 七、适用场景

- 个人工程
- 试验型项目
- 小团队无 CI 阶段

---

（本文为工程实践总结，可公开）

