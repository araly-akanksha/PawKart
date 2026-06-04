# ============================================================
# ORDER ROUTES — Quick-Commerce Fulfillment
# ============================================================
#
# Adapted from Replit's order management flow.
# Supports research objective #4:
# Automated fulfillment coordination and hyperlocal
# delivery management for sub-30-minute delivery.
#
# Status flow:
#   pending → confirmed → preparing → out_for_delivery → delivered
#                                                       → cancelled
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.dependencies import get_db
from app.models import Order, OrderItem, Product
from app.schemas import (
    OrderCreate, OrderResponse, OrderDetailResponse,
    OrderItemResponse, OrderStatusUpdate, OrderSummaryResponse
)

router = APIRouter()

VALID_STATUSES = {
    "pending", "confirmed", "preparing",
    "out_for_delivery", "delivered", "cancelled"
}


# ── Create Order ─────────────────────────────────────────────

@router.post("/orders", response_model=OrderDetailResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    # Build order items and calculate total
    order_items = []
    total_amount = 0.0

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with id {item.product_id} not found"
            )

        subtotal = product.price * item.quantity
        total_amount += subtotal

        order_items.append(OrderItem(
            product_id=product.id,
            product_name=product.product_name,
            quantity=item.quantity,
            unit_price=product.price,
            subtotal=subtotal
        ))

    # Create the order
    new_order = Order(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_address=order.customer_address,
        delivery_slot=order.delivery_slot,
        total_amount=round(total_amount, 2),
        status="pending",
        items=order_items
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return OrderDetailResponse(
        id=new_order.id,
        customer_name=new_order.customer_name,
        customer_phone=new_order.customer_phone,
        customer_address=new_order.customer_address,
        status=new_order.status,
        total_amount=new_order.total_amount,
        item_count=sum(i.quantity for i in new_order.items),
        delivery_slot=new_order.delivery_slot,
        created_at=new_order.created_at,
        updated_at=new_order.updated_at,
        items=[OrderItemResponse.model_validate(i) for i in new_order.items]
    )


# ── List Orders ──────────────────────────────────────────────

@router.get("/orders", response_model=List[OrderResponse])
def list_orders(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(Order)

    if status and status != "all":
        query = query.filter(Order.status == status)

    orders = query.order_by(Order.created_at.desc()).limit(limit).all()

    results = []
    for order in orders:
        item_count = sum(item.quantity for item in order.items)
        results.append(OrderResponse(
            id=order.id,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_address=order.customer_address,
            status=order.status,
            total_amount=order.total_amount,
            item_count=item_count,
            delivery_slot=order.delivery_slot,
            created_at=order.created_at,
            updated_at=order.updated_at
        ))

    return results


# ── Order Summary (from Replit) ──────────────────────────────
# IMPORTANT: Must be before /orders/{order_id} to avoid
# "summary" being matched as an order_id parameter.

@router.get("/orders/summary", response_model=OrderSummaryResponse)
def get_order_summary(db: Session = Depends(get_db)):
    counts = (
        db.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )

    summary = {s: 0 for s in VALID_STATUSES}
    for status, count in counts:
        if status in summary:
            summary[status] = count

    return OrderSummaryResponse(
        pending=summary["pending"],
        confirmed=summary["confirmed"],
        preparing=summary["preparing"],
        out_for_delivery=summary["out_for_delivery"],
        delivered=summary["delivered"],
        cancelled=summary["cancelled"],
        total=sum(summary.values())
    )


# ── Get Order Detail ─────────────────────────────────────────

@router.get("/orders/{order_id}", response_model=OrderDetailResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderDetailResponse(
        id=order.id,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_address=order.customer_address,
        status=order.status,
        total_amount=order.total_amount,
        item_count=sum(i.quantity for i in order.items),
        delivery_slot=order.delivery_slot,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[OrderItemResponse.model_validate(i) for i in order.items]
    )


# ── Update Order Status ─────────────────────────────────────

@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    update: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    if update.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        )

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = update.status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    return OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_address=order.customer_address,
        status=order.status,
        total_amount=order.total_amount,
        item_count=sum(i.quantity for i in order.items),
        delivery_slot=order.delivery_slot,
        created_at=order.created_at,
        updated_at=order.updated_at
    )


