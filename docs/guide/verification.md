# 验收与回归检查

本文件用于快速验证本仓库的「单次执行 Runner（模型 → 计划 → 工具 → 结果）」链路是否可复现、可回归。

> 目标：**不靠记忆命令**，照抄即可完成验收。

---

## 0. 前置条件

- 已进入项目根目录
- 已激活项目 Python 环境（例如 conda `py310`）
- 如使用 `direnv`：已执行过 `direnv allow`
- 已正确配置环境变量：
  - 本地 `.env` **不提交**
  - `.env.example` 可提交用于示例

---

## 1. 一键验收（3 条命令）

### 1.1 成功路径：echo_tool 正常执行

```bash
python scripts/run_agent_once.py --debug   "请调用 echo_tool，参数为 {"text":"hi"}，然后把工具结果原样输出为严格JSON"
```

期望：
- 终端输出为严格 JSON
- `execution_results[0].ok == true`
- `execution_results[0].output.echo == "hi"`

---

### 1.2 异常路径：工具不存在

```bash
python scripts/run_agent_once.py --debug   "请调用 not_exist_tool，参数为 {"x":1}，并输出严格JSON"
```

期望：
- 终端输出为严格 JSON
- `execution_results[0].ok == false`
- `execution_results[0].error` 包含 `Unknown tool`

---

### 1.3 异常路径：参数缺失

```bash
python scripts/run_agent_once.py --debug   "请调用 echo_tool，参数为 {}，并输出严格JSON"
```

期望：
- 终端输出为严格 JSON
- `execution_results[0].ok == false`
- `execution_results[0].error` 提示缺少必填参数（如 `missing ... 'text'`）

---

## 2. 生成样例文件（可选，但推荐）

> 目的：把一次运行的 JSON 输出固化为可审阅样例，放入 `docs/samples/`。

### 2.1 生成并写入文件

```bash
python scripts/run_agent_once.py --debug   "请调用 echo_tool，参数为 {"text":"hi"}，然后把工具结果原样输出为严格JSON"   --output-file docs/samples/echo_tool_payload.debug.json
```

### 2.2 确认文件存在

```bash
ls -la docs/samples | head
```

---

## 3. 常见问题排查

### 3.1 报错：ModuleNotFoundError: No module named 'app'

说明：当前 Python 进程找不到项目根目录下的 `app/` 包。

处理：
- 确认在项目根目录执行命令（`pwd` 应显示项目根路径）
- 若使用 `direnv`：确认 `.envrc` 里包含 `export PYTHONPATH=.` 并已 `direnv allow`
- 或临时执行：
  ```bash
  PYTHONPATH=. python scripts/run_agent_once.py "..."
  ```

### 3.2 只想要“最终工具输出”，不要整套 payload

说明：当前 Runner 支持在特定条件下“直接返回工具输出 dict”。

处理：
- 正常现象。用 `--debug` 可看到完整 payload 与 execution_results。
- 公开输出建议：默认返回完整 payload；对 demo/样例可返回工具 output（更简洁）。

---

## 4. 变更后回归建议

每次你新增一个工具或修改执行链路，至少跑：

- 1.1（成功）
- 1.2（工具不存在）
- 1.3（参数缺失）

保证错误路径也稳定。

---
