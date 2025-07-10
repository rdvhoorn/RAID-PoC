# This file defines Celery tasks for the RAID PoC system.
# Currently contains simple arithmetic tasks for testing Redis + Celery integration.

from celery import Celery

app = Celery(
    'raid_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@app.task
def add(x, y):
    return x + y
