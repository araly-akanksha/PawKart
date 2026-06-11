from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_admin
from app.models import Product, Inventory, User
import pandas as pd
import io

router = APIRouter()

@router.post("/admin/upload-catalog")
async def upload_catalog(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # Expecting at least: Product Name, Category, Price
        if 'Product Name' not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'Product Name' column")

        imported_count = 0
        for _, row in df.iterrows():
            name = str(row.get('Product Name', '')).strip()
            if not name:
                continue
                
            price = float(row.get('Price', 0.0)) if pd.notna(row.get('Price')) else 0.0
            category = str(row.get('Category', 'General')).strip()
            
            # Upsert logic (check if product exists)
            product = db.query(Product).filter(Product.product_name == name).first()
            if not product:
                product = Product(
                    product_name=name,
                    category=category,
                    price=price,
                    available=True
                )
                db.add(product)
                db.flush() # To get the product ID
                
                # Add default inventory
                inv = Inventory(
                    product_id=product.id,
                    current_stock=100,
                    reorder_level=20
                )
                db.add(inv)
                imported_count += 1
            else:
                # Update existing
                product.price = price
                product.category = category
                
        db.commit()
        return {"message": f"Successfully imported/updated {imported_count} products"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
