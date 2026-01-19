# 使用虚拟环境 .venv，并统一通过 .venv/bin/python 调用
VENV_DIR := .venv
VENV_PY  := $(VENV_DIR)/bin/python

# 默认命令
.PHONY: help venv install env-check run test clean runner-contract

help:
	@echo "可用命令："
	@echo "  make venv            创建虚拟环境 (.venv)"
	@echo "  make install         在虚拟环境中安装依赖 (requirements.txt / requirements-dev.txt)"
	@echo "  make env-check       运行环境自检脚本 scripts/env_check.py（使用 .venv）"
	@echo "  make run             运行主程序 main.py"
	@echo "  make test            运行测试（如 pytest）"
	@echo "  make runner-contract 运行 Runner Contract Gate（本地契约校验入口，对齐 CI）"
	@echo "  make clean           删除虚拟环境和临时文件"

# 创建虚拟环境
venv:
	@echo ">>> 创建虚拟环境：$(VENV_DIR)"
	python -m venv $(VENV_DIR)
	@echo ">>> 虚拟环境已创建。"

# 安装依赖
install: venv
	@echo ">>> 在虚拟环境中安装依赖..."
	$(VENV_PY) -m pip install --upgrade pip
	@if [ -f requirements.txt ]; then \
		$(VENV_PY) -m pip install -r requirements.txt; \
	else \
		echo "WARNING: 未找到 requirements.txt，跳过依赖安装"; \
	fi
	@if [ -f requirements-dev.txt ]; then \
		$(VENV_PY) -m pip install -r requirements-dev.txt; \
	else \
		echo "INFO: 未找到 requirements-dev.txt，跳过 dev 依赖安装"; \
	fi
	@echo ">>> 依赖安装完成。"

# 运行环境自检脚本（统一用 .venv，避免系统 python 混用）
env-check: install
	@echo ">>> 运行环境检查脚本 scripts/env_check.py..."
	$(VENV_PY) scripts/env_check.py

# Runner Contract Gate：本地统一入口（对齐 CI）
runner-contract: install
	@echo ">>> Runner Contract Gate: compile + semantics + samples + clean tree"
	$(VENV_PY) -m py_compile app/agents/plan_executor.py
	$(VENV_PY) -m py_compile app/agents/plan_validator.py
	$(VENV_PY) -m py_compile app/agents/runner.py
	$(VENV_PY) -m py_compile scripts/verify_execution_semantics.py
	$(VENV_PY) -m py_compile scripts/generate_samples.py
	PYTHONPATH=. $(VENV_PY) scripts/verify_execution_semantics.py | tail -n 3
	PYTHONPATH=. $(VENV_PY) scripts/verify_execution_semantics.py
	PYTHONPATH=. $(VENV_PY) scripts/generate_samples.py
	git diff --exit-code
	@test -z "$$(git status --porcelain)"

# 运行主程序
run: install
	@echo ">>> 运行主程序 main.py..."
	@if [ -f main.py ]; then \
		$(VENV_PY) main.py; \
	else \
		echo "ERROR: 未找到 main.py，请确认入口文件名称。"; \
		exit 1; \
	fi

# 测试（如果未来加上 pytest，这里可以直接用）
test: install
	@echo ">>> 运行测试..."
	@if command -v pytest >/dev/null 2>&1; then \
		$(VENV_PY) -m pytest; \
	else \
		echo "WARNING: 未安装 pytest 或未在 PATH 中，跳过测试"; \
	fi

# 清理
clean:
	@echo ">>> 清理虚拟环境和缓存文件..."
	rm -rf $(VENV_DIR) .pytest_cache __pycache__ */__pycache__
	@echo ">>> 清理完成。"
