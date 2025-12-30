import sys
import platform
import pathlib

print("===== Python 环境检查 =====")
print(f"Python 可执行文件: {sys.executable}")
print(f"Python 版本: {platform.python_version()}")
print(f"平台: {platform.platform()}")

project_root = pathlib.Path(__file__).resolve().parent
print(f"项目路径: {project_root}")

# 可选：检查常用库是否安装
packages = ["httpx", "requests", "fastapi", "uvicorn", "langchain"]
print("\n===== 依赖检查 =====")
for pkg in packages:
    try:
        __import__(pkg)
        print(f"[OK] {pkg} 已安装")
    except ImportError:
        print(f"[MISSING] {pkg} 未安装")

print("\n环境检查完成。")
