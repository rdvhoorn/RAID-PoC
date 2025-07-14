from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# You can move this to .env later
DATABASE_URL = "postgresql://P098864@localhost/raidpoc"

# Create engine and session factory
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
