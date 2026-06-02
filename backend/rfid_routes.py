from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import RFIDEvent
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

    new_event = RFIDEvent(
        rfid_tag=scan.rfid_tag,
        event_type=scan.event_type
    )

    db.add(new_event)

    db.commit()

    db.refresh(new_event)

    return {
        "message": "RFID Event Recorded",
        "event_id": new_event.id
    }