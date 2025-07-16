# Load environment variables from .env
ifneq (,$(wildcard .env))
	include .env
	export
endif

# Set python path
export PYTHONPATH := $(shell pwd)


# Define commands
up:
	@honcho start -f ./Procfile.dev

init_db:
	@echo "(Re-)Initializing database schema..."
	@$(PYTHON) utils/init_db.py

clear_db:
	@echo "Deleting all data (preserving schema)"
	@$(PYTHON) utils/clear_db.py

start_db:
	@echo "Starting PostgreSQL"
	@pg_ctl -D $(DB_DIR) -l $(DB_LOG_FILE) start

start_init_db:
	@make start_db
	@make init_db

stop_db:
	@echo "Stopping PostgreSQL server"
	@if pg_ctl -D $(DB_DIR) status > /dev/null 2>&1; then \
		pg_ctl -D $(DB_DIR) stop -m fast && echo "PostgreSQL stopped."; \
	else \
		echo "PostgreSQL is not running or status check failed."; \
	fi


# ------ In case you want to start service in isolation -----
start_celery:
	@echo "Starting Celery worker"
	@SERVICE_NAME=$(CELERY_SERVICE_NAME) PYTHONPATH=. celery -A $(CELERY_APP) worker --loglevel=info --concurrency=1 --pool=solo

start_fastapi:
	@echo "Starting FastAPI server"
	@SERVICE_NAME=$(FASTAPI_SERVICE_NAME) uvicorn api.main:app --port $(FASTAPI_PORT) --log-level info

start_redis:
	@echo "Starting Redis server"
	@redis-server --save "" --appendonly no

.PHONY: start_backend stop_backend init_db clear_db start_redis stop_redis start_db stop_db start_celery stop_celery