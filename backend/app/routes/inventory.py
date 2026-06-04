# ============================================================
# INVENTORY ROUTES — Enhanced with Low-Stock Alerts
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.dependencies import get_db
from app.models import Inventory, Product
from app.schemas import (
    InventoryCreate, InventoryUpdate, InventoryResponse,
    StockUpdate, LowStockAlert
)

router = APIRouter()


# ── List All Inventory (with product name join) ──────────────

@router.get("/inventory", response_model=List[InventoryResponse])
def list_inventory(db: Session = Depends(get_db)):
    rows = (
        db.query(Inventory, Product.product_name)
        .outerjoin(Product, Inventory.product_id == Product.id)
        .order_by(Inventory.product_id)
        .all()
    )

    results = []
    for inv, product_name in rows:
        results.append(InventoryResponse(
            id=inv.id,
            product_id=inv.product_id,
            product_name=product_name,
            current_stock=inv.current_stock,
            reorder_level=inv.reorder_level,
            unit=inv.unit,
            inventory_health_score=inv.inventory_health_score,
            last_updated=inv.last_updated
        ))

    return results


# ── Add Inventory ────────────────────────────────────────────

@router.post("/inventory", response_model=InventoryResponse, status_code=201)
def add_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db)
):
    # Check product exists
    product = db.query(Product).filter(Product.id == inventory.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if inventory already exists for this product
    existing = db.query(Inventory).filter(
        Inventory.product_id == inventory.product_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Inventory already exists for this product. Use PATCH to update."
        )

    new_inventory = Inventory(
        product_id=inventory.product_id,
        current_stock=inventory.current_stock,
        reorder_level=inventory.reorder_level,
        unit=inventory.unit,
        inventory_health_score=100.0
    )

    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)

    return InventoryResponse(
        id=new_inventory.id,
        product_id=new_inventory.product_id,
        product_name=product.product_name,
        current_stock=new_inventory.current_stock,
        reorder_level=new_inventory.reorder_level,
        unit=new_inventory.unit,
        inventory_health_score=new_inventory.inventory_health_score,
        last_updated=new_inventory.last_updated
    )


# ── Update Inventory (from Replit) ───────────────────────────

@router.patch("/inventory/{product_id}", response_model=InventoryResponse)
def update_inventory(
    product_id: int,
    updates: InventoryUpdate,
    db: Session = Depends(get_db)
):
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found for this product")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(inventory, field, value)

    inventory.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(inventory)

    product = db.query(Product).filter(Product.id == product_id).first()

    return InventoryResponse(
        id=inventory.id,
        product_id=inventory.product_id,
        product_name=product.product_name if product else None,
        current_stock=inventory.current_stock,
        reorder_level=inventory.reorder_level,
        unit=inventory.unit,
        inventory_health_score=inventory.inventory_health_score,
        last_updated=inventory.last_updated
    )


# ── Update Stock (original — kept for backward compatibility) ─

@router.put("/inventory/update-stock")
def update_stock(stock: StockUpdate, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(
        Inventory.product_id == stock.product_id
    ).first()

    if not inventory:
        raise HTTPException(status_code=404, detail="Product inventory not found")

    if stock.quantity_sold > inventory.current_stock:
        raise HTTPException(status_code=400, detail="Not enough stock available")

    inventory.current_stock -= stock.quantity_sold
    inventory.last_updated = datetime.utcnow()
    db.commit()

    alert = "Stock Level Normal"
    if inventory.current_stock <= inventory.reorder_level:
        alert = "LOW STOCK ALERT"

    return {
        "message": "Stock Updated",
        "current_stock": inventory.current_stock,
        "status": alert
    }


# ── Low Stock Alerts (from Replit) ───────────────────────────

@router.get("/inventory/low-stock", response_model=List[LowStockAlert])
def get_low_stock_alerts(db: Session = Depends(get_db)):
    rows = (
        db.query(Inventory, Product.product_name)
        .join(Product, Inventory.product_id == Product.id)
        .filter(Inventory.current_stock <= Inventory.reorder_level)
        .order_by(Inventory.current_stock)
        .all()
    )

    alerts = []
    for inv, product_name in rows:
        alerts.append(LowStockAlert(
            product_id=inv.product_id,
            product_name=product_name,
            current_stock=inv.current_stock,
            reorder_level=inv.reorder_level,
            unit=inv.unit,
            deficit=inv.reorder_level - inv.current_stock
        ))

    return alerts
