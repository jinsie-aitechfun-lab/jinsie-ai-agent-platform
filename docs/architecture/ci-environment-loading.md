# CI 环境变量加载说明（CI Environment Loading）

本文档说明在 **CI / 自动化环境** 中如何安全、稳定地加载环境变量，
以保证 Agent / API / 测试在 CI 中行为一致。

---

## 设计目标

- 不依赖 direnv
- 不提交敏感信息
- 行为与本地一致
- 失败尽早暴露

---

## CI 中的环境变量来源

推荐方式：

- CI 系统的 Secret 管理
  - GitHub Actions Secrets
  - GitLab CI Variables
  - 企业 CI 平台密钥管理

---

## 示例（GitHub Actions）

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  OPENAI_MODEL: Qwen/Qwen2.5-7B-Instruct
  OPENAI_BASE_URL: https://api.siliconflow.cn/v1
```

---

## 为什么 CI 不使用 .env / direnv

- CI 无交互式 shell
- direnv 不适用于非本地环境
- .env 文件不应进入 CI

---

## 失败策略

- 缺失关键变量 → 流程失败
- 不进入 mock / fallback 状态
- 确保 CI 结果可信

---

## 与本地开发的一致性

- Runner 初始化阶段统一校验变量
- CI 与本地使用相同代码路径

---

## 推荐提交信息

```text
docs(architecture): document CI environment loading strategy
```
