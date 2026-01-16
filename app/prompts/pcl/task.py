"""
PCL - Task 模式（任务拆解）

职责：
- 将用户输入抽象成“任务规格”（目标/约束/输入输出）
- 与 schema / validator 协作，保证任务可执行
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class TaskSpec:
    task_summary: str
    constraints: str = ""


def build_task_prompt(spec: TaskSpec) -> str:
    parts = [f"任务：{spec.task_summary}"]
    if spec.constraints:
        parts.append(f"约束：{spec.constraints}")
    return "\n".join(parts)
