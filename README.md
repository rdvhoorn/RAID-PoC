# RAID-PoC
PoC for AUMC RAID application

## Project Goal: RAID (Routine AI in Diagnostics)
RAID integrates AI analysis tools directly into the Sectra-PACS workflow to support pathologists in diagnosing tissue images. Through a new "AI Tools" dropdown in Sectra-PACS, users can request analyses such as cell classification or tumor outlining.
These requests are sent to the separate RAID application, which handles processing asynchronously. Once complete, RAID notifies Sectra-PACS, allowing results to be displayed as overlays or in a dedicated results panel.

## 🧪 Quickstart (Local HPC Testing)

### 1. Start Redis
```bash
redis-server &
```

### 2. Start Celery Worker
```bash
celery -A tasks worker --loglevel=info --concurrency=1 --pool=solo --logfile=celery.log
```

### 3. Run Test Task
```bash
python run_task.py
```

### 4. PostGreSQL stuff
```bash
pg_ctl -D ~/dbs/raid_pgdata -l ~/dbs/raidpoc_pgdb_logfile start // DB startup
python sqlalchemy_dbconnection_test.py // check whether db works correclty
pg_ctl -D ~/dbs/raid_pgdata stop // stop db
```

### 📂 File Overview for first tests
- tasks.py – defines Celery tasks (e.g., add)
- run_task.py – sends test tasks to Celery
- celery.log – Celery worker log output
- sqlalchemy_dbconnection_test.py - tests the pg db connection using sqlalchemy

### 🔧 Notes
**Avoid** running with default concurrency (--concurrency=1 --pool=solo) to prevent session crashes due to OOM fallbacks.
