import sys

REQUIRED_PACKAGES = [
    "fastapi",
    "uvicorn",
    "langchain",
    "langgraph",
]

def main():
    print("=== Python Environment Check ===")
    print("Python executable:", sys.executable)
    print("Python version:", sys.version.split()[0])
    print()

    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
            print(f"[OK] {pkg}")
        except Exception as e:
            print(f"[MISSING] {pkg} ({e.__class__.__name__}: {e})")
            missing.append(pkg)

    print()
    if missing:
        print("❌ 缺少的依赖包：", ", ".join(missing))
        print("建议安装：")
        print("  python -m pip install " + " ".join(missing))
    else:
        print("✅ 所有关键依赖已安装，环境正常。")

if __name__ == "__main__":
    main()
