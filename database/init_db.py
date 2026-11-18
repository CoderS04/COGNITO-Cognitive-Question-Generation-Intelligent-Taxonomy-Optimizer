import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.database import engine, Base, SessionLocal
from app.seed_data import seed_initial_data

def main():
    print("[COGNITO Database Initializer]")
    print(f"Connecting to database via engine: {engine.url}")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

    db = SessionLocal()
    try:
        seed_initial_data(db)
        print("Initial database seed completed successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
