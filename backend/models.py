from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy import DateTime

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String)
    category = Column(String)
    price = Column(Float)

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer)

    current_stock = Column(Integer)

    reorder_level = Column(Integer)

    inventory_health_score = Column(Float)

class RFIDEvent(Base):

    __tablename__ = "rfid_events"

    id = Column(Integer, primary_key=True, index=True)

    rfid_tag = Column(String)

    event_type = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)