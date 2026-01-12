# GitHub SSH 鉴权标准配置指南（macOS）

> 目的：在 macOS 上使用 **SSH** 作为 GitHub 的唯一鉴权方式，避免 HTTPS Token 过期问题，减少重复登录与交互弹窗，提升工程稳定性与专业性。  
> 适用范围：所有 GitHub 仓库的 clone / fetch / pull / push 操作。

---

## 一、前置条件

- 操作系统：macOS
- 已安装 OpenSSH（`ssh -V` 可检查）
- 已拥有 GitHub 账号

---

## 二、检查是否已有 SSH Key

在终端中执行：

```bash
ls ~/.ssh
```

常见的 key 文件对：

- `id_rsa` / `id_rsa.pub`
- `id_ed25519` / `id_ed25519.pub`

如果你已经有其中一对，就不需要重新生成。

查看 key 的指纹信息：

```bash
ssh-keygen -lf ~/.ssh/id_rsa.pub
# 或
ssh-keygen -lf ~/.ssh/id_ed25519.pub
```

---

## 三、将 Key 加入 ssh-agent 与 macOS Keychain

如果 agent 未启动：

```bash
eval "$(ssh-agent -s)"
```

将 key 加入系统钥匙串（macOS 推荐）：

```bash
ssh-add --apple-use-keychain ~/.ssh/id_rsa
# 或
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

成功标志：

```text
Identity added: ...
```

---

## 四、配置 ~/.ssh/config（强烈推荐）

创建或编辑配置文件：

```bash
nano ~/.ssh/config
```

推荐配置：

```sshconfig
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes
  AddKeysToAgent yes
  UseKeychain yes
```

### 各字段含义

| 字段 | 含义 |
|------|------|
| Host github.com | 对 github.com 生效 |
| HostName github.com | 实际连接地址 |
| User git | GitHub 固定 |
| IdentityFile | 指定使用的 key |
| IdentitiesOnly yes | 只使用指定 key（防止多 key 混乱） |
| AddKeysToAgent yes | 自动加入 agent |
| UseKeychain yes | macOS 记住密码 |

设置权限：

```bash
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

---

## 五、将公钥添加到 GitHub

复制公钥：

```bash
pbcopy < ~/.ssh/id_rsa.pub
```

在 GitHub 页面：

- Settings → SSH and GPG keys → New SSH key
- Title：任意（如：MacBook-Pro-2026）
- Key：粘贴刚复制的内容
- 保存

---

## 六、验证 SSH 是否打通

```bash
ssh -T git@github.com
```

成功标志：

```text
Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## 七、将 Git 仓库从 HTTPS 切换为 SSH

查看当前 remote：

```bash
git remote -v
```

设置 origin 为 SSH：

```bash
git remote set-url origin git@github.com:<ORG>/<REPO>.git
```

再次确认：

```bash
git remote -v
```

---

## 八、（可选）保留 fork push 禁用策略

如果你有 fork remote，并希望防止误 push：

```bash
git remote set-url --push fork DISABLED
```

---

## 九、常见问题排查

### 1. Permission denied (publickey)

可能原因：

- 公钥未添加到 GitHub
- 加错了 GitHub 账号
- SSH 使用了错误的 key
- 未配置 `IdentitiesOnly yes`

调试命令：

```bash
ssh -vT git@github.com
```

---

### 2. 出现 127.0.0.1:7890 / 代理拦截问题

通常是代理工具（如 Clash）劫持了 SSH 22 端口。

解决方式：

#### 方案 A：禁用 github.com 代理

在 `~/.ssh/config` 的 github.com 下面加入：

```sshconfig
ProxyCommand none
```

#### 方案 B：使用 443 端口备用通道

```sshconfig
Host github-ssh443
  HostName ssh.github.com
  User git
  Port 443
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes
  AddKeysToAgent yes
  UseKeychain yes
```

测试：

```bash
ssh -T github-ssh443
```

---

## 十、最终检查清单

- [ ] ssh-add 成功
- [ ] ~/.ssh/config 包含 `IdentitiesOnly yes`
- [ ] ssh -T git@github.com 成功
- [ ] origin remote 使用 SSH
- [ ] fork push 为 DISABLED（如需要）

---

## 推荐实践

- 始终使用 SSH 作为 GitHub 唯一鉴权方式
- main 分支禁止直推
- dev 分支作为日常开发主线
- 所有核心功能使用 PR 合入

---

这套配置适用于：开源项目 / 公司项目 / 多账号 / 多设备长期使用场景。
