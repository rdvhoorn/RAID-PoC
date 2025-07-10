# db_test.py
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData

engine = create_engine("postgresql://P098864@localhost/raidpoc")
metadata = MetaData()

jobs = Table('jobs', metadata,
    Column('id', Integer, primary_key=True),
    Column('wsi_id', String),
    Column('status', String)
)

metadata.create_all(engine)
print("DB setup complete")
