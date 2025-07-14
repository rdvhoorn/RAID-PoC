# init_db.py
from db.models import Base
from db.session import engine

def reset_database():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("✅ Database reset complete.")

if __name__ == "__main__":
    reset_database()
