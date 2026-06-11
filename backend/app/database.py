# ============================================================
# DATABASE CONNECTION
# ============================================================

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("WARNING: No DATABASE_URL found in environment variables. Falling back to default local SQLite database.")
    DATABASE_URL = "sqlite:///./pawkart.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def verify_and_update_schema():
    """Verify tables exist and add new columns to existing tables if missing."""
    from sqlalchemy import inspect, text
    
    # 1. Create any missing tables (e.g. model_evaluations, forecast_configs)
    Base.metadata.create_all(bind=engine)
    print("Database tables verified.")
    
    # 2. Check and migrate columns
    inspector = inspect(engine)
    if "inventory" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("inventory")]
        if "lead_time_days" not in columns:
            print("Migration: Adding 'lead_time_days' column to 'inventory' table...")
            with engine.begin() as conn:
                conn.execute(
                    text("ALTER TABLE inventory ADD COLUMN lead_time_days INTEGER DEFAULT 3 NOT NULL")
                )
            print("Migration: 'lead_time_days' column added successfully.")

    # 3. Check if database is completely empty and warn user
    from app.models import Product
    with engine.begin() as conn:
        res = conn.execute(text("SELECT COUNT(*) FROM products"))
        count = res.scalar()
        if count == 0:
            print("\n" + "="*60)
            print("🚨 WARNING: YOUR DATABASE IS EMPTY! 🚨")
            print("The frontend will display 'Server Offline' if there are no products.")
            print("Please run `python seed_real_data.py` to populate it.")
            print("="*60 + "\n")
