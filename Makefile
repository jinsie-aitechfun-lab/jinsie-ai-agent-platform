# ================================
# 通用配置（根据你本机情况可调整）
# ================================

# 使用当前终端里的 python（建议是 conda py310 环境）
PYTHON ?= python
PIP    ?= $(PYTHON) -m pip

# FastAPI / Uvicorn 启动入口
# 按你的项目实际改成对应的模块路径和 app 对象：
#   如果是 main_server.py 里有 app：
#     APP_MODULE = main_server:app
#   如果是 app/main.py 里有 app：
#     APP_MODULE = app.main:app
APP_MODULE ?= app.main:app

# Uvicorn 启动端口
PORT ?= 8000


# ================================
# 环境相关命令
# ================================

.PHONY: env-check env-setup env-freeze

# 运行环境自检脚本（scripts/env_check.py）
env-check:
	$(PYTHON) scripts/env_check.py

# 使用 requirements.txt 安装依赖（新环境初始化时用）
env-setup:
	$(PIP) install -r requirements.txt

# 导出当前环境依赖到 requirements-freeze.txt（快照）
env-freeze:
	$(PYTHON) -m pip freeze > requirements-freeze.txt
	@echo "✅ 已导出当前环境依赖到 requirements-freeze.txt"


# ================================
# 本地开发 / 运行服务
# ================================

.PHONY: dev run

# 开发模式启动（自动重载代码）
dev:
	$(PYTHON) -m uvicorn $(APP_MODULE) --reload --port $(PORT)

# 生产模式启动（不自动重载）
run:
	$(PYTHON) -m uvicorn $(APP_MODULE) --port $(PORT)


# ================================
# 代码质量 / 测试（可选，按需使用）
# ================================

.PHONY: lint format test

# 静态检查（需要先安装 ruff：python -m pip install ruff）
lint:
	-$(PYTHON) -m ruff app scripts tests

# 自动格式化（需要先安装 black：python -m pip install black）
format:
	-$(PYTHON) -m black app scripts tests

# 单元测试（需要 pytest：python -m pip install pytest）
test:
	$(PYTHON) -m pytest -q


# ================================
# Docker 构建与运行（后期部署时用）
# ================================

.PHONY: docker-build docker-run

# 构建 Docker 镜像（需要项目根目录有 Dockerfile）
docker-build:
	docker build -t jinsie-ai-agent-platform .

# 运行 Docker 镜像（映射 8000 端口）
docker-run:
	docker run -p 8000:8000 --name jinsie-ai-agent-platform jinsie-ai-agent-platform
