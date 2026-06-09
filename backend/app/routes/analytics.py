# ============================================================
# ANALYTICS ROUTES — Dashboard KPIs
# ============================================================
#
# Adapted from Replit's analytics endpoints.
# Supports research objective #6:
# Evaluate effectiveness using performance metrics such as
# inventory accuracy, stockout reduction, order fulfillment
# time, and forecasting precision.
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.dependencies import get_db, get_current_store_owner
from app import models
from app.models import Order, OrderItem, Product, Inventory
from app.schemas import (
    DashboardSummary, SalesDataPoint, FulfillmentStats,
    TopProductResponse
)
from typing import List

router = APIRouter()


# ── Dashboard Summary KPIs (from Replit) ─────────────────────

@router.get("/analytics/dashboard", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_store_owner)
):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    
    # Store filter
    store_filter = True if current_user.role == "admin" else (Order.store_id == current_user.store_id)
    inv_store_filter = True if current_user.role == "admin" else (Inventory.store_id == current_user.store_id)

    # Today's revenue and orders (exclude cancelled)
    today_stats = (
        db.query(
            func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
            func.count(Order.id).label("orders")
        )
        .filter(Order.created_at >= today)
        .filter(Order.status != "cancelled")
        .filter(store_filter)
        .first()
    )

    # Yesterday's stats for comparison
    yesterday_stats = (
        db.query(
            func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
            func.count(Order.id).label("orders")
        )
        .filter(and_(Order.created_at >= yesterday, Order.created_at < today))
        .filter(Order.status != "cancelled")
        .filter(store_filter)
        .first()
    )

    # Pending orders
    pending_count = (
        db.query(func.count(Order.id))
        .filter(Order.status.in_(["pending", "confirmed", "preparing"]))
        .filter(store_filter)
        .scalar() or 0
    )

    # Low stock count
    low_stock_count = (
        db.query(func.count(Inventory.id))
        .filter(Inventory.current_stock <= Inventory.reorder_level)
        .filter(inv_store_filter)
        .scalar() or 0
    )

    # Fulfillment rate (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    total_orders_30d = (
        db.query(func.count(Order.id))
        .filter(Order.created_at >= thirty_days_ago)
        .filter(store_filter)
        .scalar() or 0
    )
    delivered_30d = (
        db.query(func.count(Order.id))
        .filter(Order.created_at >= thirty_days_ago)
        .filter(Order.status == "delivered")
        .filter(store_filter)
        .scalar() or 0
    )
    fulfillment_rate = round((delivered_30d / total_orders_30d * 100), 1) if total_orders_30d > 0 else 0.0

    # Active products
    active_products = (
        db.query(func.count(Product.id))
        .filter(Product.available == True)
        .scalar() or 0
    )

    # Calculate changes
    today_revenue = float(today_stats.revenue) if today_stats else 0.0
    today_orders = int(today_stats.orders) if today_stats else 0
    yesterday_revenue = float(yesterday_stats.revenue) if yesterday_stats else 0.0
    yesterday_orders = int(yesterday_stats.orders) if yesterday_stats else 0

    revenue_change = None
    if yesterday_revenue > 0:
        revenue_change = round(((today_revenue - yesterday_revenue) / yesterday_revenue) * 100, 1)

    orders_change = None
    if yesterday_orders > 0:
        orders_change = round(((today_orders - yesterday_orders) / yesterday_orders) * 100, 1)

    return DashboardSummary(
        today_revenue=today_revenue,
        today_orders=today_orders,
        pending_orders=pending_count,
        low_stock_count=low_stock_count,
        fulfillment_rate=fulfillment_rate,
        avg_delivery_minutes=None,  # Computed in fulfillment endpoint
        active_products=active_products,
        revenue_change=revenue_change,
        orders_change=orders_change
    )


# ── 30-Day Sales Data (from Replit) ─────────────────────────

@router.get("/analytics/sales", response_model=List[SalesDataPoint])
def get_sales_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_store_owner)
):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    store_filter = True if current_user.role == "admin" else (Order.store_id == current_user.store_id)

    rows = (
        db.query(
            func.date(Order.created_at).label("date"),
            func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
            func.count(Order.id).label("order_count")
        )
        .filter(Order.created_at >= thirty_days_ago)
        .filter(Order.status != "cancelled")
        .filter(store_filter)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )

    # Build a map of existing data
    data_by_date = {str(row.date): row for row in rows}

    # Fill in missing days with zeros
    result = []
    for i in range(29, -1, -1):
        d = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        if d in data_by_date:
            row = data_by_date[d]
            result.append(SalesDataPoint(
                date=d,
                revenue=float(row.revenue),
                order_count=int(row.order_count)
            ))
        else:
            result.append(SalesDataPoint(date=d, revenue=0.0, order_count=0))

    return result


# ── Fulfillment Stats (from Replit) ──────────────────────────

@router.get("/analytics/fulfillment", response_model=FulfillmentStats)
def get_fulfillment_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_store_owner)
):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    store_filter = True if current_user.role == "admin" else (Order.store_id == current_user.store_id)

    total = (
        db.query(func.count(Order.id))
        .filter(Order.created_at >= thirty_days_ago)
        .filter(store_filter)
        .scalar() or 0
    )
    delivered = (
        db.query(func.count(Order.id))
        .filter(Order.created_at >= thirty_days_ago)
        .filter(Order.status == "delivered")
        .filter(store_filter)
        .scalar() or 0
    )
    cancelled = (
        db.query(func.count(Order.id))
        .filter(Order.created_at >= thirty_days_ago)
        .filter(Order.status == "cancelled")
        .filter(store_filter)
        .scalar() or 0
    )

    fulfillment_rate = round((delivered / total * 100), 1) if total > 0 else 0.0
    cancel_rate = round((cancelled / total * 100), 1) if total > 0 else 0.0

    # Avg delivery time (minutes between created_at and updated_at for delivered orders)
    SLA_MINUTES = 30  # Quick-commerce SLA
    delivered_orders = (
        db.query(Order.created_at, Order.updated_at)
        .filter(Order.created_at >= thirty_days_ago)
        .filter(Order.status == "delivered")
        .filter(store_filter)
        .all()
    )

    avg_delivery_minutes = None
    on_time_rate = 0.0
    if delivered_orders:
        durations = [
            (o.updated_at - o.created_at).total_seconds() / 60
            for o in delivered_orders
            if o.updated_at and o.created_at
        ]
        if durations:
            avg_delivery_minutes = round(sum(durations) / len(durations), 1)
            on_time = len([d for d in durations if d <= SLA_MINUTES])
            on_time_rate = round((on_time / len(durations)) * 100, 1)

    return FulfillmentStats(
        fulfillment_rate=fulfillment_rate,
        avg_delivery_minutes=avg_delivery_minutes,
        cancel_rate=cancel_rate,
        on_time_rate=on_time_rate
    )


# ── Top Products (from Replit) ───────────────────────────────

@router.get("/analytics/top-products", response_model=List[TopProductResponse])
def get_top_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_store_owner)
):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    store_filter = True if current_user.role == "admin" else (Order.store_id == current_user.store_id)

    rows = (
        db.query(
            OrderItem.product_id,
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.subtotal).label("revenue")
        )
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.created_at >= thirty_days_ago)
        .filter(Order.status != "cancelled")
        .filter(store_filter)
        .group_by(OrderItem.product_id, OrderItem.product_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    return [
        TopProductResponse(
            product_id=row.product_id,
            product_name=row.product_name,
            total_sold=int(row.total_sold),
            revenue=float(row.revenue)
        )
        for row in rows
    ]
