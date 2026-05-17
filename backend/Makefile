.PHONY: install dev conda-setup db-migrate db-upgrade test test-conda run-api run-worker frontend-install frontend-dev frontend-build frontend-deploy docker-up docker-backend docker-down clean

PROJECT_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
SPACY_MODEL_URL := https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
ENV_MANAGER := $(shell \
	if command -v mamba >/dev/null 2>&1; then \
		command -v mamba; \
	elif [ -x "$$HOME/.local/miniforge3/bin/mamba" ]; then \
		printf '%s\n' "$$HOME/.local/miniforge3/bin/mamba"; \
	elif [ -x "$$HOME/miniforge3/bin/mamba" ]; then \
		printf '%s\n' "$$HOME/miniforge3/bin/mamba"; \
	elif [ -x "$$HOME/mambaforge/bin/mamba" ]; then \
		printf '%s\n' "$$HOME/mambaforge/bin/mamba"; \
	elif command -v conda >/dev/null 2>&1; then \
		command -v conda; \
	elif [ -x "$$HOME/.local/miniforge3/bin/conda" ]; then \
		printf '%s\n' "$$HOME/.local/miniforge3/bin/conda"; \
	else \
		echo conda; \
	fi)

conda-setup:
	cd $(PROJECT_ROOT) && $(ENV_MANAGER) env update -n lexi -f environment.yml --prune || $(ENV_MANAGER) env create -f environment.yml
	$(ENV_MANAGER) run -n lexi python -m pip install $(SPACY_MODEL_URL)

install:
	pip install -r backend/requirements.txt
	python -m pip install $(SPACY_MODEL_URL)

dev:
	pip install -r backend/requirements.txt
	python -m pip install $(SPACY_MODEL_URL)

docker-up:
	cd $(PROJECT_ROOT) && docker compose up -d

docker-backend:
	cd $(PROJECT_ROOT) && docker compose up -d --build api worker

docker-down:
	cd $(PROJECT_ROOT) && docker compose down

db-migrate:
	cd $(PROJECT_ROOT) && alembic -c backend/alembic.ini revision --autogenerate -m "$(message)"

db-upgrade:
	cd $(PROJECT_ROOT) && alembic -c backend/alembic.ini upgrade head

db-downgrade:
	cd $(PROJECT_ROOT) && alembic -c backend/alembic.ini downgrade -1

run-api:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	celery -A backend.celery_app worker --loglevel=info

frontend-install:
	cd $(PROJECT_ROOT)/frontend && npm install

frontend-dev:
	cd $(PROJECT_ROOT)/frontend && npm run dev

frontend-build:
	cd $(PROJECT_ROOT)/frontend && npm run build

frontend-deploy:
	cd $(PROJECT_ROOT)/frontend && npm run deploy

test:
	pytest backend/tests/ -v --cov=backend --cov-report=html

test-conda:
	cd $(PROJECT_ROOT) && $(ENV_MANAGER) run -n lexi pytest backend/tests/ -v --cov=backend --cov-report=term-missing

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
