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
    DateTime, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base


# ── User ─────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="customer") # admin, store_owner, customer
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    store = relationship("Store", back_populates="users")
    orders = relationship("Order", back_populates="user")


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
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    store = relationship("Store", back_populates="products")


# ── Inventory ────────────────────────────────────────────────

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    current_stock = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)
    unit = Column(String, nullable=False, default="pcs")
    inventory_health_score = Column(Float, default=100.0)
    lead_time_days = Column(Integer, nullable=False, default=3)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('product_id', 'store_id', name='uix_product_store'),
    )

    # Relationships
    product = relationship("Product", back_populates="inventory")
    store = relationship("Store", back_populates="inventory_items")




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
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    store = relationship("Store", back_populates="orders")
    user = relationship("User", back_populates="orders")


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

    # Relationships
    users = relationship("User", back_populates="store")
    products = relationship("Product", back_populates="store")
    inventory_items = relationship("Inventory", back_populates="store")
    orders = relationship("Order", back_populates="store")


# ── Model Evaluations ────────────────────────────────────────

class ModelEvaluation(Base):
    __tablename__ = "model_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String, nullable=False)  # lstm, gru, xgboost, random_forest, ensemble
    dataset_version = Column(String, nullable=True)
    rmse = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    r2_score = Column(Float, nullable=True)
    training_time_seconds = Column(Float, nullable=True)
    inference_time_ms = Column(Float, nullable=True)
    sample_count = Column(Integer, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow)


# ── Forecast Configurations ──────────────────────────────────

class ForecastConfig(Base):
    __tablename__ = "forecast_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String, unique=True, nullable=False)  # e.g., "ensemble_weights", "active_model"
    config_value = Column(Text, nullable=False)  # JSON-serialized string
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Complaints & Reviews ─────────────────────────────────────

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    issue_description = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="open") # open, investigating, resolved
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    rating = Column(Integer, nullable=False) # 1-5
    comment = Column(Text, nullable=True)
    owner_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", backref="reviews")

