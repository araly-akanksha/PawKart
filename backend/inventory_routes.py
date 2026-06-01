from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Inventory
from schemas import InventoryCreate
from schemas import StockUpdate

router = APIRouter()

# Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/inventory")
def add_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db)
):

    new_inventory = Inventory(
        product_id=inventory.product_id,
        current_stock=inventory.current_stock,
        reorder_level=inventory.reorder_level,
        inventory_health_score=100
    )

    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)

    return {
        "message": "Inventory Added",
        "inventory_id": new_inventory.id
    }


@router.get("/inventory")
def get_inventory(
    db: Session = Depends(get_db)
):

    inventory = db.query(Inventory).all()

    return inventory

@router.put("/inventory/update-stock")
def update_stock(
    stock: StockUpdate,
    db: Session = Depends(get_db)
):

    inventory = db.query(Inventory).filter(
        Inventory.product_id == stock.product_id
    ).first()

    if not inventory:
        return {
            "error": "Product inventory not found"
        }

    if stock.quantity_sold > inventory.current_stock:
        return {
            "error": "Not enough stock available"
        }

    inventory.current_stock -= stock.quantity_sold

    db.commit()

    alert = "Stock Level Normal"

    if inventory.current_stock <= inventory.reorder_level:
        alert = "LOW STOCK ALERT"

    return {
        "message": "Stock Updated",
        "current_stock": inventory.current_stock,
        "status": alert
    }