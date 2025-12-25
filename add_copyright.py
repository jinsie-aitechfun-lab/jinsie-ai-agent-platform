#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量为项目中的 .py 文件添加统一版权头（短版）。
- 仅处理 TARGET_DIRS 中的目录（默认 app/ 和 tests/）
- 自动跳过 __pycache__ / .venv 等目录
- 已有版权头的文件不会重复添加
"""

import os
import sys
from pathlib import Path

# === 配置区 ===

# 想要处理的根目录（相对项目根目录）
TARGET_DIRS = ["app", "tests"]

# 需要排除的目录名字（不进入这些目录）
EXCLUDE_DIRS = {
    "__pycache__",
    ".venv",
    ".git",
    ".idea",
    ".vscode",
}

# 需要排除的文件（根据文件名）
EXCLUDE_FILES = {
    "__init__.py",  # 如果你不想给 __init__ 加头，就保留；想加的话，可以删掉这一行
}

# 短版版权头（注意最后两个换行，留出与代码之间的空行）
COPYRIGHT_HEADER = '''"""
Jinsie AI Agent Platform
Copyright (c) 2025 Jinsie | AITechFun Lab
SPDX-License-Identifier: MIT
"""

'''


# === 逻辑部分 ===

def has_copyright_header(content: str) -> bool:
    """简单判断：文件开头是否已经包含我们想要的版权信息"""
    # 只看前几行就够了
    head = "\n".join(content.splitlines()[:6])
    return (
        "Jinsie AI Agent Platform" in head
        or "SPDX-License-Identifier: MIT" in head
    )


def add_header_to_file(path: Path) -> None:
    """给单个 .py 文件添加版权头"""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"⚠️ 跳过非 UTF-8 文件: {path}")
        return

    if has_copyright_header(text):
        print(f"✅ 已存在版权头，跳过: {path}")
        return

    new_text = COPYRIGHT_HEADER + text
    path.write_text(new_text, encoding="utf-8")
    print(f"✨ 已添加版权头: {path}")


def traverse_and_add_header(project_root: Path) -> None:
    """遍历 TARGET_DIRS 下的 .py 文件并添加版权头"""
    for rel_dir in TARGET_DIRS:
        target_dir = project_root / rel_dir
        if not target_dir.exists():
            print(f"⚠️ 目标目录不存在，跳过: {target_dir}")
            continue

        print(f"\n📂 开始处理目录: {target_dir}")
        for root, dirs, files in os.walk(target_dir):
            # 过滤不需要进入的目录
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file_name in files:
                if not file_name.endswith(".py"):
                    continue
                if file_name in EXCLUDE_FILES:
                    continue

                file_path = Path(root) / file_name
                add_header_to_file(file_path)


def main():
    project_root = Path(__file__).resolve().parent
    print(f"🔧 项目根目录: {project_root}")

    traverse_and_add_header(project_root)

    print("\n🎉 所有处理完成，可以执行 `git status` 查看变更。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ 已中断")
        sys.exit(1)
