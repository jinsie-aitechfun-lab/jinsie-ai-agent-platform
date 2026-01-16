"""
PCL - Schema 模式（结构化输出契约）

职责：
- 约束输出必须符合可解析的结构（通常是严格 JSON）
- 明确字段、必填项、禁止项等
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SchemaSpec:
    name: str
    required_fields: List[str]


def build_schema_prompt(spec: SchemaSpec) -> str:
    fields = "、".join(spec.required_fields) if spec.required_fields else "（无）"
    return (
        "请只返回【严格合法 JSON】（不得包含代码块标记/解释性文字）。\n"
        f"Schema 名称：{spec.name}\n"
        f"必填字段：{fields}\n"
        "除非明确要求，否则不要输出额外字段。"
    )
