# Sends a test task to the Celery worker and waits for the result.
from tasks import add

for i in range(5):
    result = add.delay(i, i * 2)
    print(f"Task {i} → result: {result.get(timeout=10)}")
