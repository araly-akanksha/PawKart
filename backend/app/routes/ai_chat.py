import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas_chat import ChatRequest, ChatResponse
from app.models import Product
from app.schemas import ProductResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Basic keyword dictionary to map natural language to categories
CATEGORY_MAP = {
    "dog": "Dog Food",
    "puppy": "Dog Food",
    "cat": "Cat Food",
    "kitten": "Cat Food",
    "bird": "Bird Care",
    "parrot": "Bird Care",
    "fish": "Aquarium",
    "aquarium": "Aquarium",
    "toy": "Toys",
    "play": "Toys",
    "ball": "Toys",
    "health": "Healthcare",
    "medicine": "Healthcare",
    "pill": "Healthcare",
    "sick": "Healthcare"
}

@router.post("/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    NLP Customer Chatbot endpoint.
    Takes a natural language message, infers the category, and returns product recommendations.
    """
    message = request.message.lower()
    logger.info(f"Chat message received from customer {request.customer_id}: {message}")
    
    # 1. Intent & Category Extraction
    detected_category = None
    for keyword, category in CATEGORY_MAP.items():
        if keyword in message:
            detected_category = category
            break
            
    # 2. Database Querying
    products = []
    if detected_category:
        db_products = db.query(Product).filter(
            Product.category == detected_category,
            Product.available == True
        ).limit(3).all()
        
        reply = f"I found some great options in {detected_category} for you! Check these out:"
        products = [ProductResponse.model_validate(p) for p in db_products]
    else:
        # Generic recommendation fallback
        db_products = db.query(Product).filter(Product.available == True).limit(3).all()
        reply = "I'm not exactly sure what you're looking for, but here are some of our most popular items!"
        products = [ProductResponse.model_validate(p) for p in db_products]
        
    return ChatResponse(
        reply=reply,
        suggested_products=products
    )
