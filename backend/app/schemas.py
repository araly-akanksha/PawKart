# ============================================================
# PAWKART PYDANTIC SCHEMAS
# ============================================================
#
# Input schemas (Create/Update) and Output schemas (Response)
# for all API endpoints. Enables typed Swagger documentation.
#
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Product Schemas ──────────────────────────────────────────

class ProductCreate(BaseModel):
    product_name: str
    description: Optional[str] = None
    category: str
    price: float = Field(gt=0)
    sku: Optional[str] = None
    image_url: Optional[str] = None
    available: bool = True


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    sku: Optional[str] = None
    image_url: Optional[str] = None
    available: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    product_name: str
    category: str
    price: float
    description: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None
    available: bool = True
    store_id: Optional[int] = None

    class Config:
        from_attributes = True

class DashboardProductResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    location: str
    stockStatus: str
    quantity: int
    image: str

# ── Inventory Schemas ────────────────────────────────────────

class InventoryCreate(BaseModel):
    product_id: int
    current_stock: int = Field(ge=0)
    reorder_level: int = Field(ge=0, default=10)
    unit: str = "pcs"


class InventoryUpdate(BaseModel):
    current_stock: Optional[int] = Field(default=None, ge=0)
    reorder_level: Optional[int] = Field(default=None, ge=0)
    unit: Optional[str] = None


class StockUpdate(BaseModel):
    product_id: int
    quantity_sold: int = Field(gt=0)


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    current_stock: int
    reorder_level: int
    unit: str
    inventory_health_score: Optional[float]
    last_updated: Optional[datetime]

    class Config:
        from_attributes = True


class LowStockAlert(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    reorder_level: int
    unit: str
    deficit: int  # how many units below reorder level





# ── Order Schemas (adapted from Replit) ──────────────────────

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    delivery_slot: Optional[str] = None
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: str
    customer: str
    items: str
    amount: float
    gateway: str
    status: str

    class Config:
        from_attributes = True

class OrderDetailResponse(BaseModel):
    id: int
    customer_name: str
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    status: str
    total_amount: float
    item_count: int
    delivery_slot: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str = Field(
        description="New status: pending, confirmed, preparing, "
                    "out_for_delivery, delivered, cancelled"
    )


class OrderSummaryResponse(BaseModel):
    pending: int = 0
    confirmed: int = 0
    preparing: int = 0
    out_for_delivery: int = 0
    delivered: int = 0
    cancelled: int = 0
    total: int = 0


# ── Store Schemas (adapted from Replit) ──────────────────────

class StoreResponse(BaseModel):
    id: int
    name: str
    owner_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    logo_url: Optional[str]
    is_open: bool
    opening_time: Optional[str]
    closing_time: Optional[str]
    delivery_radius_km: Optional[float]
    min_order_amount: Optional[float]

    class Config:
        from_attributes = True


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    owner_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    is_open: Optional[bool] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    delivery_radius_km: Optional[float] = None
    min_order_amount: Optional[float] = None


# ── Analytics Schemas (adapted from Replit) ──────────────────

class DashboardSummary(BaseModel):
    today_revenue: float = 0.0
    today_orders: int = 0
    pending_orders: int = 0
    low_stock_count: int = 0
    fulfillment_rate: float = 0.0
    avg_delivery_minutes: Optional[float] = None
    active_products: int = 0
    revenue_change: Optional[float] = None
    orders_change: Optional[float] = None


class SalesDataPoint(BaseModel):
    date: str
    revenue: float
    order_count: int


class FulfillmentStats(BaseModel):
    fulfillment_rate: float
    avg_delivery_minutes: Optional[float]
    cancel_rate: float
    on_time_rate: float


class TopProductResponse(BaseModel):
    product_id: int
    product_name: str
    total_sold: int
    revenue: float


# ── Dispatch Schemas (SO4: Automated Delivery) ───────────────

class DispatchResponse(BaseModel):
    order_id: int
    message: str
    dispatched_at: datetime
    estimated_delivery_at: datetime
    stage_delay_seconds: int
    pipeline: str


# ── Forecasting Schemas ──────────────────────────────────────

class ForecastResponse(BaseModel):
    product_id: int
    predicted_demand_next_week: int
    demand_category: str
    confidence: Optional[str] = None
    explanation: Optional[str] = None


# ── Model Info Schema (SO6: Evaluation Metrics) ──────────────

class ModelInfoResponse(BaseModel):
    model_type: str
    layers: int
    units_per_layer: int
    training_records: int
    sequence_length: int
    epochs: int
    # Evaluation metrics (from offline training)
    rmse: float
    mae: float
    mape: float
    r2_score: float
    # Architecture details
    optimizer: str
    loss_function: str
    normalization: str


# ── Optimization Schemas ─────────────────────────────────────

class ReorderResponse(BaseModel):
    product_id: int
    current_stock: int
    predicted_demand: Optional[int] = None
    recommended_reorder_quantity: int
    risk_level: str
    explanation: str


# ── Auth & User Schemas ─────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "customer" # admin, store_owner, customer
    store_id: Optional[int] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    store_id: Optional[int]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    store_id: Optional[int] = None


# ── Complaint & Review Schemas ──────────────────────────────

class ComplaintCreate(BaseModel):
    customer_email: str
    order_id: Optional[int] = None
    issue_description: str

class ComplaintResponse(BaseModel):
    id: int
    customer_email: str
    order_id: Optional[int]
    issue_description: str
    status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    product_id: int
    customer_name: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    product_id: int
    customer_name: str
    rating: int
    comment: Optional[str]
    owner_response: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
