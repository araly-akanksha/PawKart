# ============================================================
# PRODUCT ROUTES — Full CRUD
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional

from app.dependencies import get_db
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()


# ── List Products ────────────────────────────────────────────

@router.get("/products", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)

    if available is not None:
        query = query.filter(Product.available == available)

    return query.order_by(Product.id).all()


# ── Create Product ───────────────────────────────────────────

@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(
        product_name=product.product_name,
        description=product.description,
        category=product.category,
        price=product.price,
        sku=product.sku,
        image_url=product.image_url,
        available=product.available
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# ── List Categories (from Replit) ────────────────────────────
# IMPORTANT: Must be before /products/{product_id} to avoid
# "categories" being matched as a product_id parameter.

@router.get("/products/categories", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(distinct(Product.category)).order_by(Product.category).all()
    return [row[0] for row in rows if row[0]]


# ── Get Single Product ───────────────────────────────────────

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# ── Update Product ───────────────────────────────────────────

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    updates: ProductUpdate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


# ── Delete Product ───────────────────────────────────────────

@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return None


# ── Toggle Availability (from Replit) ────────────────────────

@router.patch("/products/{product_id}/availability", response_model=ProductResponse)
def toggle_availability(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.available = not product.available
    db.commit()
    db.refresh(product)

    return product
