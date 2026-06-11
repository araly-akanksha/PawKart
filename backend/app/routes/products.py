# ============================================================
# PRODUCT ROUTES — Full CRUD
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional

from app.dependencies import get_db, get_current_store_owner, get_optional_current_user
from app import models
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate, ProductResponse, DashboardProductResponse

router = APIRouter()


# ── List Products ────────────────────────────────────────────

@router.get("/products", response_model=List[DashboardProductResponse])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user)
):
    query = db.query(Product, models.Inventory, models.Store).outerjoin(
        models.Inventory, Product.id == models.Inventory.product_id
    ).outerjoin(
        models.Store, Product.store_id == models.Store.id
    )

    if category:
        query = query.filter(Product.category == category)

    if available is not None:
        query = query.filter(Product.available == available)
        
    if current_user and current_user.role == "store_owner" and current_user.store_id:
        query = query.filter((Product.store_id == current_user.store_id) | (Product.store_id == None))

    results = query.order_by(Product.id).all()
    
    dashboard_products = []
    for prod, inv, store in results:
        qty = inv.current_stock if inv else 0
        if qty == 0:
            stock_status = "out-stock"
        elif qty < 20:
            stock_status = "low-stock"
        else:
            stock_status = "in-stock"
            
        dashboard_products.append({
            "id": prod.id,
            "name": prod.product_name,
            "category": prod.category,
            "price": prod.price,
            "location": store.name if store else "Warehouse A",
            "stockStatus": stock_status,
            "quantity": qty,
            "image": prod.image_url or f"https://placehold.co/300x200/EDE8F9/7C5CBF?text={prod.product_name.replace(' ', '+')}"
        })
    return dashboard_products


# ── Create Product ───────────────────────────────────────────

@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(
    product: ProductCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_store_owner)
):
    new_product = Product(
        product_name=product.product_name,
        description=product.description,
        category=product.category,
        price=product.price,
        sku=product.sku,
        image_url=product.image_url,
        available=product.available,
        store_id=current_user.store_id if current_user.role == "store_owner" else None
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_store_owner)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Store owner can only update their own products
    if current_user.role == "store_owner" and product.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="Not enough permissions to edit this product")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


# ── Delete Product ───────────────────────────────────────────

@router.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_store_owner)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if current_user.role == "store_owner" and product.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this product")

    db.delete(product)
    db.commit()

    return None


# ── Toggle Availability (from Replit) ────────────────────────

@router.patch("/products/{product_id}/availability", response_model=ProductResponse)
def toggle_availability(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_store_owner)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if current_user.role == "store_owner" and product.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    product.available = not product.available
    db.commit()
    db.refresh(product)

    return product

# ── Get Reviews (Mocked for Frontend) ────────────────────────
@router.get("/reviews")
def list_reviews():
    return [
      { "id": 1, "customer": "Rahul Sharma", "rating": 5, "date": "1 day ago", "text": "My dog absolutely loved the Premium Dog Food. High quality ingredients and visible improvement in coat health.", "product": "Premium Dog Food", "replied": True },
      { "id": 2, "customer": "Priya Singh", "rating": 4, "date": "3 days ago", "text": "Pet Shampoo packaging was excellent and shampoo smells fresh. Delivery was delayed by 1 day.", "product": "Pet Shampoo", "replied": False },
      { "id": 3, "customer": "Karan Johar", "rating": 1, "date": "5 days ago", "text": "Chew toy broke in 5 minutes. Not suitable for large breeds. Very disappointed.", "product": "Chew Toy", "replied": False }
    ]
