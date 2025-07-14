from db.session import SessionLocal
from db.models import Job, ResultFile

session = SessionLocal()

# Delete result files first (foreign key)
session.query(ResultFile).delete()
session.query(Job).delete()

session.commit()
session.close()
print("All rows deleted from Job and ResultFile tables.")
