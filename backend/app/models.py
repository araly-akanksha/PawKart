# ============================================================
# PAWKART DATABASE MODELS
# ============================================================
#
# Original models: Product, Inventory, RFIDEvent
# Enhanced fields: description, sku, available, unit, rfid_tag_id
# New models: Order, OrderItem, Store (adapted from Replit)
#
# ============================================================

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base


# ── Product ──────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    sku = Column(String, unique=True, nullable=True)
    image_url = Column(String, nullable=True)
    available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inventory = relationship("Inventory", back_populates="product", uselist=False)


# ── Inventory ────────────────────────────────────────────────

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    current_stock = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)
    unit = Column(String, nullable=False, default="pcs")
    inventory_health_score = Column(Float, default=100.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="inventory")


# ── RFID Events ──────────────────────────────────────────────

class RFIDEvent(Base):
    __tablename__ = "rfid_events"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )
    rfid_tag_id = Column(String, nullable=True)
    event_type = Column(String, nullable=False)  # SALE, RESTOCK, RETURN, AUDIT
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product")


# ── Orders (adapted from Replit) ─────────────────────────────
#
# Status flow for quick-commerce fulfillment:
#   pending → confirmed → preparing → out_for_delivery → delivered
#                                                      → cancelled

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)
    customer_address = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="pending")
    total_amount = Column(Float, nullable=False, default=0.0)
    delivery_slot = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


# ── Store Settings (adapted from Replit) ─────────────────────

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, default="My Pet Store")
    owner_name = Column(String, nullable=False, default="Store Owner")
    email = Column(String, nullable=False, default="owner@store.com")
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)
    is_open = Column(Boolean, default=True, nullable=False)
    opening_time = Column(String, default="09:00")
    closing_time = Column(String, default="21:00")
    delivery_radius_km = Column(Float, nullable=True)
    min_order_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
