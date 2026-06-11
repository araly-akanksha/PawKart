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
#
# Dispatch simulation (demo mode):
#   Each stage advances every 30s (represents real-world minutes).
#   Total = ~90s demo = represents sub-30-minute SLA delivery.
# ============================================================

import time
import threading
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.dependencies import get_db, get_current_user, get_current_store_owner, get_optional_current_user
from app import models
from app.models import Order, OrderItem, Product
from app.schemas import (
    OrderCreate, OrderResponse, OrderDetailResponse,
    OrderItemResponse, OrderStatusUpdate, OrderSummaryResponse,
    DispatchResponse
)

router = APIRouter()

VALID_STATUSES = {
    "pending", "confirmed", "preparing",
    "out_for_delivery", "delivered", "cancelled"
}

# ── In-memory dispatch tracker ───────────────────────────────
# Stores {order_id: dispatched_at_iso} for SLA tracking
# Resets on server restart (acceptable for prototype)
_dispatch_registry: dict = {}

# Demo timing: 30s per stage (represents real-world minutes)
STAGE_DELAY_SECONDS = 30


def _auto_advance(order_id: int, new_status: str, delay: int):
    """Background thread: waits `delay` seconds then sets order to new_status."""
    from app.database import SessionLocal

    time.sleep(delay)
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.status not in ("delivered", "cancelled"):
            order.status = new_status
            order.updated_at = datetime.utcnow()
            db.commit()
    except Exception:
        pass
    finally:
        db.close()



# ── Create Order ─────────────────────────────────────────────

@router.post("/orders", response_model=OrderDetailResponse, status_code=201)
def create_order(
    order: OrderCreate, 
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user)
):
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

        # FIX PHANTOM INVENTORY: Lock and deduct stock
        from app.models import Inventory, Product
        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).with_for_update().first()
        
        # Priority 2: Cross-Store Routing
        if inventory and inventory.current_stock < item.quantity:
            # Try to find another product with same SKU in a different store
            alt_product = db.query(Product).join(Inventory).filter(
                Product.sku == product.sku,
                Inventory.current_stock >= item.quantity
            ).first()
            if alt_product:
                product = alt_product
                inventory = db.query(Inventory).filter(Inventory.product_id == product.id).with_for_update().first()
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for {product.product_name} anywhere in the network."
                )

        if inventory:
            inventory.current_stock -= item.quantity

        order_items.append(OrderItem(
            product_id=product.id,
            product_name=product.product_name,
            quantity=item.quantity,
            unit_price=product.price,
            subtotal=subtotal
        ))

    # Set store_id based on the first product's store (assuming single-store checkout for now)
    first_product = db.query(Product).filter(Product.id == order.items[0].product_id).first()
    store_id = first_product.store_id if first_product else None

    # Create the order
    new_order = Order(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_address=order.customer_address,
        delivery_slot=order.delivery_slot,
        total_amount=round(total_amount, 2),
        status="pending",
        items=order_items,
        user_id=current_user.id if current_user else None,
        store_id=store_id
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
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user)
):
    query = db.query(Order)

    if current_user:
        if current_user.role == "customer":
            query = query.filter(Order.user_id == current_user.id)
        elif current_user.role == "store_owner":
            query = query.filter(Order.store_id == current_user.store_id)

    if status and status != "all":
        query = query.filter(Order.status == status)

    orders = query.order_by(Order.created_at.desc()).limit(limit).all()

    results = []
    for order in orders:
        items_str = ", ".join([f"{item.product_name} x {item.quantity}" for item in order.items])
        if not items_str:
            items_str = "No items"
            
        results.append({
            "id": f"PK{order.id + 1000}",
            "customer": order.customer_name,
            "items": items_str,
            "amount": order.total_amount,
            "gateway": "UPI",
            "status": order.status
        })

    return results


# ── Order Summary (from Replit) ──────────────────────────────
# IMPORTANT: Must be before /orders/{order_id} to avoid
# "summary" being matched as an order_id parameter.

@router.get("/orders/summary", response_model=OrderSummaryResponse)
def get_order_summary(
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user)
):
    query = db.query(Order.status, func.count(Order.id))
    
    if current_user and current_user.role == "store_owner":
        query = query.filter(Order.store_id == current_user.store_id)
        
    counts = query.group_by(Order.status).all()

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
def get_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role == "customer" and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "store_owner" and order.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

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

@router.patch("/orders/{order_id}/status", response_model=OrderDetailResponse)
def update_order_status(
    order_id: int,
    update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user)
):
    if update.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        )

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if current_user and current_user.role == "store_owner" and order.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    order.status = update.status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

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


# ── Dispatch Order (SO4: Automated Fulfillment) ──────────────
#
# Triggers the full automated delivery pipeline:
#   Now:   confirmed
#   +30s:  preparing
#   +60s:  out_for_delivery
#   +90s:  delivered   ← sub-30-min SLA met ✅
#
# Demo mode: 30s/stage represents real-world minutes.
# Tracks dispatch time for SLA evaluation (research objective #6).

@router.post("/orders/{order_id}/dispatch", response_model=DispatchResponse)
def dispatch_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_store_owner)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if current_user.role == "store_owner" and order.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if order.status in ("delivered", "cancelled"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot dispatch order with status '{order.status}'"
        )

    # Set to confirmed immediately
    order.status = "confirmed"
    dispatched_at = datetime.utcnow()
    order.updated_at = dispatched_at
    db.commit()

    # Register dispatch time for SLA tracking
    _dispatch_registry[order_id] = dispatched_at.isoformat()

    # Estimated delivery = 3 stages × 30s = 90s (demo)
    estimated_delivery = dispatched_at + timedelta(seconds=STAGE_DELAY_SECONDS * 3)

    # Launch background threads for automatic stage advancement
    stages = [
        ("preparing",        STAGE_DELAY_SECONDS),
        ("out_for_delivery", STAGE_DELAY_SECONDS * 2),
        ("delivered",        STAGE_DELAY_SECONDS * 3),
    ]
    for status, delay in stages:
        t = threading.Thread(
            target=_auto_advance,
            args=(order_id, status, delay),
            daemon=True
        )
        t.start()

    return DispatchResponse(
        order_id=order_id,
        message="🚀 Order dispatched! Auto-advancing through delivery pipeline.",
        dispatched_at=dispatched_at,
        estimated_delivery_at=estimated_delivery,
        stage_delay_seconds=STAGE_DELAY_SECONDS,
        pipeline="confirmed → preparing (+30s) → out_for_delivery (+60s) → delivered (+90s)"
    )


# ── Dispatch Status ──────────────────────────────────────────

@router.get("/orders/{order_id}/dispatch-status")
def get_dispatch_status(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    dispatched_at_str = _dispatch_registry.get(order_id)

    if not dispatched_at_str:
        return {
            "order_id": order_id,
            "status": order.status,
            "dispatched": False,
            "elapsed_seconds": None,
            "sla_met": None
        }

    dispatched_at = datetime.fromisoformat(dispatched_at_str)
    elapsed = (datetime.utcnow() - dispatched_at).total_seconds()
    sla_seconds = STAGE_DELAY_SECONDS * 3  # 90s demo = 30min real
    sla_met = elapsed <= sla_seconds if order.status == "delivered" else None

    return {
        "order_id": order_id,
        "status": order.status,
        "dispatched": True,
        "dispatched_at": dispatched_at_str,
        "elapsed_seconds": round(elapsed),
        "sla_seconds": sla_seconds,
        "sla_met": sla_met,
        "estimated_delivery_at": (
            dispatched_at + timedelta(seconds=sla_seconds)
        ).isoformat()
    }
