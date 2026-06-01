from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Product
from schemas import ProductCreate

router = APIRouter()

# Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/products")
def add_product(product: ProductCreate,
                db: Session = Depends(get_db)):

    new_product = Product(
        product_name=product.product_name,
        category=product.category,
        price=product.price
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product Added",
        "product_id": new_product.id
    }


@router.get("/products")
def get_products(db: Session = Depends(get_db)):

    products = db.query(Product).all()

    return products