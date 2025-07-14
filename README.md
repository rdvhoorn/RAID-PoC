# RAID-PoC
PoC for AUMC RAID application

## Project Goal: RAID (Routine AI in Diagnostics)
RAID integrates AI analysis tools directly into the Sectra-PACS workflow to support pathologists in diagnosing tissue images. Through a new "AI Tools" dropdown in Sectra-PACS, users can request analyses such as cell classification or tumor outlining.
These requests are sent to the separate RAID application, which handles processing asynchronously. Once complete, RAID notifies Sectra-PACS, allowing results to be displayed as overlays or in a dedicated results panel.

## 🧪 Quickstart (Local HPC Testing)
When correctly setup, just use the make file to startup (`make up`) and stop (`make down`). 

# Full setup
Three parts
1. Environment setup
2. PostGreSQL database initialization
3. Config file setup

## Environment setup
Assuming miniconda is installed
```bash
conda env create -f environment.yml
conda activate RAID-PoC
pip install uv
uv pip install -r requirements.txt
```

## Postgres setup
Assuming the environment is activated
```bash
initdb -D <path/to/where/you/want/your/databasefolder>
```

## .env file
Copy paste the `example.env` file and rename to `.env`. Set the right parameters, given your install

# File structure
```bash
raid_poc/
├── db/
│   ├── models.py       # DB model definition
│   └── session.py      # DB session init
├── tasks/
│   └── slurm_tasks.py  # Slurm task definition for deploying inference jobs
├── scripts/
│   └── raid_infer.sh  # SLURM inference simulation job
├── utils
│   ├── clear_db.py    # Clearing all db entries
│   ├── config.py      # Config loading file from .env (no need to edit)
│   └── init_db.py     # DB initialization script
├── run_task.py        # Manual test input file
├── example.env        # Contains paths like OUTPUT_DIR
├── Makefile           # Script definitions for easier application running

```

### 🔧 Notes
**Avoid** running with default concurrency (--concurrency=1 --pool=solo) to prevent session crashes due to OOM fallbacks on helios.
