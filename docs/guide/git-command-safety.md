# Git 安全命令 vs 危险命令速查表（公开工程版）

适用场景：你在做开源/工程项目时，想**撤销、回退、改提交**，但又不想误删工作区文件。

---

## 1) 一句话口诀

- **不想丢文件：优先用 `--soft` 或默认（`--mixed`）**
- **只有在你确认“工作区也不要了”时，才用 `--hard`**
- **不知道该怎么选：先用 `git status` + `git diff`，再决定**

---

## 2) `reset` 三种模式对照表

| 目的 | 推荐命令 | 会发生什么 | 典型用途 |
|---|---|---|---|
| 撤销最近一次 commit，但保留改动在“暂存区” | `git reset --soft HEAD^` | HEAD 回退；**暂存区保留**；工作区保留 | “我提交早了，想补文件/改 message 后重新 commit” |
| 撤销最近一次 commit，但保留改动在“工作区”（默认） | `git reset HEAD^` 或 `git reset --mixed HEAD^` | HEAD 回退；暂存区清空；**工作区保留** | “我想重新分批 add/commit” |
| 撤销 commit 且清空工作区改动（危险） | `git reset --hard HEAD^` | HEAD 回退；暂存区清空；**工作区清空** | “我确认这些改动都不要了，回到上一版快照” |

> 重点：`--hard` 会**直接删除未提交的改动**（包括从未进入 Git 历史的新增文件）。

---

## 3) 最常见的 6 个场景（直接抄命令）

### 场景 A：commit 了但想改 message（未 push）
```bash
git commit --amend
```

### 场景 B：commit 了但漏了文件（未 push）
```bash
git add <漏掉的文件>
git commit --amend --no-edit
```

### 场景 C：想撤销最近一次 commit，但不丢文件，然后重新提交（未 push）
```bash
git reset --soft HEAD^
# 现在文件仍在暂存区，可直接补充/删改后再提交
git add -A
git commit -m "..."
```

### 场景 D：想把一个文件恢复到上一次提交的状态（不影响其他文件）
```bash
git restore <file>
# 或恢复到某个 commit 的版本
git restore --source <commit_hash> -- <file>
```

### 场景 E：误用了 reset/checkout，想“回到刚才”
```bash
git reflog --date=local -n 20
# 找到目标位置后：
git reset --hard <reflog里的hash>
```

### 场景 F：已经 push 到远程，但要撤销（推荐“安全撤销”）
```bash
git revert <commit_hash>
```

> 已 push 的历史：**优先 `revert`**，避免强推破坏协作。

---

## 4) 高频“危险命令”清单（慎用）

### 危险：会改历史 / 可能丢文件
- `git reset --hard ...`（会丢工作区新增/改动）
- `git push --force` / `git push --force-with-lease`（会改远端历史）
- `git clean -fd`（会删除未跟踪文件/目录）

### 相对安全：可逆 / 不丢文件（优先）
- `git restore ...`
- `git revert ...`
- `git reset --soft ...`
- `git reset ...`（默认 mixed）

---

## 5) 你需要记住的 3 条“自保规则”

1. **执行任何 reset 前**先看：
   ```bash
   git status
   git diff
   ```
2. 只要你有一点点不确定：**不要用 `--hard`**
3. 真出事了：**先 `reflog`，后操作**（不要连续乱试命令）

---

## 6) 最小应急流程（30 秒）

当你觉得“完了，我改乱了”：

```bash
git status
git reflog --date=local -n 20
# 找到你想回到的那条记录，复制 hash
git reset --hard <hash>
```

> 如果你担心丢文件：把 `--hard` 换成 `--mixed`，先保留工作区再说。
