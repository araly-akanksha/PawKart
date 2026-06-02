from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from database import SessionLocal
from models import Inventory

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/optimize-reorder/{product_id}")
def optimize_reorder(
    product_id: int,
    db: Session = Depends(get_db)
):

    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()

    if not inventory:
        return {"error": "Inventory not found"}

    suggested_reorder = max(
        int(inventory.current_stock * 0.30),
        10
    )

    return {
        "product_id": product_id,
        "current_stock": inventory.current_stock,
        "recommended_reorder_level": suggested_reorder
    }