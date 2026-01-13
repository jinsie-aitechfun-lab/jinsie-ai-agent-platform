# Contributing Guide

感谢你对 **Jinsie AI Agent Platform** 的关注！  
本项目欢迎社区参与，但为保持架构一致性与代码质量，贡献范围有明确边界。

---

## 🟦 贡献范围说明（非常重要）

### ✔ 欢迎的贡献类型（非核心逻辑）
以下类型的轻量贡献非常欢迎：

- 文档优化（README、指南、示例）
- 拼写/格式修复
- 注释补充
- 提供示例代码
- 添加测试样例
- Issue 反馈与讨论

这些贡献不会影响主架构，是非常有价值的协作方式。

---

## ❗ 关于核心模块的贡献说明
为确保架构的一致性，项目的核心逻辑（如 `app/agents/`, `app/rag/`, `app/pipelines/` 等）  
目前主要由维护者进行设计与调整。

非常欢迎通过 Issue 讨论思路、提出改进建议或分享需求。  
核心模块的变更将在讨论后由维护者统一评估和合并。


---

## 🟩 如何提交贡献（适用于轻量贡献）
1. Fork 仓库  
2. 创建分支：  
   ```bash
   git checkout -b fix/your-update

##  🟦 开发约定
开发本仓库时，请遵守统一的 Git 提交信息规范，以便后续代码审阅与变更追踪。
提交信息格式遵循 Conventional Commits

标题格式：type: short description，例如：

```bash
feat: add task scheduler agent for multi-step workflows
docs: update architecture overview for agent graphs
chore: add __init__.py to make app a Python package
```
详细规范见：

docs/git-commit-style.md