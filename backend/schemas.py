from pydantic import BaseModel

class ProductCreate(BaseModel):
    product_name: str
    category: str
    price: float

class InventoryCreate(BaseModel):
    product_id: int
    current_stock: int
    reorder_level: int

class StockUpdate(BaseModel):
    product_id: int
    quantity_sold: int


class RFIDScan(BaseModel):
    rfid_tag: str
    event_type: str