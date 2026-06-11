from pydantic import BaseModel
from typing import List, Optional
from app.schemas import ProductResponse

class ChatRequest(BaseModel):
    customer_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str
    suggested_products: List[ProductResponse] = []
