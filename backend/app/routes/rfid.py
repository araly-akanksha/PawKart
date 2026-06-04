# ============================================================
# RFID ROUTES — Enhanced with Event History & Stats
# ============================================================
#
# Supports research objective #1:
# Real-time inventory monitoring using RFID tags
# and event-driven synchronization
#
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.dependencies import get_db
from app.models import RFIDEvent, Inventory, Product
from app.schemas import RFIDScan, RFIDEventResponse, RFIDStatsResponse

router = APIRouter()

VALID_EVENT_TYPES = {"SALE", "RESTOCK", "RETURN", "AUDIT"}


# ── RFID Scan (original — enhanced) ─────────────────────────
#
# When an RFID tag is scanned:
#   RFID Tag Scanned → Product Identified → Inventory Updated
#   → Low Stock Check → Alert Generated

@router.post("/rfid-scan")
def rfid_scan(scan: RFIDScan, db: Session = Depends(get_db)):
    # Validate event type
    if scan.event_type.upper() not in VALID_EVENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_type. Must be one of: {', '.join(VALID_EVENT_TYPES)}"
        )

    # Check product exists
    product = db.query(Product).filter(Product.id == scan.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Record the RFID event
    event = RFIDEvent(
        product_id=scan.product_id,
        rfid_tag_id=scan.rfid_tag_id,
        event_type=scan.event_type.upper()
    )
    db.add(event)

    # Update inventory based on event type
    inventory = db.query(Inventory).filter(
        Inventory.product_id == scan.product_id
    ).first()

    stock_alert = None

    if inventory:
        if scan.event_type.upper() == "SALE":
            if inventory.current_stock > 0:
                inventory.current_stock -= 1
            else:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Cannot process SALE — stock is already at 0"
                )

        elif scan.event_type.upper() == "RESTOCK":
            inventory.current_stock += 1

        elif scan.event_type.upper() == "RETURN":
            inventory.current_stock += 1

        # Check for low stock after update
        if inventory.current_stock <= inventory.reorder_level:
            stock_alert = {
                "alert": "LOW STOCK",
                "current_stock": inventory.current_stock,
                "reorder_level": inventory.reorder_level,
                "deficit": inventory.reorder_level - inventory.current_stock
            }

    db.commit()

    return {
        "message": "RFID Event Recorded",
        "event_type": scan.event_type.upper(),
        "product_id": scan.product_id,
        "product_name": product.product_name,
        "current_stock": inventory.current_stock if inventory else None,
        "stock_alert": stock_alert
    }


# ── List RFID Events ────────────────────────────────────────

@router.get("/rfid-events", response_model=List[RFIDEventResponse])
def list_rfid_events(
    product_id: Optional[int] = Query(None, description="Filter by product"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(RFIDEvent)

    if product_id:
        query = query.filter(RFIDEvent.product_id == product_id)

    if event_type:
        query = query.filter(RFIDEvent.event_type == event_type.upper())

    return query.order_by(RFIDEvent.timestamp.desc()).limit(limit).all()


# ── Latest RFID Events ──────────────────────────────────────

@router.get("/rfid-events/latest", response_model=List[RFIDEventResponse])
def get_latest_events(
    count: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    return (
        db.query(RFIDEvent)
        .order_by(RFIDEvent.timestamp.desc())
        .limit(count)
        .all()
    )


# ── RFID Event Stats ────────────────────────────────────────

@router.get("/rfid-events/stats", response_model=RFIDStatsResponse)
def get_rfid_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(RFIDEvent.id)).scalar() or 0

    def count_type(event_type: str) -> int:
        return (
            db.query(func.count(RFIDEvent.id))
            .filter(RFIDEvent.event_type == event_type)
            .scalar() or 0
        )

    return RFIDStatsResponse(
        total_events=total,
        sale_count=count_type("SALE"),
        restock_count=count_type("RESTOCK"),
        return_count=count_type("RETURN"),
        audit_count=count_type("AUDIT")
    )
