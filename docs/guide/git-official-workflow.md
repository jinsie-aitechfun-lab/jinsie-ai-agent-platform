# Git 官方工作流与鉴权规范（中文版）

> 本文为项目官方 Git 工作流标准文档中文版。
> 适用于：日常开发、PR 流程、远程仓库管理、鉴权策略、VSCode 与终端协作。

---

## 一、核心原则

1. **Commit 属于仓库，不属于分支**
2. **分支只是指向 commit 的指针**
3. **Push 推送的是分支指针，不是“提交本体”**
4. **PR 是代码进入主干的唯一入口**
5. **任何人都不允许直推 main / dev**

---

## 二、标准开发流程

### 1. 永远从 dev 分支拉新分支

```bash
git checkout dev
git pull --ff-only
git checkout -b feature/xxx
```

### 2. 开发 + 提交

```bash
git add -A
git commit -m "feat: xxx"
```

### 3. 推送远端

```bash
git push -u origin feature/xxx
```

### 4. 提 PR（GitHub 页面）

- base: dev
- compare: feature/xxx

### 5. 合并策略

- Squash merge
- 删除分支

---

## 三、为什么可以在一个分支 commit，在另一个分支 push？

这是 Git 的**正常行为**。

因为：

> Commit 是独立对象，分支只是指向它的“标签”。

你可以：

1. 在 dev 上产生 commit
2. 新建分支指向这个 commit
3. 推送这个新分支

这不是“跨分支提交”，而是“指针移动”。

---

## 四、官方远程仓库结构

| 名称 | 作用 |
|------|------|
| origin | 主仓库（你有写权限） |
| fork | 仅用于观察/同步，不允许 push |

强制配置：

```bash
git remote set-url --push fork DISABLED
```

---

## 五、鉴权策略

### HTTPS + PAT（当前官方方案）

- 不再使用 GitHub 密码
- 使用 Personal Access Token 作为密码

### SSH（后续可选）

- 需要配置 SSH key
- 更稳定
- 不依赖 VSCode Askpass

---

## 六、VSCode Askpass 说明

VSCode 会：

- 注入 GIT_ASKPASS
- 接管终端认证
- 弹出 UI 输入框

我们已关闭 VSCode 注入：

```bash
unset GIT_ASKPASS SSH_ASKPASS VSCODE_GIT_*
```

以后所有认证：

- 终端 → 系统 keychain → PAT

---

## 七、事故处理标准流程

### 情况：误提交、误推、分支混乱

处理原则：

1. 永远不 force push main/dev
2. 使用 revert / PR 修复
3. 所有修复都有记录

---


