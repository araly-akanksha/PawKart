from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import RFIDEvent, Inventory
from schemas import RFIDScan

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/rfid-scan")
def rfid_scan(
    scan: RFIDScan,
    db: Session = Depends(get_db)
):

    event = RFIDEvent(
        product_id=scan.product_id,
        event_type=scan.event_type
    )

    db.add(event)

    inventory = db.query(Inventory).filter(
        Inventory.product_id == scan.product_id
    ).first()

    if inventory:

        if scan.event_type == "SALE":

            inventory.current_stock -= 1

        elif scan.event_type == "RESTOCK":

            inventory.current_stock += 1

    db.commit()

    return {
        "message": "RFID Event Recorded",
        "event_type": scan.event_type,
        "current_stock":
        inventory.current_stock if inventory else None
    }