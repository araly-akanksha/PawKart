# ============================================================
# INVENTORY OPTIMIZATION ROUTES
# ============================================================
#
# Supports research objective #3:
# Dynamic reorder-point optimization that minimizes stockouts,
# reduces manual inventory errors, and improves replenishment.
#
# Integrates with forecasting for demand-aware reorder points.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.dependencies import get_db, get_current_store_owner
from app import models
from app.models import Inventory, Product, OrderItem, Order
from app.schemas import ReorderResponse

router = APIRouter()


# ── Risk Level Classification ────────────────────────────────

def classify_risk(current_stock: int, reorder_level: int) -> str:
    if current_stock <= 0:
        return "Critical"
    elif current_stock < reorder_level * 0.5:
        return "High Risk"
    elif current_stock < reorder_level:
        return "Moderate Risk"
    else:
        return "Low Risk"


# ── Demand-Aware Reorder Calculation ─────────────────────────

def calculate_reorder_quantity(
    current_stock: int,
    reorder_level: int,
    weekly_demand: int
) -> int:
    """
    Smart reorder calculation:
    - If stock is critically low: order 2 weeks of demand
    - If stock is below reorder level: order 1.5 weeks of demand
    - If stock is healthy: order enough to maintain 2 weeks buffer
    - Minimum order of 10 units
    """
    if weekly_demand == 0:
        # No recent demand — use basic heuristic
        if current_stock < reorder_level:
            return max(reorder_level * 2, 10)
        return 0

    if current_stock <= 0:
        # Critical — order 2 weeks supply
        return max(weekly_demand * 2, 10)
    elif current_stock < reorder_level:
        # Below threshold — order 1.5 weeks supply
        return max(int(weekly_demand * 1.5), 10)
    else:
        # Healthy — check if we have less than 2 weeks buffer
        two_week_supply = weekly_demand * 2
        if current_stock < two_week_supply:
            return max(two_week_supply - current_stock, 10)
        return 0


# ── Optimize Reorder Endpoint ───────────────────────────────

@router.get("/optimize-reorder/{product_id}", response_model=ReorderResponse)
def optimize_reorder(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_store_owner)
):
    # Get inventory
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found for this product")
        
    if current_user.role == "store_owner" and inventory.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Get product name
    product = db.query(Product).filter(Product.id == product_id).first()

    # Calculate weekly demand from last 30 days of orders
    thirty_days_ago = datetime.now() - timedelta(days=30)

    total_sold = (
        db.query(func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(Order, OrderItem.order_id == Order.id)
        .filter(OrderItem.product_id == product_id)
        .filter(Order.created_at >= thirty_days_ago)
        .filter(Order.status != "cancelled")
        .scalar()
    ) or 0

    weekly_demand = int(round(total_sold / 30 * 7))

    # Calculate smart reorder
    reorder_qty = calculate_reorder_quantity(
        inventory.current_stock,
        inventory.reorder_level,
        weekly_demand
    )

    risk_level = classify_risk(inventory.current_stock, inventory.reorder_level)

    # Build explanation (supports research objective #5: explainable AI)
    product_name = product.product_name if product else f"Product #{product_id}"
    unit = inventory.unit
    stock = inventory.current_stock
    threshold = inventory.reorder_level

    # Calculate days of coverage
    daily_demand = weekly_demand / 7 if weekly_demand > 0 else 0
    days_coverage = round(stock / daily_demand, 1) if daily_demand > 0 else float('inf')
    stock_ratio = round(stock / threshold, 2) if threshold > 0 else float('inf')

    # Urgency icon
    urgency = {"Critical": "🔴", "High Risk": "🟠", "Moderate Risk": "🟡", "Low Risk": "🟢"}
    icon = urgency.get(risk_level, "⚪")

    if reorder_qty == 0:
        explanation = (
            f"{icon} Reorder Analysis for '{product_name}':\n\n"
            f"• Current stock: {stock} {unit} (threshold: {threshold})\n"
            f"• Stock-to-threshold ratio: {stock_ratio}x ✅\n"
            f"• Weekly demand: ~{weekly_demand} units\n"
            f"• Days of coverage: ~{days_coverage} days\n\n"
            f"Verdict: Stock is healthy. No reorder needed at this time."
        )
    else:
        explanation = (
            f"{icon} Reorder Analysis for '{product_name}':\n\n"
            f"• Current stock: {stock} {unit} (threshold: {threshold})\n"
            f"• Stock-to-threshold ratio: {stock_ratio}x "
            f"{'⚠️ BELOW THRESHOLD' if stock <= threshold else ''}\n"
            f"• Weekly demand: ~{weekly_demand} units "
            f"(calculated from 30-day order history: {total_sold} units sold)\n"
            f"• Days of coverage: ~{days_coverage} days "
            f"{'🚨 LESS THAN 1 WEEK' if days_coverage < 7 else ''}\n\n"
            f"Recommendation: Order {reorder_qty} {unit} to restore a 2-week safety buffer.\n\n"
            f"Reasoning: At current consumption rate of ~{round(daily_demand, 1)} {unit}/day, "
            f"stock will deplete in ~{days_coverage} days. "
            f"A 2-week buffer requires {weekly_demand * 2} {unit}. "
            f"Current shortfall: {max(weekly_demand * 2 - stock, 0)} {unit}."
        )

    return ReorderResponse(
        product_id=product_id,
        current_stock=inventory.current_stock,
        predicted_demand=weekly_demand,
        recommended_reorder_quantity=reorder_qty,
        risk_level=risk_level,
        explanation=explanation
    )
