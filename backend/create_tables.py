# ============================================================
# CREATE TABLES
# ============================================================
# Run this to create all database tables:
#   cd backend && python create_tables.py
#
# Note: Tables are also auto-created when the app starts.
# This script is useful for initial setup or testing.
# ============================================================

from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

print("All tables created successfully!")
print("Tables: products, inventory, rfid_events, orders, order_items, stores")