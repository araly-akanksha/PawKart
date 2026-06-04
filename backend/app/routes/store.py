# ============================================================
# STORE SETTINGS ROUTES
# ============================================================
#
# Adapted from Replit's store management.
# Store profile with delivery configuration for
# quick-commerce operations.
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Store
from app.schemas import StoreResponse, StoreUpdate

router = APIRouter()


# ── Get Store Profile ────────────────────────────────────────
# Auto-creates a default store if none exists (like Replit)

@router.get("/store", response_model=StoreResponse)
def get_store(db: Session = Depends(get_db)):
    store = db.query(Store).first()

    if not store:
        # Auto-create default store
        store = Store(
            name="PawKart Pet Store",
            owner_name="Store Owner",
            email="owner@pawkart.com",
            is_open=True,
            opening_time="09:00",
            closing_time="21:00"
        )
        db.add(store)
        db.commit()
        db.refresh(store)

    return store


# ── Update Store Profile ────────────────────────────────────

@router.patch("/store", response_model=StoreResponse)
def update_store(updates: StoreUpdate, db: Session = Depends(get_db)):
    store = db.query(Store).first()

    if not store:
        # Auto-create then update
        store = Store(
            name="PawKart Pet Store",
            owner_name="Store Owner",
            email="owner@pawkart.com"
        )
        db.add(store)
        db.commit()
        db.refresh(store)

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(store, field, value)

    db.commit()
    db.refresh(store)

    return store
