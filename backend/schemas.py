from pydantic import BaseModel

class ProductCreate(BaseModel):
    product_name: str
    category: str
    price: float