# Agent 单次执行骨架（公开工程版）

本文件用于说明本项目的最小 Agent 执行闭环结构，适用于工程说明。

---

## 一、整体链路

CLI 输入 → runner（调度） → executor（执行计划） → tool（真实函数） → 结果回填 → 输出策略

---

## 二、入口层（CLI → runner）

```python
def main():
    query = read_query_from_cli()
    payload_or_output = run_agent_once_json(query, debug=flag_debug)
    print_json(payload_or_output)
```

职责：
- 接收外部输入
- 调用 runner
- 打印 JSON
- 不写业务逻辑

---

## 三、runner（调度层）

```python
def run_agent_once_json(query: str, debug: bool = False) -> dict:
    payload = model_generate_plan(query)
    payload = execute_plan(payload)

    if debug:
        return payload

    return extract_final_output(payload)
```

职责：
- 调模型生成计划
- 调 executor 执行
- 决定输出策略

---

## 四、executor（执行层）

```python
def execute_plan(payload: dict) -> dict:
    steps = payload.get("steps") or []
    results = []

    for step in steps:
        tool = (step or {}).get("tool") or {}
        name = tool.get("name")
        args = tool.get("args") or {}

        try:
            out = dispatch_tool(name, args)
            results.append({"step_id": step.get("step_id"), "tool": name, "ok": True, "output": out})
        except Exception as e:
            results.append({"step_id": step.get("step_id"), "tool": name, "ok": False, "error": str(e)})

    payload["execution_results"] = results
    return payload
```

职责：
- 遍历 steps
- 调用 dispatch_tool
- 捕获异常
- 写 execution_results

---

## 五、工具注册表（registry）

```python
TOOLS = {
    "echo_tool": echo_tool,
}

def dispatch_tool(name: str, args: dict) -> dict:
    if name not in TOOLS:
        raise ValueError(f"Unknown tool: {name}")
    fn = TOOLS[name]
    return fn(**args)
```

职责：
- name → 函数映射
- 解耦 executor 与工具实现

---

## 六、非 debug 输出策略

```python
def extract_final_output(payload: dict) -> dict:
    results = payload.get("execution_results")
    if not results or not isinstance(results, list):
        return payload

    last = results[-1]
    if not isinstance(last, dict):
        return payload

    if last.get("ok") is True:
        out = last.get("output")
        if isinstance(out, dict):
            return out

    return payload
```

含义：
- 默认只返回最后一步成功结果
- 若异常则返回完整 payload

---

本结构适用于后续扩展 read_file_tool、write_file_tool、http_fetch_tool 等。
