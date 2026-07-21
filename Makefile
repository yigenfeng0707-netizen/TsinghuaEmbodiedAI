# Makefile for TsinghuaEmbodiedAI
# 简化常用命令，提供一键操作

# Python 解释器
PYTHON := python

# Docker
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# 颜色定义
COLOR_RESET := \033[0m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_BLUE := \033[34m

.DEFAULT_GOAL := help

##@ 通用

help: ## 显示所有可用命令
	@printf "$(COLOR_BLUE)TsinghuaEmbodiedAI Makefile$(COLOR_RESET)\n"
	@printf "$(COLOR_YELLOW)可用命令:$(COLOR_RESET)\n\n"
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make <target>\n\nTargets:\n"} \
	  /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(COLOR_GREEN)%-20s$(COLOR_RESET) %s\n", $$1, $$2 } \
	  /^##@/ { printf "\n$(COLOR_YELLOW)%s$(COLOR_RESET)\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ 环境设置

setup: ## 创建虚拟环境并安装依赖
	$(PYTHON) -m venv venv
	@echo "请激活虚拟环境:"
	@echo "  Linux/Mac: source venv/bin/activate"
	@echo "  Windows:   venv\\Scripts\\activate"
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt

setup-dev: setup ## 安装开发依赖（含测试工具）
	pip install pytest pytest-cov flake8 black isort

check-deps: ## 检查依赖是否完整
	@$(PYTHON) -c "import mujoco; print(f'MuJoCo: {mujoco.__version__}')"
	@$(PYTHON) -c "import numpy; print(f'NumPy: {numpy.__version__}')"
	@$(PYTHON) -c "import numba; print(f'Numba: {numba.__version__}')"
	@$(PYTHON) -c "import torch; print(f'PyTorch: {torch.__version__}')"
	@echo "$(COLOR_GREEN)[OK] 依赖检查通过$(COLOR_RESET)"

##@ 模型与数据

download-models: ## 下载模型 checkpoint 和 demo 数据
	$(PYTHON) scripts/download_models.py

check-models: ## 检查模型文件是否就位
	$(PYTHON) scripts/download_models.py --check-only

##@ 测试

test: ## 运行所有测试
	pytest tests/ -v

test-cov: ## 运行测试并生成覆盖率报告
	pytest tests/ --cov=JCIIOT --cov-report=html
	@echo "$(COLOR_GREEN)覆盖率报告已生成: htmlcov/index.html$(COLOR_RESET)"

syntax-check: ## Python 语法检查
	@find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | while read f; do \
		$(PYTHON) -m py_compile "$$f" || exit 1; \
	done
	@echo "$(COLOR_GREEN)[OK] 所有 Python 文件语法正确$(COLOR_RESET)"

##@ 论文

paper-build: ## 编译 LaTeX 论文
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
	@echo "$(COLOR_GREEN)PDF 已生成: paper/main.pdf$(COLOR_RESET)"

paper-clean: ## 清理 LaTeX 编译中间文件
	cd paper && latexmk -c
	@rm -f paper/*.aux paper/*.bbl paper/*.blg paper/*.fls paper/*.fdb_latexmk paper/*.log paper/*.out paper/*.synctex.gz
	@echo "$(COLOR_GREEN)LaTeX 中间文件已清理$(COLOR_RESET)"

paper-view: paper-build ## 编译并打开 PDF
	@echo "打开 PDF..."
	@if command -v open > /dev/null; then open paper/main.pdf; \
	elif command -v xdg-open > /dev/null; then xdg-open paper/main.pdf; \
	else echo "请手动打开: paper/main.pdf"; fi

##@ Docker

docker-build: ## 构建 Docker 镜像
	$(DOCKER) build -t jciiot:latest .

docker-up: ## 启动 Docker 容器（后台）
	$(DOCKER_COMPOSE) up -d
	@echo "$(COLOR_GREEN)容器已启动$(COLOR_RESET)"
	@echo "进入容器: make docker-shell"

docker-down: ## 停止 Docker 容器
	$(DOCKER_COMPOSE) down

docker-shell: ## 进入 Docker 容器
	$(DOCKER_COMPOSE) exec jciiot bash

docker-logs: ## 查看 Docker 日志
	$(DOCKER_COMPOSE) logs -f jciiot

##@ 验证

validate-100: ## 验证 100/100（需要 DSW 实例运行中）
	@echo "$(COLOR_YELLOW)启动 ChampionTransportFlow 100/100 验证...$(COLOR_RESET)"
	$(PYTHON) scripts/debug_stages/stage264_test_champion_flow.py

validate-pickup: ## 验证 PickUpSkill（5 关卡）
	@echo "$(COLOR_YELLOW)启动 PickUpSkill 端到端测试...$(COLOR_RESET)"
	$(PYTHON) scripts/debug_stages/stage253_test_all_5_pickup.py

##@ 清理

clean: ## 清理所有生成文件
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache htmlcov .coverage
	rm -rf venv
	find . -name "*.pyc" -delete
	@echo "$(COLOR_GREEN)清理完成$(COLOR_RESET)"

clean-all: clean paper-clean ## 清理所有（含 LaTeX 中间文件）
	@echo "$(COLOR_GREEN)全部清理完成$(COLOR_RESET)"

##@ Git

git-status: ## 查看 git 状态
	@git status --short
	@git log --oneline -5

.PHONY: help setup setup-dev check-deps download-models check-models test test-cov syntax-check \
		paper-build paper-clean paper-view docker-build docker-up docker-down docker-shell docker-logs \
		validate-100 validate-pickup clean clean-all git-status
