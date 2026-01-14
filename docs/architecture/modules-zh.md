------

# modules-zh.md（中文版 · 自用理解版）

你可以直接新建：
 `docs/architecture/modules-zh.md`
 然后粘贴以下内容。

------

# 系统模块边界定义（中文理解版）

> 本文档是 `modules.md` 的中文对照理解版，用于作者本人理解与长期维护。
>  这是**系统级边界契约**，不是目录结构说明。

------

## 模块 1：entry_shell（入口壳层）

**职责（Purpose）**：
 负责 CLI / 启动脚本层。解析参数，调用编排中枢，输出或保存结果。

**归属（Owns）**：
 `scripts/*.py`（入口级脚本）

**禁止（Must NOT）**：

- ❌ 直接调用 tools
- ❌ 实现任何 contract 规则
- ❌ 实现执行逻辑

**一句话理解**：
 这是系统的“壳”，不是“大脑”，不允许有业务判断。

------

## 模块 2：agent_orchestration（Agent 编排中枢）

**职责（Purpose）**：
 负责一次 Agent 运行的完整编排流程：

> prompt → LLM → JSON 解析 → 合约校验 → 执行 → 输出收敛

**归属（Owns）**：
 `app/agents/runner.py`

**禁止（Must NOT）**：

- ❌ 定义 contract 规则（那是 contract_prompt 的事）
- ❌ 直接 dispatch 工具
- ❌ 实现 step 依赖逻辑（那是 execution_engine 的事）

**一句话理解**：
 这是系统的“调度大脑”，只负责编排，不做具体执行。

------

## 模块 3：contract_prompt（契约与提示系统）

**职责（Purpose）**：
 定义系统的**输出契约**与**运行时校验规则**，以及系统 prompt。

**归属（Owns）**：

- `app/agents/plan_validator.py`
- `app/prompts/system/agent_system.md`

**禁止（Must NOT）**：

- ❌ 执行 steps
- ❌ 调用 tools
- ❌ 调用 LLM

**一句话理解**：
 这是系统的“宪法 + 法院”，不干活，只裁决对错。

------

## 模块 4：execution_engine（执行引擎）

**职责（Purpose）**：
 根据依赖规则执行 steps，生成 `execution_results` 与 `__meta__`。

**归属（Owns）**：
 `app/agents/plan_executor.py`

**禁止（Must NOT）**：

- ❌ 生成 plans
- ❌ 校验 payload 结构合法性（那是 validator 的事）
- ❌ 实现 tool registry

**一句话理解**：
 这是系统的“执行内核”，只负责**如何跑**，不负责**该不该跑**。

------

## 模块 5：tool_runtime（工具运行时）

**职责（Purpose）**：
 负责 tool 的注册、列举、调度执行；提供默认工具；保持 tool 接口稳定。

**归属（Owns）**：
 `app/tools/*`

**禁止（Must NOT）**：

- ❌ 编排整个运行流程
- ❌ 强制执行 contract
- ❌ 决定 step 顺序

**一句话理解**：
 这是系统的“插件层 / 外设层”，只提供能力，不做决策。

------

## 模块依赖方向（非常重要）

允许的 import 方向：

```
entry_shell -> agent_orchestration -> execution_engine -> tool_runtime
agent_orchestration -> contract_prompt
execution_engine -> contract_prompt（仅用于后置校验时）
```

### 绝对规则：

- `contract_prompt` 不允许 import 其他模块（只能用 stdlib）

------

## 重要说明

> 本文档定义的是 **模块边界（Module Boundaries）**，不是目录结构。
>  你现在不需要重构目录，只需要遵守边界。