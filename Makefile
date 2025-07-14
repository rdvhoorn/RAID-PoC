# Load environment variables from .env
ifneq (,$(wildcard .env))
	include .env
	export
endif

# Set python path
export PYTHONPATH := $(shell pwd)


# Define commands
up:
	@echo "Starting backend: PostgreSQL + Redis + Celery"
	@make start_db
	@make init_db
	@make start_redis
	@make start_celery

down:
	@echo "Stopping backend: PostgreSQL + Redis + Celery"
	@make stop_celery
	@make stop_redis
	@make stop_db

init_db:
	@echo "(Re-)Initializing database schema..."
	@$(PYTHON) utils/init_db.py

clear_db:
	@echo "Deleting all data (preserving schema)"
	@$(PYTHON) utils/clear_db.py

start_redis:
	@echo "Starting Redis server in detached mode"
	@redis-server --save "" --appendonly no --daemonize yes 

stop_redis:
	@echo "Stopping Redis server"
	@if redis-cli ping > /dev/null 2>&1; then \
		redis-cli shutdown; \
	else \
		echo "Redis is not running."; \
	fi

start_db:
	@echo "Starting PostgreSQL"
	@pg_ctl -D $(DB_DIR) -l $(DB_LOG_FILE) start

stop_db:
	@pg_ctl -D $(DB_DIR) stop

start_celery:
	@echo "Starting Celery worker in background"
	@celery -A $(CELERY_APP) worker --loglevel=info --concurrency=1 --pool=solo --detach --logfile=$(CELERY_LOGFILE) --pidfile=$(CELERY_PIDFILE)

stop_celery:
	@echo "Stopping Celery worker"
	@if [ -f $(CELERY_PIDFILE) ]; then \
		kill `cat $(CELERY_PIDFILE)` && rm -f $(CELERY_PIDFILE); \
	else \
		echo "No Celery PID file found."; \
	fi

.PHONY: start_backend stop_backend init_db clear_db start_redis stop_redis start_db stop_db start_celery stop_celery